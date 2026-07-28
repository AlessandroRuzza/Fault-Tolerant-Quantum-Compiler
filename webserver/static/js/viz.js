/*
 * Lattice renderer.
 *
 * The compiler emits WISQ's `scmr` schema: a flat lattice of `width * height`
 * nodes indexed row-major (node = y * width + x), a map from logical qubit to
 * node, and `steps` — a list where each entry holds every gate routed *in
 * parallel* during that step, each with the node path lattice surgery follows.
 *
 * So one step is one picture: a lattice with all of its paths growing at once.
 * A whole compilation is a wall of those pictures, read left to right and then
 * top to bottom.
 *
 * Each panel keeps two canvases' worth of work apart: the lattice itself (grid
 * lines, idle nodes, qubits, magic states) never changes during playback and is
 * cached in an offscreen bitmap, while only the paths are redrawn per frame.
 * On a 60x60 lattice that is the difference between 3,600 arcs per panel per
 * frame and a single blit.
 */
'use strict';

const FTQCViz = (function () {
  // ── palette ───────────────────────────────────────────────────────────
  // Read from the stylesheet rather than hardcoded, so the canvas follows the
  // light/dark switch with everything else. Cached; `refreshPalette` drops it.
  let paletteCache = null;

  function palette() {
    if (paletteCache) return paletteCache;
    const cs = getComputedStyle(document.documentElement);
    const get = (name) => cs.getPropertyValue(name).trim();
    paletteCache = {
      nodeAlg: get('--node-alg'),
      nodeMagic: get('--node-magic'),
      nodeIdle: get('--node-idle'),
      gridLine: get('--grid-line'),
      pathCx: get('--path-cx'),
      pathT: get('--path-t'),
      pathOther: get('--path-other'),
      text: get('--text'),
      textFaint: get('--text-faint'),
      surface: get('--bg-sunken'),
    };
    return paletteCache;
  }

  function refreshPalette() {
    paletteCache = null;
  }

  // ── model ─────────────────────────────────────────────────────────────

  /** Classify a gate for colouring. Two-qubit routes and T routes read very
   *  differently on the lattice — one joins two logical qubits, the other
   *  reaches out to a magic state — so they never share a colour. */
  function gateKind(gate) {
    const op = String(gate.op || '').toLowerCase();
    if (op === 't' || op === 'tdg' || op === 'tdag') return 't';
    if (op === 'cx' || op === 'cnot' || op === 'cz' || op === 'swap') return 'cx';
    return (gate.qubits && gate.qubits.length >= 2) ? 'cx' : 'other';
  }

  function kindColor(kind, p) {
    if (kind === 't') return p.pathT;
    if (kind === 'cx') return p.pathCx;
    return p.pathOther;
  }

  /**
   * Normalize a compile response into everything the renderer needs.
   * Tolerates both shapes of `map` seen in the wild: the current array of
   * [qubit, node] pairs, and the older object keyed by qubit.
   */
  function buildModel(route) {
    const arch = route.arch || {};
    const steps = Array.isArray(route.steps) ? route.steps : [];

    const qubitToNode = new Map();
    const nodeToQubit = new Map();
    const rawMap = route.map;
    if (Array.isArray(rawMap)) {
      for (const pair of rawMap) {
        if (!Array.isArray(pair) || pair.length < 2) continue;
        qubitToNode.set(Number(pair[0]), Number(pair[1]));
        nodeToQubit.set(Number(pair[1]), Number(pair[0]));
      }
    } else if (rawMap && typeof rawMap === 'object') {
      for (const [qubit, node] of Object.entries(rawMap)) {
        qubitToNode.set(Number(qubit), Number(node));
        nodeToQubit.set(Number(node), Number(qubit));
      }
    }

    let width = Number(arch.width) | 0;
    let height = Number(arch.height) | 0;
    if (!(width > 0 && height > 0)) {
      // No `arch` block: recover a square lattice big enough to hold every
      // node index that actually appears.
      let maxNode = 0;
      for (const node of nodeToQubit.keys()) maxNode = Math.max(maxNode, node);
      for (const step of steps) {
        for (const gate of step) {
          for (const node of (gate.path || [])) maxNode = Math.max(maxNode, node);
        }
      }
      width = height = Math.max(1, Math.ceil(Math.sqrt(maxNode + 1)));
    }

    const magicStates = new Set((arch.magic_states || []).map(Number));
    const algNodes = new Set(
      (arch.alg_qubits && arch.alg_qubits.length
        ? arch.alg_qubits.map(Number)
        : [...nodeToQubit.keys()])
    );

    // Per-step path geometry in lattice coordinates, plus cumulative lengths so
    // a partial reveal is a lookup rather than a re-walk. Lattice paths are
    // rectilinear and unit-spaced, so "length" is just the segment count.
    const stepData = steps.map((gates) => {
      const paths = [];
      for (const gate of gates) {
        const nodes = gate.path || [];
        if (nodes.length === 0) continue;
        const points = nodes.map((node) => ({
          x: Number(node) % width,
          y: Math.floor(Number(node) / width),
        }));
        const cumulative = [0];
        let total = 0;
        for (let i = 1; i < points.length; i += 1) {
          total += Math.hypot(points[i].x - points[i - 1].x, points[i].y - points[i - 1].y);
          cumulative.push(total);
        }
        paths.push({
          gate,
          kind: gateKind(gate),
          points,
          cumulative,
          total,
          qubits: (gate.qubits || []).map(Number),
        });
      }
      return { gates, paths };
    });

    return {
      width,
      height,
      steps: stepData,
      qubitToNode,
      nodeToQubit,
      magicStates,
      algNodes,
      gateCount: Array.isArray(route.gates) ? route.gates.length : null,
    };
  }

  // ── geometry ──────────────────────────────────────────────────────────

  /** Fit the lattice into `w x h` CSS pixels, centred, with a small margin. */
  function layout(model, w, h) {
    const pad = Math.max(6, Math.min(w, h) * 0.04);
    const cell = Math.min(
      (w - pad * 2) / Math.max(1, model.width),
      (h - pad * 2) / Math.max(1, model.height)
    );
    return {
      cell,
      originX: (w - cell * model.width) / 2 + cell / 2,
      originY: (h - cell * model.height) / 2 + cell / 2,
    };
  }

  const toPx = (geo, point) => ({
    x: geo.originX + point.x * geo.cell,
    y: geo.originY + point.y * geo.cell,
  });

  /** Walk a polyline to the point sitting `length` along it. */
  function pointAtLength(path, length) {
    const { points, cumulative } = path;
    if (points.length === 1) return points[0];
    for (let i = 1; i < points.length; i += 1) {
      if (cumulative[i] >= length || i === points.length - 1) {
        const segment = cumulative[i] - cumulative[i - 1];
        const ratio = segment > 0 ? Math.min(1, (length - cumulative[i - 1]) / segment) : 1;
        return {
          x: points[i - 1].x + (points[i].x - points[i - 1].x) * ratio,
          y: points[i - 1].y + (points[i].y - points[i - 1].y) * ratio,
        };
      }
    }
    return points[points.length - 1];
  }

  // ── static layer ──────────────────────────────────────────────────────

  function drawLattice(ctx, model, geo, w, h, opts) {
    const p = palette();
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = p.surface;
    ctx.fillRect(0, 0, w, h);

    const { cell } = geo;

    // Grid lines are a readability aid, not information; below ~9px per cell
    // they turn the panel into a grey block, so they drop out.
    if (cell >= 9) {
      ctx.strokeStyle = p.gridLine;
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let x = 0; x < model.width; x += 1) {
        const px = Math.round(geo.originX + x * cell) + 0.5;
        ctx.moveTo(px, geo.originY);
        ctx.lineTo(px, geo.originY + (model.height - 1) * cell);
      }
      for (let y = 0; y < model.height; y += 1) {
        const py = Math.round(geo.originY + y * cell) + 0.5;
        ctx.moveTo(geo.originX, py);
        ctx.lineTo(geo.originX + (model.width - 1) * cell, py);
      }
      ctx.stroke();
    }

    // Idle nodes: one path, one fill. Skipped entirely on dense lattices where
    // they would only add noise.
    if (opts.showIdle && cell >= 5) {
      const r = Math.max(0.8, cell * 0.09);
      ctx.fillStyle = p.nodeIdle;
      ctx.beginPath();
      for (let y = 0; y < model.height; y += 1) {
        for (let x = 0; x < model.width; x += 1) {
          const node = y * model.width + x;
          if (model.algNodes.has(node) || model.magicStates.has(node)) continue;
          const c = toPx(geo, { x, y });
          ctx.moveTo(c.x + r, c.y);
          ctx.arc(c.x, c.y, r, 0, Math.PI * 2);
        }
      }
      ctx.fill();
    }

    // Magic states: diamonds, so they stay distinguishable from qubits even
    // when the lattice is too small to render either at any real size.
    const magicR = Math.max(2, cell * 0.24);
    ctx.fillStyle = p.nodeMagic;
    ctx.beginPath();
    for (const node of model.magicStates) {
      const c = toPx(geo, { x: node % model.width, y: Math.floor(node / model.width) });
      ctx.moveTo(c.x, c.y - magicR);
      ctx.lineTo(c.x + magicR, c.y);
      ctx.lineTo(c.x, c.y + magicR);
      ctx.lineTo(c.x - magicR, c.y);
      ctx.closePath();
    }
    ctx.fill();

    // Logical qubits.
    const algR = Math.max(2, cell * 0.26);
    ctx.fillStyle = p.nodeAlg;
    ctx.beginPath();
    for (const node of model.algNodes) {
      const c = toPx(geo, { x: node % model.width, y: Math.floor(node / model.width) });
      ctx.moveTo(c.x + algR, c.y);
      ctx.arc(c.x, c.y, algR, 0, Math.PI * 2);
    }
    ctx.fill();

    if (opts.showLabels && cell >= 18) {
      ctx.fillStyle = p.surface;
      ctx.font = `600 ${Math.round(cell * 0.32)}px ui-monospace, monospace`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      for (const [node, qubit] of model.nodeToQubit) {
        const c = toPx(geo, { x: node % model.width, y: Math.floor(node / model.width) });
        ctx.fillText(String(qubit), c.x, c.y);
      }
    }
  }

  // ── animated layer ────────────────────────────────────────────────────

  /**
   * Draw one step's paths at `progress` (0 → nothing, 1 → every path complete).
   *
   * Every path in the step advances on the same clock: they were scheduled to
   * happen together, and showing them race to the same finish line is the whole
   * point of the picture.
   */
  function drawPaths(ctx, model, stepIndex, geo, progress, opts) {
    const step = model.steps[stepIndex];
    if (!step) return;
    const p = palette();
    const { cell } = geo;
    const lineWidth = Math.max(1.5, cell * 0.19);
    const follow = opts.highlightQubit;

    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    // Nothing has been established yet at the very start of the cycle. Bail
    // rather than stroke a zero-length dash, which round line caps would
    // otherwise render as a dot at every path's origin.
    if (progress <= 0) return;

    for (const path of step.paths) {
      const dimmed = follow !== null && follow !== undefined && !path.qubits.includes(follow);
      ctx.globalAlpha = dimmed ? 0.14 : 1;

      const color = kindColor(path.kind, p);
      const shown = path.total * progress;

      // A single-node path is a gate that needs no traversal; show it as a ring
      // rather than a zero-length line, which would otherwise vanish.
      if (path.points.length < 2 || path.total === 0) {
        const c = toPx(geo, path.points[0]);
        ctx.strokeStyle = color;
        ctx.lineWidth = lineWidth * 0.7;
        ctx.beginPath();
        ctx.arc(c.x, c.y, Math.max(3, cell * 0.34) * progress, 0, Math.PI * 2);
        ctx.stroke();
        continue;
      }

      // Reveal by dash: one dash as long as the drawn portion, followed by a
      // gap longer than the path, leaves exactly the leading `shown` units.
      const px = path.points.map((pt) => toPx(geo, pt));
      const pixelTotal = path.total * cell;
      ctx.setLineDash([Math.max(0, shown * cell), pixelTotal + cell]);

      // Casing: a wider, translucent stroke under the line keeps crossing
      // paths legible where two routes share a corridor.
      ctx.strokeStyle = color;
      ctx.globalAlpha = (dimmed ? 0.14 : 1) * 0.22;
      ctx.lineWidth = lineWidth * 2.1;
      ctx.beginPath();
      ctx.moveTo(px[0].x, px[0].y);
      for (let i = 1; i < px.length; i += 1) ctx.lineTo(px[i].x, px[i].y);
      ctx.stroke();

      ctx.globalAlpha = dimmed ? 0.14 : 1;
      ctx.lineWidth = lineWidth;
      ctx.beginPath();
      ctx.moveTo(px[0].x, px[0].y);
      for (let i = 1; i < px.length; i += 1) ctx.lineTo(px[i].x, px[i].y);
      ctx.stroke();
      ctx.setLineDash([]);

      // Leading tip, so the eye can follow which way a route is growing.
      if (progress > 0 && progress < 1 && !dimmed && cell >= 6) {
        const tip = toPx(geo, pointAtLength(path, shown));
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(tip.x, tip.y, lineWidth * 0.85, 0, Math.PI * 2);
        ctx.fill();
      }

      // Endpoints get a ring once the route lands, marking the two nodes the
      // surgery actually joins.
      if (progress >= 1 && cell >= 8) {
        ctx.strokeStyle = color;
        ctx.lineWidth = Math.max(1.2, cell * 0.09);
        for (const end of [px[0], px[px.length - 1]]) {
          ctx.beginPath();
          ctx.arc(end.x, end.y, Math.max(3, cell * 0.36), 0, Math.PI * 2);
          ctx.stroke();
        }
      }
    }
    ctx.globalAlpha = 1;
  }

  // ── panel ─────────────────────────────────────────────────────────────

  /**
   * One step's canvas. Owns its backing bitmap and its cached lattice layer;
   * `render(progress)` is cheap enough to call every frame for every panel
   * currently on screen.
   */
  class Panel {
    /**
     * `measure` is the element whose box dictates the canvas size. For a wall
     * panel that is the containing box, never the canvas: `resize` pins the
     * canvas's own width and height in pixels, so measuring the canvas would
     * read back the size we just pinned and the panel would never follow a
     * window resize. The detail canvas is sized explicitly by its caller and so
     * measures itself.
     */
    constructor(canvas, model, stepIndex, opts, measure) {
      this.canvas = canvas;
      this.measure = measure || canvas;
      this.ctx = canvas.getContext('2d');
      this.model = model;
      this.stepIndex = stepIndex;
      this.opts = opts;
      this.background = document.createElement('canvas');
      this.backgroundCtx = this.background.getContext('2d');
      this.dirty = true;
      this.cssWidth = 0;
      this.cssHeight = 0;
    }

    invalidate() {
      this.dirty = true;
    }

    /** Match the backing store to the element's CSS box and the display DPI. */
    resize() {
      const rect = this.measure.getBoundingClientRect();
      const width = Math.max(1, Math.round(rect.width));
      const height = Math.max(1, Math.round(rect.height));
      if (width === this.cssWidth && height === this.cssHeight && !this.dirty) return false;

      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      this.cssWidth = width;
      this.cssHeight = height;
      for (const canvas of [this.canvas, this.background]) {
        canvas.width = Math.round(width * dpr);
        canvas.height = Math.round(height * dpr);
      }
      // Only the backing store is set here. The canvas's *displayed* size is
      // left to CSS (wall panels) or to whoever sized it explicitly (the detail
      // canvas): writing an inline width and height back onto the element would
      // pin it at the size we just measured, and for a panel that measures its
      // container that pin is exactly what stops it from ever shrinking again.
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      this.backgroundCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
      this.geo = layout(this.model, width, height);
      this.dirty = true;
      return true;
    }

    render(progress) {
      this.resize();
      if (this.dirty) {
        drawLattice(this.backgroundCtx, this.model, this.geo, this.cssWidth, this.cssHeight, this.opts);
        this.dirty = false;
      }
      const ctx = this.ctx;
      ctx.save();
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      ctx.drawImage(this.background, 0, 0);
      ctx.restore();
      drawPaths(ctx, this.model, this.stepIndex, this.geo, progress, this.opts);
    }
  }

  // ── clock ─────────────────────────────────────────────────────────────

  /**
   * A single shared clock and a single rAF loop drive every visible panel, so
   * the wall of lattices stays in lockstep and the browser only schedules one
   * animation callback no matter how many steps are on screen.
   *
   * The cycle spends most of its time growing the routes and the tail holding
   * the finished picture, which is the frame worth actually reading.
   */
  const GROW_FRACTION = 0.72;

  function easeInOut(t) {
    return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
  }

  class Clock {
    constructor() {
      this.phase = 0;
      this.speed = 1;
      this.playing = true;
      this.cycleSeconds = 2.6;
      this.lastTimestamp = null;
      this.subscribers = new Set();
      this.frame = null;
      this.onTick = null;
    }

    get progress() {
      if (this.phase <= GROW_FRACTION) {
        return easeInOut(this.phase / GROW_FRACTION);
      }
      return 1;
    }

    subscribe(fn) {
      this.subscribers.add(fn);
      this.start();
      return () => this.subscribers.delete(fn);
    }

    setPhase(phase) {
      this.phase = Math.min(0.999999, Math.max(0, phase));
      this.emit();
    }

    play() {
      this.playing = true;
      this.lastTimestamp = null;
      this.start();
    }

    pause() {
      this.playing = false;
    }

    start() {
      if (this.frame !== null) return;
      const step = (timestamp) => {
        this.frame = requestAnimationFrame(step);
        if (this.lastTimestamp === null) this.lastTimestamp = timestamp;
        const delta = (timestamp - this.lastTimestamp) / 1000;
        this.lastTimestamp = timestamp;
        if (this.playing) {
          this.phase = (this.phase + (delta * this.speed) / this.cycleSeconds) % 1;
          this.emit();
        }
      };
      this.frame = requestAnimationFrame(step);
    }

    stop() {
      if (this.frame !== null) cancelAnimationFrame(this.frame);
      this.frame = null;
      this.lastTimestamp = null;
    }

    emit() {
      const progress = this.progress;
      for (const fn of this.subscribers) fn(progress);
      if (this.onTick) this.onTick(this.phase, progress);
    }
  }

  return {
    buildModel,
    gateKind,
    kindColor,
    palette,
    refreshPalette,
    layout,
    drawLattice,
    drawPaths,
    Panel,
    Clock,
  };
})();
