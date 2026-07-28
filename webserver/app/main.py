"""HTTP surface for the compiler.

Three endpoints back the single-page frontend: one describes the form, one
lists the circuits, one runs a compilation and returns the routed schedule.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from . import compiler, spec

logger = logging.getLogger("ftqc.web")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(
    title="Fault-Tolerant Quantum Compiler",
    description="Compile a QASM circuit onto a surface-code lattice and watch "
    "the lattice-surgery routes it schedules.",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# One slot per concurrent compilation. A run pins a core for its whole
# duration, so without this a handful of tabs would starve each other and every
# request would hit its timeout instead of one queueing politely behind another.
_run_slots = asyncio.Semaphore(compiler.MAX_CONCURRENT_RUNS)


class CompileRequest(BaseModel):
    settings: dict[str, Any] = Field(default_factory=dict)
    circuit: str | None = None
    qasm_text: str | None = None
    qasm_name: str = "uploaded"


@app.exception_handler(compiler.CompileError)
async def _compile_error_handler(_request, exc: compiler.CompileError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/api/spec")
async def get_spec() -> dict:
    """Everything the frontend needs to render the configuration form."""
    return spec.form_spec()


@app.get("/api/circuits")
async def get_circuits() -> dict:
    return {"circuits": compiler.available_circuits()}


@app.get("/api/health")
async def health() -> dict:
    return {
        "ok": compiler.BINARY.is_file(),
        "binary": str(compiler.BINARY),
        "circuits": len(compiler.available_circuits()),
        "free_slots": _run_slots._value,  # noqa: SLF001 — diagnostics only
    }


@app.post("/api/compile")
async def compile_circuit(request: CompileRequest) -> dict:
    try:
        config = spec.build_config(request.settings)
    except spec.ConfigError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if request.qasm_text is None and not request.circuit:
        raise HTTPException(status_code=422, detail="Pick a circuit or paste QASM.")

    async with _run_slots:
        result = await run_in_threadpool(
            compiler.run_compile,
            config,
            circuit=request.circuit,
            qasm_text=request.qasm_text,
            qasm_name=request.qasm_name,
        )

    logger.info(
        "compiled circuit=%s steps=%s in %.2fs",
        request.circuit or request.qasm_name,
        result.total_steps,
        result.elapsed_seconds,
    )

    return {
        "config": config,
        "route": result.route,
        "metrics": result.metrics,
        "stdout": result.stdout,
        "elapsed_seconds": result.elapsed_seconds,
        "total_steps": result.total_steps,
        "truncated": result.truncated,
        "warnings": result.warnings,
    }


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
