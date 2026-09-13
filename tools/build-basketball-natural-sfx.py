"""Material-inspired basketball synthesis, using the original pack's PCM finish."""
from pathlib import Path
import importlib.util
import json
import math
import random
import struct
import wave
import zipfile

spec = importlib.util.spec_from_file_location('arcade', Path(__file__).with_name('build-basketball-sfx.py'))
arcade = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arcade)
SR, RATE, TAU = arcade.SR, arcade.RATE, math.tau
ROOT = Path(__file__).resolve().parents[1] / 'audio' / 'basketball-natural'


def unit(values):
    scale = max(abs(v) for v in values) or 1
    return [v / scale for v in values]


def texture(rng, n, f, q):
    return unit(arcade.bandpass(arcade.noise(rng, n), f, q))


def reflections(values):
    # Quiet early court reflections, with no long reverberant tail.
    out = values.copy()
    for delay, gain in [(0.0113, 0.12), (0.0197, 0.075), (0.0311, 0.035)]:
        offset = round(delay * SR)
        for i in range(offset, len(values)):
            out[i] += values[i - offset] * gain
    return out


def squeak(v, rng):
    duration = [0.180, 0.285, 0.220][v]
    n = round(duration * SR)
    scuff = texture(rng, n, 1900, 0.65)
    rubber = texture(rng, n, 3100, 2.0)
    jitter = texture(rng, n, 85, 0.55)
    out = [0.0] * n
    # Separate irregular stick/slip gestures instead of a continuous oscillator sweep.
    gestures = [
        [(0.012, 0.123, 1680, 1.0)],
        [(0.012, 0.084, 1910, 0.85), (0.123, 0.108, 1530, 1.0)],
        [(0.018, 0.150, 1320, 1.0)],
    ][v]
    for start, length, pitch, gain in gestures:
        phase = rng.random() * TAU
        for i in range(round(start * SR), min(n, round((start + length) * SR))):
            t = i / SR - start
            u = t / length
            frequency = pitch * (1 + 0.035 * jitter[i] + 0.075 * math.sin(math.pi * u) - 0.045 * u)
            phase += TAU * frequency / SR
            env = min(1, t / 0.007) * min(1, (length - t) / 0.018)
            grip = 0.63 + 0.37 * abs(jitter[i])
            tone = math.sin(phase) + 0.24 * math.sin(2.03 * phase) + 0.07 * math.sin(3.07 * phase)
            out[i] += gain * env * grip * (0.43 * tone + 0.16 * rubber[i])
    for i in range(n):
        t = i / SR
        env = min(1, t / 0.008) * math.exp(-t / 0.078) * max(0, 1 - t / duration)
        out[i] += 0.22 * scuff[i] * env
    return reflections(out)


def impact(v, rng, board=False):
    duration = ([0.295, 0.340, 0.260] if board else [0.260, 0.300, 0.230])[v]
    n = round(duration * SR)
    contact = texture(rng, n, 1850 if board else 1200, 0.75)
    skin = texture(rng, n, 720, 3.7)
    surface = texture(rng, n, 2700 if board else 2300, 1.2)
    scale = [1.0, 0.91, 1.09][v]
    # Inharmonic, damped shell modes: a hollow pneumatic ball plus the struck surface.
    modes = [(176, .72, .041), (427, .34, .025), (693, .22, .035), (1090, .11, .017)]
    if board:
        modes += [(242, .42, .054), (518, .25, .048), (947, .15, .027), (1670, .07, .019)]
    else:
        modes += [(91, .28, .032), (307, .15, .021)]
    phases = [rng.uniform(-0.18, 0.18) for _ in modes]
    out = []
    for i in range(n):
        t = i / SR
        attack = min(1, t / 0.0007)
        body = sum(amp * math.sin(TAU * freq * scale * t + phase) * math.exp(-t / (decay * (1.12 if v == 1 else 1)))
                   for (freq, amp, decay), phase in zip(modes, phases))
        # The contact has a broad slap followed by a much softer skin release.
        slap = contact[i] * (1.15 if board else 0.80) * math.exp(-t / 0.0045)
        release = math.exp(-((t - 0.008) / 0.003) ** 2) * 0.19 * surface[i]
        air = skin[i] * 0.30 * math.exp(-t / 0.042)
        out.append(attack * (body + slap + release + air))
    return reflections(out)


