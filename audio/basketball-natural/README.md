# Basketball / Natural '94

Twelve original synthesized effects designed for more natural basketball material textures, with exactly the original pack's 11,025 Hz mono / 8-bit quantization / saturation finish. These are synthesized effects, not field recordings. No third-party samples were used.

| Group | Variations | Duration |
| --- | --- | --- |
| Shoe squeak | Short stop, double grip, lower skid | 180 / 285 / 220 ms |
| Backboard | Standard hollow slap, heavier hit, tight hit | 295 / 340 / 260 ms |
| Net swish | Cord brushes, longer rustle, quick pass | 310 / 370 / 260 ms |
| Floor bounce | Standard bounce, heavy bounce, light bounce | 260 / 300 / 230 ms |

Rubber friction uses irregular stick/slip gestures and scuff noise. Ball impacts use damped, inharmonic shell resonances plus surface contact. Net sounds use uneven cord brushes and cloth noise. Quiet early reflections add court character without long tails.

Open `preview.html` for individual playback. `preview.wav` plays the table order, three variations per group. `manifest.json` includes paths and preview timestamps.

- `wav/`: 16-bit PCM containers with 8-bit sound baked in, 11,025 Hz mono; recommended for game integration.
- `pcm8/`: identical waveforms in unsigned 8-bit PCM WAV, 11,025 Hz mono, 88.2 kbps.
- Same file names as the first pack for easy substitution. Peaks remain below full scale; edges fade to silence.
- Compression is dynamic saturation. Files use uncompressed PCM, avoiding lossy codec padding on short one-shots.

Preload sounds and unlock audio on the first user interaction. Randomize variants without immediate repeats; scale impact gain by collision strength and debounce repeated contact events. Use shoe squeaks on stops and turns, and net swishes on made baskets. Leave mixing headroom for simultaneous sounds.

Regenerate with `python tools/build-basketball-natural-sfx.py`; uses the original generator's PCM utilities and only Python's standard library. This pack is supplied for integration and does not alter gameplay.
