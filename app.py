import os
import time
import secrets
from threading import Lock
from flask import Flask, jsonify, request

app = Flask(__name__)

CONTROL_PASSWORD = os.environ.get("CONTROL_PASSWORD", "")
lock = Lock()

started_at = None
power = 10
request_count = 0

PAGE = r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Daily Edit</title>

<link href="https://fonts.googleapis.com/css2?family=Creepster&family=DM+Sans:wght@400;500;700;800&display=swap" rel="stylesheet">

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #fcfbf9;
    color: #232830;
    font-family: 'DM Sans', Arial, sans-serif;
}

header {
    height: 80px;
    max-width: 1120px;
    margin: auto;
    padding: 0 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.brand {
    font-size: 25px;
    font-weight: 800;
    color: #161922;
}

nav {
    color: #777;
    font-size: 14px;
}

.hero {
    text-align: center;
    background: #f1efe9;
    padding: 110px 24px;
}

.hero h1 {
    font-size: clamp(40px, 7vw, 78px);
    letter-spacing: -3px;
    margin: 20px auto;
    max-width: 850px;
}

.hero p {
    font-size: 17px;
    color: #777;
    max-width: 600px;
    margin: auto;
}

.eyebrow {
    color: #927856;
    font-size: 12px;
    letter-spacing: 3px;
}

main {
    max-width: 1120px;
    margin: 70px auto;
    padding: 0 24px;
}

.cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 22px;
}

article {
    min-height: 250px;
    background: white;
    border: 1px solid #eee;
    border-radius: 15px;
    overflow: hidden;
}

.art {
    height: 120px;
    background: #e8e3d9;
}

article:nth-child(2) .art {
    background: #d8e1e5;
}

article:nth-child(3) .art {
    background: #e5dad9;
}

.article-content {
    padding: 20px;
}

article h3 {
    margin: 0 0 10px;
}

article p {
    color: #777;
    font-size: 14px;
}

footer {
    max-width: 1120px;
    margin: 80px auto 0;
    padding: 25px;
    border-top: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    color: #999;
    font-size: 12px;
}

#request-meter {
    font-size: 10px;
    opacity: .6;
}

/* HORROR SCREEN */

#horror {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 1000;
    overflow: auto;
    text-align: center;
    color: white;
    padding: 155px 18px 50px;

    background:
        radial-gradient(
            ellipse at center,
            #49000b 0%,
            #190006 50%,
            #030001 100%
        );
}

#horror.on {
    display: block;
}

/* BLOOD AT TOP */

.blood-top {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 72px;
    z-index: 4;

    background: linear-gradient(
        180deg,
        #c80c21 0%,
        #990411 32%,
        #67000b 74%,
        #360004 100%
    );

    box-shadow:
        0 12px 32px rgba(88, 0, 7, .75),
        inset 0 -10px 16px rgba(22, 0, 3, .55);
}

.blood-top::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 25px;

    background: linear-gradient(
        rgba(255, 194, 194, .28),
        transparent
    );
}

