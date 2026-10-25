
from flask import Flask, jsonify, request
from threading import Lock
import os
import secrets
import time

app = Flask(__name__)

CONTROL_PASSWORD = os.getenv("CONTROL_PASSWORD", "")

lock = Lock()

started = None
rounds = 10
real_requests = 0

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Cyber Security Lab</title>
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body {
    background: #0b1120;
    color: white;
    font-family: Arial;
    text-align: center;
    padding: 60px 15px;
}

.card {
    background: #1e293b;
    padding: 35px;
    border-radius: 18px;
    max-width: 550px;
    margin: auto;
}

h1 { color: #38bdf8; }

.green { color: #4ade80; }
.red { color: #ff4545; }

.number {
    font-size: 55px;
    font-weight: bold;
    color: #38bdf8;
}
</style>
</head>

<body>

<div class="card">
    <h1>CYBER SECURITY LAB</h1>

    <h2 id="status" class="green">SERVER ONLINE</h2>

    <p id="message">Everything is working normally.</p>

    <h3>Simulated Requests</h3>
    <div id="count" class="number">0</div>

    <h3 id="round"></h3>

    <p>Actual HTTP requests:
       <span id="real">0</span>
    </p>
</div>

<script>
async function update() {
    try {
        const response = await fetch("/api/status", {
            cache: "no-store"
        });

        const data = await response.json();

        document.getElementById("count").textContent =
            data.simulated.toLocaleString();

        document.getElementById("real").textContent =
            data.real;

        document.getElementById("round").textContent =
            data.round;

        const status = document.getElementById("status");
        const message = document.getElementById("message");

        if (data.phase === "online") {
            status.textContent = "SERVER ONLINE";
            status.className = "green";
            message.textContent = "Everything is working normally.";
        }
        else if (data.phase === "running") {
            status.textContent = "SITE UNDER ATTACK!";
            status.className = "red";
            message.textContent = "Simulated load increasing...";
        }
        else {
            status.textContent = "503 - SERVICE UNAVAILABLE";
            status.className = "red";
            message.textContent =
                "Website intentionally taken offline.";
        }

    } catch (error) {
        document.getElementById("status").textContent =
            "CONNECTION LOST";
    }
}

setInterval(update, 500);
update();
</script>

</body>
</html>
"""

DOWN_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>503 - Service Unavailable</title>
<style>
body {
    background: #160b12;
    color: white;
    font-family: Arial;
    text-align: center;
    padding-top: 130px;
}
h1 {
    color: #ff4545;
    font-size: 45px;
}
</style>
</head>
<body>
<h1>503 - SERVICE UNAVAILABLE</h1>
<h2>Website Offline</h2>
<p>Controlled cybersecurity demonstration.</p>
</body>
</html>
"""


def get_phase():
    with lock:
        start_time = started
        selected = rounds
        actual = real_requests

    if start_time is None:
        return "online", 0, "", actual

    elapsed = time.monotonic() - start_time

    if elapsed >= selected:
        return (
            "down",
            2 ** selected - 1,
            "Experiment finished",
            actual
        )

    n = int(elapsed)

    return (
        "running",
        2 ** (n + 1) - 1,
        f"Round {n + 1} of {selected}",
        actual
    )


@app.before_request
def count_request():
    global real_requests

    with lock:
        real_requests += 1


@app.get("/")
def home():
    phase, _, _, _ = get_phase()

    if phase == "down":
        return DOWN_HTML, 503

    return HTML, 200


@app.get("/api/status")
def status():
    phase, simulated, round_name, actual = get_phase()

    response = jsonify(
        phase=phase,
        simulated=simulated,
        round=round_name,
        real=actual
    )
    response.headers["Cache-Control"] = "no-store"
    return response


def authorized():
    supplied = request.headers.get("X-Control-Key", "")

    return bool(CONTROL_PASSWORD) and secrets.compare_digest(
        supplied, CONTROL_PASSWORD
    )


@app.post("/api/start")
def start():
    global started, rounds

    if not authorized():
        return jsonify(error="Unauthorized"), 401

    data = request.get_json(silent=True) or {}

    selected = data.get("rounds", 10)

    if type(selected) is not int or selected not in (10, 12):
        return jsonify(error="Invalid power"), 400

    with lock:
        rounds = selected
        started = time.monotonic()

    return jsonify(message="Started")


@app.post("/api/reset")
def reset():
    global started, real_requests

    if not authorized():
        return jsonify(error="Unauthorized"), 401

    with lock:
        started = None
        real_requests = 0

    return jsonify(message="Restored")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050)
