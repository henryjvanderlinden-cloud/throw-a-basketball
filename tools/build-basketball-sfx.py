"""Deterministic, original arcade basketball sounds. Standard-library Python only."""
from pathlib import Path
import json
import math
import random
import struct
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1] / 'audio' / 'basketball-arcade'
SR = 44100
RATE = 11025
TAU = math.tau


def noise(rng, n):
    return [rng.uniform(-1, 1) for _ in range(n)]


def bandpass(values, frequency, q):
    omega = TAU * frequency / SR
    alpha = math.sin(omega) / (2 * q)
    a0 = 1 + alpha
    b0, b2 = alpha / a0, -alpha / a0
    a1, a2 = -2 * math.cos(omega) / a0, (1 - alpha) / a0
    x1 = x2 = y1 = y2 = 0.0
    result = []
    for x in values:
        y = b0 * x + b2 * x2 - a1 * y1 - a2 * y2
        result.append(y)
        x2, x1, y2, y1 = x1, x, y1, y
    return result


def squeak(variant, rng):
    duration = [0.145, 0.225, 0.185][variant]
    n = int(duration * SR)
    grit = bandpass(noise(rng, n), 3300, 0.8)
    phase = 0.0
    out = []
    for i in range(n):
        t, u = i / SR, i / n
        f = [1580, 1850, 1370][variant] + [580, -640, 820][variant] * u
        f += 70 * math.sin(TAU * (31 + variant * 9) * t)
        phase += TAU * f / SR
        gate = 1.0
        if variant == 1:
            gate = 1 - 0.94 * math.exp(-((u - 0.48) / 0.075) ** 6)
        env = min(1, t / 0.005) * max(0, 1 - u) ** 0.55 * gate
        tone = math.sin(phase) + 0.32 * math.sin(2 * phase) + 0.13 * math.sin(3 * phase)
        out.append(env * (0.60 * tone + 0.18 * grit[i]))
    return out


def impact(variant, rng, board=False):
    duration = ([0.25, 0.30, 0.23] if board else [0.21, 0.26, 0.19])[variant]
    n = int(duration * SR)
    grit = bandpass(noise(rng, n), 2100 if board else 1250, 0.8)
    base = ([155, 135, 180] if board else [108, 92, 126])[variant]
    phase = 0.0
    out = []
    for i in range(n):
        t = i / SR
        phase += TAU * (base + 115 * math.exp(-t / 0.008)) / SR
        body = math.sin(phase) * math.exp(-t / (0.046 if board else 0.040))
        body += 0.25 * math.sin(phase * 1.61) * math.exp(-t / 0.020)
        attack = grit[i] * math.exp(-t / 0.009) * (1.5 if board else 0.8)
        ring = 0.0
        if board:
            for f, amp, decay in [(435, 0.36, 0.043), (790, 0.22, 0.027), (1360, 0.13, 0.018)]:
                ring += amp * math.sin(TAU * f * (1 + variant * 0.07) * t) * math.exp(-t / decay)
        else:
            ring = 0.18 * math.sin(TAU * (670 + variant * 80) * t) * math.exp(-t / 0.017)
        out.append(min(1, t / 0.001) * (body + attack + ring))
    return out


def swish(variant, rng):
    duration = [0.27, 0.34, 0.23][variant]
    n = int(duration * SR)
    raw = noise(rng, n)
    air = bandpass(raw, 2850 + variant * 260, 0.65)
    fabric = bandpass(raw, 1150 + variant * 120, 1.1)
    out = []
    for i in range(n):
        t, u = i / SR, i / n
        env = min(1, t / 0.022) * (1 - u) ** 1.7
        flutter = 0.74 + 0.26 * math.sin(TAU * (49 + variant * 8) * t + 4 * u)
        cords = sum(math.exp(-((t - p) / 0.0035) ** 2) for p in [0.045, 0.078, 0.108])
        out.append(env * (1.5 * air[i] * flutter + 0.5 * fabric[i]) + 0.13 * cords * fabric[i])
    return out


def arcade(values, peak):
    # Intentional decimation without an antialiasing filter: period-style foldover.
    values = values[::4]
    average = sum(values) / len(values)
    values = [v - average for v in values]
    maximum = max(abs(v) for v in values)
    values = [math.tanh(v / maximum * 1.7) for v in values]
    maximum = max(abs(v) for v in values)
    result = []
    for i, v in enumerate(values):
        edge = min(1, i / 8, (len(values) - 1 - i) / 55)
        # 8-bit quantization and a quiet noise gate; silence remains exactly silent.
        v = v / maximum * peak * edge
        result.append(round(v * 127) / 128 if abs(v) > 0.006 else 0.0)
    return result


