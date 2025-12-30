# StarWeb Audio System

## Modern Synthesis Engine

The AudioManager now uses advanced Web Audio API techniques instead of basic pure tones:

### Features
- **Multi-oscillator synthesis** - Rich, layered sounds using multiple oscillators
- **ADSR envelopes** - Attack, Decay, Sustain, Release for natural-sounding notes
- **Reverb effects** - Convolver-based reverb for spacious sounds
- **Filters** - Lowpass/bandpass filters for warmth and character
- **3 Instrument types**:
  - `bell` - Multiple harmonics for bell-like tones
  - `rich` - 3 detuned sawtooth oscillators for thick, analog sounds
  - `pad` - Soft, warm layered sound

### Current Sounds

All sounds are now synthesized with musical qualities:

1. **Turn Complete** - C Major arpeggio with bell harmonics + reverb
2. **Chat Message** - Gentle two-note pluck (A5 → C6)
3. **Admin Message** - Power chord (A4-C#5-E5) with rich synthesis
4. **Command Confirm** - Quick positive blip with ADSR
5. **Error** - Descending alert (600Hz → 400Hz) with tension
6. **Fleet Move** - Smooth pitch-bend swoosh with bandpass filter
7. **Battle** - Low dramatic hits (A2 → C3) with rich harmonics
8. **World Conquered** - Victorious fanfare with reverb

## Adding Custom Audio Files (Optional)

For even better sounds, you can load custom audio files:

### 1. Find Royalty-Free Sounds

**Recommended sources:**
- [Freesound.org](https://freesound.org) - CC0 and CC-BY licensed sounds
- [OpenGameArt.org](https://opengameart.org) - Game sounds, many CC0
- [ZapSplat](https://www.zapsplat.com) - Free sound effects (account required)
- [BBC Sound Effects](https://sound-effects.bbcrewind.co.uk/) - 16,000+ free sounds
- [Sonniss GDC Bundle](https://sonniss.com/gameaudiogdc) - Annual free bundle

### 2. Add Audio Files to Project

Place your audio files in: `/client/audio/sounds/`

Supported formats: MP3, WAV, OGG (WAV recommended for best quality)

Example structure:
```
client/audio/
├── AudioManager.js
├── README.md
└── sounds/
    ├── turn-complete.wav
    ├── chat-message.wav
    ├── admin-message.wav
    ├── command-confirm.wav
    ├── error.wav
    ├── fleet-move.wav
    ├── battle.wav
    └── world-conquered.wav
```

### 3. Load Audio Files

In `client/main.js` or wherever you initialize the audio manager:

```javascript
// Load custom audio files after AudioManager is initialized
async function loadCustomSounds() {
    const manager = window.audioManager;

    // Load sound files
    await manager.loadAudioFile('turn-complete', 'client/audio/sounds/turn-complete.wav');
    await manager.loadAudioFile('chat-message', 'client/audio/sounds/chat-message.wav');
    await manager.loadAudioFile('admin-message', 'client/audio/sounds/admin-message.wav');
    await manager.loadAudioFile('command-confirm', 'client/audio/sounds/command-confirm.wav');
    await manager.loadAudioFile('error', 'client/audio/sounds/error.wav');
    await manager.loadAudioFile('fleet-move', 'client/audio/sounds/fleet-move.wav');
    await manager.loadAudioFile('battle', 'client/audio/sounds/battle.wav');
    await manager.loadAudioFile('world-conquered', 'client/audio/sounds/world-conquered.wav');

    console.log('Custom sounds loaded!');
}

// Call after page load
loadCustomSounds();
```

### 4. Update AudioManager to Use Custom Files

Modify the sound methods in `AudioManager.js` to prefer loaded files:

```javascript
playTurnComplete() {
    if (this.audioBuffers.has('turn-complete')) {
        this.playAudioFile('turn-complete');
    } else {
        // Fallback to synthesized version
        // ... existing synthesis code ...
    }
}
```

## Audio File Specifications

For best results:

- **Sample rate:** 44.1kHz or 48kHz
- **Bit depth:** 16-bit or 24-bit
- **Format:** WAV (uncompressed) or OGG (compressed)
- **Duration:** 0.2s - 2s for most sounds
- **Volume:** Normalize to -6dB to -3dB (leave headroom)

## Testing Sounds

Open browser console and type:
```javascript
audioManager.testAllSounds();
```

This plays all sounds in sequence.

## Troubleshooting

**No sound playing:**
- Check browser console for errors
- Ensure audio is enabled (🔊 button)
- Try clicking page first (browser autoplay policy)
- Check master volume is not 0

**Sounds too quiet/loud:**
```javascript
audioManager.setVolume(0.5); // 0.0 to 1.0
```

**Load custom file:**
```javascript
await audioManager.loadAudioFile('my-sound', '/path/to/sound.wav');
audioManager.playAudioFile('my-sound');
```

## License Notes

The synthesized sounds are programmatically generated and have no licensing restrictions.

If you add custom audio files, ensure they are:
- Public domain (CC0)
- Creative Commons licensed with proper attribution
- Licensed for commercial use if applicable
- Not copyrighted material

Always check the license before using audio files!