.blood-top::after {
    content: "";
    position: absolute;
    left: 0;
    bottom: -15px;
    width: 100%;
    height: 27px;

    background:
        radial-gradient(ellipse at 8% 0,
            #84000c 0 23px, transparent 24px),
        radial-gradient(ellipse at 29% 0,
            #a00113 0 17px, transparent 18px),
        radial-gradient(ellipse at 50% 0,
            #7b000a 0 27px, transparent 28px),
        radial-gradient(ellipse at 73% 0,
            #97000f 0 22px, transparent 23px),
        radial-gradient(ellipse at 92% 0,
            #85000b 0 19px, transparent 20px);
}

/* REALISTIC BLOOD DRIPS */

.drip {
    position: absolute;
    top: 60px;
    width: 30px;
    height: 90px;

    border-radius: 0 0 48% 48%;

    background: linear-gradient(
        90deg,
        #550006,
        #bf081e 32%,
        #9b0011 55%,
        #3e0005
    );

    box-shadow:
        inset 3px 0 6px rgba(255,161,161,.17),
        inset -4px 0 7px rgba(0,0,0,.45),
        0 4px 15px rgba(77,0,8,.35);

    transform-origin: top;
    animation: slowOoze 6s ease-in-out infinite;
}

.drip::after {
    content: "";
    position: absolute;
    left: 50%;
    bottom: -12px;

    transform: translateX(-50%);

    width: 120%;
    height: 25px;

    border-radius: 55% 55% 60% 60%;

    background:
        radial-gradient(
            circle at 30% 25%,
            rgba(245,139,139,.4),
            transparent 30%
        ),
        linear-gradient(
            125deg,
            #99000c,
            #c30a20 45%,
            #450005
        );

    box-shadow: 0 5px 12px rgba(0,0,0,.35);
}

.d1 {
    left: 5%;
    height: 78px;
    width: 27px;
    animation-delay: -1s;
}

.d2 {
    left: 16%;
    height: 117px;
    width: 22px;
    animation-delay: -3s;
}

.d3 {
    left: 28%;
    height: 65px;
    width: 28px;
    animation-delay: -2s;
}

.d4 {
    left: 40%;
    height: 138px;
    width: 33px;
    animation-delay: -4s;
}

.d5 {
    left: 53%;
    height: 92px;
    width: 24px;
    animation-delay: -.5s;
}

.d6 {
    left: 65%;
    height: 126px;
    width: 29px;
    animation-delay: -3.6s;
}

.d7 {
    left: 78%;
    height: 73px;
    width: 21px;
    animation-delay: -1.7s;
}

.d8 {
    left: 90%;
    height: 109px;
    width: 31px;
    animation-delay: -2.8s;
}

@keyframes slowOoze {
    0%, 100% {
        transform: scaleY(.91);
        filter: brightness(.93);
    }

    50% {
        transform: scaleY(1.08);
        filter: brightness(1.07);
    }
}

/* BLOOD FLOWING DOWN SCREEN */

.blood-run {
    position: absolute;
    top: 0;
    z-index: 1;

    width: 5px;
    height: 75vh;

    background: linear-gradient(
        rgba(166,0,21,.7),
        rgba(156,0,16,.48),
        transparent
    );

    opacity: .28;
    filter: blur(1px);

    animation: runDown 9s linear infinite;
}

.r1 {
    left: 9%;
    animation-delay: -2s;
}

.r2 {
    left: 32%;
    animation-delay: -6s;
}

.r3 {
    left: 61%;
    animation-delay: -4s;
}

.r4 {
    left: 86%;
    animation-delay: -1s;
}

@keyframes runDown {
    from {
        transform: translateY(-90%);
    }

    to {
        transform: translateY(140%);
    }
}

/* BLOOD SPLATTERS */

.splatter {
    position: fixed;
    width: 220px;
    height: 220px;
    pointer-events: none;

    opacity: .8;

    background:
        radial-gradient(circle at 50% 50%,
            #a80017 0 19%, transparent 20%),
        radial-gradient(circle at 25% 30%,
            #a00012 0 9%, transparent 10%),
        radial-gradient(circle at 80% 22%,
            #bd0019 0 7%, transparent 8%),
        radial-gradient(circle at 85% 75%,
            #79000d 0 10%, transparent 11%),
        radial-gradient(circle at 12% 85%,
            #bc001b 0 6%, transparent 7%);
}

.s1 {
    left: -70px;
    top: 26%;
    transform: rotate(18deg) scale(1.2);
}

.s2 {
    right: -70px;
    top: 42%;
    transform: rotate(-32deg) scale(1.3);
}

.s3 {
    left: 15%;
    bottom: -130px;
    transform: rotate(48deg);
}

.s4 {
    right: 10%;
    bottom: -115px;
    transform: rotate(-48deg);
}

/* HORROR MESSAGE */

.horror-content {
    position: relative;
    z-index: 2;
    max-width: 900px;
    margin: auto;
}

#warning {
    font-family: 'Creepster', Georgia, serif;
    font-size: clamp(43px, 9vw, 104px);
    color: #fb1936;

    letter-spacing: 2px;
    line-height: 1.2;
    min-height: 1.3em;

    text-shadow:
        0 0 12px #e6002a,
        0 0 45px #ad0016;
}

#subtext {
    font-family: Georgia, serif;
    font-size: clamp(13px, 2.7vw, 22px);
    letter-spacing: 3px;
    color: #eeb7bf;

    min-height: 2.6em;
    margin: 12px 0 24px;
}

/* FIVE CREEPY PICTURES */

.horror-gallery {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
    flex-wrap: nowrap;
    margin: 24px auto;
    max-width: 930px;
}

.horror-photo {
    display: block;
    width: 17%;
    height: clamp(150px, 24vw, 270px);
    object-fit: cover;

    border: 2px solid #920719;

    box-shadow:
        0 0 30px rgba(164,0,37,.65),
        0 0 8px #ff173d;

    filter: contrast(1.35) saturate(.55);
}

.horror-photo:nth-child(1) {
    transform: rotate(-7deg);
}

.horror-photo:nth-child(2) {
    transform: rotate(4deg);
}

.horror-photo:nth-child(3) {
    width: 22%;
    height: clamp(190px, 30vw, 330px);
    z-index: 1;

    border-color: #fb1c39;
    box-shadow: 0 0 55px #e80036;
}

.horror-photo:nth-child(4) {
    transform: rotate(-4deg);
}

.horror-photo:nth-child(5) {
    transform: rotate(7deg);
}

/* SMALL REQUEST COUNTER */

.tiny-counter {
    position: fixed;
    z-index: 5;
    bottom: 15px;
    right: 17px;

    color: #bb7e87;
    font: 10px Arial, sans-serif;
    opacity: .7;
}

@media (max-width: 650px) {
    .cards {
        grid-template-columns: 1fr;
    }

    #horror {
        padding-top: 165px;
    }

    .horror-gallery {
        gap: 4px;
    }

    .horror-photo {
        height: 33vw;
    }

    .horror-photo:nth-child(3) {
        height: 43vw;
    }
}

@media (prefers-reduced-motion: reduce) {
    .drip, .blood-run {
        animation: none;
    }
}
</style>
</head>

<body>

<header>
    <div class="brand">The Daily Edit.</div>
    <nav>Stories &nbsp;&nbsp; About</nav>
</header>

<section class="hero">
    <div class="eyebrow">
        THOUGHTS · CULTURE · EVERYDAY LIFE
    </div>

    <h1>A little inspiration for every day.</h1>

    <p>
        Fresh perspectives on the things that matter.
        Discover simple ideas, thoughtful stories
        and new ways to see the world.
    </p>
</section>

<main>
    <h2>Featured stories</h2>

    <div class="cards">
        <article>
            <div class="art"></div>
            <div class="article-content">
                <h3>Small things, big changes</h3>
                <p>
                    Why little habits often make
                    the greatest difference.
                </p>
            </div>
        </article>

        <article>
            <div class="art"></div>
            <div class="article-content">
                <h3>Living with technology</h3>
                <p>
                    Finding a better balance
                    in a connected world.
                </p>
            </div>
        </article>

        <article>
            <div class="art"></div>
            <div class="article-content">
                <h3>Making room for creativity</h3>
                <p>
                    Simple ways to find inspiration
                    in ordinary moments.
                </p>
            </div>
        </article>
    </div>
</main>

<footer>
    <span>© The Daily Edit</span>

    <span id="request-meter">
        Requests served: <span id="actual">0</span>
    </span>
</footer>

<!-- HORROR SCENE -->

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

    <div class="blood-run r1"></div>
    <div class="blood-run r2"></div>
    <div class="blood-run r3"></div>
    <div class="blood-run r4"></div>

    <div class="splatter s1"></div>
    <div class="splatter s2"></div>
    <div class="splatter s3"></div>
    <div class="splatter s4"></div>

    <div class="horror-content">

        <div id="warning"></div>
        <div id="subtext"></div>

        <div class="horror-gallery">
            <img class="horror-photo"
                 src="/static/creepy.jpg" alt="Horror">

            <img class="horror-photo"
                 src="/static/creepy.jpg" alt="Horror">

            <img class="horror-photo"
                 src="/static/creepy.jpg" alt="Horror">

            <img class="horror-photo"
                 src="/static/creepy.jpg" alt="Horror">

            <img class="horror-photo"
                 src="/static/creepy.jpg" alt="Horror">
        </div>
    </div>

    <div class="tiny-counter">
        Requests served:
        <span id="hActual">0</span>
    </div>

</div>

<script>
let active = false;
let failed = 0;
let redirected = false;
let timers = [];

function typeLine(id, text, speed, delay) {
    const el = document.getElementById(id);
    el.textContent = '';

    for (let n = 1; n <= text.length; n++) {
        timers.push(
            setTimeout(() => {
                el.textContent = text.slice(0, n);
            }, delay + n * speed)
        );
    }
}

function horrorOn() {
    if (active) return;

    active = true;

    document.getElementById('horror')
        .classList.add('on');

    typeLine(
        'warning',
        "YOU'VE BEEN HACKED",
        145,
        0
    );

    typeLine(
        'subtext',
        'THE END IS NEAR',
        115,
        2800
    );
}

function horrorOff() {
    if (!active) return;

    active = false;

    timers.forEach(clearTimeout);
    timers = [];

    document.getElementById('horror')
        .classList.remove('on');
}

async function poll() {
    if (redirected) return;

    try {
        const res = await fetch(
            '/api/status?t=' + Date.now(),
            { cache: 'no-store' }
        );

        if (res.status === 503) {
            redirected = true;
            location.reload();
            return;
        }

        if (!res.ok) {
            throw Error('HTTP ' + res.status);
        }

        const data = await res.json();

        failed = 0;

        document.getElementById('actual')
            .textContent = data.actual.toLocaleString();

        document.getElementById('hActual')
            .textContent = data.actual.toLocaleString();

        if (data.phase === 'running') {
            horrorOn();
        } else {
            horrorOff();
        }

    } catch (err) {
        failed++;

        if (failed >= 3) {
            redirected = true;
            location.reload();
        }
    }
}

setInterval(poll, 900);
poll();
</script>

</body>
</html>
'''

ERROR_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>503 Service Unavailable</title>
</head>
<body style="
    background:#141414;
    color:white;
    text-align:center;
    font:20px Arial;
    padding-top:15vh;
">
<h1>503 Service Unavailable</h1>
<p>This website is temporarily offline.</p>
</body>
</html>
"""


def current_state():
    with lock:
        start = started_at
        selected = power
        actual = request_count

    if start is None:
        return "online", 0, actual

    elapsed = time.monotonic() - start
    step = min(selected, int(elapsed) + 1)

    if selected == 10:
        visual = 2 ** step - 1
    else:
        visual = 2 ** step

    phase = "complete" if elapsed >= selected else "running"

    return phase, visual, actual


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
    phase, _, _ = current_state()

    if phase == "complete":
        return ERROR_PAGE, 503

    return PAGE, 200


@app.get("/api/status")
def status():
    phase, visual, actual = current_state()

    return jsonify(
        phase=phase,
        visual=visual,
        actual=actual
    ), (503 if phase == "complete" else 200)


@app.post("/api/start")
def start():
    global started_at, power

    if not authorized():
        return jsonify(error="Unauthorized"), 401

    data = request.get_json(silent=True) or {}
    selected = data.get("rounds")

    if type(selected) is not int or selected not in (10, 12):
        return jsonify(error="Select Power 10 or 12"), 400

    with lock:
        power = selected
        started_at = time.monotonic()

    return jsonify(
        message="Started",
        power=selected
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
    app.run(
        host="127.0.0.1",
        port=5050
    )
