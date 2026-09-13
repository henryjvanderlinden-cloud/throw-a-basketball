# Full Court Pressure

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