def write_wav(path, values, bits=16):
    path.parent.mkdir(parents=True, exist_ok=True)
    if bits == 8:
        data = bytes(max(0, min(255, round(v * 128) + 128)) for v in values)
    else:
        data = struct.pack('<' + 'h' * len(values), *(round(v * 32768) for v in values))
    with wave.open(str(path), 'wb') as wav:
        wav.setparams((1, bits // 8, RATE, len(values), 'NONE', 'not compressed'))
        wav.writeframes(data)


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest = {'sampleRate': RATE, 'channels': 1, 'textureBits': 8, 'effects': {}}
    preview = [0.0] * int(RATE * 0.25)
    sections = []
    for category, function, gain in [
        ('shoe-squeak', squeak, 0.65),
        ('backboard', lambda v, r: impact(v, r, True), 0.88),
        ('net-swish', swish, 0.64),
        ('floor-bounce', impact, 0.86),
    ]:
        rows = []
        for v in range(3):
            name = f'{category}-{v+1:02d}'
            rng = random.Random(9010 + len(manifest['effects']) * 10 + v)
            values = arcade(function(v, rng), gain)
            write_wav(ROOT / 'wav' / f'{name}.wav', values)
            write_wav(ROOT / 'pcm8' / f'{name}.wav', values, 8)
            start = len(preview) / RATE
            preview += values + [0.0] * int(RATE * 0.43)
            info = {'file': f'wav/{name}.wav', 'pcm8': f'pcm8/{name}.wav',
                    'durationMs': round(len(values) / RATE * 1000), 'previewStartSeconds': round(start, 3)}
            manifest['effects'][name] = info
            rows.append(f'<li><span>{name} <small>{info["durationMs"]} ms</small></span><audio controls preload="none" src="wav/{name}.wav"></audio></li>')
        sections.append(f'<section><h2>{category.replace("-", " ").title()}</h2><ul>{"".join(rows)}</ul></section>')
        preview += [0.0] * int(RATE * 0.38)
    write_wav(ROOT / 'preview.wav', preview)
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'preview.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Basketball Arcade SFX</title>
<style>body{background:#111522;color:#f7ead8;font:16px system-ui;max-width:850px;margin:40px auto;padding:0 20px}h1{color:#ffad4d}h2{font-size:21px}section{background:#20283c;padding:16px 24px;border-radius:14px;margin:18px 0}ul{padding:0;list-style:none}li{display:flex;align-items:center;justify-content:space-between;gap:15px;margin:14px 0;flex-wrap:wrap}small{color:#adb6c9}audio{height:36px;max-width:100%}p{line-height:1.6;color:#c4cadd}</style>
<h1>Basketball / Arcade '94</h1><p>12 original synthesized one-shots. 11.025 kHz mono, 8-bit crunch, short tails.<br>Listen to the full set or audition each variation below.</p><audio controls src="preview.wav"></audio>''' + ''.join(sections) + '</html>', encoding='utf-8')
    (ROOT / 'README.md').write_text('''# Basketball / Arcade '94

Twelve original synthesized sound effects, created for this game. No third-party samples were used.

| Group | Variations | Length |
| --- | --- | --- |
| Shoe squeak | Quick chirp, double squeak, rising skid | 145–225 ms |
| Backboard | Standard, low/heavy, high/tight | 230–300 ms |
| Net swish | Standard, longer flutter, quick swish | 230–340 ms |
| Floor bounce | Standard, low/heavy, high/light | 190–260 ms |

Open `preview.html` to audition individual clips. `preview.wav` plays the groups in the table order, three variations per group, with silent gaps. Preview timestamps are in `manifest.json`.

## Files and sound

- `wav/`: mono 16-bit PCM WAV at 11,025 Hz, with the 8-bit texture already baked in. Use these as the default game assets (176.4 kbps).
- `pcm8/`: the same sounds as unsigned 8-bit PCM WAV at 11,025 Hz, half the audio payload (88.2 kbps).
- Both versions intentionally use low sample rate, 8-bit quantization, mild aliasing, and soft saturation for an early-90s sampled arcade character. Aliasing is the crunchy artifact; antialiasing would suppress it.
- Compression here is dynamic saturation, not MP3-style file compression. PCM keeps short effects free of lossy codec padding.
- Peaks stay below full scale, with short edge fades and no long room reverb. Swishes and squeaks are quieter than impacts.

## Game integration

Use the paths in `manifest.json`. Preload/decode the default WAV files once; start audio after the player's first tap or key press. Randomize variants while avoiding the previous choice. Scale impact volume with collision strength; add an approximately 60–90 ms per-contact cooldown to avoid repeated collision triggers. Trigger swish only when a basket is made and shoe squeaks on stops or direction changes. Keep output gain conservative when several sounds overlap.

Assets are supplied ready for integration; this pack does not change game behavior.

Regenerate with `python tools/build-basketball-sfx.py` from the repository root. Generation is deterministic and needs only the Python standard library.
''', encoding='utf-8')
    zip_path = ROOT / 'basketball-arcade-sfx.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ROOT.rglob('*')):
            if path.is_file() and path != zip_path:
                archive.write(path, path.relative_to(ROOT))
    for name, info in manifest['effects'].items():
        with wave.open(str(ROOT / info['file']), 'rb') as wav:
            samples = struct.unpack('<' + 'h' * wav.getnframes(), wav.readframes(wav.getnframes()))
            assert wav.getnchannels() == 1 and wav.getframerate() == RATE
            assert max(map(abs, samples)) < 32767
            assert samples[0] == samples[-1] == 0
            assert any(samples)
        print(f'{name}: {info["durationMs"]} ms, peak {max(map(abs, samples))/32768:.3f}')
    print(f'Created 12 effects in two formats. Preview: {len(preview)/RATE:.2f}s. ZIP: {zip_path.stat().st_size:,} bytes')


if __name__ == '__main__':
    main()
