import os
import time
import secrets
from threading import Lock
from flask import Flask, jsonify, request

app = Flask(__name__)

CONTROL_PASSWORD = os.getenv("CONTROL_PASSWORD", "")
lock = Lock()

started_at = None
power = 10
step_seconds = 1.0
request_count = 0

IMAGE = "/static/creepy-removebg-preview.png"

PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Daily Edit</title>

<link href="https://fonts.googleapis.com/css2?family=UnifrakturCook:wght@700&family=MedievalSharp&display=swap" rel="stylesheet">

<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    background: #f7f5f0;
    color: #262626;
    font-family: Arial, sans-serif;
}

/* NORMAL WEBSITE */

header {
    max-width: 1100px;
    margin: auto;
    padding: 25px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.logo {
    font-size: 26px;
    font-weight: bold;
}

nav { color: #777; }

.hero {
    background: #eeeae2;
    padding: 110px 20px;
    text-align: center;
}

.hero h1 {
    font-size: clamp(36px, 7vw, 75px);
    margin: 0 auto 20px;
    max-width: 800px;
}

.hero p {
    font-size: 18px;
    color: #777;
}

main {
    max-width: 1100px;
    padding: 20px;
    margin: 60px auto;
}

.cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}

article {
    padding: 30px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 5px 25px #00000010;
}

article p {
    color: #777;
    line-height: 1.6;
}

footer {
    padding: 35px 20px;
    text-align: center;
    color: #999;
    font-size: 12px;
}

.normal-counter {
    margin-top: 12px;
    font-size: 10px;
}

/* HORROR BACKGROUND */

#horror {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 9999;
    overflow: hidden;
    background:
        radial-gradient(
            ellipse at center,
            #51000b 0%,
            #190005 45%,
            #020001 100%
        );
    color: white;
}

#horror.active { display: block; }

#horror::before {
    content: "";
    position: absolute;
    inset: 0;
    z-index: 5;
    pointer-events: none;
    box-shadow: inset 0 0 155px 45px #000a;
}

/* THICK BLOOD CEILING */

.blood-top {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 80px;
    z-index: 8;

    background: linear-gradient(
        180deg,
        #db142c,
        #940012 40%,
        #490005
    );

    box-shadow:
        0 10px 35px #76000b,
        inset 0 8px 14px #ffa3a344;
}

.blood-top::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 20px;
    background: linear-gradient(
        #ffffff27,
        transparent
    );
}

/* DRIPPING BLOOD */

.drip {
    position: absolute;
    top: 69px;
    width: 28px;
    border-radius: 0 0 50% 50%;

    background: linear-gradient(
        90deg,
        #400005,
        #a00013 30%,
        #d30d25 60%,
        #600008
    );

    box-shadow:
        inset 3px 0 6px #ffb4b433,
        inset -4px 0 8px #0008;

    transform-origin: top;
    animation: ooze 7s ease-in-out infinite;
}

