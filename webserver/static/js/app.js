/*
 * Wiring: builds the configuration form from /api/spec, posts a run, and lays
 * the returned routing out as a wall of animated lattices.
 *
 * Panels mount lazily. A deep circuit routes into hundreds or thousands of
 * steps, and holding a live canvas for every one of them would exhaust memory
 * long before it exhausted the user's patience; an IntersectionObserver keeps
 * canvases only for the panels near the viewport and hands the rest back.
 */
'use strict';

(function () {
  const $ = (selector) => document.querySelector(selector);
  const STORAGE_KEY = 'ftqc.settings.v1';
  const THEME_KEY = 'ftqc.theme';

  const state = {
    spec: null,
    circuits: [],
    model: null,
    result: null,
    panels: new Map(),
    detailPanel: null,
    detailStep: 0,
    observer: null,
    unsubscribe: null,
    options: { showLabels: true, showIdle: true, highlightQubit: null },
  };

  const clock = new FTQCViz.Clock();

  // ── theme ─────────────────────────────────────────────────────────────

  function applyTheme(theme) {
    if (theme) document.documentElement.setAttribute('data-theme', theme);
    else document.documentElement.removeAttribute('data-theme');
    FTQCViz.refreshPalette();
    invalidateAllPanels();
  }

  function initTheme() {
    applyTheme(localStorage.getItem(THEME_KEY) || null);
    $('#theme-toggle').addEventListener('click', () => {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const current =
        document.documentElement.getAttribute('data-theme') || (prefersDark ? 'dark' : 'light');
      const next = current === 'dark' ? 'light' : 'dark';
      localStorage.setItem(THEME_KEY, next);
      applyTheme(next);
    });
  }

  // ── form ──────────────────────────────────────────────────────────────

  function fieldControl(field, value) {
    const wrapper = document.createElement('div');
    wrapper.className = field.kind === 'bool' ? 'field inline' : 'field';

    const label = document.createElement('label');
    label.textContent = field.label;
    label.htmlFor = `f-${field.key}`;

    let input;
    if (field.kind === 'enum') {
      input = document.createElement('select');
      for (const choice of field.choices) {
        const option = document.createElement('option');
        option.value = choice;
        option.textContent = choice;
        input.appendChild(option);
      }
      input.value = value;
    } else if (field.kind === 'bool') {
      input = document.createElement('input');
      input.type = 'checkbox';
      input.checked = Boolean(value);
    } else {
      // Slider plus a number box: the slider is for exploring the range, the
      // box for typing the value you already know.
      input = document.createElement('input');
      input.type = 'number';
      input.value = value;
      input.step = field.step ?? (field.kind === 'int' ? 1 : 'any');
      if (field.min !== undefined) input.min = field.min;
      if (field.max !== undefined) input.max = field.max;
    }
    input.id = `f-${field.key}`;
    input.dataset.key = field.key;
    input.dataset.kind = field.kind;

    wrapper.appendChild(label);

    if (field.kind === 'int' || field.kind === 'float') {
      const row = document.createElement('div');
      row.className = 'numeric-row';
      const range = document.createElement('input');
      range.type = 'range';
      range.min = field.min ?? 0;
      range.max = field.max ?? 100;
      range.step = field.step ?? (field.kind === 'int' ? 1 : 0.01);
      range.value = value;
      range.setAttribute('aria-label', `${field.label} slider`);
      range.addEventListener('input', () => { input.value = range.value; });
      input.addEventListener('input', () => { range.value = input.value; });
      row.append(range, input);
      wrapper.appendChild(row);
    } else {
      wrapper.appendChild(input);
    }

    if (field.help) {
      const help = document.createElement('p');
      help.className = 'help';
      help.textContent = field.help;
      wrapper.appendChild(help);
    }
    return wrapper;
  }

  function buildForm(spec, saved) {
    const container = $('#generated-groups');
    container.textContent = '';

    for (const group of spec.groups) {
      const fields = spec.fields.filter((f) => f.group === group.id);
      if (!fields.length) continue;

      const section = document.createElement('section');
      section.className = 'field-group';
      // Architecture and routing are the knobs anyone reaches for first; the
      // weights are a tuned optimum best left alone, so they start collapsed.
      if (group.id === 'architecture' || group.id === 'routing') section.classList.add('open');

      const heading = document.createElement('h2');
      heading.textContent = group.label;
      heading.tabIndex = 0;
      const toggle = () => section.classList.toggle('open');
      heading.addEventListener('click', toggle);
      heading.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); toggle(); }
      });

      const body = document.createElement('div');
      body.className = 'group-body';
      if (group.blurb) {
        const blurb = document.createElement('p');
        blurb.className = 'help group-blurb';
        blurb.textContent = group.blurb;
        body.appendChild(blurb);
      }
      for (const field of fields) {
        const value = saved && field.key in saved ? saved[field.key] : field.default;
        body.appendChild(fieldControl(field, value));
      }

      section.append(heading, body);
      container.appendChild(section);
    }
  }

  function readForm() {
    const settings = {};
    for (const input of document.querySelectorAll('#generated-groups [data-key]')) {
      const { key, kind } = input.dataset;
      if (kind === 'bool') settings[key] = input.checked;
      else if (kind === 'enum') settings[key] = input.value;
      else settings[key] = Number(input.value);
    }
    return settings;
  }

  function writeForm(settings) {
    for (const input of document.querySelectorAll('#generated-groups [data-key]')) {
      const { key, kind } = input.dataset;
      if (!(key in settings)) continue;
      if (kind === 'bool') input.checked = Boolean(settings[key]);
      else input.value = settings[key];
      input.dispatchEvent(new Event('input'));
    }
  }

  // ── circuits ──────────────────────────────────────────────────────────

  function renderCircuitOptions(filterText) {
    const select = $('#circuit-select');
    const previous = select.value;
    const needle = filterText.trim().toLowerCase();
    select.textContent = '';

    const groups = new Map();
    for (const circuit of state.circuits) {
      if (needle && !circuit.name.toLowerCase().includes(needle)) continue;
      if (!groups.has(circuit.group)) groups.set(circuit.group, []);
      groups.get(circuit.group).push(circuit);
    }

    let shown = 0;
    for (const [name, circuits] of groups) {
      const optgroup = document.createElement('optgroup');
      optgroup.label = name;
      for (const circuit of circuits) {
        const option = document.createElement('option');
        option.value = circuit.value;
        option.textContent = circuit.name;
        optgroup.appendChild(option);
        shown += 1;
      }
      select.appendChild(optgroup);
    }

    if (previous && [...select.options].some((o) => o.value === previous)) {
      select.value = previous;
    } else if (select.options.length) {
      const example = [...select.options].find((o) => o.textContent === 'example');
      select.value = (example || select.options[0]).value;
    }
    $('#circuit-count').textContent = `${shown} of ${state.circuits.length} circuits`;
  }

  // ── metrics ───────────────────────────────────────────────────────────

  // Ordered by what a reader wants first: the result, how good it is, whether
  // it is even complete, then the problem it was solving, then the analysis.
  const METRIC_LAYOUT = [
    { key: 'routing_steps', name: 'Routing steps', headline: true },
    { key: 'optimality', name: 'Optimality %', digits: 1, headline: true },
    { key: 'min_routing_steps', name: 'Lower bound' },
    { key: 'non_routed_layer_pct', name: 'Unrouted layers %', digits: 2 },
    { key: 'grid', name: 'Lattice' },
    { key: 'num_qubits', name: 'Logical qubits' },
    { key: 'resolved_number_of_magic_states', name: 'Magic states' },
    { key: 'gates', name: 'Gates' },
    { key: 'elapsed', name: 'Compile time' },
    { key: 'avg_parallelism', name: 'Avg parallelism', digits: 2 },
    { key: 'max_parallelism', name: 'Max parallelism', digits: 2 },
    { key: 'max_interaction_degree', name: 'Max degree' },
    { key: 'cnot_interaction_density', name: 'CNOT density', digits: 3 },
    { key: 'cnot_graph_modularity', name: 'CNOT modularity', digits: 3 },
  ];

  function renderMetrics(result) {
    const container = $('#metrics');
    container.textContent = '';
    const metrics = result.metrics || {};
    const arch = (result.route && result.route.arch) || {};

    // `min_routing_steps` is the circuit's layering depth, which is a genuine
    // floor: gates in different layers depend on each other, so even a perfect
    // router needs one step per layer. Optimality is how close this run got to
    // that floor — 100% means it could not have been scheduled any shallower.
    const lowerBound = metrics.min_routing_steps;
    const actual = metrics.routing_steps;
    const optimality =
      typeof lowerBound === 'number' && typeof actual === 'number' && actual > 0
        ? (lowerBound / actual) * 100
        : null;

    const derived = {
      ...metrics,
      optimality,
      grid:
        arch.width && arch.height
          ? `${arch.width}×${arch.height}`
          : metrics.resolved_graph_x && metrics.resolved_graph_y
            ? `${metrics.resolved_graph_x}×${metrics.resolved_graph_y}`
            : null,
      gates: result.route && result.route.gates ? result.route.gates.length : null,
      elapsed: `${result.elapsed_seconds.toFixed(2)}s`,
    };

    for (const entry of METRIC_LAYOUT) {
      const raw = derived[entry.key];
      if (raw === null || raw === undefined) continue;
      const card = document.createElement('div');
      card.className = entry.headline ? 'metric headline' : 'metric';
      const value = document.createElement('div');
      value.className = 'value';
      value.textContent =
        typeof raw === 'number' && entry.digits !== undefined
          ? raw.toFixed(entry.digits)
          : typeof raw === 'number'
            ? raw.toLocaleString()
            : String(raw);
      const name = document.createElement('div');
      name.className = 'name';
      name.textContent = entry.name;
      card.append(value, name);
      container.appendChild(card);
    }
  }

  // ── step wall ─────────────────────────────────────────────────────────

  function invalidateAllPanels() {
    for (const panel of state.panels.values()) panel.invalidate();
    if (state.detailPanel) state.detailPanel.invalidate();
    renderActive(clock.progress);
  }

  function renderActive(progress) {
    for (const panel of state.panels.values()) panel.render(progress);
    if (state.detailPanel && $('#detail').open) state.detailPanel.render(progress);
  }

  function mountPanel(element) {
    const index = Number(element.dataset.step);
    if (state.panels.has(index)) return;
    const box = element.querySelector('.canvas-box');
    const canvas = document.createElement('canvas');
    box.appendChild(canvas);
    const panel = new FTQCViz.Panel(canvas, state.model, index, state.options, box);
    state.panels.set(index, panel);
    panel.render(clock.progress);
  }

  function unmountPanel(element) {
    const index = Number(element.dataset.step);
    const panel = state.panels.get(index);
    if (!panel) return;
    panel.canvas.remove();
    state.panels.delete(index);
  }

  function buildStepWall(model) {
    const container = $('#steps');
    container.textContent = '';
    if (state.observer) state.observer.disconnect();
    state.panels.clear();

    // Keep panels roughly the lattice's shape, but refuse the extremes: a
    // 4x120 lattice would otherwise produce a column of slivers.
    const ratio = Math.min(2.4, Math.max(0.55, model.width / Math.max(1, model.height)));

    const fragment = document.createDocumentFragment();
    model.steps.forEach((step, index) => {
      const element = document.createElement('div');
      element.className = 'step';
      element.dataset.step = String(index);
      element.setAttribute('role', 'listitem');
      element.tabIndex = 0;
      element.setAttribute(
        'aria-label',
        `Routing step ${index + 1}, ${step.paths.length} routes. Activate to enlarge.`
      );

      const head = document.createElement('div');
      head.className = 'step-head';
      head.innerHTML =
        `<span class="step-index">step ${index + 1}</span>` +
        `<span class="step-count">${step.paths.length} route${step.paths.length === 1 ? '' : 's'}</span>`;

      const box = document.createElement('div');
      box.className = 'canvas-box';
      box.style.setProperty('--ratio', String(ratio));

      element.append(head, box);
      element.addEventListener('click', () => openDetail(index));
      element.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); openDetail(index); }
      });
      fragment.appendChild(element);
    });
    container.appendChild(fragment);

    // The generous margin means a panel is already drawn by the time it
    // scrolls into view, so fast scrolling never shows an empty box.
    state.observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) mountPanel(entry.target);
          else unmountPanel(entry.target);
        }
      },
      { root: null, rootMargin: '600px 0px', threshold: 0 }
    );
    for (const element of container.children) state.observer.observe(element);
  }

  // ── detail dialog ─────────────────────────────────────────────────────

  function renderGateList(index) {
    const list = $('#detail-gates');
    list.textContent = '';
    const step = state.model.steps[index];
    if (!step) return;
    for (const path of step.paths) {
      const item = document.createElement('li');
      item.className = `op-${path.kind}`;
      const qubits = path.qubits.join(', ');
      item.innerHTML =
        `<span class="op">${path.gate.op}</span> q[${qubits}]` +
        `<div class="meta">${path.points.length} node${path.points.length === 1 ? '' : 's'}` +
        ` · gate #${path.gate.id}</div>`;
      list.appendChild(item);
    }
  }

  function sizeDetailCanvas() {
    if (!state.detailPanel) return;
    const box = $('.detail-canvas');
    const rect = box.getBoundingClientRect();
    const ratio = state.model.width / Math.max(1, state.model.height);
    let width = rect.width - 2;
    let height = width / ratio;
    if (height > rect.height - 2) {
      height = rect.height - 2;
      width = height * ratio;
    }
    state.detailPanel.canvas.style.width = `${Math.max(80, width)}px`;
    state.detailPanel.canvas.style.height = `${Math.max(80, height)}px`;
    state.detailPanel.invalidate();
  }

  function openDetail(index) {
    const dialog = $('#detail');
    state.detailStep = index;
    const step = state.model.steps[index];

    $('#detail-title').textContent = `Routing step ${index + 1} of ${state.model.steps.length}`;
    $('#detail-subtitle').textContent =
      `${step.paths.length} route${step.paths.length === 1 ? '' : 's'} scheduled in parallel` +
      ` on a ${state.model.width}×${state.model.height} lattice`;
    renderGateList(index);

    const canvas = $('#detail-canvas');
    // Inherit from the live options object rather than copying it, so toggling
    // "follow qubit" or "idle nodes" while the dialog is open still reaches it.
    // Labels are the one override: at this size they always fit.
    const detailOptions = Object.create(state.options);
    detailOptions.showLabels = true;
    state.detailPanel = new FTQCViz.Panel(canvas, state.model, index, detailOptions, canvas);
    if (!dialog.open) dialog.showModal();
    requestAnimationFrame(() => {
      sizeDetailCanvas();
      state.detailPanel.render(clock.progress);
    });
  }

  function stepDetail(delta) {
    const next = state.detailStep + delta;
    if (next < 0 || next >= state.model.steps.length) return;
    openDetail(next);
  }

  // ── controls ──────────────────────────────────────────────────────────

  function initControls() {
    const playToggle = $('#play-toggle');
    playToggle.addEventListener('click', () => {
      if (clock.playing) {
        clock.pause();
        playToggle.textContent = 'Play';
        playToggle.setAttribute('aria-pressed', 'false');
      } else {
        clock.play();
        playToggle.textContent = 'Pause';
        playToggle.setAttribute('aria-pressed', 'true');
      }
    });

    const speed = $('#speed');
    speed.addEventListener('input', () => {
      clock.speed = Number(speed.value);
      $('#speed-out').textContent = `${clock.speed.toFixed(2)}×`;
    });

    const columns = $('#columns');
    columns.addEventListener('input', () => {
      const value = Number(columns.value);
      $('#columns-out').textContent = value === 0 ? 'auto' : String(value);
      const steps = $('#steps');
      if (value === 0) {
        steps.style.setProperty('--columns', 'auto-fill');
        steps.style.setProperty('--min-col', '220px');
      } else {
        steps.style.setProperty('--columns', String(value));
        steps.style.setProperty('--min-col', '0px');
      }
      invalidateAllPanels();
    });

    const scrub = $('#scrub');
    let scrubbing = false;
    scrub.addEventListener('pointerdown', () => {
      scrubbing = true;
      clock.pause();
      playToggle.textContent = 'Play';
      playToggle.setAttribute('aria-pressed', 'false');
    });
    scrub.addEventListener('pointerup', () => { scrubbing = false; });
    scrub.addEventListener('input', () => {
      clock.setPhase(Number(scrub.value) / 1000);
    });
    clock.onTick = (phase, progress) => {
      if (!scrubbing) scrub.value = String(Math.round(phase * 1000));
      $('#scrub-out').textContent = `${Math.round(progress * 100)}%`;
    };

    $('#show-labels').addEventListener('change', (event) => {
      state.options.showLabels = event.target.checked;
      invalidateAllPanels();
    });
    $('#show-idle').addEventListener('change', (event) => {
      state.options.showIdle = event.target.checked;
      invalidateAllPanels();
    });
    $('#highlight').addEventListener('change', (event) => {
      const value = event.target.value;
      state.options.highlightQubit = value === '' ? null : Number(value);
      renderActive(clock.progress);
    });

    $('#download-route').addEventListener('click', () => {
      if (!state.result) return;
      const blob = new Blob([JSON.stringify(state.result.route, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'route.json';
      link.click();
      URL.revokeObjectURL(url);
    });

    $('#detail-close').addEventListener('click', () => $('#detail').close());
    $('#detail-prev').addEventListener('click', () => stepDetail(-1));
    $('#detail-next').addEventListener('click', () => stepDetail(1));
    $('#detail').addEventListener('close', () => { state.detailPanel = null; });
    $('#detail').addEventListener('click', (event) => {
      // Clicking the backdrop (i.e. the dialog element itself) closes it.
      if (event.target === $('#detail')) $('#detail').close();
    });
    document.addEventListener('keydown', (event) => {
      if (!$('#detail').open) return;
      if (event.key === 'ArrowLeft') stepDetail(-1);
      if (event.key === 'ArrowRight') stepDetail(1);
    });

    // Resize fires in bursts while a window is dragged, and each one repaints
    // the cached lattice of every mounted panel. Collapse a burst into one
    // repaint on the next frame, once the layout has settled.
    let resizeFrame = null;
    window.addEventListener('resize', () => {
      if (resizeFrame !== null) return;
      resizeFrame = requestAnimationFrame(() => {
        resizeFrame = null;
        if ($('#detail').open) sizeDetailCanvas();
        invalidateAllPanels();
      });
    });

    $('#circuit-source').addEventListener('change', (event) => {
      const paste = event.target.value === 'paste';
      $('#qasm-paste').classList.toggle('hidden', !paste);
      $('#circuit-picker').classList.toggle('hidden', paste);
    });
    $('#circuit-filter').addEventListener('input', (event) => {
      renderCircuitOptions(event.target.value);
    });

    $('#reset-button').addEventListener('click', () => {
      writeForm(state.spec.defaults);
      localStorage.removeItem(STORAGE_KEY);
      setStatus('Settings reset to the tuned defaults.');
    });
  }

  // ── run ───────────────────────────────────────────────────────────────

  function setStatus(message, isError) {
    const status = $('#form-status');
    status.textContent = message || '';
    status.classList.toggle('error', Boolean(isError));
  }

  function renderWarnings(warnings) {
    const container = $('#warnings');
    container.textContent = '';
    for (const warning of warnings || []) {
      const note = document.createElement('div');
      note.className = 'note';
      note.textContent = warning;
      container.appendChild(note);
    }
  }

  function populateHighlight(model) {
    const select = $('#highlight');
    select.textContent = '';
    const none = document.createElement('option');
    none.value = '';
    none.textContent = '— none —';
    select.appendChild(none);
    for (const qubit of [...model.qubitToNode.keys()].sort((a, b) => a - b)) {
      const option = document.createElement('option');
      option.value = String(qubit);
      option.textContent = `q[${qubit}]`;
      select.appendChild(option);
    }
    state.options.highlightQubit = null;
  }

  async function compile(event) {
    event.preventDefault();
    const button = $('#compile-button');
    button.disabled = true;
    button.classList.add('busy');
    setStatus('Compiling…');

    const settings = readForm();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));

    const body = { settings };
    if ($('#circuit-source').value === 'paste') {
      body.qasm_text = $('#qasm-text').value;
      body.qasm_name = 'pasted';
    } else {
      body.circuit = $('#circuit-select').value;
    }

    try {
      const response = await fetch('/api/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || 'The compilation failed.');

      state.result = payload;
      state.model = FTQCViz.buildModel(payload.route);

      $('#empty-state').classList.add('hidden');
      $('#result-view').classList.remove('hidden');

      renderWarnings(payload.warnings);
      renderMetrics(payload);
      populateHighlight(state.model);
      buildStepWall(state.model);

      if (state.unsubscribe) state.unsubscribe();
      state.unsubscribe = clock.subscribe(renderActive);
      clock.play();
      $('#play-toggle').textContent = 'Pause';

      const shown = state.model.steps.length;
      setStatus(
        `Routed in ${payload.total_steps} step${payload.total_steps === 1 ? '' : 's'}` +
        `${payload.truncated ? ` (showing ${shown})` : ''} · ${payload.elapsed_seconds.toFixed(2)}s`
      );
    } catch (error) {
      setStatus(error.message, true);
    } finally {
      button.disabled = false;
      button.classList.remove('busy');
    }
  }

  // ── boot ──────────────────────────────────────────────────────────────

  async function init() {
    initTheme();
    initControls();
    $('#config-form').addEventListener('submit', compile);

    try {
      const [spec, circuits] = await Promise.all([
        fetch('/api/spec').then((r) => r.json()),
        fetch('/api/circuits').then((r) => r.json()),
      ]);
      state.spec = spec;
      state.circuits = circuits.circuits || [];

      let saved = null;
      try {
        saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
      } catch {
        saved = null;
      }
      buildForm(spec, saved);
      renderCircuitOptions('');

      if (!state.circuits.length) {
        setStatus('No bundled circuits found — paste QASM instead.', true);
      }
    } catch (error) {
      setStatus(`Could not reach the compiler service: ${error.message}`, true);
    }
  }

  init();
})();
