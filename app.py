import os
import time
import secrets
from pathlib import Path
from threading import Lock
from flask import Flask, jsonify, request, send_file

app = Flask(__name__)

CONTROL_PASSWORD = os.getenv("CONTROL_PASSWORD", "")
lock = Lock()

started_at = None
duration = 18
request_count = 0

IMAGE_NAMES = [
    "creepy-removebg-preview.png"
]


@app.get("/monster")
def monster_image():
    folder = Path(app.root_path) / "static"

    for name in IMAGE_NAMES:
        file = folder / name
        if file.is_file():
            return send_file(file)

    # Fallback: find another image automatically
    if folder.exists():
        for file in sorted(folder.iterdir()):
            if file.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
                return send_file(file)

    return "Monster image missing from static folder", 404


PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Daily Edit</title>

<link href="https://fonts.googleapis.com/css2?family=UnifrakturCook:wght@700&family=MedievalSharp&display=swap" rel="stylesheet">

<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    background: #f7f5f0;
    color: #222;
    font-family: Arial, sans-serif;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1100px;
    margin: auto;
    padding: 25px;
}

.logo {
    font-size: 25px;
    font-weight: 800;
}

nav { color: #888; }

.hero {
    padding: 110px 20px;
    background: #ebe8e0;
    text-align: center;
}

.hero h1 {
    font-size: clamp(36px, 7vw, 70px);
    margin: 0 0 20px;
}

.hero p {
    font-size: 18px;
    color: #777;
}

main {
    max-width: 1100px;
    margin: 70px auto;
    padding: 20px;
}

.cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}

article {
    border-radius: 16px;
    background: white;
    padding: 30px;
    box-shadow: 0 4px 25px #0000000d;
}

article p {
    color: #777;
    line-height: 1.6;
}

footer {
    text-align: center;
    color: #999;
    padding: 40px;
}

#normalCount {
    font-size: 10px;
    margin-top: 12px;
}

/* HORROR SCREEN */

#horror {
    position: fixed;
    inset: 0;
    z-index: 9999;
    display: none;
    overflow: hidden;
    color: white;
    background:
      radial-gradient(ellipse at center,
        #55000e 0%, #170004 45%, #020001 100%);
}

#horror.active { display: block; }

#horror::before {
    content: "";
    position: absolute;
    inset: 0;
    z-index: 4;
    pointer-events: none;
    box-shadow: inset 0 0 170px 50px #000c;
}

/* WET BLOOD */

.blood-top {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 75px;
    z-index: 8;
    background: linear-gradient(
        #cf1029,
        #980015 40%,
        #4c0007
    );
    box-shadow:
        0 10px 35px #640007,
        inset 0 8px 14px #ffb2b23b;
}

