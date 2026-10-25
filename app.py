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

<link href="https://fonts.googleapis.com/css2?family=MedievalSharp&family=Cinzel:wght@400;700;900&display=swap" rel="stylesheet">

<style>
* {
    box-sizing: border-box;
}

html, body {
    margin: 0;
    padding: 0;
}

body {
    background: #fbfaf7;
    color: #1f2430;
    font-family: Arial, sans-serif;
}

/* ===== NORMAL WEBSITE ===== */

header {
    max-width: 1140px;
    margin: auto;
    padding: 24px 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.brand {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -.5px;
}

nav {
    color: #7a7a7a;
    font-size: 14px;
}

.hero {
    background: linear-gradient(180deg, #f3f0e7 0%, #f8f6f2 100%);
    padding: 100px 24px 90px;
    text-align: center;
    border-top: 1px solid #eee8dd;
    border-bottom: 1px solid #eee8dd;
}

.eyebrow {
    font-size: 12px;
    letter-spacing: 3px;
    color: #8d7759;
    margin-bottom: 12px;
}

.hero h1 {
    margin: 0 auto 14px;
    max-width: 800px;
    font-size: clamp(38px, 7vw, 74px);
    line-height: 1.02;
    letter-spacing: -2px;
}

.hero p {
    margin: 0 auto;
    max-width: 640px;
    font-size: 18px;
    line-height: 1.7;
    color: #6f7378;
}

main {
    max-width: 1140px;
    margin: 70px auto;
    padding: 0 22px;
}

.section-title {
    margin: 0 0 22px;
    font-size: 30px;
}

.cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 22px;
}

.card {
    background: white;
    border: 1px solid #ececec;
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(0,0,0,.04);
}

.card-art {
    height: 140px;
    background: linear-gradient(135deg, #e7dfd0, #f2eee8);
}

.card:nth-child(2) .card-art {
    background: linear-gradient(135deg, #dae4ea, #eef3f6);
}

.card:nth-child(3) .card-art {
    background: linear-gradient(135deg, #ead8d8, #f7efef);
}

.card-body {
    padding: 20px;
}

.card h3 {
    margin: 0 0 10px;
    font-size: 22px;
}

.card p {
    margin: 0;
    color: #70757c;
    line-height: 1.7;
}

footer {
    max-width: 1140px;
    margin: 70px auto 0;
    padding: 26px 22px 34px;
    border-top: 1px solid #ececec;
    color: #9a9a9a;
    font-size: 12px;
    display: flex;
    justify-content: space-between;
    gap: 12px;
}

#request-meter {
    opacity: .75;
    font-size: 11px;
}

/* ===== HORROR OVERLAY ===== */

#horror {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 9999;
    overflow: hidden;
    color: #fff;
    background:
        radial-gradient(circle at center, rgba(88,0,12,.22) 0%, rgba(17,0,4,.76) 38%, rgba(0,0,0,.96) 100%),
        linear-gradient(180deg, #160003 0%, #050001 100%);
}

#horror.on {
    display: block;
}

/* ===== MOVING FOG ===== */

.fog,
.fog2 {
    position: absolute;
    inset: -10%;
    background:
        radial-gradient(circle at 20% 35%, rgba(110,0,16,.08), transparent 28%),
        radial-gradient(circle at 75% 25%, rgba(150,150,150,.035), transparent 25%),
        radial-gradient(circle at 50% 80%, rgba(110,0,20,.06), transparent 28%);
    filter: blur(30px);
    animation: drift 18s linear infinite;
    pointer-events: none;
}

.fog2 {
    animation-duration: 28s;
    animation-direction: reverse;
    opacity: .8;
}

@keyframes drift {
    0%   { transform: translate3d(-2%, -1%, 0) scale(1.03); }
    50%  { transform: translate3d(2%, 2%, 0) scale(1.08); }
    100% { transform: translate3d(-2%, -1%, 0) scale(1.03); }
}

/* ===== BLOOD BAR ===== */

.blood-top {
    position: absolute;
    inset: 0 0 auto 0;
    height: 84px;
    background:
        linear-gradient(180deg, #c10c20 0%, #8e0212 30%, #5b000b 68%, #2c0005 100%);
    box-shadow:
        0 10px 40px rgba(80,0,0,.82),
        inset 0 -14px 18px rgba(0,0,0,.32);
    z-index: 5;
}

.blood-top::before {
    content: "";
    position: absolute;
    inset: 0 0 auto 0;
    height: 24px;
    background: linear-gradient(180deg, rgba(255,180,180,.2), rgba(255,255,255,0));
    mix-blend-mode: screen;
    pointer-events: none;
}

.blood-top::after {
    content: "";
    position: absolute;
    left: 0;
    bottom: -16px;
    width: 100%;
    height: 34px;
    background:
        radial-gradient(circle at 5% 0,  #7c000b 0 18px, transparent 19px),
        radial-gradient(circle at 13% 0, #950010 0 24px, transparent 25px),
        radial-gradient(circle at 24% 0, #85000d 0 14px, transparent 15px),
        radial-gradient(circle at 37% 0, #9a0011 0 28px, transparent 29px),
        radial-gradient(circle at 51% 0, #6b000a 0 17px, transparent 18px),
        radial-gradient(circle at 66% 0, #a00012 0 24px, transparent 25px),
        radial-gradient(circle at 80% 0, #78000b 0 16px, transparent 17px),
        radial-gradient(circle at 92% 0, #91000f 0 21px, transparent 22px);
    opacity: .96;
}

/* ===== BLOOD DRIPS ===== */

.drip {
    position: absolute;
    top: 70px;
    width: 28px;
    border-radius: 0 0 18px 18px;
    background:
        linear-gradient(180deg, #690007 0%, #a70014 32%, #8a0010 72%, #430006 100%);
    box-shadow:
        inset -4px 0 6px rgba(0,0,0,.28),
        inset 3px 0 5px rgba(255,145,145,.12),
        0 0 16px rgba(120,0,0,.24);
    transform-origin: top center;
    animation: ooze 7s ease-in-out infinite;
    z-index: 5;
}

.drip::before {
    content: "";
    position: absolute;
    top: -8px;
    left: 3px;
    width: 22px;
    height: 18px;
    border-radius: 50%;
    background: #8c000d;
}

.drip::after {
    content: "";
    position: absolute;
    bottom: -14px;
    left: 50%;
    transform: translateX(-50%);
    width: 34px;
    height: 30px;
    border-radius: 50% 50% 58% 58%;
    background:
        radial-gradient(circle at 30% 25%, rgba(255,180,180,.22), transparent 28%),
        radial-gradient(circle at 50% 60%, #b50b17 0%, #83000d 60%, #4e0006 100%);
    box-shadow: 0 3px 10px rgba(0,0,0,.28);
}

.d1 { left: 6%;  height: 88px;  width: 24px; animation-delay: 0s;   }
.d2 { left: 15%; height: 130px; width: 22px; animation-delay: .9s;  }
.d3 { left: 28%; height: 74px;  width: 20px; animation-delay: 1.6s; }
.d4 { left: 39%; height: 146px; width: 34px; animation-delay: .3s;  }
.d5 { left: 51%; height: 98px;  width: 25px; animation-delay: 2s;   }
.d6 { left: 64%; height: 136px; width: 28px; animation-delay: .8s;  }
.d7 { left: 77%; height: 82px;  width: 22px; animation-delay: 1.1s; }
.d8 { left: 89%; height: 118px; width: 30px; animation-delay: .4s;  }

@keyframes ooze {
    0%   { transform: scaleY(.92); filter: brightness(.92); }
    25%  { transform: scaleY(1.00); filter: brightness(1.02); }
    50%  { transform: scaleY(1.10); filter: brightness(1.05); }
    75%  { transform: scaleY(1.00); filter: brightness(.97); }
    100% { transform: scaleY(.92); filter: brightness(.92); }
}

/* ===== BLOOD STREAMS ===== */

.blood-run {
    position: absolute;
    top: -100%;
    width: 5px;
    height: 130vh;
    background: linear-gradient(180deg, rgba(130,0,10,.9), rgba(130,0,10,.18), transparent 85%);
    opacity: .26;
    filter: blur(1px);
    animation: runDown 8.5s linear infinite;
    z-index: 1;
}

.r1 { left: 10%; animation-delay: 0s; }
.r2 { left: 30%; animation-delay: 2s; }
.r3 { left: 57%; animation-delay: 1s; }
.r4 { left: 83%; animation-delay: 3.3s; }

@keyframes runDown {
    0%   { transform: translateY(-100%); opacity: 0; }
    15%  { opacity: .22; }
    65%  { opacity: .32; }
    100% { transform: translateY(100%); opacity: 0; }
}

/* ===== BLOOD SPLATTERS ===== */

.splatter {
    position: absolute;
    width: 260px;
    height: 260px;
    opacity: .9;
    pointer-events: none;
    background:
        radial-gradient(circle at 50% 50%, #a40015 0 20%, transparent 21%),
        radial-gradient(circle at 24% 28%, #8b0010 0 8%, transparent 9%),
        radial-gradient(circle at 76% 18%, #c10f21 0 7%, transparent 8%),
        radial-gradient(circle at 84% 69%, #87000f 0 10%, transparent 11%),
        radial-gradient(circle at 13% 77%, #700009 0 7%, transparent 8%),
        radial-gradient(circle at 56% 8%, #c90d1e 0 4%, transparent 5%),
        radial-gradient(circle at 90% 44%, #8b0010 0 5%, transparent 6%);
    filter: blur(.25px);
}

.s1 { top: 16%; left: -60px; transform: rotate(18deg) scale(1.25); }
.s2 { top: 34%; right: -70px; transform: rotate(-28deg) scale(1.35); }
.s3 { bottom: -50px; left: 4%; transform: rotate(50deg) scale(1.0); }
.s4 { bottom: -60px; right: 7%; transform: rotate(-46deg) scale(1.15); }

/* ===== CONTENT ===== */

.horror-content {
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    text-align: center;
    padding: 150px 20px 110px;
    z-index: 4;
}

.center-stack {
    max-width: 920px;
    position: relative;
    z-index: 6;
}

#warning {
    font-family: 'MedievalSharp', 'Cinzel', serif;
    font-size: clamp(42px, 8vw, 94px);
    line-height: 1.12;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #ed1d32;
    min-height: 1.3em;
    text-shadow:
        0 0 8px #ff364a,
        0 0 22px #a40014,
        0 0 55px rgba(110,0,0,.95);
}

#subtext {
    margin-top: 14px;
    font-family: 'Cinzel', serif;
    font-size: clamp(15px, 2.4vw, 24px);
    letter-spacing: 4px;
    color: #efc2c8;
    min-height: 2em;
    text-shadow: 0 0 14px rgba(110,0,10,.55);
}

/* ===== MONSTERS ===== */

.monster-layer {
    position: absolute;
    inset: 0;
    z-index: 3;
    pointer-events: none;
}

.monster {
    position: absolute;
    opacity: .94;
    filter:
        brightness(.9)
        contrast(1.2)
        saturate(.7)
        drop-shadow(0 0 16px rgba(255,10,40,.12))
        drop-shadow(0 0 38px rgba(100,0,0,.45));
    animation: pulseShadow 6s ease-in-out infinite;
    user-select: none;
}

@keyframes pulseShadow {
    0%, 100% { transform-origin: center; }
    50% { filter:
        brightness(.96)
        contrast(1.25)
        saturate(.72)
        drop-shadow(0 0 18px rgba(255,15,50,.16))
        drop-shadow(0 0 45px rgba(120,0,0,.52));
    }
}

/* One huge behind text */
.m1 {
    width: min(34vw, 310px);
    left: 50%;
    top: 18%;
    transform: translateX(-50%) scale(1.2);
    opacity: .28;
}

/* Upside down from top */
.m2 {
    width: min(20vw, 180px);
    left: 14%;
    top: -12px;
    transform: rotate(180deg);
    opacity: .92;
}

/* Left side creeping in */
.m3 {
    width: min(18vw, 170px);
    left: -18px;
    top: 43%;
    transform: rotate(-24deg);
}

/* Right side leaning in */
.m4 {
    width: min(17vw, 160px);
    right: -8px;
    top: 34%;
    transform: rotate(18deg) scaleX(-1);
}

/* Bottom partially hidden */
.m5 {
    width: min(24vw, 220px);
    left: 62%;
    bottom: -26px;
    transform: translateX(-50%) rotate(-8deg);
    opacity: .88;
}

.counter-chip {
    position: absolute;
    right: 18px;
    bottom: 16px;
    z-index: 7;
    font-size: 11px;
    color: #c38a92;
    background: rgba(20,0,5,.45);
    border: 1px solid rgba(132,16,29,.55);
    border-radius: 10px;
    padding: 8px 10px;
    backdrop-filter: blur(4px);
}

.counter-chip b {
    color: #ff707c;
    font-variant-numeric: tabular-nums;
}

@media (max-width: 900px) {
    .cards {
        grid-template-columns: 1fr;
    }

    .m1 { width: 42vw; top: 20%; }
    .m2 { width: 24vw; left: 6%; }
    .m3 { width: 22vw; }
    .m4 { width: 21vw; }
    .m5 { width: 28vw; left: 66%; }

    .horror-content {
        padding-top: 170px;
    }
}

@media (max-width: 600px) {
    .hero {
        padding: 80px 20px;
    }

    #warning {
        letter-spacing: 2px;
    }

    .m1 { width: 50vw; opacity: .24; }
    .m2 { width: 28vw; top: 18px; }
    .m3 { width: 25vw; top: 49%; }
    .m4 { width: 25vw; top: 40%; }
    .m5 { width: 33vw; left: 68%; }

    .counter-chip {
        font-size: 10px;
        right: 12px;
        bottom: 12px;
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
    <div class="eyebrow">THOUGHTS · CULTURE · EVERYDAY LIFE</div>
    <h1>A little inspiration for every day.</h1>
    <p>
        Fresh perspectives on the things that matter. Discover thoughtful
        stories, simple ideas, and quiet inspiration for daily life.
    </p>
</section>

<main>
    <h2 class="section-title">Featured stories</h2>

    <div class="cards">
        <div class="card">
            <div class="card-art"></div>
            <div class="card-body">
                <h3>Small things, big changes</h3>
                <p>Why the smallest habits often make the biggest difference over time.</p>
            </div>
        </div>

        <div class="card">
            <div class="card-art"></div>
            <div class="card-body">
                <h3>Living with technology</h3>
                <p>Finding a better balance in a world that always wants your attention.</p>
            </div>
        </div>

        <div class="card">
            <div class="card-art"></div>
            <div class="card-body">
                <h3>Making room for creativity</h3>
                <p>Simple ways to invite more imagination into your ordinary routine.</p>
            </div>
        </div>
    </div>
</main>

<footer>
    <span>© The Daily Edit</span>
    <span id="request-meter">Requests served: <span id="actual">0</span></span>
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

    <div class="blood-run r1"></div>
    <div class="blood-run r2"></div>
    <div class="blood-run r3"></div>
    <div class="blood-run r4"></div>

    <div class="splatter s1"></div>
    <div class="splatter s2"></div>
    <div class="splatter s3"></div>
    <div class="splatter s4"></div>

    <div class="fog"></div>
    <div class="fog2"></div>

    <div class="monster-layer">
        <img class="monster m1" src="/static/monster.png" alt="monster">
        <img class="monster m2" src="/static/monster.png" alt="monster">
        <img class="monster m3" src="/static/monster.png" alt="monster">
        <img class="monster m4" src="/static/monster.png" alt="monster">
        <img class="monster m5" src="/static/monster.png" alt="monster">
    </div>

    <div class="horror-content">
        <div class="center-stack">
            <div id="warning"></div>
            <div id="subtext"></div>
        </div>
    </div>

    <div class="counter-chip">
        Requests served: <b id="hActual">0</b><br>
        Visual load: <b id="hDemo">0</b>
    </div>
</div>

<script>
let active = false;
let failed = 0;
let redirected = false;
let timers = [];

function typeLine(id, text, speed, delay) {
    const element = document.getElementById(id);
    element.textContent = '';

    for (let n = 1; n <= text.length; n++) {
        timers.push(setTimeout(() => {
            element.textContent = text.slice(0, n);
        }, delay + n * speed));
    }
}

function horrorOn() {
    if (active) return;
    active = true;
    document.getElementById('horror').classList.add('on');

    typeLine('warning', "YOU'VE BEEN HACKED", 135, 0);
    typeLine('subtext', "AN ANCIENT CURSE HAS AWAKENED", 62, 2800);
}

function horrorOff() {
    if (!active) return;
    active = false;
    timers.forEach(clearTimeout);
    timers = [];
    document.getElementById('horror').classList.remove('on');
}

async function poll() {
    if (redirected) return;

    try {
        const response = await fetch('/api/status?t=' + Date.now(), { cache: 'no-store' });

        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }

        const data = await response.json();
        failed = 0;

        document.getElementById('actual').textContent = data.actual.toLocaleString();
        document.getElementById('hActual').textContent = data.actual.toLocaleString();
        document.getElementById('hDemo').textContent = data.visual.toLocaleString();

        if (data.phase === 'running') {
            horrorOn();
        } else {
            horrorOff();
        }

    } catch (error) {
        failed++;
        if (failed >= 3) {
            redirected = true;
        }
    }
}

setInterval(poll, 900);
poll();
</script>

</body>
</html>
'''

def current_state():
    with lock:
        start = started_at
        selected = power
        actual = request_count

    if start is None:
        return "online", 0, actual

    elapsed = time.monotonic() - start
    step = min(selected, int(elapsed) + 1)

    visual = (2 ** step - 1) if selected == 10 else (2 ** step)
    phase = "complete" if elapsed >= selected else "running"

    return phase, visual, actual

def authorized():
    entered = request.headers.get("X-Control-Key", "")
    return bool(CONTROL_PASSWORD) and secrets.compare_digest(entered, CONTROL_PASSWORD)

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
    return PAGE, 200

@app.get("/api/status")
def status():
    phase, visual, actual = current_state()
    return jsonify(phase=phase, visual=visual, actual=actual), 200

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

    return jsonify(message="Started", power=selected)

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
