"""Original 60-second, seamlessly wrapped, retro martial-arts game composition."""
from pathlib import Path
import json
import math
import random
import struct
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1] / 'audio' / 'basketball-soundtrack'
RATE = 11025
BPM = 128
BEAT = 60 / BPM
BARS = 32
LENGTH = round(BARS * 4 * BEAT * RATE)
TAU = math.tau
rng = random.Random(940913)
mix = [0.0] * LENGTH
events = []


def hz(note):
    return 440 * 2 ** ((note - 69) / 12)


def voice(kind, note, seconds):
    n = round(seconds * RATE)
    f = hz(note)
    result = []
    # Slight inharmonicity and changing partial envelopes imitate early sampled/FM timbres.
    for i in range(n):
        t = i / RATE
        p = TAU * f * t
        attack = min(1, t / 0.003)
        release = min(1, (seconds - t) / 0.025)
        if kind == 'pluck':
            value = (math.sin(p + .62 * math.sin(2*p) * math.exp(-t/.042)) * math.exp(-t/.20)
                     + .32 * math.sin(2.002*p) * math.exp(-t/.075)
                     + .18 * math.sin(3.01*p) * math.exp(-t/.032))
        elif kind == 'bass':
            value = (math.sin(p) + .24 * math.sin(2*p) + .10 * math.sin(3*p)) * math.exp(-t/.22)
        elif kind == 'bell':
            value = (math.sin(p + 1.1 * math.sin(1.414*p) * math.exp(-t/.25))
                     + .20 * math.sin(2.76*p) * math.exp(-t/.12)) * math.exp(-t/.38)
        elif kind == 'flute':
            envelope = (1 - math.exp(-t/.035)) * math.exp(-t/.9)
            value = (math.sin(p + .055*math.sin(TAU*5.1*t)) + .13*math.sin(2*p)) * envelope
        elif kind == 'gong':
            value = sum(a * math.sin(p * ratio + .16*math.sin(TAU*3*t)) * math.exp(-t/decay)
                        for ratio, a, decay in [(1, .65, .65), (1.48, .35, .48), (2.13, .22, .35), (3.72, .10, .20)])
        else:
            raise ValueError(kind)
        result.append(value * attack * release)
    return result


def drum(kind, accent):
    duration = {'low': .30, 'high': .17, 'wood': .08, 'shaker': .045}[kind]
    n = round(duration * RATE)
    phase = 0.0
    previous = 0.0
    out = []
    for i in range(n):
        t = i / RATE
        white = rng.uniform(-1, 1)
        hiss = (white - previous) * .5
        previous = white
        if kind in ('low', 'high'):
            base = 68 if kind == 'low' else 142
            decay = .074 if kind == 'low' else .041
            phase += TAU * (base + 54*math.exp(-t/.009)) / RATE
            value = (math.sin(phase) + .27*math.sin(1.59*phase)) * math.exp(-t/decay)
            value += .36*hiss*math.exp(-t/.010)
        elif kind == 'wood':
            value = (.65*math.sin(TAU*920*t) + .40*math.sin(TAU*1475*t)) * math.exp(-t/.012)
            value += hiss*.30*math.exp(-t/.005)
        else:
            value = hiss * math.exp(-t/.010)
        out.append(value * min(1, t/.001) * min(1, (duration-t)/.009) * accent)
    return out


def place(values, beat, gain, room=False):
    start = round(beat * BEAT * RATE)
    for i, value in enumerate(values):
        mix[(start+i) % LENGTH] += value * gain
    if room:
        for delay, level in [(.087, .115), (.173, .065)]:
            offset = round(delay * RATE)
            for i, value in enumerate(values):
                mix[(start+offset+i) % LENGTH] += value * gain * level


def note(kind, midi, beat, length, gain):
    place(voice(kind, midi, length * BEAT), beat, gain, room=kind != 'bass')
    events.append({'voice': kind, 'midi': midi, 'beat': beat, 'lengthBeats': length})


