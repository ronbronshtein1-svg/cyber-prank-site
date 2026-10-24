
from flask import Flask, jsonify, request
import os
import time
import secrets
from threading import Lock

app = Flask(__name__)

CONTROL_PASSWORD = os.environ.get("CONTROL_PASSWORD", "")

lock = Lock()
attack_started = None

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
    max-width: 550px;
    margin: auto;
    padding: 35px;
    border-radius: 18px;
}
h1 { color: #38bdf8; }
.green { color: #4ade80; }
.red { color: #ff4545; }
.number {
    font-size: 55px;
    font-weight: bold;
    color: #38bdf8;
}
#status { font-size: 28px; }
.small { color: #94a3b8; }
</style>
</head>

<body>
<div class="card">
    <h1>CYBER SECURITY LAB</h1>

    <h2 id="status" class="green">SERVER ONLINE</h2>
    <p id="message">Everything is working normally.</p>

    <p>Simulated requests:</p>
    <div class="number" id="count">0</div>

    <p id="round"></p>
    <p id="warning"></p>
    <p class="small">Network security demonstration</p>
</div>

<script>
async function update() {
    try {
        const response = await fetch("/api/status", {
            cache: "no-store"
        });
        const data = await response.json();

        document.getElementById("count").textContent =
            data.total;

        document.getElementById("round").textContent =
            data.round;

        const status = document.getElementById("status");
        const message = document.getElementById("message");
        const warning = document.getElementById("warning");

        if (data.phase === "online") {
            status.textContent = "SERVER ONLINE";
            status.className = "green";
            message.textContent = "Everything is working normally.";
            warning.textContent = "";
        }
        else if (data.phase === "attack") {
            status.textContent = "⚠️ SITE UNDER ATTACK!";
            status.className = "red";
            message.textContent = "Simulated traffic increasing!";
            warning.textContent = "Security alert!";
        }
        else {
            status.textContent = "💀 SERVER CRASHED!";
            status.className = "red";
            message.textContent = "503 - Service Unavailable (simulation)";
            warning.textContent = "Simulated attack complete!";
        }
    }
    catch (error) {
        console.error("Connection error:", error);
    }
}

setInterval(update, 300);
update();
</script>
</body>
</html>
"""

@app.get("/")
def home():
    return HTML


@app.get("/api/status")
def status():
    with lock:
        started = attack_started

    if started is None:
        data = {
            "phase": "online",
            "total": 0,
            "round": ""
        }
    else:
        elapsed = time.monotonic() - started

        if elapsed >= 6:
            data = {
                "phase": "crashed",
                "total": 63,
                "round": "6 rounds completed"
            }
        else:
            n = max(0, int(elapsed))
            data = {
                "phase": "attack",
                "total": 2 ** (n + 1) - 1,
                "round": f"Round {n + 1}: 2^{n} requests"
            }

    response = jsonify(data)
    response.headers["Cache-Control"] = "no-store"
    return response


def authorized():
    supplied = request.headers.get("X-Control-Key", "")
    return bool(CONTROL_PASSWORD) and secrets.compare_digest(
        supplied, CONTROL_PASSWORD
    )


@app.post("/api/start")
def start_attack():
    global attack_started

    if not authorized():
        return jsonify(error="Unauthorized"), 401

    with lock:
        attack_started = time.monotonic()

    return jsonify(message="Simulation started")


@app.post("/api/reset")
def reset():
    global attack_started

    if not authorized():
        return jsonify(error="Unauthorized"), 401

    with lock:
        attack_started = None

    return jsonify(message="Website restored")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050)
