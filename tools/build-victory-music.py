"""A four-second victory sting and a 24-second looping major-key celebration."""
from pathlib import Path
from functools import lru_cache
import importlib.util
import json
import math
import wave
import zipfile
import numpy as np

spec=importlib.util.spec_from_file_location('engine',Path(__file__).with_name('build-full-court-soundtrack.py'))
e=importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
e.BPM=120
e.BEAT=.5
SR, BEAT, TAU=e.SR,.5,math.tau
ROOT=Path(__file__).resolve().parents[1]/'audio'/'victory-lap'


@lru_cache(maxsize=None)
def horn(midi,beats):
    duration=beats*BEAT
    t=np.arange(round(duration*SR))/SR
    p=TAU*440*2**((midi-69)/12)*t
    y=sum((np.sin(p*k)+.16*np.sin(p*k*1.002))/k**1.5 for k in range(1,5))
    y*=.76+.24*np.exp(-t/.07)
    return y*np.minimum(1,t/.012)*np.clip((duration-t)/.055,0,1)


class Arrangement:
    def __init__(self,seconds,loop):
        self.mix=np.zeros(round(seconds*SR))
        self.loop=loop
        self.events=[]

    def add(self,sound,beat,gain,echo=False):
        layers=[(0,1)]
        if echo:
            layers += [(.09,.115),(.19,.055),(.32,.027)]
        for delay,level in layers:
            start=round((beat*BEAT+delay)*SR)
            values=sound*gain*level
            if self.loop:
                start%=len(self.mix)
            if start>=len(self.mix):
                continue
            count=min(len(values),len(self.mix)-start)
            self.mix[start:start+count]+=values[:count]
            if self.loop and count<len(values):
                self.mix[:len(values)-count]+=values[count:]

    def note(self,kind,midi,beat,length,gain):
        sound=horn(midi,length) if kind=='horn' else e.instrument(kind,midi,length)
        self.add(sound,beat,gain,kind in ('horn','keys'))
        self.events.append({'part':kind,'midi':midi,'beat':beat,'lengthBeats':length,'gain':gain})

    def chord(self,kind,pitches,beat,length,gain):
        for pitch in pitches:
            self.note(kind,pitch,beat,length,gain/len(pitches)**.5)

    def hit(self,kind,beat,gain,variant=0):
        self.add(e.percussion(kind,variant),beat,gain)
        self.events.append({'part':kind,'beat':beat,'gain':gain})


