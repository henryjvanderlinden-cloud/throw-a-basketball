// The gate on audio/synth.js: render each track in JavaScript and compare it
// with the WAV that Python produced. Not "sounds right" -- sample for sample
// against the reference the game shipped with.
//
//     node tools/test-synth.js
//
// The bar is 99.99% of samples identical with no sample off by more than one
// 8-bit quantisation step, which is the smallest difference the format can
// express. The residual comes from storing the percussion as float32.
const fs = require('fs'), path = require('path');
const SYNTH = require('../audio/synth.js');
const root = path.resolve(__dirname, '..');
global.window = {};
eval(fs.readFileSync(path.join(root, 'audio/score-data.js'), 'utf8').replace(/^\/\/.*$/gm, ''));
eval(fs.readFileSync(path.join(root, 'audio/score-rest.js'), 'utf8').replace(/^\/\/.*$/gm, ''));
const data = global.window.SCORE_DATA;
Object.assign(data.tracks, global.window.SCORE_REST.tracks);

const TRACKS = [
  ['menu', 'audio/full-court-pressure/full-court-pressure.wav'],
  ['play', 'audio/overtime-overdrive/overtime-overdrive.wav'],
];
let failed = 0;
for (const [key, wavPath] of TRACKS) {
  const track = data.tracks[key];
  if (!track) { console.log('FAIL  ' + key + ': no score'); failed++; continue; }
  const t0 = Date.now();
  const out = SYNTH.renderSync(track, data);
  const ms = Date.now() - t0;
  const wav = fs.readFileSync(path.join(root, wavPath));
  const ref = new Int16Array(wav.buffer, wav.byteOffset + 44, (wav.length - 44) / 2);
  let same = 0, maxd = 0;
  const n = Math.min(out.pcm.length, ref.length);
  for (let i = 0; i < n; i++) {
    const a = out.pcm[i] * 256, b = ref[i];        // python writes pcm*256 into the 16-bit file
    if (a === b) same++; else maxd = Math.max(maxd, Math.abs(a - b) / 256);
  }
  const pct = 100 * same / n;
  const ok = out.pcm.length === ref.length && pct > 99.99 && maxd <= 1;
  if (!ok) failed++;
  const pad = (v, w) => String(v).padEnd(w);
  console.log((ok ? 'PASS  ' : 'FAIL  ') + pad(key, 7) + pad(n + ' samples', 18) +
              pad(ms + ' ms', 9) + 'identical ' + pct.toFixed(4) + '%   worst ' +
              maxd + ' step(s)');
}
process.exit(failed ? 1 : 0);
