// Renders the music from its score, in the browser, instead of loading it.
//
// A direct port of tools/build-full-court-soundtrack.py and the voice set that
// build-overtime-anthem.py layers over it. The acceptance test is not "sounds
// right", it is tools/test-synth.js: render here and compare against the WAV
// Python produces, sample for sample.
//
// The percussion is not synthesised here. It is built in Python from numpy's
// PCG64 noise, which cannot be reproduced in JavaScript without reimplementing
// PCG64 and SeedSequence exactly, so those thirteen buffers arrive as float32
// data in score-data.js. Everything pitched is arithmetic and ports directly.

'use strict';

(function (root) {
  const TAU = Math.PI * 2;

  function decodePerc(entry) {
    const bin = typeof atob === 'function'
      ? atob(entry.d)
      : Buffer.from(entry.d, 'base64').toString('binary');
    const bytes = new Uint8Array(entry.n * 4);
    for (let i = 0; i < bytes.length; i++) bytes[i] = bin.charCodeAt(i);
    // float32, little-endian. int16 was not precise enough: see export-score-data.py
    return new Float32Array(bytes.buffer, 0, entry.n);
  }

  // ---- voices ---------------------------------------------------------------
  // Each returns one note as a Float64Array. These are transcriptions of the
  // Python; the shapes and constants are deliberately identical, including the
  // edge windows, which is why they read oddly for JavaScript.

  function envEdge(t, duration) {
    return Math.min(1, t / 0.003) * Math.min(1, (duration - t) / 0.018);
  }

  function voices_fullcourt(kind, midi, beats, BEAT, SR) {
    const duration = beats * BEAT;
    const n = rint(duration * SR);
    const y = new Float64Array(n);
    const f = 440 * Math.pow(2, (midi - 69) / 12);
    for (let i = 0; i < n; i++) {
      const t = i / SR;
      const phase = TAU * f * t;
      let edge = envEdge(t, duration);
      let v;
      if (kind === 'bass') {
        v = Math.sin(phase + 0.85 * Math.sin(phase * 2) * Math.exp(-t / 0.027));
        v += 0.30 * Math.sin(2 * phase) * Math.exp(-t / 0.13)
           + 0.13 * Math.sin(3 * phase) * Math.exp(-t / 0.06);
        v = Math.tanh(v * 1.25) * (0.70 * Math.exp(-t / 0.16) + 0.30 * Math.exp(-t / 0.60));
      } else if (kind === 'lead') {
        const p = phase + 0.020 * Math.sin(TAU * 5.5 * t);
        v = Math.sin(p + 0.32 * Math.sin(2 * p) * Math.exp(-t / 0.055))
          + 0.27 * Math.sin(2 * p) + 0.11 * Math.sin(3 * p);
        v *= 0.68 + 0.32 * Math.exp(-t / 0.06);
        edge *= Math.min(1, (duration - t) / 0.042);
      } else if (kind === 'stab') {
        v = 0;
        for (let k = 1; k <= 5; k++) v += Math.sin(phase * k + 0.14 * Math.sin(phase)) / k;
        v *= Math.min(1, t / 0.009) * Math.exp(-t / 0.105);
      } else if (kind === 'keys') {
        v = Math.sin(phase + 1.6 * Math.sin(phase) * Math.exp(-t / 0.060)) * Math.exp(-t / 0.25);
        v += 0.14 * Math.sin(3 * phase) * Math.exp(-t / 0.055);
      } else if (kind === 'muted') {
        v = (Math.sin(phase) + 0.42 * Math.sin(2 * phase) + 0.18 * Math.sin(3 * phase))
            * Math.exp(-t / 0.040);
      } else if (kind === 'riser') {
        const p = TAU * (f * t + 1.5 * f * t * t / duration);
        v = Math.sin(p + 0.8 * Math.sin(p * 2)) * Math.pow(t / duration, 1.5) * 0.6;
      } else {
        throw new Error('unknown voice ' + kind);
      }
      y[i] = v * Math.max(0, Math.min(1, edge));
    }
    return y;
  }

  function voices_overtime(kind, midi, beats, BEAT, SR) {
    if (['lead', 'bass', 'stab', 'organ', 'pad'].indexOf(kind) < 0) {
      return voices_fullcourt(kind, midi, beats, BEAT, SR);
    }
    const duration = beats * BEAT;
    const n = rint(duration * SR);
    const y = new Float64Array(n);
    const f = 440 * Math.pow(2, (midi - 69) / 12);
    for (let i = 0; i < n; i++) {
      const t = i / SR;
      const p = TAU * f * t;
      const edge = Math.min(1, t / 0.004) * Math.max(0, Math.min(1, (duration - t) / 0.024));
      let v;
      if (kind === 'lead') {
        v = 0;
        for (let k = 1; k <= 6; k++) {
          v += (Math.sin(p * k) + 0.27 * Math.sin(p * k * 1.0035)) / Math.pow(k, 1.45);
        }
        v += 0.11 * Math.sin(p * 2 + 1.4 * Math.sin(p)) * Math.exp(-t / 0.045);
        v *= 0.72 + 0.28 * Math.exp(-t / 0.055);
      } else if (kind === 'bass') {
        v = Math.sin(p) + 0.44 * Math.sin(2 * p) + 0.23 * Math.sin(3 * p) + 0.13 * Math.sin(4 * p);
        v = Math.tanh(v * 1.3) * (0.30 + 0.70 * Math.exp(-t / 0.085));
      } else if (kind === 'stab') {
        v = 0;
        for (let k = 1; k <= 6; k++) v += Math.sin(p * k + 0.28 * Math.sin(p * 0.5)) / Math.pow(k, 1.25);
        v *= Math.min(1, t / 0.008) * Math.exp(-t / 0.12);
      } else if (kind === 'organ') {
        v = 0.80 * Math.sin(p) + 0.45 * Math.sin(2 * p) + 0.18 * Math.sin(3 * p) + 0.23 * Math.sin(4 * p);
        v *= Math.exp(-t / 0.17);
      } else {
        v = Math.sin(p) + 0.20 * Math.sin(2 * p * 1.002) + 0.12 * Math.sin(3 * p);
        v *= Math.min(1, t / 0.055) * Math.max(0, Math.min(1, (duration - t) / 0.12));
      }
      y[i] = v * edge;
    }
    return y;
  }

  const VOICES = { voices_fullcourt, voices_overtime, voices_victory: voices_fullcourt };

  // ---- the engine -----------------------------------------------------------

  // Python's round() is half-to-even and Math.round is half-up. Thirty-one of
  // this score's placements land on exactly .5, and a one-sample shift smears
  // across a whole note -- it was 18,230 differing samples before this existed.
  function rint(x) {
    const r = Math.round(x);
    if (Math.abs(x % 1) === 0.5 && r % 2 !== 0) return r - Math.sign(x);
    return r;
  }

  // numpy's pairwise summation, because np.mean uses it and a naive left-to-right
  // sum of 1.3M floats drifts far enough to tip samples sitting exactly on a
  // quantisation boundary. Same blocking as numpy's pairwise_sum: unrolled by
  // eight up to 128, split in half above that, the split kept a multiple of 8.
  function pairwiseSum(a, from, n) {
    if (n < 8) {
      let r = 0;
      for (let i = 0; i < n; i++) r += a[from + i];
      return r;
    }
    if (n <= 128) {
      let r0 = a[from], r1 = a[from+1], r2 = a[from+2], r3 = a[from+3];
      let r4 = a[from+4], r5 = a[from+5], r6 = a[from+6], r7 = a[from+7];
      let i = 8;
      for (; i < n - (n % 8); i += 8) {
        r0 += a[from+i];   r1 += a[from+i+1]; r2 += a[from+i+2]; r3 += a[from+i+3];
        r4 += a[from+i+4]; r5 += a[from+i+5]; r6 += a[from+i+6]; r7 += a[from+i+7];
      }
      let r = ((r0 + r1) + (r2 + r3)) + ((r4 + r5) + (r6 + r7));
      for (; i < n; i++) r += a[from + i];
      return r;
    }
    let n2 = n >> 1;
    n2 -= n2 % 8;
    return pairwiseSum(a, from, n2) + pairwiseSum(a, from + n2, n - n2);
  }

  function periodicAdd(dest, sound, start, gain, N) {
    start = ((start % N) + N) % N;
    const first = Math.min(sound.length, N - start);
    for (let i = 0; i < first; i++) dest[start + i] += sound[i] * gain;
    for (let i = first; i < sound.length; i++) dest[i - first] += sound[i] * gain;
  }

  // Which bus each pitched voice lands on, exactly as note() decides in Python.
  function busOf(kind) {
    if (kind === 'bass') return 'bass';
    if (kind === 'lead') return 'lead';
    if (kind === 'riser') return 'fx';
    return 'keys';
  }

  // Rendering a two-minute track takes a few hundred milliseconds, which is a
  // visible freeze if it happens in one go on the menu. So the work is a
  // generator that yields often, and renderAsync drives it in ~8 ms slices
  // between frames. renderSync exists for the test harness, which has no frames.
  function* renderSteps(track, data) {
    const SR = data.sampleRate;
    const N = rint(SR * track.seconds);
    const BEAT = 60 / track.bpm;
    const voice = VOICES[track.voices] || voices_fullcourt;
    const buses = {
      drums: new Float64Array(N), bass: new Float64Array(N),
      keys: new Float64Array(N), lead: new Float64Array(N), fx: new Float64Array(N)
    };
    const kicks = [];
    const percCache = Object.create(null);
    const noteCache = Object.create(null);
    const echo1 = rint(0.75 * BEAT * SR), echo2 = rint(1.5 * BEAT * SR);

    for (let n = 0; n < track.events.length; n++) {
      const ev = track.events[n];
      const kind = track.parts[ev[0]], gain = ev[2];
      const start = rint(ev[1] * BEAT * SR);
      if (ev[3] === null || ev[3] === undefined) {
        const key = kind + ':' + ev[5];
        let buf = percCache[key];
        if (!buf) {
          const entry = data.perc[key];
          if (!entry) continue;
          buf = percCache[key] = decodePerc(entry);
        }
        periodicAdd(buses.drums, buf, start, gain, N);
        if (kind === 'kick') kicks.push(ev[1]);
      } else {
        const key = kind + '|' + ev[3] + '|' + ev[4];
        let buf = noteCache[key];
        if (!buf) buf = noteCache[key] = voice(kind, ev[3], ev[4], BEAT, SR);
        const bus = buses[busOf(kind)];
        periodicAdd(bus, buf, start, gain, N);
        if (ev[5]) {
          periodicAdd(bus, buf, start + echo1, gain * 0.14, N);
          periodicAdd(bus, buf, start + echo2, gain * 0.045, N);
        }
      }
      if ((n & 63) === 0) yield 0.6 * n / track.events.length;
    }

    // Kick ducking. Which buses duck, how hard, and how far they may fall all
    // differ between tracks, so they arrive with the score.
    const D = track.duck || { secs: 0.13, amount: 0.18, decay: 0.043, floors: { bass: 0.66 } };
    const dipN = rint(D.secs * SR);
    const dip = new Float64Array(dipN);
    for (let i = 0; i < dipN; i++) dip[i] = D.amount * Math.exp(-(i / SR) / D.decay);
    const duck = new Float64Array(N).fill(1);
    for (const beat of kicks) periodicAdd(duck, dip, rint(beat * BEAT * SR), -1, N);
    for (const name in D.floors) {
      const floor = D.floors[name], b = buses[name];
      for (let i = 0; i < N; i++) b[i] *= Math.max(floor, Math.min(1, duck[i]));
    }
    yield 0.7;

    const mix = new Float64Array(N);
    for (const k in buses) {
      const b = buses[k];
      for (let i = 0; i < N; i++) mix[i] += b[i];
      yield 0.8;
    }
    const mean = pairwiseSum(mix, 0, N) / N;
    let peak = 0;
    for (let i = 0; i < N; i++) { mix[i] -= mean; const a = Math.abs(mix[i]); if (a > peak) peak = a; }
    yield 0.9;
    let peak2 = 0;
    for (let i = 0; i < N; i++) {
      mix[i] = Math.tanh(mix[i] / peak * 1.85);
      const a = Math.abs(mix[i]);
      if (a > peak2) peak2 = a;
    }
    yield 0.95;
    // The game wants floats in [-1,1]; the reference WAV wants the 8-bit step
    // grid. Quantise either way, because the grid is the sound.
    const pcm = new Int16Array(N);
    const f32 = new Float32Array(N);
    for (let i = 0; i < N; i++) {
      const q = rint(mix[i] / peak2 * 108);
      pcm[i] = q;
      f32[i] = q / 128;
    }
    return { pcm: pcm, samples: f32, sampleRate: SR, mean: mean, peak: peak, peak2: peak2 };
  }

  function renderSync(track, data) {
    const it = renderSteps(track, data);
    let r;
    do { r = it.next(); } while (!r.done);
    return r.value;
  }

  // Slices the work across frames so the menu keeps animating while it runs.
  function renderAsync(track, data, done, onProgress) {
    const it = renderSteps(track, data);
    const now = () => (typeof performance !== 'undefined' ? performance.now() : Date.now());
    const step = () => {
      const t0 = now();
      let r;
      do { r = it.next(); } while (!r.done && now() - t0 < 8);
      if (r.done) { done(r.value); return; }
      if (onProgress && typeof r.value === 'number') onProgress(r.value);
      if (typeof requestAnimationFrame === 'function') requestAnimationFrame(step);
      else setTimeout(step, 0);
    };
    step();
  }

  const api = { render: renderSync, renderSync, renderAsync, decodePerc,
                voices_fullcourt, voices_overtime, rint };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.SYNTH = api;
})(typeof self !== 'undefined' ? self : this);
