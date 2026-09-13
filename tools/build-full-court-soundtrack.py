"""Original two-minute basketball arcade score, with periodic mixing and 8-bit PCM."""
from pathlib import Path
from functools import lru_cache
import json
import math
import wave
import zipfile
import numpy as np

ROOT = Path(__file__).resolve().parents[1] / 'audio' / 'full-court-pressure'
SR = 11025
BPM = 128
BEAT = 60 / BPM
N = SR * 120
TAU = math.tau
BUS = {name: np.zeros(N) for name in ('drums', 'bass', 'keys', 'lead', 'fx')}
EVENTS = []
KICKS = []


def periodic_add(destination, sound, start):
    start %= N
    first = min(len(sound), N - start)
    destination[start:start+first] += sound[:first]
    if first < len(sound):
        destination[:len(sound)-first] += sound[first:]


def place(bus, sound, beat, gain, echo=False):
    start = round(beat * BEAT * SR)
    periodic_add(BUS[bus], sound * gain, start)
    if echo:
        for delay, level in [(.75, .14), (1.5, .045)]:
            periodic_add(BUS[bus], sound * gain * level, start + round(delay * BEAT * SR))


@lru_cache(maxsize=None)
def instrument(kind, midi, beats):
    duration = beats * BEAT
    t = np.arange(round(duration * SR)) / SR
    f = 440 * 2 ** ((midi - 69) / 12)
    phase = TAU * f * t
    edge = np.minimum(1, t/.003) * np.minimum(1, (duration-t)/.018)
    if kind == 'bass':
        # Bright, short FM/slap-like bass stays audible on small speakers.
        y = np.sin(phase + .85*np.sin(phase*2)*np.exp(-t/.027))
        y += .30*np.sin(2*phase)*np.exp(-t/.13) + .13*np.sin(3*phase)*np.exp(-t/.06)
        y = np.tanh(y*1.25) * (.70*np.exp(-t/.16)+.30*np.exp(-t/.60))
    elif kind == 'lead':
        p = phase + .020*np.sin(TAU*5.5*t)
        y = np.sin(p + .32*np.sin(2*p)*np.exp(-t/.055)) + .27*np.sin(2*p) + .11*np.sin(3*p)
        y *= .68 + .32*np.exp(-t/.06)
        edge *= np.minimum(1, (duration-t)/.042)
    elif kind == 'stab':
        y = sum(np.sin(phase*k + .14*np.sin(phase)) / k for k in range(1,6))
        y *= np.minimum(1,t/.009)*np.exp(-t/.105)
    elif kind == 'keys':
        y = np.sin(phase + 1.6*np.sin(phase)*np.exp(-t/.060)) * np.exp(-t/.25)
        y += .14*np.sin(3*phase)*np.exp(-t/.055)
    elif kind == 'muted':
        y = (np.sin(phase)+.42*np.sin(2*phase)+.18*np.sin(3*phase))*np.exp(-t/.040)
    elif kind == 'riser':
        p = TAU*(f*t + 1.5*f*t*t/duration)
        y = np.sin(p + .8*np.sin(p*2)) * (t/duration)**1.5 * .6
    else:
        raise ValueError(kind)
    return y * np.clip(edge,0,1)


