
from flask import Flask, jsonify, request
from threading import Lock
import os
import secrets
import time

app = Flask(__name__)

CONTROL_PASSWORD = os.getenv("CONTROL_PASSWORD", "")
lock = Lock()

started_at = None
power_level = 10

PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cyber Prank</title>
<style>
body {
    margin: 0;
    min-height: 100vh;
    display: grid;
    place-items: center;
    background: #070b16;
    color: white;
    font-family: Arial, sans-serif;
    text-align: center;
}
.panel {
    background: #152033;
    padding: 45px 25px;
    width: 85%;
    max-width: 540px;
    border-radius: 22px;
    box-shadow: 0 0 40px #081d35;
}
h1 { color: #38bdf8; }
#status { color: #4ade80; }
#count {
    font-size: clamp(65px, 14vw, 110px);
    font-weight: bold;
    color: #38bdf8;
    margin: 30px 0;
}
.small { color: #94a3b8; }
</style>
</head>
<body>
<div class="panel">
    <h1>CYBER SECURITY LAB</h1>
    <h2 id="status">SERVER ONLINE</h2>
    <div id="count">0</div>
    <p class="small">VISUAL LOAD METER</p>
</div>
<script>
async function update() {
    try {
        const r = await fetch("/api/status", {
            cache: "no-store"
        });
        const data = await r.json();

        document.getElementById("count").textContent =
            data.load.toLocaleString();

        const status = document.getElementById("status");

        if (data.phase === "online") {
            status.textContent = "SERVER ONLINE";
            status.style.color = "#4ade80";
        } else if (data.phase === "running") {
            status.textContent = "LOAD TEST DISPLAY ACTIVE";
            status.style.color = "#fb7185";
        } else {
            status.textContent = "SERVICE UNAVAILABLE";
            status.style.color = "#ff4545";
        }
    } catch (error) {
        const status = document.getElementById("status");
        status.textContent = "CONNECTION LOST";
        status.style.color = "#ff4545";
    }
}
setInterval(update, 400);
update();
</script>
</body>
</html>
"""

OFFLINE = """
<!DOCTYPE html>
<html>
<head><title>503 - Service Unavailable</title></head>
<body style="background:#120912;color:white;
text-align:center;padding-top:120px;font-family:Arial">
<h1 style="color:#ff4545">503 SERVICE UNAVAILABLE</h1>
<h2>Website Offline</h2>
</body>
</html>
"""


def get_state():
    with lock:
        started = started_at
        power = power_level

    if started is None:
        return "online", 0

    elapsed = time.monotonic() - started
    step = min(int(elapsed), power)

    if step == 0:
        load = 0
    elif power == 10:
        load = 2 ** step - 1
    else:
        load = 2 ** step

    phase = "offline" if elapsed >= power else "running"
    return phase, load


def authorized():
    supplied = request.headers.get("X-Control-Key", "")
    return bool(CONTROL_PASSWORD) and secrets.compare_digest(
        supplied, CONTROL_PASSWORD
    )


@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/")
def home():
    phase, _ = get_state()

    if phase == "offline":
        return OFFLINE, 503

    return PAGE


@app.get("/api/status")
def status():
    phase, load = get_state()
    return jsonify(phase=phase, load=load)


@app.post("/api/start")
def start():
    global started_at, power_level

    if not authorized():
        return jsonify(error="Unauthorized"), 401

    data = request.get_json(silent=True) or {}
    selected = data.get("rounds")

    if type(selected) is not int or selected not in (10, 12):
        return jsonify(error="Invalid power level"), 400

    with lock:
        power_level = selected
        started_at = time.monotonic()

    return jsonify(message="Started")


@app.post("/api/reset")
def reset():
    global started_at

    if not authorized():
        return jsonify(error="Unauthorized"), 401

    with lock:
        started_at = None

    return jsonify(message="Restored")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050)
