# Overtime Overdrive

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