def master(arrangement,peak):
    y=arrangement.mix.copy()
    if arrangement.loop:
        y-=np.mean(y)
    else:
        # A one-shot ends in exact silence; no wraparound echoes on the sting.
        y[:55]*=np.linspace(0,1,55)
        y[-441:]*=np.linspace(1,0,441)
    y=np.tanh(y/np.max(np.abs(y))*1.65)
    return np.rint(y/np.max(np.abs(y))*peak).astype(np.int16)


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    sting=Arrangement(4,False)
    # Opening C/G/E/C/A contour recalls the gameplay anthem, now in C major.
    for beat,pitch,length in [(0,72,.32),(.5,79,.32),(1,76,.32),(1.5,79,.32),(2,84,2.5)]:
        sting.note('horn',pitch,beat,length,.27)
    for i in range(8):
        sting.hit('snare',i*.25,.055+.013*i,i%3)
    sting.hit('kick',0,.39)
    sting.hit('kick',2,.49)
    sting.hit('crash',2,.15)
    sting.hit('clap',2,.23)
    sting.chord('horn',[60,64,67],0,.4,.17)
    sting.chord('horn',[60,64,67,72],2,2.5,.29)
    sting.note('bass',36,2,2.3,.30)
    for beat,pitch in [(3,79),(3.5,84),(4,88),(4.5,91)]:
        sting.note('keys',pitch,beat,2.3,.10)
    # Three four-bar phrases: theme, lighter keyboard answer, celebratory return.
    loop=Arrangement(24,True)
    tune=[
        [(0,72,.40),(.5,79,.40),(1.5,76,.60),(2.5,72,.30),(3,81,.65)],
        [(0,79,.65),(1,76,.35),(1.75,72,.55),(2.75,74,.30),(3.25,76,.45)],
        [(0,77,.65),(1,81,.35),(1.75,79,.50),(2.75,77,.30),(3.25,74,.45)],
        [(0,79,.65),(1,77,.35),(1.75,74,.55),(2.75,71,.30),(3.25,74,.45)],
    ]
    harmonies=[(36,[60,64,67]),(33,[60,64,69]),(41,[60,65,69]),(43,[59,62,67])]
    for bar in range(12):
        phrase,local=divmod(bar,4)
        start=bar*4
        root,chord=harmonies[local]
        for offset,gain in [(0,.43),(2,.37),(2.75,.23)]:
            loop.hit('kick',start+offset,gain)
        for offset in (1,3):
            loop.hit('snare',start+offset,.23,local%3)
            loop.hit('clap',start+offset+.012,.19)
        for step in range(8):
            loop.hit('hat',start+step*.5+(.025 if step%2 else 0),.049 if step%2==0 else .073,step%3)
        if local%2:
            loop.hit('open',start+3.5,.066)
        if local==3:
            for j,offset in enumerate((3.25,3.5,3.75)):
                loop.hit('tom',start+offset,.105+j*.015,j)
        if bar in (0,8):
            loop.hit('crash',start,.07)
        for offset,pitch,length,gain in [(0,root,.65,.25),(1.5,root+7,.3,.19),
                                        (2.5,root,.35,.23),(3.5,root+12,.28,.16)]:
            loop.note('bass',pitch,start+offset,length,gain)
        for offset in (.5,2.25):
            loop.chord('stab',chord,start+offset,.5,.125)
        if phrase==1:
            # A softer reply keeps a short score-screen loop from exhausting the listener.
            for j,offset in enumerate((0,.75,1.5,2.5,3.25)):
                loop.note('keys',chord[j%3]+12,start+offset,.85,.15)
            loop.chord('horn',chord,start,1.2,.095)
        else:
            for offset,pitch,length in tune[local]:
                if bar==11 and offset>=2.75:
                    continue
                loop.note('horn',pitch,start+offset,length,.19)
            if phrase==2 and local in (0,2):
                loop.note('keys',chord[2]+24,start+3.5,.7,.07)
    for beat,pitch in [(46.75,67),(47.25,71),(47.75,74)]:
        loop.note('horn',pitch,beat,.19,.13)
    sting_pcm=master(sting,110)
    loop_pcm=master(loop,101)
    for name,pcm in [('victory-sting',sting_pcm),('victory-lap-loop',loop_pcm)]:
        e.write_wav(ROOT/f'{name}.wav',pcm)
        e.write_wav(ROOT/f'{name}-pcm8.wav',pcm,8)
    # Audition the intended flow, then hear the victory loop repeat once.
    entry=loop_pcm.copy()
    entry[:55]=np.rint(entry[:55]*np.linspace(0,1,55)).astype(np.int16)
    e.write_wav(ROOT/'victory-sequence-preview.wav',np.concatenate((sting_pcm,entry,loop_pcm)))
    e.write_wav(ROOT/'loop-seam-preview.wav',np.concatenate((loop_pcm[-4*SR:],loop_pcm[:4*SR])))
    manifest={'title':'Victory Lap','bpm':120,'key':'C major','sampleRate':SR,'channels':1,'textureBits':8,
              'sting':{'file':'victory-sting.wav','pcm8File':'victory-sting-pcm8.wav','durationSeconds':4,'loop':False},
              'loop':{'file':'victory-lap-loop.wav','pcm8File':'victory-lap-loop-pcm8.wav','durationSeconds':24,
                      'bars':12,'loopStartFrame':0,'loopEndFrameExclusive':24*SR},
              'sequence':{'stingStartSeconds':0,'loopStartSeconds':4,'loopEntryFadeMilliseconds':5},
              'loopSections':[{'name':'Victory theme','startSeconds':0},{'name':'Keyboard reply','startSeconds':8},
                              {'name':'Celebration return','startSeconds':16}]}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (ROOT/'score.json').write_text(json.dumps({'sting':sting.events,'loop':loop.events},indent=2)+'\n',encoding='utf-8')
    (ROOT/'preview.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Victory Lap</title><style>body{background:#151d28;color:#f7eed9;font:17px system-ui;max-width:760px;margin:42px auto;padding:24px}h1{font-size:42px;color:#ffce58;margin-bottom:8px}h2{font-size:21px;margin-top:30px}p{line-height:1.7;color:#c4cedb}audio{width:100%;margin:8px 0}small{color:#c4cedb}</style><h1>VICTORY LAP</h1><p>Champions on the court.<br>120 BPM · C major · 8-bit texture · 11.025 kHz mono</p><h2>Victory sting · 4 seconds</h2><audio controls src="victory-sting.wav"></audio><p>Drum roll, rising brass call, and a celebratory chord.</p><h2>Celebration loop · 24 seconds</h2><audio controls loop src="victory-lap-loop.wav"></audio><p>Looping enabled. Main theme, keyboard reply, and a brighter return.</p><h2>Sting → loop → repeat</h2><audio controls src="victory-sequence-preview.wav"></audio><small>52-second demonstration. The loop starts at 0:04 and repeats at 0:28.</small><h2>Loop boundary check</h2><audio controls src="loop-seam-preview.wav"></audio><small>Last four seconds followed by the first four. Repeat boundary at 0:04.</small></html>''',encoding='utf-8')
    (ROOT/'README.md').write_text('''# Victory Lap

Two original victory-screen music assets in the established 8-bit arcade sound: a 4-second one-shot fanfare and a 24-second seamless celebration loop. 120 BPM, C major. Synth brass, drum roll, claps, bright keyboard accents, and a bouncy bass groove. The C–G–E–C–A theme turns Overtime Overdrive's minor opening contour into a major-key victory payoff. No third-party samples or existing song material are used.

## Files

- `victory-sting.wav`: one-shot fanfare, exactly 4 seconds; play once when the winner appears.
- `victory-lap-loop.wav`: 12-bar loop, exactly 24 seconds; victory theme (0–8s), keyboard reply (8–16s), celebratory return (16–24s).
- `*-pcm8.wav`: identical waveforms stored in unsigned 8-bit PCM.
- Default WAVs use 16-bit PCM containers with the 8-bit waveform baked in. All files are mono at 11,025 Hz; PCM8 assets use 88.2 kbps.
- `victory-sequence-preview.wav`: sting followed by two loop cycles (52 seconds).
- `loop-seam-preview.wav`: four seconds before and after the repeat point.
- `preview.html`: players for all of the above; automatic looping on the loop player.
- `manifest.json`: exact lengths, loop bounds, and transition settings.
- `score.json`: note and percussion events.

## Game integration

On victory, stop or briefly fade the gameplay track, play the sting once, then start the looping asset exactly 4 seconds later using the audio engine's scheduling clock. Apply a 5 ms entry fade only when starting the loop for the first time. Leave later repeats untouched. Alternatively, use the loop by itself with the same short entry fade.

Loop the complete 264,600-frame file: frame 0 to 264,600 exclusive, or 0 to 24 seconds. Instrument and reflection tails wrap across the repeat point. The sting contains 44,100 frames and ends at silence. Use sample-accurate audio scheduling and looping rather than media ended-event callbacks. HTML playback is for auditioning and may vary by browser.

The sting is mastered a little louder than the loop. Keep mixing headroom for any UI sounds. No gameplay code was changed.

Regenerate with `python tools/build-victory-music.py`. Requires NumPy and the adjacent `build-full-court-soundtrack.py` audio utilities.
''',encoding='utf-8')
    report={}
    for name,pcm in [('victory-sting',sting_pcm),('victory-lap-loop',loop_pcm)]:
        with wave.open(str(ROOT/f'{name}.wav'),'rb') as f:
            assert (f.getnframes(),f.getframerate(),f.getnchannels(),f.getsampwidth())==(len(pcm),SR,1,2)
            data16=np.frombuffer(f.readframes(len(pcm)),dtype='<i2')
        with wave.open(str(ROOT/f'{name}-pcm8.wav'),'rb') as f:
            assert (f.getnframes(),f.getframerate(),f.getnchannels(),f.getsampwidth())==(len(pcm),SR,1,1)
            data8=np.frombuffer(f.readframes(len(pcm)),dtype=np.uint8).astype(np.int16)
        assert np.array_equal(data16,(data8-128)*256)
        assert 0<np.max(np.abs(data16))<32767
        report[name]={'seconds':len(pcm)/SR,'peakDbfs':round(float(20*np.log10(np.max(np.abs(pcm))/128)),2)}
    assert sting_pcm[0]==sting_pcm[-1]==0
    assert np.any(sting_pcm[-SR:]),'Sting should retain its natural tail'
    seam=abs(int(loop_pcm[0])-int(loop_pcm[-1]))
    typical=float(np.quantile(np.abs(np.diff(loop_pcm.astype(float))),.99))
    assert seam<=max(4,typical),'Unexpected loop discontinuity'
    report['loopBoundary']={'step8bitUnits':seam,'sampleStep99Percentile':typical}
    sections=np.split(loop_pcm,3)
    assert all(not np.array_equal(sections[i],sections[j]) for i in range(3) for j in range(i+1,3))
    report['loopSectionRmsDbfs']=[round(float(20*np.log10(np.sqrt(np.mean((p.astype(float)/128)**2)))),2) for p in sections]
    (ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(ROOT/'victory-lap-pack.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.iterdir()):
            if p.is_file() and p.suffix!='.zip':
                z.write(p,p.name)
    print(json.dumps(report,indent=2),flush=True)
    print(str(ROOT/'victory-lap-pack.zip'),flush=True)


if __name__=='__main__':
    main()
