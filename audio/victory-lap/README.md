# Victory Lap

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
