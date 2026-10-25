
from flask import Flask, jsonify, request
from threading import Lock
import secrets
import time
import os

app = Flask(__name__)

CONTROL_PASSWORD = os.environ.get("CONTROL_PASSWORD", "")

lock = Lock()
started = None
rounds = 10
real_requests = 0

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Cyber Security Lab</title>
    <meta name="viewport"
          content="width=device-width, initial-scale=1">

    <style>
        body {
            background: #0b1120;
            color: white;
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px 15px;
        }

        .card {
            background: #1e293b;
            max-width: 520px;
            margin: auto;
            padding: 35px;
            border-radius: 18px;
        }

        h1 { color: #38bdf8; }
        .green { color: #4ade80; }
        .red { color: #ff4545; }

        .number {
            color: #38bdf8;
            font-size: 52px;
            font-weight: bold;
        }

        .small {
            color: #94a3b8;
            font-size: 14px;
        }
    </style>
</head>

<body>
<div class="card">
    <h1>CYBER SECURITY LAB</h1>

    <h2 id="status" class="green">SERVER ONLINE</h2>

    <p id="message">Website working normally.</p>

    <p>Simulated Requests:</p>
    <div id="count" class="number">0</div>

    <h3 id="round"></h3>

    <p>
        Actual HTTP Requests:
        <span id="real">0</span>
    </p>

    <p id="warning"></p>
    <p class="small">Controlled security experiment</p>
</div>

<script>
async function update() {
    const status = document.getElementById("status");
    const message = document.getElementById("message");
    const warning = document.getElementById("warning");

    try {
        const response = await fetch("/api/status", {
            cache: "no-store"
        });

        if (!response.ok) {
            throw new Error("Server unavailable");
        }

        const data = await response.json();

        document.getElementById("count").textContent =
            data.simulated.toLocaleString();

        document.getElementById("real").textContent =
            data.real;

        document.getElementById("round").textContent =
            data.round;

        if (data.phase === "online") {
            status.textContent = "SERVER ONLINE";
            status.className = "green";

            message.textContent =
                "Website working normally.";

            warning.textContent = "";
        }

        else if (data.phase === "running") {
            status.textContent = "SITE UNDER ATTACK!";
            status.className = "red";

            message.textContent =
                "Simulated traffic increasing!";

            warning.textContent =
                "Security experiment in progress...";
        }

        else {
            status.textContent =
                "SIMULATED LIMIT REACHED";

            status.className = "red";

            message.textContent =
                "Website shutdown requested.";

            warning.textContent =
                "Waiting for hosting service...";
        }

    } catch (error) {
        status.textContent = "SERVER CONNECTION LOST!";
        status.className = "red";

        message.textContent =
            "The website is currently unavailable.";

        warning.textContent =
            "Unable to contact the server.";
    }
}

setInterval(update, 1000);
update();
</script>

</body>
</html>
"""


@app.before_request
def count_request():
    global real_requests

    with lock:
        real_requests += 1


@app.get("/")
def home():
    return HTML


@app.get("/api/status")
def status():
    with lock:
        start_time = started
        selected_rounds = rounds
        actual = real_requests

    if start_time is None:
        phase = "online"
        simulated = 0
        round_label = ""

    else:
        elapsed = time.monotonic() - start_time

        if elapsed >= selected_rounds:
            phase = "finished"
            simulated = 2 ** selected_rounds - 1
            round_label = "Countdown completed"

        else:
            phase = "running"
            n = max(0, int(elapsed))

            simulated = 2 ** (n + 1) - 1
            round_label = (
                f"Round {n + 1} of {selected_rounds}"
            )

    response = jsonify(
        phase=phase,
        simulated=simulated,
        real=actual,
        round=round_label
    )

    response.headers["Cache-Control"] = "no-store"
    return response


def authorized():
    provided = request.headers.get("X-Control-Key", "")

    return (
        bool(CONTROL_PASSWORD)
        and secrets.compare_digest(
            provided, CONTROL_PASSWORD
        )
    )


@app.post("/api/start")
def start():
    global started, rounds

    if not authorized():
        return jsonify(error="Unauthorized"), 401

    data = request.get_json(silent=True) or {}

    try:
        selected = int(data.get("rounds", 10))
    except (ValueError, TypeError):
        return jsonify(error="Invalid rounds"), 400

    if selected not in (10, 12):
        return jsonify(error="Choose 10 or 12"), 400

    with lock:
        rounds = selected
        started = time.monotonic()

    return jsonify(message="Experiment started")


@app.post("/api/reset")
def reset():
    global started, real_requests

    if not authorized():
        return jsonify(error="Unauthorized"), 401

    with lock:
        started = None
        real_requests = 0

    return jsonify(message="Website restored")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050)
