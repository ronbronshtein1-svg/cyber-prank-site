import os
import secrets
import time
from threading import Lock

from flask import Flask, jsonify, request

app = Flask(__name__)

CONTROL_PASSWORD = os.environ.get("CONTROL_PASSWORD", "")
lock = Lock()

started_at = None
duration = 12
request_count = 0


PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Daily Edit</title>

<link href="https://fonts.googleapis.com/css2?family=UnifrakturCook:wght@700&family=MedievalSharp&display=swap" rel="stylesheet">

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #faf9f6;
    color: #262626;
}

/* NORMAL WEBSITE */

header {
    max-width: 1100px;
    margin: auto;
    padding: 25px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 25px;
    font-weight: bold;
}

nav {
    color: #777;
}

.hero {
    text-align: center;
    background: #efede7;
    padding: 110px 20px;
}

.hero h1 {
    font-size: clamp(38px, 7vw, 75px);
    max-width: 800px;
    margin: 15px auto;
}

.hero p {
    color: #777;
    font-size: 18px;
}

main {
    max-width: 1100px;
    margin: 65px auto;
    padding: 20px;
}

.cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}

article {
    background: white;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 6px 25px #0000000c;
}

article p {
    color: #777;
    line-height: 1.6;
}

footer {
    text-align: center;
    color: #999;
    padding: 25px;
}

.normal-counter {
    font-size: 10px;
    margin-top: 10px;
}

/* HORROR WORLD */

#horror {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 9999;
    overflow: hidden;

    background:
        radial-gradient(
            ellipse at center,
            #4b000c 0%,
            #1b0005 45%,
            #020001 100%
        );

    color: white;
}

#horror.active {
    display: block;
}

/* DARK VIGNETTE */

#horror::after {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: 7;
    box-shadow: inset 0 0 150px 65px #000b;
}

/* BLOOD CEILING */

.blood-top {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 75px;
    z-index: 6;

    background: linear-gradient(
        180deg,
        #d01329,
        #990015 35%,
        #560008 100%
    );

    box-shadow:
        0 12px 40px #570006,
        inset 0 7px 15px #ff757533;
}

.drip {
    position: absolute;
    top: 65px;
    width: 28px;
    border-radius: 0 0 55% 55%;

    background: linear-gradient(
        90deg,
        #470003,
        #a90017,
        #ce1029,
        #650009
    );

    box-shadow:
        inset 4px 0 6px #ff85852e,
        inset -4px 0 8px #0008;

    transform-origin: top;
    animation: dripMove 7s ease-in-out infinite;
}

