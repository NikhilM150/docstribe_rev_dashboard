"""
server.py — DocStribe Patient Intelligence Dashboard
=====================================================
Flask proxy server for the Claude API.

The frontend calls POST /api/chat (same origin).
This server forwards the request to Anthropic, keeping the API
key securely on the server side via the ANTHROPIC_API_KEY env var.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...   # Linux/macOS
    set    ANTHROPIC_API_KEY=sk-ant-...   # Windows CMD
    $env:ANTHROPIC_API_KEY="sk-ant-..."   # Windows PowerShell

    python server.py                      # default: http://localhost:8080
    python server.py --port 5000          # custom port

The frontend is served as static files from the same origin,
so no CORS issues arise for same-origin requests. flask-cors is
still included as a safety net for dev tools / cross-origin calls.
"""

import argparse
import os
import sys

# ── Auto-install dependencies if needed ──────────────────────────────────────
def _ensure(pkg, import_name=None):
    import importlib
    try:
        importlib.import_module(import_name or pkg)
    except ImportError:
        import subprocess
        print(f"[INFO] Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

_ensure("flask")
_ensure("flask_cors", "flask_cors")
_ensure("anthropic")

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import anthropic

# ── App setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
CORS(app, resources={r"/api/*": {"origins": "*"}})

MODEL = "claude-sonnet-4-5"


# ── Health check ─────────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    """Returns server status and whether the API key is configured."""
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    return jsonify({
        "status": "ok",
        "model": MODEL,
        "apiKeyConfigured": has_key,
        "message": "API key set — proxy ready" if has_key else "ANTHROPIC_API_KEY not set",
    })


# ── Main proxy endpoint ───────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Accepts:
        {
            "messages":    [{"role": "user", "content": "..."}],
            "systemPrompt": "...",
            "maxTokens":   1024   (optional)
        }

    Returns:
        { "text": "..." }       on success
        { "error": "..." }      on failure
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify({
            "error": "ANTHROPIC_API_KEY environment variable is not set on the server."
        }), 500

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON request body."}), 400

    messages = data.get("messages")
    if not messages or not isinstance(messages, list):
        return jsonify({"error": "'messages' must be a non-empty list."}), 400

    system_prompt = data.get("systemPrompt", "")
    max_tokens    = int(data.get("maxTokens", 1024))

    # Cap max_tokens to a safe limit
    max_tokens = min(max_tokens, 4096)

    try:
        client = anthropic.Anthropic(api_key=api_key)

        kwargs = dict(
            model      = MODEL,
            max_tokens = max_tokens,
            messages   = messages,
        )
        if system_prompt:
            kwargs["system"] = system_prompt

        response = client.messages.create(**kwargs)
        text = response.content[0].text if response.content else ""
        return jsonify({"text": text})

    except anthropic.AuthenticationError:
        return jsonify({"error": "Invalid Anthropic API key on the server."}), 401
    except anthropic.RateLimitError:
        return jsonify({"error": "Anthropic rate limit reached. Please wait and retry."}), 429
    except anthropic.BadRequestError as e:
        return jsonify({"error": f"Bad request to Claude: {e}"}), 400
    except anthropic.APIError as e:
        return jsonify({"error": f"Claude API error: {e}"}), 502
    except Exception as e:
        return jsonify({"error": f"Unexpected server error: {e}"}), 500


# ── Serve index.html (and all static assets) from the same origin ────────────
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_static(path):
    if path and os.path.exists(os.path.join(BASE_DIR, path)):
        return send_from_directory(BASE_DIR, path)
    return send_from_directory(BASE_DIR, "index.html")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DocStribe proxy server")
    parser.add_argument("--port", type=int, default=8080,
                        help="Port to listen on (default: 8080)")
    parser.add_argument("--host", default="0.0.0.0",
                        help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--debug", action="store_true",
                        help="Enable Flask debug mode")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    print("\n" + "=" * 58)
    print("  DocStribe Patient Intelligence Dashboard — Proxy Server")
    print("=" * 58)
    print(f"  URL    : http://localhost:{args.port}")
    print(f"  Model  : {MODEL}")
    print(f"  API Key: {'[SET]  Proxy ready' if api_key else '[NOT SET]  Set ANTHROPIC_API_KEY env var'}")
    print("=" * 58 + "\n")

    if not api_key:
        print("[WARNING] ANTHROPIC_API_KEY is not set.")
        print("          Users can still provide their own key in the UI,")
        print("          but the server proxy will return 500 until the key is set.\n")

    app.run(host=args.host, port=args.port, debug=args.debug)