@lru_cache(maxsize=None)
def percussion(kind, variant=0):
    duration = {'kick':.24, 'snare':.18, 'clap':.15, 'hat':.043,
                'open':.16, 'tom':.17, 'crash':.65}[kind]
    t = np.arange(round(duration*SR))/SR
    rng = np.random.default_rng(199100 + variant + 37*list(('kick','snare','clap','hat','open','tom','crash')).index(kind))
    white = rng.uniform(-1,1,len(t))
    high = white - np.concatenate(([0],white[:-1]))
    if kind == 'kick':
        p = TAU*(54*t + 82*.010*(1-np.exp(-t/.010)))
        y = np.sin(p)*np.exp(-t/.065) + .22*np.sin(2*p)*np.exp(-t/.024)
        y += .15*high*np.exp(-t/.003)
    elif kind == 'snare':
        body = np.sin(TAU*(185+variant*6)*t)*np.exp(-t/.028)
        y = .58*body + .56*high*np.exp(-t/.037) + .24*white*np.exp(-t/.064)
    elif kind == 'clap':
        envelope = sum(np.where(t>=p,np.exp(-np.maximum(0,t-p)/.011),0) for p in (0,.009,.019))
        y = .42*high*envelope + .13*white*np.exp(-np.maximum(0,t-.019)/.038)*(t>=.019)
    elif kind in ('hat','open'):
        decay = .011 if kind=='hat' else .052
        metal = sum(np.sin(TAU*f*t) for f in (3127,4073,4651))/3
        y = (.74*high+.16*metal)*np.exp(-t/decay)
    elif kind == 'tom':
        base = [145,117,93][variant%3]
        p = TAU*(base*t + 35*.014*(1-np.exp(-t/.014)))
        y = (np.sin(p)+.24*np.sin(1.56*p))*np.exp(-t/.047)+.08*high*np.exp(-t/.010)
    else:
        metal = sum(np.sin(TAU*f*t) for f in (2243,2977,3761,4583))/4
        y = (.65*high+.17*metal)*np.exp(-t/.18)
    return y*np.minimum(1,t/.0008)*np.clip((duration-t)/.010,0,1)


def hit(kind, beat, gain, variant=0):
    place('drums',percussion(kind,variant),beat,gain)
    if kind == 'kick':
        KICKS.append(beat)
    EVENTS.append({'part':kind,'beat':round(beat,4),'gain':gain})


def note(kind, midi, beat, beats, gain, echo=False):
    bus = 'bass' if kind=='bass' else 'lead' if kind=='lead' else 'fx' if kind=='riser' else 'keys'
    place(bus,instrument(kind,midi,beats),beat,gain,echo)
    EVENTS.append({'part':kind,'note':midi,'beat':round(beat,4),'lengthBeats':beats,'gain':gain})