.drip::after {
    content: "";
    position: absolute;
    bottom: -15px;
    left: -12%;
    width: 125%;
    height: 30px;
    border-radius: 50%;

    background: radial-gradient(
        circle at 33% 25%,
        #ff9f9f66,
        #b40018 35%,
        #490005
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
    0%, 100% { transform: scaleY(.88); }
    50% { transform: scaleY(1.12); }
}

/* BLOOD FOG */

.fog {
    position: absolute;
    inset: -20%;
    z-index: 1;
    pointer-events: none;

    background:
        radial-gradient(
            ellipse at 30% 50%,
            #b900173b,
            transparent 50%
        ),
        radial-gradient(
            ellipse at 70% 65%,
            #8e001939,
            transparent 50%
        );

    filter: blur(55px);
    animation: fogMove 14s ease-in-out infinite alternate;
}

@keyframes fogMove {
    from { transform: translateX(-6%); }
    to { transform: translateX(6%); }
}

/* FIVE MONSTERS */

.monster {
    position: absolute;
    z-index: 2;
    pointer-events: none;
    object-fit: contain;
    max-height: 65vh;

    filter:
        brightness(.85)
        contrast(1.4)
        drop-shadow(0 0 25px #b4002388);
}

.m1 {
    width: 35vw;
    max-width: 330px;
    left: 50%;
    top: 16%;
    opacity: .27;
    transform: translateX(-50%) scale(1.3);
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

/* GOTHIC TEXT */

.message {
    position: absolute;
    z-index: 6;
    inset: 0;

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    text-align: center;
    padding: 155px 18px 95px;
}

#warning {
    font-family: "UnifrakturCook", "MedievalSharp", serif;
    font-size: clamp(39px, 7.3vw, 94px);
    color: #ff203d;
    line-height: 1.15;
    max-width: 1000px;
    min-height: 1.4em;

    text-shadow:
        0 0 12px #ff193a,
        0 0 36px #ad0019,
        0 0 68px #640007;
}

#subtext {
    font-family: "MedievalSharp", serif;
    font-size: clamp(15px, 2.5vw, 26px);
    color: #e9a6b0;
    letter-spacing: 2px;
    margin-top: 24px;
    min-height: 2em;
    text-shadow: 0 0 18px #a0001a;
}

/* SMALL COUNTER */

.counter {
    position: absolute;
    z-index: 10;
    right: 14px;
    bottom: 14px;

    color: #d7a0a8;
    background: #150004bb;
    border: 1px solid #6e0b1c;
    border-radius: 10px;

    padding: 11px 14px;
    font-size: 12px;
    line-height: 1.8;
}

.counter b {
    color: #ff6476;
    font-variant-numeric: tabular-nums;
}

@media (max-width: 700px) {
    .cards { grid-template-columns: 1fr; }
    .m1 { width: 48vw; }
    .m2 { width: 28vw; left: 4%; }
    .m3 { width: 25vw; }
    .m4 { width: 25vw; }
    .m5 { width: 35vw; }
}

@media (prefers-reduced-motion: reduce) {
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

    <div class="normal-counter">
        Actual HTTP requests:
        <span id="actual">0</span>
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
    </div>

    <div class="counter">
        Simulated requests: <b id="visual">0</b><br>
        Power: 2^<b id="step">0</b><br>
        Actual HTTP requests: <b id="hActual">0</b>
    </div>

</div>

<script>
let active = false;
let timers = [];
let transitioning = false;

function typeLine(id, message, speed, delay) {
    const el = document.getElementById(id);
    el.textContent = "";

    for (let i = 1; i <= message.length; i++) {
        const timer = setTimeout(() => {
            el.textContent = message.slice(0, i);
        }, delay + i * speed);

        timers.push(timer);
    }
}

function horrorOn() {
    if (active) return;

    active = true;

    document.getElementById("horror")
        .classList.add("active");

    typeLine(
        "warning",
        "YOU SHOULD NOT HAVE COME HERE",
        95,
        0
    );

    typeLine(
        "subtext",
        "IT SEES YOU. IT KNOWS YOU ARE HERE.",
        70,
        3400
    );
}

function horrorOff() {
    if (!active) return;

    active = false;

    timers.forEach(clearTimeout);
    timers = [];

    document.getElementById("horror")
        .classList.remove("active");
}

async function poll() {
    if (transitioning) return;

    try {
        const response = await fetch(
            "/api/status?t=" + Date.now(),
            { cache: "no-store" }
        );

        if (response.status === 503) {
            transitioning = true;
            window.location.replace(
                "/?offline=" + Date.now()
            );
            return;
        }

        if (!response.ok) return;

        const data = await response.json();

        document.getElementById("actual")
            .textContent = data.actual.toLocaleString();

        document.getElementById("hActual")
            .textContent = data.actual.toLocaleString();

        document.getElementById("visual")
            .textContent = data.visual.toLocaleString();

        document.getElementById("step")
            .textContent = data.step;

        if (data.phase === "running") {
            horrorOn();
        } else {
            horrorOff();
        }

    } catch (e) {
        console.error("Status unavailable", e);
    }
}

setInterval(poll, 500);
poll();
</script>
</body>
</html>
"""

ERROR_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>503 Service Unavailable</title>
<style>
body {
    margin: 0;
    min-height: 100vh;
    background: #111;
    color: white;
    font-family: Arial, sans-serif;
    display: grid;
    place-items: center;
    text-align: center;
}
main {
    padding: 30px;
    max-width: 700px;
}
h1 {
    font-size: clamp(36px, 7vw, 70px);
    margin-bottom: 12px;
}
p {
    color: #ccc;
    font-size: 18px;
    line-height: 1.6;
}
small { color: #aaa; }
</style>
</head>
<body>
<main>
    <h1>503 Service Unavailable</h1>
    <p>The server is temporarily unable to handle this request.</p>
    <small>HTTP ERROR 503</small>
</main>
</body>
</html>
"""


def current_state():
    with lock:
        start = started_at
        selected = power
        interval = step_seconds
        actual = request_count

    if start is None:
        return "online", 0, 0, actual

    elapsed = time.monotonic() - start

    # Each step doubles the displayed load.
    # The interval is long enough for the horror
    # text animation to finish, even at Power 4.
    step = min(selected, int(elapsed / interval) + 1)
    visual = 2 ** step

    if elapsed >= selected * interval:
        phase = "complete"
    else:
        phase = "running"

    return phase, step, visual, actual


def authorized():
    entered = request.headers.get("X-Control-Key", "")

    return (
        bool(CONTROL_PASSWORD)
        and secrets.compare_digest(entered, CONTROL_PASSWORD)
    )


@app.before_request
def count_http_request():
    global request_count

    with lock:
        request_count += 1


@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/")
def home():
    phase, _, _, _ = current_state()

    if phase == "complete":
        return ERROR_PAGE, 503

    return PAGE, 200


@app.get("/api/status")
def status():
    phase, step, visual, actual = current_state()

    return jsonify(
        phase=phase,
        step=step,
        visual=visual,
        actual=actual,
        power=power
    ), (503 if phase == "complete" else 200)


@app.post("/api/start")
def start():
    global started_at, power, step_seconds

    if not authorized():
        return jsonify(error="Unauthorized"), 401

    data = request.get_json(silent=True) or {}
    selected = data.get("power")

    if type(selected) is not int or not (4 <= selected <= 20):
        return jsonify(error="Choose Power 4 through 20"), 400

    # Never send 2^n real requests.
    # n only controls the displayed value.
    interval = max(0.7, 8.0 / selected)

    with lock:
        power = selected
        step_seconds = interval
        started_at = time.monotonic()

    return jsonify(
        message="Started",
        power=selected,
        max_visual=2 ** selected,
        step_seconds=interval
    )


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