def swish(v, rng):
    duration = [0.310, 0.370, 0.260][v]
    n = round(duration * SR)
    low = texture(rng, n, 870, 0.8)
    mid = texture(rng, n, 2100, 0.65)
    high = texture(rng, n, 4200, 0.9)
    flutter = texture(rng, n, 55, 0.65)
    # Uneven cord brushes as the ball parts the net; final knot catches are quieter.
    brushes = [(rng.uniform(.025, duration * .69), rng.uniform(.006, .021), rng.uniform(.15, .45)) for _ in range(11)]
    out = []
    for i in range(n):
        t, u = i / SR, i / n
        env = (1 - math.exp(-t / .025)) * math.exp(-t / (.073 + v * .006))
        catches = sum(gain * math.exp(-((t - center) / width) ** 2) for center, width, gain in brushes)
        flow = env * (0.85 + 0.35 * flutter[i])
        value = flow * (0.70 * low[i] + 0.85 * mid[i] + 0.12 * high[i])
        value += catches * (0.29 * mid[i] + 0.20 * high[i]) * (1 - u) ** 1.3
        out.append(value * min(1, (duration - t) / .040))
    return reflections(out)


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest = {'sampleRate': RATE, 'channels': 1, 'textureBits': 8, 'source': 'Original material-inspired synthesis; not field recordings', 'effects': {}}
    preview = [0.0] * round(.25 * RATE)
    sections = []
    groups = [('shoe-squeak', squeak, .65), ('backboard', lambda v, r: impact(v, r, True), .88), ('net-swish', swish, .64), ('floor-bounce', impact, .86)]
    for g, (category, make, gain) in enumerate(groups):
        rows = []
        for v in range(3):
            name = f'{category}-{v+1:02d}'
            values = arcade.arcade(make(v, random.Random(199403 + g * 50 + v)), gain)
            arcade.write_wav(ROOT / 'wav' / f'{name}.wav', values)
            arcade.write_wav(ROOT / 'pcm8' / f'{name}.wav', values, 8)
            info = {'file': f'wav/{name}.wav', 'pcm8': f'pcm8/{name}.wav', 'durationMs': round(1000 * len(values) / RATE), 'previewStartSeconds': round(len(preview) / RATE, 3)}
            manifest['effects'][name] = info
            preview += values + [0.0] * round(.43 * RATE)
            rows.append(f'<li><span>{name} <small>{info["durationMs"]} ms</small></span><audio controls preload="none" src="wav/{name}.wav"></audio></li>')
        preview += [0.0] * round(.38 * RATE)
        sections.append(f'<section><h2>{category.replace("-", " ").title()}</h2><ul>{"".join(rows)}</ul></section>')
    arcade.write_wav(ROOT / 'preview.wav', preview)
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'preview.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Basketball Natural / 8-bit</title>
<style>body{background:#111b20;color:#f5eee1;font:16px system-ui;max-width:850px;margin:40px auto;padding:0 20px}h1{color:#e7b675}h2{font-size:21px}section{background:#22323b;padding:16px 24px;border-radius:14px;margin:18px 0}ul{padding:0;list-style:none}li{display:flex;align-items:center;justify-content:space-between;gap:15px;margin:14px 0;flex-wrap:wrap}small{color:#afbfc7}audio{height:36px;max-width:100%}p{line-height:1.6;color:#c4cadd}</style>
<h1>Basketball / Natural '94</h1><p>More natural material textures, the same 8-bit / 11.025 kHz finish.<br>12 original synthesized effects: rubber grip, hollow impacts, and net brushes.</p><audio controls src="preview.wav"></audio>''' + ''.join(sections) + '</html>', encoding='utf-8')
    (ROOT / 'README.md').write_text('''# Basketball / Natural '94

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
''', encoding='utf-8')
    for name, info in manifest['effects'].items():
        with wave.open(str(ROOT / info['file']), 'rb') as f:
            assert (f.getnchannels(), f.getframerate(), f.getsampwidth()) == (1, RATE, 2)
            pcm16 = struct.unpack('<' + 'h' * f.getnframes(), f.readframes(f.getnframes()))
        with wave.open(str(ROOT / info['pcm8']), 'rb') as f:
            assert (f.getnchannels(), f.getframerate(), f.getsampwidth()) == (1, RATE, 1)
            pcm8 = f.readframes(f.getnframes())
        assert list(pcm16) == [(v - 128) * 256 for v in pcm8]
        assert 0 < max(map(abs, pcm16)) < 32767 and pcm16[0] == pcm16[-1] == 0
        assert abs(sum(pcm16) / len(pcm16)) < 327.68, 'Excessive DC offset'
        print(f'{name}: {info["durationMs"]} ms; both PCM formats verified')
    archive_path = ROOT / 'basketball-natural-sfx.zip'
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file() and p.suffix != '.zip':
                z.write(p, p.relative_to(ROOT))
    print(f'Pack: {archive_path}; {archive_path.stat().st_size:,} bytes; preview {len(preview)/RATE:.2f} seconds')


if __name__ == '__main__':
    main()
