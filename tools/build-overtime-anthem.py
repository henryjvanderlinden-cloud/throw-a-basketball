"""Original early-90s Eurodance stadium anthem; 144 BPM, 72 bars, 120 seconds."""
from pathlib import Path
from functools import lru_cache
import importlib.util
import json
import math
import wave
import zipfile
import numpy as np

spec = importlib.util.spec_from_file_location('engine', Path(__file__).with_name('build-full-court-soundtrack.py'))
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
e.BPM = 144
e.BEAT = 60 / e.BPM
ROOT = Path(__file__).resolve().parents[1] / 'audio' / 'overtime-overdrive'
SR, N, BEAT, TAU = e.SR, e.N, e.BEAT, math.tau
original_voice = e.instrument


@lru_cache(maxsize=None)
def rave_voice(kind, midi, beats):
    if kind not in ('lead', 'bass', 'stab', 'organ', 'pad'):
        return original_voice(kind, midi, beats)
    duration = beats * BEAT
    t = np.arange(round(duration * SR)) / SR
    f = 440 * 2 ** ((midi - 69) / 12)
    p = TAU * f * t
    edge = np.minimum(1,t/.004)*np.clip((duration-t)/.024,0,1)
    if kind == 'lead':
        # Compact sampled-brass/saw hybrid with restrained detuning, not a modern supersaw.
        y = sum((np.sin(p*k)+.27*np.sin(p*k*1.0035)) / k**1.45 for k in range(1,7))
        y += .11*np.sin(p*2 + 1.4*np.sin(p)) * np.exp(-t/.045)
        y *= .72+.28*np.exp(-t/.055)
    elif kind == 'bass':
        y = np.sin(p)+.44*np.sin(2*p)+.23*np.sin(3*p)+.13*np.sin(4*p)
        y = np.tanh(y*1.3)*(.30+.70*np.exp(-t/.085))
    elif kind == 'stab':
        y = sum(np.sin(p*k + .28*np.sin(p*.5))/k**1.25 for k in range(1,7))
        y *= np.minimum(1,t/.008)*np.exp(-t/.12)
    elif kind == 'organ':
        y = (.80*np.sin(p)+.45*np.sin(2*p)+.18*np.sin(3*p)+.23*np.sin(4*p))
        y *= np.exp(-t/.17)
    else:
        y = np.sin(p)+.20*np.sin(2*p*1.002)+.12*np.sin(3*p)
        y *= np.minimum(1,t/.055)*np.clip((duration-t)/.12,0,1)
    return y*edge


e.instrument = rave_voice


