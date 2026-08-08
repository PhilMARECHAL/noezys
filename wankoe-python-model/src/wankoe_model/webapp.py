"""Web interface (specification preamble) — stdlib-only HTTP server.

Zero external dependency: the server uses ``http.server`` and serves a
single self-contained page (``web/index.html``, no CDN). Every capability
of the model is exposed as a JSON endpoint over the same pure functions
used programmatically:

    GET  /                   the user interface
    GET  /api/parameters     the default parameter set (data file, verbatim)
    GET  /api/measurements   stored belt-cut measurement names
    POST /api/scenario       {"overrides", "measurement"?} -> run_scenario photo
    POST /api/planning       {"overrides", "measurement"?} -> run_required_hours
    POST /api/seasonal       {"overrides", "measurement"?} -> run_seasonal_balance
    POST /api/design         {"overrides", "measurement"?, "all_measurements"?}
    POST /api/sweep          {"overrides", "config"} -> run_sweep
    POST /api/fit            {"overrides", "observations", "free_parameters"}

Errors are returned as HTTP 400 with {"error": message} — the engine's
actionable messages (typo suggestions, mode lists, capacity ceilings)
surface directly in the UI.

Run:  python -m wankoe_model.webapp [port]      (default port 8977)
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .design import run_design_check, run_design_check_all_measurements
from .feed import apply_measurement, list_measurements
from .fit import fit_parameters
from .optimize import run_sweep
from .planning import run_required_hours
from .scenario import (
    DEFAULT_PARAMETERS_PATH,
    load_parameters,
    run_scenario,
    run_seasonal_balance,
)

WEB_DIR = Path(__file__).resolve().parent / "web"


def handle_api(endpoint: str, payload: dict | None) -> dict:
    """Dispatches one API call. Pure: JSON-able payload in, JSON-able out."""
    payload = payload or {}
    if endpoint == "parameters":
        with open(DEFAULT_PARAMETERS_PATH, encoding="utf-8") as f:
            return json.load(f)
    if endpoint == "measurements":
        return {"measurements": list(list_measurements())}
    params = load_parameters(overrides=payload.get("overrides") or {})
    # optional: run against a stored belt-cut measurement instead of the default curve
    if payload.get("measurement"):
        params = apply_measurement(params, payload["measurement"])
    if endpoint == "design":
        if payload.get("all_measurements"):
            return run_design_check_all_measurements(params)
        return run_design_check(params)
    if endpoint == "scenario":
        return run_scenario(params)
    if endpoint == "planning":
        return run_required_hours(params)
    if endpoint == "seasonal":
        return run_seasonal_balance(params)
    if endpoint == "sweep":
        config = payload.get("config")
        if not config:
            raise ValueError("sweep: missing 'config' (variables, method, objective)")
        return run_sweep(params, config)
    if endpoint == "fit":
        observations = payload.get("observations")
        free_parameters = payload.get("free_parameters")
        if not observations or not free_parameters:
            raise ValueError("fit: missing 'observations' and/or 'free_parameters'")
        return fit_parameters(
            params,
            observations,
            free_parameters,
            max_rounds=int(payload.get("max_rounds", 80)),
        )
    raise ValueError(
        f"unknown endpoint '{endpoint}' "
        "(known: parameters, measurements, scenario, planning, seasonal, sweep, fit, design)"
    )


class _Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, obj) -> None:
        self._send(
            status,
            json.dumps(obj, ensure_ascii=False).encode("utf-8"),
            "application/json; charset=utf-8",
        )

    def do_GET(self):  # noqa: N802 (http.server naming)
        if self.path in ("/", "/index.html"):
            page = (WEB_DIR / "index.html").read_bytes()
            self._send(200, page, "text/html; charset=utf-8")
        elif self.path == "/api/parameters":
            try:
                self._send_json(200, handle_api("parameters", None))
            except Exception as exc:  # surfaced to the client, not swallowed
                self._send_json(400, {"error": str(exc)})
        else:
            self._send_json(404, {"error": f"not found: {self.path}"})

    def do_POST(self):  # noqa: N802
        if not self.path.startswith("/api/"):
            self._send_json(404, {"error": f"not found: {self.path}"})
            return
        endpoint = self.path[len("/api/"):]
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length) or b"{}")
            self._send_json(200, handle_api(endpoint, payload))
        except (ValueError, KeyError, ZeroDivisionError, OverflowError) as exc:
            self._send_json(400, {"error": str(exc)})

    def log_message(self, fmt, *args):  # quiet console
        pass


def serve(port: int = 8977) -> None:
    server = ThreadingHTTPServer(("0.0.0.0", port), _Handler)
    print(f"Wankoe model web interface: http://localhost:{port}/  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    serve(int(sys.argv[1]) if len(sys.argv) > 1 else 8977)