def write_wav(path, pcm, bits=16):
    data = (pcm+128).astype(np.uint8).tobytes() if bits==8 else (pcm.astype(np.int16)*256).astype('<i2').tobytes()
    with wave.open(str(path),'wb') as f:
        f.setparams((1,bits//8,SR,len(pcm),'NONE','not compressed'))
        f.writeframes(data)


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    # Original blues/pentatonic hooks in E. Tuple: beat offset, MIDI note, gate length.
    hook_a = [
        [(0,76,.42),(.75,76,.20),(1.5,79,.40),(2.25,81,.22),(2.75,79,.45),(3.5,76,.30)],
        [(.25,74,.35),(1,76,.70),(2.5,71,.22),(3,74,.22),(3.5,76,.32)],
        [(0,79,.40),(.75,81,.22),(1.25,82,.20),(1.75,83,.55),(2.75,81,.30),(3.5,79,.30)],
        [(0,76,.70),(1.25,74,.30),(2,71,.45),(3.25,74,.28)],
    ]
    hook_b = [
        [(0,83,.65),(1,81,.25),(1.75,79,.35),(2.5,76,.65)],
        [(.5,79,.32),(1.25,81,.32),(2,83,.32),(2.75,86,.65)],
        [(0,84,.65),(1,83,.25),(1.75,81,.35),(2.5,79,.65)],
        [(.25,78,.40),(1,75,.40),(1.75,71,.55),(3,74,.25),(3.5,75,.25)],
    ]
    bridge = [
        [(0,79,.65),(1.5,76,.35),(2.5,74,.45)],
        [(.5,76,.35),(1.5,79,.35),(2.5,83,.70)],
        [(0,81,.70),(1.25,79,.35),(2.5,76,.60)],
        [(0,78,.35),(.75,75,.35),(1.5,71,.65),(3.25,75,.30)],
    ]
    # Root and upper voicing: Em7, D, Cmaj7, B7. Bridge opens with Cmaj7 and Am7.
    harmony = [(40,[64,67,71,74]),(38,[62,66,69]),(36,[60,64,67,71]),(35,[59,63,66,69])]
    alt_harmony = [(36,[60,64,67,71]),(40,[64,67,71,74]),(33,[60,64,67,69]),(35,[59,63,66,69])]
    for bar in range(64):
        section, local = divmod(bar,8)
        start = bar*4
        breakdown = section==3
        sparse = breakdown and local < 4
        root,chord = (alt_harmony if section==5 else harmony)[(local//2)%4]
        # Immediate groove; swung subdivisions, small ghost notes, alternating kick patterns.
        kicks = [0,1.75,2.5] if local%2==0 else [0,.75,2,2.75]
        if sparse:
            kicks = [0,2.5]
        if local==7:
            kicks = [0,1.75,2.5]
        for offset in kicks:
            hit('kick',start+offset,.49 if offset==0 else .43)
        for offset in (1,3):
            hit('snare',start+offset,.37,local%3)
            if not sparse:
                hit('clap',start+offset+.012,.16)
        if local%2 and not sparse:
            hit('snare',start+2.77,.075,2)
        if local%4==2:
            hit('snare',start+.77,.065,1)
        for step in range(8):
            if sparse and step%2==0:
                continue
            offset = step*.5 + (.025 if step%2 else 0)
            hit('hat',start+offset,.092 if step%2 else .055,step%3)
        if not sparse and local%2==1:
            hit('open',start+3.5,.088)
        if local in (3,7):
            # Short fills, with a different contour at each section boundary.
            fill = [3.25,3.5,3.75] if local==7 else [3.5,3.75]
            for j,offset in enumerate(fill):
                hit('tom' if section%2==0 else 'snare',start+offset,.17+j*.015,j%3)
        if local==0 and section!=3:
            hit('crash',start,.11)
        if section in (4,6) and local in (2,6):
            for offset in (2.25,2.55):
                hit('hat',start+offset,.057,1)
        # Short funk bass phrases with octave answers and chromatic approach notes.
        bass = [(0,root,.43,.30),(.75,root,.19,.23),(1.5,root+12,.25,.20),
                (2,root+7,.25,.24),(2.75,root,.35,.29),(3.5,root+10,.20,.20)]
        if local%2:
            bass = [(0,root,.55,.30),(1.25,root+7,.22,.22),(1.75,root+12,.32,.22),
                    (2.5,root,.35,.28),(3.25,root-1,.18,.19),(3.5,root,.27,.25)]
        for offset,pitch,length,gain in bass:
            note('bass',pitch,start+offset,length,gain)
        if not sparse:
            stabs = [(.5,.12),(2.25,.10)] if section!=5 else [(.5,.095),(2.75,.08)]
            if local%2==1:
                stabs.append((3.5,.08))
            for offset,gain in stabs:
                for pitch in chord:
                    note('stab',pitch,start+offset,.43,gain/len(chord)**.5)
        if section in (1,2,4,6,7) or (breakdown and local>=4):
            for j,offset in enumerate((.25,1.25,2.75,3.25)):
                note('muted',chord[j%len(chord)]+12,start+offset,.22,.070)
        if breakdown:
            # Bass solo space, then a few answering keyboard figures and a build.
            if local>=4:
                for offset,pitch in [(.5,76),(1.25,79),(2.5,74)]:
                    note('keys',pitch,start+offset,.65,.11,True)
            if local==7:
                for j in range(6):
                    hit('snare',start+2.5+j*.25,.09+j*.022,j%3)
            continue
        melody = bridge[local%4] if section==5 else hook_b[local%4] if section in (2,6) else hook_a[local%4]
        for offset,pitch,length in melody:
            # Different endings, octave responses, and phrase gaps keep returns distinct.
            if section==1 and local>=4 and offset>=2.5:
                pitch += 12 if pitch<=76 else 0
            if section==7 and local==7 and offset>=2:
                continue
            kind = 'keys' if section==5 else 'lead'
            note(kind,pitch,start+offset,length+(.28 if kind=='keys' else 0),.17 if kind=='keys' else .18,True)
        if section in (4,6) and local in (1,5):
            for offset,pitch in [(2.25,88),(3.25,86)]:
                note('keys',pitch,start+offset,.55,.085,True)
        if local==7 and section in (1,5):
            note('riser',52,start+2.5,1.5,.055)
    # A brief final pickup into the opening E hook, with room/delay tails wrapped.
    for offset,pitch in [(254.5,71),(255,74),(255.5,75)]:
        note('lead',pitch,offset,.24,.145,True)
    # Gentle kick ducking keeps bass and percussion defined; process the loop periodically.
    duck = np.ones(N)
    env_t = np.arange(round(.13*SR))/SR
    dip = .18*np.exp(-env_t/.043)
    for beat in KICKS:
        periodic_add(duck,-dip,round(beat*BEAT*SR))
    BUS['bass'] *= np.clip(duck,.66,1)
    mix = sum(BUS.values())
    mix -= np.mean(mix)
    peak = np.max(np.abs(mix))
    master = np.tanh(mix/peak*1.85)
    master /= np.max(np.abs(master))
    pcm = np.rint(master*108).astype(np.int16)
    write_wav(ROOT/'full-court-pressure.wav',pcm)
    write_wav(ROOT/'full-court-pressure-pcm8.wav',pcm,8)
    write_wav(ROOT/'loop-seam-preview.wav',np.concatenate((pcm[-6*SR:],pcm[:6*SR])))
    names = ['Tip-off hook','Hook variation','Second hook','Bass and drums break',
             'Main hook returns','Keyboard contrast','Second hook lift','Final hook and turnaround']
    manifest = {'title':'Full Court Pressure','durationSeconds':120,'bpm':BPM,'timeSignature':'4/4',
                'bars':64,'sampleRate':SR,'channels':1,'textureBits':8,'loopStartFrame':0,
                'loopEndFrameExclusive':N,'defaultFile':'full-court-pressure.wav',
                'pcm8File':'full-court-pressure-pcm8.wav',
                'sections':[{'name':name,'startSeconds':i*15} for i,name in enumerate(names)]}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (ROOT/'score.json').write_text(json.dumps(EVENTS,indent=2)+'\n',encoding='utf-8')
    buttons=''.join(f'<button onclick="const a=document.getElementById(\'track\');a.currentTime={i*15};a.play()">{i*15//60}:{i*15%60:02d} · {name}</button>' for i,name in enumerate(names))
    (ROOT/'preview.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Full Court Pressure</title><style>body{background:#10151e;color:#eee9df;font:17px system-ui;max-width:780px;margin:45px auto;padding:24px}h1{color:#ffad3d;font-size:42px;margin-bottom:8px}p{color:#b9c5d5;line-height:1.65}audio{width:100%;margin:15px 0}nav{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}button{padding:15px;text-align:left;background:#253247;color:#f4e8d4;border:1px solid #41516a;border-radius:8px;cursor:pointer}button:hover{background:#364761}small{color:#b9c5d5}</style><h1>FULL COURT PRESSURE</h1><p>Basketball arcade funk · 128 BPM · 2:00<br>Crunchy breaks, slap-style bass, synth hooks, and stadium stabs.<br>11.025 kHz mono / 8-bit texture.</p><audio id="track" controls loop src="full-court-pressure.wav"></audio><small>Looping enabled. Jump to any section:</small><nav>''' + buttons + '''</nav><h2>Loop boundary</h2><audio controls src="loop-seam-preview.wav"></audio><p>Last six seconds followed immediately by the first six. The repeat happens halfway through this preview.</p></html>''',encoding='utf-8')
    (ROOT/'README.md').write_text('''# Full Court Pressure

Original two-minute basketball arcade soundtrack: syncopated breakbeats, snare/clap backbeats, swung hats, bright slap-style synth bass, bluesy hooks, FM keys, and stadium-style chord stabs. Newly composed and synthesized; no existing game melodies or third-party recordings are sampled.

128 BPM, 4/4, 64 bars, exactly 120 seconds. The eight 15-second sections are: tip-off hook, hook variation, second hook, bass/drums break, main hook return, keyboard contrast, second hook lift, final hook and turnaround. Bass patterns alternate, hooks develop, and short percussion fills mark transitions.

## Files

- `full-court-pressure.wav`: recommended game asset, mono 16-bit PCM container with an 8-bit waveform baked in, 11,025 Hz.
- `full-court-pressure-pcm8.wav`: identical waveform in unsigned 8-bit PCM, 11,025 Hz, 88.2 kbps.
- `preview.html`: looping player with section-jump buttons.
- `loop-seam-preview.wav`: six seconds before and after the repeat point.
- `manifest.json`: section times, format, and exact loop bounds.
- `score.json`: note and percussion events.

## Loop integration

Both full tracks contain exactly 1,323,000 samples. Loop from frame 0 to frame 1,323,000 exclusive, or 0–120 seconds. All sound and delay tails are mixed across the boundary. No fade-out, inserted silence, or lossy codec padding. Use the game audio engine's sample-accurate looping; restarting playback from an ended event can introduce a gap. The included HTML player is for auditioning; browser media-element repeats are not a sample-accuracy guarantee.

Keep music below gameplay effects; start around 25–35% gain and adjust by ear. The master has approximately 1.5 dB peak headroom, gentle saturation, and the same low-resolution character as the sound-effect packs. No gameplay code was changed.

Regenerate with `python tools/build-full-court-soundtrack.py` (requires NumPy).
''',encoding='utf-8')
    # Verify exact length, format equivalence, non-silent sections and boundary continuity.
    with wave.open(str(ROOT/'full-court-pressure.wav'),'rb') as f:
        assert (f.getnframes(),f.getframerate(),f.getnchannels(),f.getsampwidth()) == (N,SR,1,2)
        data16=np.frombuffer(f.readframes(N),dtype='<i2')
    with wave.open(str(ROOT/'full-court-pressure-pcm8.wav'),'rb') as f:
        assert (f.getnframes(),f.getframerate(),f.getnchannels(),f.getsampwidth()) == (N,SR,1,1)
        data8=np.frombuffer(f.readframes(N),dtype=np.uint8).astype(np.int16)
    assert np.array_equal(data16,(data8-128)*256)
    assert np.max(np.abs(data16)) < 32767
    jumps=np.abs(np.diff(pcm.astype(float)))
    seam=abs(int(pcm[0])-int(pcm[-1]))
    assert seam <= max(4,np.quantile(jumps,.99)), 'Unexpected seam discontinuity'
    levels=[20*np.log10(np.sqrt(np.mean((part.astype(float)/128)**2))) for part in np.split(pcm,8)]
    assert all(-30<level<-6 for level in levels)
    # Low-resolution sections must differ, including repeated hooks.
    assert all(not np.array_equal(pcm[i*15*SR:(i+1)*15*SR],pcm[j*15*SR:(j+1)*15*SR]) for i in range(8) for j in range(i+1,8))
    report={'durationSeconds':N/SR,'peakDbfs':round(20*np.log10(108/128),2),
            'sectionRmsDbfs':[round(v,2) for v in levels],'seamStep8bitUnits':seam,
            'sampleStep99Percentile':float(np.quantile(jumps,.99)), 'scheduledEvents':len(EVENTS)}
    (ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(ROOT/'full-court-pressure-pack.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.iterdir()):
            if p.is_file() and p.suffix!='.zip':
                z.write(p,p.name)
    print(json.dumps(report,indent=2),flush=True)
    print(str(ROOT/'full-court-pressure-pack.zip'),flush=True)


if __name__ == '__main__':
    main()