def chord(kind, pitches, beat, length, gain):
    for pitch in pitches:
        e.note(kind,pitch,beat,length,gain/len(pitches)**.5,kind=='organ')


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    # New eight-bar tune over Cm / Ab / Eb / Bb. No borrowed melody or audio.
    tune = [
        [(0,72,.38),(.5,79,.38),(1.5,75,.62),(2.5,72,.30),(3,82,.65)],
        [(0,79,.62),(1,82,.30),(1.5,79,.30),(2,75,.62),(3,74,.30),(3.5,72,.30)],
        [(0,68,.38),(.5,75,.38),(1.5,72,.62),(2.5,75,.30),(3,80,.65)],
        [(0,79,.60),(1,75,.35),(1.75,72,.60),(2.75,70,.30),(3.25,72,.48)],
        [(0,75,.38),(.5,82,.38),(1.5,79,.62),(2.5,75,.30),(3,77,.65)],
        [(0,79,.62),(1,82,.30),(1.5,79,.30),(2,77,.62),(3,75,.30),(3.5,70,.30)],
        [(0,77,.38),(.5,82,.38),(1.5,74,.62),(2.5,77,.30),(3,80,.65)],
        [(0,77,.60),(1,74,.35),(1.75,70,.60),(2.75,74,.30),(3.25,71,.48)],
    ]
    answer = [
        [(0,79,.9),(1.5,75,.35),(2,72,.65),(3,75,.65)],
        [(0,82,.65),(1,79,.65),(2,77,.35),(2.5,75,.35),(3,72,.65)],
        [(0,80,.9),(1.5,75,.35),(2,72,.65),(3,75,.65)],
        [(0,84,.65),(1,80,.65),(2,79,.35),(2.5,75,.35),(3,72,.65)],
        [(0,82,.9),(1.5,79,.35),(2,75,.65),(3,79,.65)],
        [(0,87,.65),(1,82,.65),(2,79,.35),(2.5,77,.35),(3,75,.65)],
        [(0,82,.9),(1.5,77,.35),(2,74,.65),(3,77,.65)],
        [(0,86,.65),(1,82,.65),(2,80,.35),(2.5,77,.35),(3,74,.65)],
    ]
    harmony=[(36,[60,63,67]),(32,[56,60,63]),(39,[63,67,70]),(34,[58,62,65])]
    for bar in range(72):
        section, local = divmod(bar,8)
        start = bar*4
        root, pitches = harmony[local//2]
        breakdown = section==4
        build = section==5
        lean = section==2
        # Four-on-the-floor dance foundation, in contrast to the selection-screen breakbeat.
        kicks = [0,1,2,3]
        if breakdown:
            kicks = [0] if local%2==0 else []
        elif build and local<4:
            kicks = [0,2]
        for offset in kicks:
            e.hit('kick',start+offset,.54)
        if not breakdown or local>=6:
            for offset in (1,3):
                e.hit('snare',start+offset,.29,local%3)
                e.hit('clap',start+offset+.008,.25)
        if not breakdown:
            for step in range(8):
                e.hit('hat',start+step*.5,.052 if step%2==0 else .073,step%3)
            for offset in (.5,1.5,2.5,3.5):
                e.hit('open',start+offset,.080 if build else .105)
            if section in (1,3,6,7,8) and local%2:
                for offset in (2.25,2.75,3.75):
                    e.hit('hat',start+offset,.051,2)
        if local==0 and section!=4:
            e.hit('crash',start,.13)
        if local==7 and not breakdown:
            for j,offset in enumerate((3.25,3.5,3.75)):
                e.hit('tom' if section%2 else 'snare',start+offset,.13+j*.025,j%3)
        if build and local>=6:
            spacing = .5 if local==6 else .25
            for j in range(round(4/spacing)):
                e.hit('snare',start+j*spacing,.065+.007*j,j%3)
            if local==7:
                e.note('riser',48,start,4,.045)
        if breakdown:
            chord('pad',pitches,start,3.7,.16)
            for j,offset in enumerate((0,1.5,2.5)):
                e.note('organ',pitches[j]+12,start+offset,1.1,.14,True)
            if local>=4:
                e.note('bass',root,start,1.2,.16)
            continue
        for j,offset in enumerate((.5,1.5,2.5,3.5)):
            pitch = root+(12 if local%2 and j==3 else 0)
            e.note('bass',pitch,start+offset,.39,.30)
        if local%2 and not build:
            e.note('bass',root+7,start+3.25,.17,.16)
        # Large, short chord calls on the beat plus rhythmic organ responses.
        if not lean:
            for offset in (0,1.5,2.5):
                chord('stab',pitches,start+offset,.48,.145 if build else .17)
        if section in (1,2,3,5,6,7,8):
            for j,offset in enumerate((.75,1.75,2.75,3.75)):
                e.note('organ',pitches[j%3]+12,start+offset,.37,.09,False)
        if lean:
            if local%2==0:
                chord('stab',[p+12 for p in pitches],start,1.0,.20)
            for offset,pitch in [(1.5,pitches[2]+12),(2.5,pitches[1]+12),(3.5,pitches[0]+12)]:
                e.note('lead',pitch,start+offset,.28,.14,True)
            continue
        if build and local<4:
            for offset,pitch in [(0,tune[local][0][1]),(2,tune[local][2][1])]:
                e.note('organ',pitch,start+offset,.7,.12,True)
            continue
        phrase = answer[local] if section in (3,7) else tune[local]
        for offset,pitch,length in phrase:
            if section==8 and local==7 and offset>=2.5:
                continue
            e.note('lead',pitch,start+offset,length,.21,True)
            # Low octave reinforcement gives the late return more weight.
            if section==6 and offset in (0,1.5):
                e.note('lead',pitch-12,start+offset,length,.065,False)
        if section in (1,7) and local in (1,3,5):
            e.note('keys',pitches[2]+24,start+3.5,.45,.067,True)
    # Final rising pickup resolves to the opening C; echoes wrap sample-accurately.
    for beat,pitch in [(286.5,67),(287,70),(287.5,71)]:
        e.note('lead',pitch,beat,.31,.18,True)
    duck=np.ones(N)
    dt=np.arange(round(.14*SR))/SR
    for beat in e.KICKS:
        e.periodic_add(duck,-.23*np.exp(-dt/.048),round(beat*BEAT*SR))
    e.BUS['bass']*=np.clip(duck,.6,1)
    e.BUS['keys']*=np.clip(duck,.75,1)
    mix=sum(e.BUS.values())
    mix-=np.mean(mix)
    master=np.tanh(mix/np.max(np.abs(mix))*1.85)
    pcm=np.rint(master/np.max(np.abs(master))*108).astype(np.int16)
    e.write_wav(ROOT/'overtime-overdrive.wav',pcm)
    e.write_wav(ROOT/'overtime-overdrive-pcm8.wav',pcm,8)
    e.write_wav(ROOT/'loop-seam-preview.wav',np.concatenate((pcm[-6*SR:],pcm[:6*SR])))
    names=['Opening anthem','Anthem variation','Organ and bass groove','Second soaring hook',
           'Stadium breakdown','Rebuild and snare rise','Anthem returns','Second hook peak','Final drive and turnaround']
    sections=[{'name':name,'startSeconds':round(i*32*BEAT,6)} for i,name in enumerate(names)]
    manifest={'title':'Overtime Overdrive','durationSeconds':120,'bpm':144,'bars':72,'timeSignature':'4/4',
              'sampleRate':SR,'channels':1,'textureBits':8,'loopStartFrame':0,'loopEndFrameExclusive':N,
              'defaultFile':'overtime-overdrive.wav','pcm8File':'overtime-overdrive-pcm8.wav','sections':sections}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (ROOT/'score.json').write_text(json.dumps(e.EVENTS,indent=2)+'\n',encoding='utf-8')
    buttons=''.join(f'<button onclick="const a=document.getElementById(\'track\');a.currentTime={s["startSeconds"]};a.play()">{int(s["startSeconds"])//60}:{int(s["startSeconds"])%60:02d} · {s["name"]}</button>' for s in sections)
    (ROOT/'preview.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Overtime Overdrive</title><style>body{background:#101421;color:#f4eddf;font:17px system-ui;max-width:790px;margin:45px auto;padding:24px}h1{color:#d7ff54;font-size:42px;margin-bottom:8px}p{color:#c1c7d9;line-height:1.65}audio{width:100%;margin:15px 0}nav{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}button{padding:15px;text-align:left;background:#27304d;color:#f4eddf;border:1px solid #46527a;border-radius:8px;cursor:pointer}button:hover{background:#3a4669}small{color:#c1c7d9}</style><h1>OVERTIME OVERDRIVE</h1><p>An original stadium Eurodance anthem.<br>144 BPM · 2:00 · 11.025 kHz mono · 8-bit texture<br>Driving kicks, offbeat bass, rave brass, organ responses, and big melodic hooks.</p><audio id="track" controls loop src="overtime-overdrive.wav"></audio><small>Looping enabled. Jump to a section:</small><nav>''' + buttons + '''</nav><h2>Loop boundary</h2><audio controls src="loop-seam-preview.wav"></audio><p>Last six seconds followed by the first six; the loop boundary is at 0:06.</p></html>''',encoding='utf-8')
    (ROOT/'README.md').write_text('''# Overtime Overdrive

An original instrumental stadium anthem with early-90s Eurodance energy, written for the basketball game. Four-on-the-floor kicks, snare/clap backbeats, offbeat synth bass, bright rave brass, organ responses, and two original melodic hooks. No existing melody, lyrics, vocals, or recording is sampled.

144 BPM, 4/4, 72 bars, exactly 120 seconds. Nine eight-bar sections: opening anthem, variation, organ/bass groove, second hook, breakdown, rebuild, anthem return, second-hook peak, final drive and turnaround. Each section lasts 13 1/3 seconds. The breakdown and rebuild create contrast before the final run of hooks.

## Files

- `overtime-overdrive.wav`: recommended asset; mono 16-bit PCM container with an 8-bit waveform baked in, 11,025 Hz.
- `overtime-overdrive-pcm8.wav`: identical waveform in unsigned 8-bit PCM, 11,025 Hz, 88.2 kbps.
- `preview.html`: looping player and section-jump buttons.
- `loop-seam-preview.wav`: six seconds before and after the loop boundary.
- `manifest.json`: exact loop bounds and section timings.
- `score.json`: note and percussion events.

## Integration

Loop the complete file: frame 0 to frame 1,323,000 exclusive (0 to 120 seconds). Sound and echo tails wrap into the opening. No fade-out or inserted silence. Use sample-accurate audio-engine looping, not an ended-event restart. HTML media looping is for auditioning and is browser dependent.

Both formats retain the sound-effect packs' 8-bit / 11.025 kHz texture with saturation and about 1.5 dB peak headroom. Start background music at 25–35% gain under effects and adjust by ear. This asset pack does not modify gameplay.

Regenerate with `python tools/build-overtime-anthem.py`. Requires NumPy and the adjacent `build-full-court-soundtrack.py` audio utilities.
''',encoding='utf-8')
    with wave.open(str(ROOT/'overtime-overdrive.wav'),'rb') as f:
        assert (f.getnframes(),f.getframerate(),f.getnchannels(),f.getsampwidth())==(N,SR,1,2)
        data16=np.frombuffer(f.readframes(N),dtype='<i2')
    with wave.open(str(ROOT/'overtime-overdrive-pcm8.wav'),'rb') as f:
        assert (f.getnframes(),f.getframerate(),f.getnchannels(),f.getsampwidth())==(N,SR,1,1)
        data8=np.frombuffer(f.readframes(N),dtype=np.uint8).astype(np.int16)
    assert np.array_equal(data16,(data8-128)*256)
    assert np.max(np.abs(data16))<32767
    seam=abs(int(pcm[0])-int(pcm[-1]))
    percentile=float(np.quantile(np.abs(np.diff(pcm.astype(float))),.99))
    assert seam<=max(4,percentile),'Unexpected loop discontinuity'
    levels=[float(20*np.log10(np.sqrt(np.mean((p.astype(float)/128)**2)))) for p in np.split(pcm,9)]
    assert all(-32<level<-6 for level in levels)
    report={'durationSeconds':N/SR,'peakDbfs':round(20*np.log10(108/128),2),
            'sectionRmsDbfs':[round(v,2) for v in levels],'seamStep8bitUnits':seam,
            'sampleStep99Percentile':percentile,'scheduledEvents':len(e.EVENTS)}
    (ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(ROOT/'overtime-overdrive-pack.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.iterdir()):
            if p.is_file() and p.suffix!='.zip':
                z.write(p,p.name)
    print(json.dumps(report,indent=2),flush=True)
    print(str(ROOT/'overtime-overdrive-pack.zip'),flush=True)


if __name__=='__main__':
    main()