.blood-top::before {
    content: "";
    position: absolute;
    inset: 0 0 auto;
    height: 16px;
    background: linear-gradient(#ffffff26, transparent);
}

.drip {
    position: absolute;
    top: 65px;
    width: 28px;
    border-radius: 0 0 50% 50%;
    transform-origin: top;
    background: linear-gradient(
        90deg,
        #3f0005,
        #a00013 30%,
        #d00923 60%,
        #610007
    );
    box-shadow:
        inset 3px 0 6px #ffb4b433,
        inset -4px 0 9px #0009;
    animation: ooze 7s ease-in-out infinite;
}

.drip::after {
    content: "";
    position: absolute;
    width: 125%;
    height: 30px;
    bottom: -14px;
    left: -12%;
    border-radius: 50%;
    background: radial-gradient(
        circle at 33% 25%,
        #ff8c8c77,
        #b50019 35%,
        #520006 100%
    );
}

.d1 { left: 5%; height: 100px; animation-delay: -1s; }
.d2 { left: 16%; height: 145px; animation-delay: -3s; }
.d3 { left: 29%; height: 75px; animation-delay: -2s; }
.d4 { left: 41%; height: 165px; animation-delay: -4s; }
.d5 { left: 54%; height: 110px; animation-delay: -.5s; }
.d6 { left: 67%; height: 135px; animation-delay: -3.5s; }
.d7 { left: 79%; height: 85px; animation-delay: -2s; }
.d8 { left: 91%; height: 125px; animation-delay: -1.5s; }

@keyframes ooze {
    0%, 100% { transform: scaleY(.87); }
    50% { transform: scaleY(1.13); }
}

/* MOVING SHADOWS */

.fog {
    position: absolute;
    inset: -20%;
    background:
      radial-gradient(ellipse at 30% 50%, #bd001a38, transparent 50%),
      radial-gradient(ellipse at 70% 70%, #8a001438, transparent 50%);
    filter: blur(55px);
    animation: fogMove 12s ease-in-out infinite alternate;
}

@keyframes fogMove {
    from { transform: translateX(-5%); }
    to { transform: translateX(5%); }
}

/* MONSTERS */

.monster {
    position: absolute;
    z-index: 2;
    object-fit: contain;
    pointer-events: none;
    max-height: 65vh;
    filter:
      brightness(.82)
      contrast(1.4)
      drop-shadow(0 0 28px #bd001d88);
}

.m1 {
    width: 35vw;
    max-width: 330px;
    left: 50%;
    top: 16%;
    transform: translateX(-50%) scale(1.3);
    opacity: .28;
}

.m2 {
    width: 20vw;
    max-width: 190px;
    left: 10%;
    top: -20px;
    transform: rotate(180deg);
}

.m3 {
    width: 19vw;
    max-width: 180px;
    left: -20px;
    top: 42%;
    transform: rotate(-32deg);
}

.m4 {
    width: 20vw;
    max-width: 185px;
    right: -20px;
    top: 35%;
    transform: rotate(28deg) scaleX(-1);
}

.m5 {
    width: 24vw;
    max-width: 230px;
    right: 21%;
    bottom: -60px;
    transform: rotate(-15deg);
}

/* ANCIENT HORROR TEXT */

.message {
    position: absolute;
    z-index: 6;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 160px 18px 100px;
}

#warning {
    font-family: "UnifrakturCook", "MedievalSharp", serif;
    font-size: clamp(39px, 7.5vw, 94px);
    color: #ff1b38;
    max-width: 1000px;
    min-height: 1.4em;
    line-height: 1.15;
    text-shadow:
        0 0 12px #ff163b,
        0 0 35px #ad001b,
        0 0 65px #650008;
}

#subtext {
    font-family: "MedievalSharp", serif;
    color: #e6a6ae;
    font-size: clamp(15px, 2.5vw, 26px);
    letter-spacing: 2px;
    margin-top: 20px;
    min-height: 2em;
    text-shadow: 0 0 18px #a0001a;
}

#offlineMessage {
    display: none;
    margin-top: 30px;
    color: #ff6a79;
    font-family: "MedievalSharp", serif;
    font-size: 20px;
}

/* COUNTER */

.counter {
    position: absolute;
    z-index: 10;
    right: 15px;
    bottom: 15px;
    font-size: 11px;
    color: #b9848a;
    background: #12000499;
    padding: 9px 12px;
    border: 1px solid #6f1121;
    border-radius: 9px;
}

.counter b { color: #ff6074; }

@media(max-width:700px) {
    .cards { grid-template-columns: 1fr; }
    .m1 { width: 48vw; }
    .m2 { width: 28vw; left: 4%; }
    .m3 { width: 25vw; }
    .m4 { width: 25vw; }
    .m5 { width: 35vw; }
}

@media(prefers-reduced-motion:reduce) {
    .drip, .fog { animation: none; }
}
</style>
</head>

<body>

<header>
    <div class="logo">The Daily Edit.</div>
    <nav>Stories &nbsp; About</nav>
</header>

<section class="hero">
    <h1>A little inspiration for every day.</h1>
    <p>Fresh perspectives on the things that matter.</p>
</section>

<main>
    <h2>Featured Stories</h2>
    <div class="cards">
        <article>
            <h3>Small Things, Big Changes</h3>
            <p>Simple habits that transform everyday life.</p>
        </article>
        <article>
            <h3>Living With Technology</h3>
            <p>Finding balance in a connected world.</p>
        </article>
        <article>
            <h3>Making Room for Creativity</h3>
            <p>Discover inspiration in ordinary moments.</p>
        </article>
    </div>
</main>

<footer>
    © The Daily Edit
    <div id="normalCount">
        HTTP requests served: <span id="actual">0</span>
    </div>
</footer>

<div id="horror">
    <div class="blood-top">
        <i class="drip d1"></i>
        <i class="drip d2"></i>
        <i class="drip d3"></i>
        <i class="drip d4"></i>
        <i class="drip d5"></i>
        <i class="drip d6"></i>
        <i class="drip d7"></i>
        <i class="drip d8"></i>
    </div>

    <div class="fog"></div>

    <img class="monster m1" src="/static/creepy-removebg-preview.png" alt="">
    <img class="monster m2" src="/static/creepy-removebg-preview.png" alt="">
    <img class="monster m3" src="/static/creepy-removebg-preview.png" alt="">
    <img class="monster m4" src="/static/creepy-removebg-preview.png" alt="">
    <img class="monster m5" src="/static/creepy-removebg-preview.png" alt="">

    <div class="message">
        <div id="warning"></div>
        <div id="subtext"></div>
        <div id="offlineMessage">
            THE CONNECTION HAS BEEN SEVERED
        </div>
    </div>

    <div class="counter">
        HTTP requests served: <b id="hActual">0</b>
    </div>
</div>

<script>
let active = false;
let failures = 0;
let timers = [];

function typeLine(id, text, speed, delay) {
    const el = document.getElementById(id);
    el.textContent = "";

    for (let i = 1; i <= text.length; i++) {
        timers.push(setTimeout(() => {
            el.textContent = text.slice(0, i);
        }, delay + i * speed));
    }
}

function startHorror() {
    if (active) return;
    active = true;

    document.getElementById("horror")
        .classList.add("active");

    typeLine(
        "warning",
        "YOU SHOULD NOT HAVE COME HERE",
        145,
        0
    );

    typeLine(
        "subtext",
        "IT SEES YOU. IT KNOWS YOU ARE HERE.",
        100,
        5300
    );
}

function stopHorror() {
    if (!active) return;
    active = false;
    timers.forEach(clearTimeout);
    timers = [];
    document.getElementById("horror")
        .classList.remove("active");
    document.getElementById("offlineMessage")
        .style.display = "none";
}

async function poll() {
    try {
        const response = await fetch(
            "/api/status?t=" + Date.now(),
            { cache: "no-store" }
        );

        if (!response.ok) throw Error("Request failed");

        const data = await response.json();
        failures = 0;

        document.getElementById("actual")
            .textContent = data.actual.toLocaleString();

        document.getElementById("hActual")
            .textContent = data.actual.toLocaleString();

        if (data.phase !== "online") {
            startHorror();
        } else {
            stopHorror();
        }

        document.getElementById("offlineMessage")
            .style.display = "none";

    } catch (e) {
        failures++;

        // Do not mistake a single network error
        // for a confirmed hosting suspension.
        if (active && failures >= 3) {
            document.getElementById("offlineMessage")
                .style.display = "block";
        }
    }
}

setInterval(poll, 1000);
poll();
</script>
</body>
</html>
"""


def get_state():
    with lock:
        start = started_at
        seconds = duration
        count = request_count

    if start is None:
        return "online", count

    elapsed = time.monotonic() - start
    phase = "complete" if elapsed >= seconds else "running"
    return phase, count


def authorized():
    supplied = request.headers.get("X-Control-Key", "")
    return (
        bool(CONTROL_PASSWORD)
        and secrets.compare_digest(supplied, CONTROL_PASSWORD)
    )


@app.before_request
def count_request():
    global request_count

    with lock:
        request_count += 1


@app.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/")
def home():
    return PAGE


@app.get("/api/status")
def status():
    phase, count = get_state()
    return jsonify(
        phase=phase,
        actual=count
    )


@app.post("/api/start")
def start():
    global started_at, duration

    if not authorized():
        return jsonify(error="Unauthorized"), 401

    data = request.get_json(silent=True) or {}
    seconds = data.get("seconds")

    if type(seconds) is not int or seconds not in (18, 25):
        return jsonify(error="Choose 18 or 25 seconds"), 400

    with lock:
        started_at = time.monotonic()
        duration = seconds

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