.drip::after {
    content: "";
    position: absolute;
    width: 120%;
    height: 28px;
    left: -10%;
    bottom: -13px;
    border-radius: 50%;

    background:
        radial-gradient(
            circle at 30% 25%,
            #ffaaaa55,
            transparent 35%
        ),
        linear-gradient(#bd071e, #550006);
}

.d1 {left:5%; height:100px; animation-delay:-1s;}
.d2 {left:15%; height:140px; animation-delay:-3s;}
.d3 {left:27%; height:75px; animation-delay:-2s;}
.d4 {left:40%; height:160px; animation-delay:-4s;}
.d5 {left:53%; height:105px; animation-delay:-.5s;}
.d6 {left:65%; height:135px; animation-delay:-3.5s;}
.d7 {left:79%; height:85px; animation-delay:-2.3s;}
.d8 {left:90%; height:120px; animation-delay:-1.7s;}

@keyframes dripMove {
    0%,100% {
        transform: scaleY(.88);
    }

    50% {
        transform: scaleY(1.12);
    }
}

/* BLOOD STREAMS */

.stream {
    position: absolute;
    width: 5px;
    height: 90vh;
    top: -100%;
    z-index: 1;
    opacity: .35;

    background: linear-gradient(
        #a40016,
        #65000799,
        transparent
    );

    animation: flowDown 9s linear infinite;
}

.stream:nth-child(1) {
    left: 12%;
}

.stream:nth-child(2) {
    left: 34%;
    animation-delay: -3s;
}

.stream:nth-child(3) {
    left: 62%;
    animation-delay: -5s;
}

.stream:nth-child(4) {
    left: 85%;
    animation-delay: -2s;
}

@keyframes flowDown {
    to {
        transform: translateY(230vh);
    }
}

/* RED FOG */

.fog {
    position: absolute;
    inset: -20%;
    z-index: 1;
    pointer-events: none;

    background:
        radial-gradient(
            ellipse at 30% 50%,
            #b9001724,
            transparent 45%
        ),
        radial-gradient(
            ellipse at 70% 60%,
            #91001c24,
            transparent 48%
        );

    filter: blur(40px);
    animation: fogMove 15s ease-in-out infinite alternate;
}

@keyframes fogMove {
    from {
        transform: translateX(-5%);
    }

    to {
        transform: translateX(5%);
    }
}

/* FIVE MONSTERS */

.monster {
    position: absolute;
    z-index: 2;
    pointer-events: none;
    object-fit: contain;
    max-height: 60vh;

    filter:
        brightness(.82)
        contrast(1.35)
        drop-shadow(0 0 25px #a5002466);
}

/* HUGE MONSTER BEHIND TEXT */

.m1 {
    width: 32vw;
    max-width: 320px;
    left: 50%;
    top: 18%;

    transform: translateX(-50%) scale(1.25);
    opacity: .23;
}

/* UPSIDE DOWN */

.m2 {
    width: 20vw;
    max-width: 190px;
    left: 12%;
    top: -30px;

    transform: rotate(180deg);
}

/* LEFT SIDE */

.m3 {
    width: 19vw;
    max-width: 180px;
    left: -35px;
    top: 43%;

    transform: rotate(-30deg);
}

/* RIGHT SIDE */

.m4 {
    width: 19vw;
    max-width: 180px;
    right: -25px;
    top: 38%;

    transform: rotate(30deg) scaleX(-1);
}

/* BOTTOM MONSTER */

.m5 {
    width: 25vw;
    max-width: 240px;
    right: 20%;
    bottom: -75px;

    transform: rotate(-15deg);
}

/* HORROR TEXT */

.message {
    position: absolute;
    z-index: 5;
    inset: 0;

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    padding: 150px 16px 90px;
    text-align: center;
}

#warning {
    font-family: "UnifrakturCook", "MedievalSharp", serif;
    font-size: clamp(43px, 8vw, 100px);
    color: #ff1e3b;
    line-height: 1.17;
    max-width: 1000px;
    min-height: 1.3em;

    text-shadow:
        0 0 10px #fa153e,
        0 0 30px #be0018,
        0 0 65px #5e0009;
}

#subtext {
    font-family: "MedievalSharp", serif;
    font-size: clamp(15px, 2.7vw, 28px);
    letter-spacing: 3px;
    color: #e3a3ab;
    margin-top: 30px;
    min-height: 2em;

    text-shadow: 0 0 18px #a60021;
}

.tiny-counter {
    position: absolute;
    bottom: 12px;
    right: 16px;
    z-index: 10;

    font-size: 10px;
    color: #c18a92;
    opacity: .75;
}

@media(max-width:700px) {
    .cards {
        grid-template-columns: 1fr;
    }

    .m1 {
        width: 48vw;
    }

    .m2 {
        width: 29vw;
        left: 5%;
    }

    .m3 {
        width: 27vw;
    }

    .m4 {
        width: 27vw;
    }

    .m5 {
        width: 35vw;
    }

    .message {
        padding-top: 165px;
    }
}

@media(prefers-reduced-motion:reduce) {
    .drip, .stream, .fog {
        animation: none;
    }
}
</style>
</head>

<body>