def write_wav(path, values, bits=16):
    if bits == 8:
        data = bytes(v + 128 for v in values)
    else:
        data = struct.pack('<' + 'h' * len(values), *(v * 256 for v in values))
    with wave.open(str(path), 'wb') as f:
        f.setparams((1, bits // 8, RATE, len(values), 'NONE', 'not compressed'))
        f.writeframes(data)


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    # A: eight-bar call and response, D minor pentatonic. All melodies are newly composed.
    theme = [
        [(0,74,.75), (1,77,.5), (1.75,81,.75), (3,79,.5)],
        [(.5,77,.5), (1.25,74,1), (3,72,.5), (3.5,74,.5)],
        [(0,77,.5), (.75,79,.5), (1.5,81,1), (3,84,.75)],
        [(.5,81,.75), (1.5,79,.5), (2.5,77,1)],
        [(0,79,.75), (1,81,.5), (2,84,.75), (3.25,81,.5)],
        [(0,79,.5), (1,77,.75), (2.5,74,1)],
        [(.5,72,.5), (1.25,74,.5), (2,77,.5), (3,79,.5)],
        [(0,77,.75), (1.25,74,1.5)],
    ]
    bridge = [
        [(0,81,1.5), (2.5,79,1)], [(0,77,1), (1.75,74,1.75)],
        [(.5,79,1.25), (2.5,84,1)], [(0,81,2.5)],
        [(0,84,1), (1.5,86,1), (3,84,.75)], [(0,81,1.25), (2,79,1.5)],
        [(0,77,.75), (1.25,79,.75), (2.5,81,1)], [(0,79,1), (1.5,77,1), (3,72,.5)],
    ]
    roots = [38,38,41,36,43,43,36,38]
    for bar in range(BARS):
        start = bar * 4
        section, local = divmod(bar, 8)
        root = roots[local]
        # Low drum with syncopated lighter responses, sparse enough for game effects.
        hits = [(0,'low',.40), (1.5,'high',.16), (2.5,'low',.26), (3.5,'wood',.115)]
        if section == 2:
            hits = [(0,'low',.32), (2,'wood',.11), (3.5,'high',.15)]
        if local in (3,7):
            hits += [(3,'high',.14), (3.75,'high',.12)]
        for offset, kind, gain in hits:
            place(drum(kind, rng.uniform(.92,1.04)), start+offset, gain)
        for step in range(8):
            if section == 2 and step % 2 == 0:
                continue
            place(drum('shaker',1), start + step*.5, .038 if step % 2 else .024)
        for offset, pitch, length, gain in [(0,root,.85,.27),(1.5,root+12,.40,.13),(2.5,root+7,.70,.18)]:
            note('bass', pitch, start+offset, length, gain)
        # Quiet open-fifth punctuation leaves the foreground uncluttered.
        if local % 2 == 0:
            note('bell',root+24,start+.5,2.2,.085)
            note('bell',root+31,start+.5,1.8,.055)
        melody = bridge[local] if section == 2 else theme[local]
        for offset, pitch, length in melody:
            if section == 1 and local in (2,6) and offset >= 3:
                pitch += 5
            instrument = 'flute' if section == 2 else 'pluck'
            note(instrument,pitch,start+offset,length+(0.18 if instrument=='pluck' else 0),.205 if section==2 else .27)
        if section in (1,3) and local in (1,5):
            note('bell',86,start+3.5,.65,.085)
        if local == 0:
            note('gong',50,start,3,.09)
    # Pickup into the first phrase; all delayed tails wrap to the start of the loop.
    note('pluck',72,127,.40,.16)
    note('pluck',77,127.5,.42,.19)
    mean = sum(mix) / LENGTH
    centered = [v - mean for v in mix]
    peak = max(map(abs,centered))
    compressed = [math.tanh(v / peak * 1.45) for v in centered]
    peak = max(map(abs,compressed))
    pcm = [round(v / peak * 104) for v in compressed]
    write_wav(ROOT/'court-of-the-dragon.wav',pcm)
    write_wav(ROOT/'court-of-the-dragon-pcm8.wav',pcm,8)
    # An explicit repeat-boundary audition: final four seconds, then first four.
    write_wav(ROOT/'loop-seam-preview.wav',pcm[-4*RATE:]+pcm[:4*RATE])
    metadata = {'title':'Court of the Dragon', 'durationSeconds':60, 'bpm':BPM, 'bars':BARS,
                'timeSignature':'4/4', 'key':'D minor pentatonic', 'sampleRate':RATE,
                'channels':1, 'textureBits':8, 'loopStartFrame':0, 'loopEndFrameExclusive':LENGTH,
                'defaultFile':'court-of-the-dragon.wav','pcm8File':'court-of-the-dragon-pcm8.wav',
                'arrangement':[{'section':'Theme','startSeconds':0},{'section':'Theme variation','startSeconds':15},
                               {'section':'Flute response','startSeconds':30},{'section':'Theme return and pickup','startSeconds':45}]}
    (ROOT/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    (ROOT/'score.json').write_text(json.dumps(events,indent=2)+'\n',encoding='utf-8')
    (ROOT/'preview.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Court of the Dragon</title><style>body{background:#151c22;color:#f3e6d1;font:17px system-ui;max-width:720px;margin:70px auto;padding:24px}h1{color:#e3ae66}p{line-height:1.7;color:#bfc7cb}audio{width:100%;margin:16px 0}small{color:#a8b8ba}</style><h1>Court of the Dragon</h1><p>Original martial-arts arcade soundtrack.<br>60 seconds · 128 BPM · 8-bit texture · 11.025 kHz mono</p><audio controls loop src="court-of-the-dragon.wav"></audio><small>Looping is enabled. Press play to hear the full arrangement repeat.</small><p>Plucked melody, hollow drums, wooden percussion, bell accents, and a flute response. Four 15-second sections lead back into the opening.</p><h2>Loop boundary check</h2><audio controls src="loop-seam-preview.wav"></audio><small>The last four seconds followed immediately by the first four seconds.</small></html>''',encoding='utf-8')
    (ROOT/'README.md').write_text('''# Court of the Dragon

An original 60-second soundtrack loop with a retro martial-arts game mood: pentatonic plucked melody, hollow drums, wooden percussion, bell accents, and a contrasting flute passage. This is a new composition and synthesized performance; no game music or third-party recordings are sampled.

128 BPM, 4/4, 32 bars, D minor pentatonic. Four 15-second sections: theme, variation, flute response, theme return. A final pickup leads into the opening. Instrument and room tails wrap across the boundary; no fade-out or inserted silence.

- `court-of-the-dragon.wav`: recommended game asset, mono 16-bit PCM container with 8-bit quantization baked in, 11,025 Hz.
- `court-of-the-dragon-pcm8.wav`: identical waveform in unsigned 8-bit PCM, 11,025 Hz, 88.2 kbps.
- `preview.html`: looping player and separate boundary audition.
- `loop-seam-preview.wav`: last four seconds followed by first four seconds.
- `manifest.json`: tempo, sections, and exact loop boundaries.
- `score.json`: note events for future rearrangement.

Both full-track files contain exactly 661,500 frames (60 seconds). Set loop start to 0 and loop end to 60 seconds, or frame 661,500 exclusive. PCM needs no encoder-delay trimming. In a game, decode once and use the audio engine's sample-accurate loop facility; repeatedly restarting a finished audio element can introduce gaps. Start with the music at about 25–35% gain underneath gameplay effects, then adjust by ear.

The master retains the sound pack's low-resolution character and mild saturation, with about 1.8 dB peak headroom. No gameplay code was changed.

Regenerate with `python tools/build-arcade-soundtrack.py` using Python's standard library.
''',encoding='utf-8')
    with wave.open(str(ROOT/'court-of-the-dragon.wav'),'rb') as f:
        assert (f.getnframes(),f.getframerate(),f.getnchannels(),f.getsampwidth()) == (LENGTH,RATE,1,2)
        data16 = struct.unpack('<'+'h'*LENGTH,f.readframes(LENGTH))
    with wave.open(str(ROOT/'court-of-the-dragon-pcm8.wav'),'rb') as f:
        data8 = f.readframes(LENGTH)
        assert f.getsampwidth() == 1 and f.getnframes() == LENGTH
    assert list(data16) == [(v-128)*256 for v in data8]
    assert max(map(abs,pcm)) == 104
    assert len(set(pcm)) > 100
    jumps = sorted(abs(pcm[i]-pcm[i-1]) for i in range(1,LENGTH))
    seam_jump = abs(pcm[0]-pcm[-1])
    assert seam_jump <= max(4,jumps[int(len(jumps)*.99)]), 'Unexpected boundary discontinuity'
    rms = (sum(v*v for v in pcm)/LENGTH)**.5/128
    with zipfile.ZipFile(ROOT/'court-of-the-dragon-pack.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.iterdir()):
            if p.is_file() and p.suffix != '.zip':
                z.write(p,p.name)
    print(json.dumps({'durationSeconds':LENGTH/RATE,'noteEvents':len(events),'peakDbfs':20*math.log10(104/128),
                      'rmsDbfs':20*math.log10(rms),'seamStep8bitUnits':seam_jump,
                      'typical99PercentStep':jumps[int(len(jumps)*.99)],'output':str(ROOT)},indent=2))


if __name__ == '__main__':
    main()
