// Background sky, after ryanridden.com's js/stars.js: scattered stars with transients (fast rise, slow decay,
// warm halo). Added here: a few variable stars that pulse steadily, and a few asteroids that drift across in
// straight lines. One fixed, viewport-sized canvas behind the page, so a frame only redraws what is on screen.
// With prefers-reduced-motion the sky is drawn once and nothing moves.
(function () {
  var canvas = document.createElement('canvas');
  canvas.id = 'sky';
  canvas.setAttribute('aria-hidden', 'true');
  canvas.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:0;';
  document.body.insertBefore(canvas, document.body.firstChild);
  var ctx = canvas.getContext('2d');
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var W = 0, H = 0, stars = [], transients = [], asteroids = [];
  var N_ASTEROIDS = 8;
  var VAR_FRACTION = 0.12;
  // ms between transients
  var TRANSIENT_GAP = [2000, 4000];
  var nextTransient = 0, last = null;

  function rand(a, b) { return a + Math.random() * (b - a); }

  function buildStars() {
    stars = [];
    var count = Math.round((W * H) / 4000);
    for (var i = 0; i < count; i++) {
      var s = {x: Math.random() * W, y: Math.random() * H, r: Math.random() < 0.15 ? 1.2 : 0.7,
               alpha: 0.3 + Math.random() * 0.65, period: 0};
      // variable: steady sinusoidal pulse that brightens and fades about a mid-level base
      if (Math.random() < VAR_FRACTION) {
        s.period = rand(3000, 9000); s.phase = rand(0, 2 * Math.PI);
        s.alpha = rand(0.45, 0.65); s.amp = rand(0.25, 0.4); s.r = 0.9;
      }
      stars.push(s);
    }
  }

  // asteroid: enters from a random edge and crosses the screen at a slow, steady rate
  function spawnAsteroid(anywhere) {
    var ang = rand(0, 2 * Math.PI), v = rand(10, 28) / 1000;
    var a = {vx: Math.cos(ang) * v, vy: Math.sin(ang) * v, r: rand(0.8, 1.1), alpha: rand(0.55, 0.85)};
    if (anywhere) { a.x = Math.random() * W; a.y = Math.random() * H; }
    else {
      // start just outside the edge it is moving away from
      if (Math.abs(a.vx) > Math.abs(a.vy)) { a.x = a.vx > 0 ? -5 : W + 5; a.y = Math.random() * H; }
      else { a.y = a.vy > 0 ? -5 : H + 5; a.x = Math.random() * W; }
    }
    return a;
  }

  function dot(x, y, r, alpha) {
    ctx.beginPath();
    ctx.arc(x, y, r, 0, 2 * Math.PI);
    ctx.fillStyle = 'rgba(255,255,255,' + alpha + ')';
    ctx.fill();
  }

  function render(now) {
    ctx.clearRect(0, 0, W, H);
    var boost = {};
    for (var j = 0; j < transients.length; j++) boost[transients[j].index] = transients[j];
    for (var i = 0; i < stars.length; i++) {
      var s = stars[i], alpha = s.alpha, r = s.r, t = boost[i];
      if (s.period && !still) {
        var w = Math.sin(2 * Math.PI * now / s.period + s.phase);
        alpha = Math.max(0.05, Math.min(1, alpha + s.amp * w));
        r += 0.45 * w;
      }
      if (t) {
        alpha = Math.min(1, alpha + t.alphaBoost);
        r += t.rBoost;
        if (t.alphaBoost > 0.2) {
          ctx.beginPath();
          ctx.arc(s.x, s.y, r * 4, 0, 2 * Math.PI);
          ctx.fillStyle = 'rgba(255,240,200,' + (t.alphaBoost * 0.18) + ')';
          ctx.fill();
        }
      }
      dot(s.x, s.y, r, alpha);
    }
    for (var k = 0; k < asteroids.length; k++) dot(asteroids[k].x, asteroids[k].y, asteroids[k].r, asteroids[k].alpha);
  }

  function step(now) {
    var dt = last == null ? 16 : Math.min(now - last, 100);
    last = now;

    if (now >= nextTransient && stars.length) {
      transients.push({index: Math.floor(Math.random() * stars.length), elapsed: 0,
                       duration: 2500 + Math.random() * 500 + Math.random() * 2000, alphaBoost: 0, rBoost: 0});
      nextTransient = now + rand(TRANSIENT_GAP[0], TRANSIENT_GAP[1]);
    }
    for (var i = transients.length - 1; i >= 0; i--) {
      var t = transients[i];
      t.elapsed += dt;
      var p = t.elapsed / t.duration;
      if (p >= 1) { transients.splice(i, 1); continue; }
      // fast rise (~15% of duration), slow decay
      var b = p < 0.15 ? p / 0.15 : Math.pow(1 - (p - 0.15) / 0.85, 1.8);
      t.alphaBoost = b * 0.9;
      t.rBoost = b * 1.8;
    }
    for (var k = 0; k < asteroids.length; k++) {
      var a = asteroids[k];
      a.x += a.vx * dt; a.y += a.vy * dt;
      if (a.x < -10 || a.x > W + 10 || a.y < -10 || a.y > H + 10) asteroids[k] = spawnAsteroid(false);
    }
    render(now);
    requestAnimationFrame(step);
  }

  function size() {
    var dpr = window.devicePixelRatio || 1;
    W = window.innerWidth; H = window.innerHeight;
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    buildStars();
    transients = [];
    asteroids = [];
    for (var i = 0; i < N_ASTEROIDS; i++) asteroids.push(spawnAsteroid(true));
    if (still) render(0);
  }

  var pending = null;
  window.addEventListener('resize', function () { clearTimeout(pending); pending = setTimeout(size, 150); });
  size();
  if (!still) {
    nextTransient = performance.now() + 1000 + Math.random() * 1500;
    requestAnimationFrame(step);
  }
})();