<header>
    <div class="logo">The Daily Edit.</div>
    <nav>Home &nbsp; Stories &nbsp; About</nav>
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
            <p>Discover simple habits for everyday life.</p>
        </article>

        <article>
            <h3>Living With Technology</h3>
            <p>Finding balance in a connected world.</p>
        </article>

        <article>
            <h3>Making Room for Creativity</h3>
            <p>Find inspiration in ordinary moments.</p>
        </article>
    </div>
</main>

<footer>
    © The Daily Edit
    <div class="normal-counter">
        Requests served: <span id="actual">0</span>
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

    <div>
        <div class="stream"></div>
        <div class="stream"></div>
        <div class="stream"></div>
        <div class="stream"></div>
    </div>

    <div class="fog"></div>

    <img class="monster m1"
         src="/static/creepy-removebg-preview" alt="">

    <img class="monster m2"
         src="/static/creepy-removebg-preview" alt="">

    <img class="monster m3"
         src="/static/creepy-removebg-preview" alt="">

    <img class="monster m4"
         src="/static/creepy-removebg-preview" alt="">

    <img class="monster m5"
         src="/static/creepy-removebg-preview" alt="">

    <div class="message">
        <div id="warning"></div>
        <div id="subtext"></div>
    </div>

    <div class="tiny-counter">
        Requests served: <span id="hActual">0</span>
    </div>

</div>

<script>
let active = false;
let timers = [];

function typeLine(id, text, speed, delay) {
    const element = document.getElementById(id);

    element.textContent = "";

    for (let i = 1; i <= text.length; i++) {
        timers.push(setTimeout(() => {
            element.textContent = text.slice(0, i);
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
        140,
        0
    );

    typeLine(
        "subtext",
        "IT SEES YOU. IT KNOWS YOU ARE HERE.",
        80,
        4500
    );
}

function stopHorror() {
    if (!active) return;

    active = false;

    timers.forEach(clearTimeout);
    timers = [];

    document.getElementById("horror")
        .classList.remove("active");
}

async function poll() {
    try {
        const response = await fetch(
            "/api/status?t=" + Date.now(),
            {cache:"no-store"}
        );

        if (!response.ok) return;

        const data = await response.json();

        document.getElementById("actual")
            .textContent = data.actual.toLocaleString();

        document.getElementById("hActual")
            .textContent = data.actual.toLocaleString();

        if (data.phase === "running" ||
            data.phase === "complete") {
            startHorror();
        } else {
            stopHorror();
        }
    } catch (error) {
        // The browser may remain on the last loaded page
        // if the hosting service becomes unavailable.
    }
}

setInterval(poll, 1000);
poll();
</script>

</body>
</html>
"""


def current_state():
    with lock:
        start = started_at
        selected = duration
        actual = request_count

    if start is None:
        return "online", actual

    elapsed = time.monotonic() - start
    phase = "complete" if elapsed >= selected else "running"

    return phase, actual


def authorized():
    entered = request.headers.get("X-Control-Key", "")

    return (
        bool(CONTROL_PASSWORD)
        and secrets.compare_digest(entered, CONTROL_PASSWORD)
    )


@app.before_request
def count_request():
    global request_count

    with lock:
        request_count += 1


@app.after_request
def prevent_cache(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/")
def home():
    return PAGE


@app.get("/api/status")
def status():
    phase, actual = current_state()

    return jsonify(
        phase=phase,
        actual=actual
    )


@app.post("/api/start")
def start():
    global started_at, duration

    if not authorized():
        return jsonify(error="Unauthorized"), 401

    data = request.get_json(silent=True) or {}
    seconds = data.get("seconds")

    if type(seconds) is not int or seconds not in (10, 12):
        return jsonify(error="Invalid duration"), 400

    with lock:
        duration = seconds
        started_at = time.monotonic()

    return jsonify(message="Started")


@app.post("/api/reset")
def reset():
    global started_at

    if not authorized():
        return jsonify(error="Unauthorized"), 401

    with lock:
        started_at = None

    return jsonify(message="Reset")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050)
