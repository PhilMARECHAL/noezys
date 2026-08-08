"""Tests of the web interface API (dispatch layer + HTTP smoke test)."""

import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from wankoe_model.webapp import WEB_DIR, _Handler, handle_api


# ------------------------------------------------------------- dispatch
def test_parameters_endpoint_returns_the_data_file():
    params = handle_api("parameters", None)
    assert "machines" in params and "CR.5009" in params["machines"]


def test_scenario_endpoint_runs_with_overrides():
    result = handle_api(
        "scenario",
        {"overrides": {"default_scenario": {"flow_rates_tph": {"zone_1_1_feed": 125}}}},
    )
    assert result["products"]["KFS"]["present"] is True
    assert result["scenario"]["flow_rates_tph"]["zone_1_1_feed"] == 125


def test_planning_endpoint():
    plan = handle_api("planning", {})
    assert set(plan["zones"]) == {"1.1", "1.2", "1.3"}


def test_typo_surfaces_as_value_error():
    with pytest.raises(ValueError, match="did you mean"):
        handle_api("scenario", {"overrides": {"calibration": {"Wii": {"default": 15}}}})


def test_unknown_endpoint_rejected():
    with pytest.raises(ValueError, match="unknown endpoint"):
        handle_api("nope", {})


def test_sweep_endpoint_requires_config():
    with pytest.raises(ValueError, match="config"):
        handle_api("sweep", {})


def test_page_is_self_contained():
    page = (WEB_DIR / "index.html").read_text(encoding="utf-8")
    assert "WANKOE" in page
    # strict self-containment: no external scripts, styles or fonts
    assert "http://" not in page.replace("http://localhost", "")
    assert "https://" not in page


# ------------------------------------------------------------- HTTP smoke
def test_http_server_serves_page_and_api():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as res:
            assert res.status == 200
            assert b"WANKOE" in res.read()
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/scenario",
            data=json.dumps({"overrides": {}}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as res:
            body = json.loads(res.read())
            assert body["products"]["KFS"]["tph"] > 0
        # a typo returns HTTP 400 with the actionable message
        bad = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/scenario",
            data=json.dumps({"overrides": {"calibration": {"Wii": {"default": 1}}}}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(bad)
            assert False, "expected HTTP 400"
        except urllib.error.HTTPError as exc:
            assert exc.code == 400
            assert "did you mean" in json.loads(exc.read())["error"]
    finally:
        server.shutdown()
