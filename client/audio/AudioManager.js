/**
 * Audio Manager - Modern audio system with synthesized instruments and sample support
 *
 * Features:
 * - Multi-oscillator synthesis with ADSR envelopes
 * - Audio file loading and caching
 * - Reverb and filter effects
 * - Layered instrument sounds
 * - Much better than pure tones!
 */

class AudioManager {
    constructor() {
        this.enabled = true;
        this.audioContext = null;
        this.masterVolume = 0.3;
        this.audioBuffers = new Map(); // Cache for loaded audio files
        this.reverbNode = null;

        // Load settings from localStorage
        const savedSettings = localStorage.getItem('starweb_audio_settings');
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            this.enabled = settings.enabled !== false;
            this.masterVolume = settings.volume || 0.3;
        }

        // Initialize audio context on first user interaction
        this.initAudioContext();
    }

    initAudioContext() {
        if (!this.audioContext) {
            try {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                this.setupEffects();
            } catch (e) {
                console.warn('Web Audio API not supported:', e);
            }
        }
    }

    setupEffects() {
        if (!this.audioContext) return;

        // Create a simple reverb using convolver
        this.reverbNode = this.audioContext.createConvolver();
        this.reverbNode.connect(this.audioContext.destination);

        // Generate impulse response for reverb
        this.createReverbImpulse();
    }

    createReverbImpulse() {
        if (!this.audioContext || !this.reverbNode) return;

        const sampleRate = this.audioContext.sampleRate;
        const length = sampleRate * 0.5; // 0.5 second reverb
        const impulse = this.audioContext.createBuffer(2, length, sampleRate);

        for (let channel = 0; channel < 2; channel++) {
            const channelData = impulse.getChannelData(channel);
            for (let i = 0; i < length; i++) {
                channelData[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, 2);
            }
        }

        this.reverbNode.buffer = impulse;
    }

    /**
     * Resume audio context if suspended (browser autoplay policy)
     */
    async resumeContext() {
        if (!this.audioContext) return;
        if (this.audioContext.state === 'suspended') {
            await this.audioContext.resume();
        }
    }

    /**
     * Play a synthesized instrument note with ADSR envelope
     */
    playNote(frequency, duration, instrument = 'sine', options = {}) {
        if (!this.enabled || !this.audioContext) return;

        this.resumeContext();

        const now = this.audioContext.currentTime;
        const attack = options.attack || 0.01;
        const decay = options.decay || 0.1;
        const sustain = options.sustain || 0.7;
        const release = options.release || 0.1;
        const volume = (options.volume || 1.0) * this.masterVolume;
        const detune = options.detune || 0;

        // Create oscillator(s)
        const oscillators = [];
        const gainNode = this.audioContext.createGain();

        if (instrument === 'rich') {
            // Rich sound: 3 oscillators slightly detuned
            for (let i = 0; i < 3; i++) {
                const osc = this.audioContext.createOscillator();
                osc.type = 'sawtooth';
                osc.frequency.value = frequency;
                osc.detune.value = (i - 1) * 10 + detune; // Slight detune for richness
                osc.connect(gainNode);
                oscillators.push(osc);
            }
        } else if (instrument === 'bell') {
            // Bell-like: multiple harmonics
            const harmonics = [1, 2.76, 4.07, 5.43];
            harmonics.forEach((ratio, i) => {
                const osc = this.audioContext.createOscillator();
                osc.type = 'sine';
                osc.frequency.value = frequency * ratio;
                const harmGain = this.audioContext.createGain();
                harmGain.gain.value = 1 / (i + 1); // Decreasing harmonics
                osc.connect(harmGain);
                harmGain.connect(gainNode);
                oscillators.push(osc);
            });
        } else if (instrument === 'pad') {
            // Pad: soft, warm sound
            const osc1 = this.audioContext.createOscillator();
            osc1.type = 'sine';
            osc1.frequency.value = frequency;
            const osc2 = this.audioContext.createOscillator();
            osc2.type = 'triangle';
            osc2.frequency.value = frequency;
            osc2.detune.value = 5;
            osc1.connect(gainNode);
            osc2.connect(gainNode);
            oscillators.push(osc1, osc2);
        } else {
            // Default: single oscillator
            const osc = this.audioContext.createOscillator();
            osc.type = instrument;
            osc.frequency.value = frequency;
            osc.detune.value = detune;
            osc.connect(gainNode);
            oscillators.push(osc);
        }

        // Add filter for warmth
        const filter = this.audioContext.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.value = options.filterFreq || 2000;
        filter.Q.value = options.filterQ || 1;

        gainNode.connect(filter);

        // Route to destination (with optional reverb)
        if (options.reverb && this.reverbNode) {
            const dry = this.audioContext.createGain();
            const wet = this.audioContext.createGain();
            dry.gain.value = 0.7;
            wet.gain.value = 0.3;

            filter.connect(dry);
            dry.connect(this.audioContext.destination);
            filter.connect(wet);
            wet.connect(this.reverbNode);
        } else {
            filter.connect(this.audioContext.destination);
        }

        // ADSR envelope
        gainNode.gain.setValueAtTime(0, now);
        gainNode.gain.linearRampToValueAtTime(volume, now + attack);
        gainNode.gain.linearRampToValueAtTime(volume * sustain, now + attack + decay);
        gainNode.gain.setValueAtTime(volume * sustain, now + duration - release);
        gainNode.gain.linearRampToValueAtTime(0, now + duration);

        // Start and stop oscillators
        oscillators.forEach(osc => {
            osc.start(now);
            osc.stop(now + duration);
        });
    }

    /**
     * Play a melody (sequence of notes)
     */
    playMelody(notes, instrument = 'sine') {
        if (!this.enabled || !this.audioContext) return;

        let currentTime = this.audioContext.currentTime;

        notes.forEach(note => {
            setTimeout(() => {
                this.playNote(note.frequency, note.duration, instrument, note.options || {});
            }, (currentTime - this.audioContext.currentTime + (note.delay || 0)) * 1000);
            currentTime += note.duration + (note.delay || 0);
        });
    }

    /**
     * Load an audio file and cache it
     */
    async loadAudioFile(name, url) {
        if (this.audioBuffers.has(name)) {
            return this.audioBuffers.get(name);
        }

        try {
            const response = await fetch(url);
            const arrayBuffer = await response.arrayBuffer();
            const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            this.audioBuffers.set(name, audioBuffer);
            console.log(`Loaded audio: ${name}`);
            return audioBuffer;
        } catch (e) {
            console.error(`Failed to load audio ${name}:`, e);
            return null;
        }
    }

    /**
     * Play a loaded audio file
     */
    playAudioFile(name, options = {}) {
        if (!this.enabled || !this.audioContext) return;

        const buffer = this.audioBuffers.get(name);
        if (!buffer) {
            console.warn(`Audio file ${name} not loaded`);
            return;
        }

        this.resumeContext();

        const source = this.audioContext.createBufferSource();
        source.buffer = buffer;

        const gainNode = this.audioContext.createGain();
        gainNode.gain.value = (options.volume || 1.0) * this.masterVolume;

        source.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        source.start(0);
    }

    // ============================================================================
    // GAME EVENT SOUNDS - Much better than pure tones!
    // ============================================================================

    /**
     * Turn complete - triumphant chord progression
     */
    playTurnComplete() {
        // Play a nice C Major chord arpeggio
        const baseTime = 0;
        const notes = [
            { frequency: 523.25, duration: 0.15, delay: 0, options: { instrument: 'bell', reverb: true } },      // C5
            { frequency: 659.25, duration: 0.15, delay: 0.08, options: { instrument: 'bell', reverb: true } },   // E5
            { frequency: 783.99, duration: 0.15, delay: 0.08, options: { instrument: 'bell', reverb: true } },   // G5
            { frequency: 1046.50, duration: 0.4, delay: 0.08, options: { instrument: 'bell', reverb: true } }    // C6
        ];

        notes.forEach(note => {
            setTimeout(() => {
                this.playNote(note.frequency, note.duration, 'bell', {
                    reverb: true,
                    attack: 0.005,
                    decay: 0.1,
                    sustain: 0.6,
                    release: 0.2
                });
            }, note.delay * 1000);
        });
    }

    /**
     * Chat message - gentle notification pluck
     */
    playChatMessage() {
        this.playNote(880, 0.12, 'bell', {
            attack: 0.001,
            decay: 0.05,
            sustain: 0.3,
            release: 0.1,
            volume: 0.4,
            filterFreq: 2000
        });
        setTimeout(() => {
            this.playNote(1046.50, 0.08, 'bell', {
                attack: 0.001,
                decay: 0.05,
                sustain: 0.2,
                release: 0.08,
                volume: 0.3
            });
        }, 80);
    }

    /**
     * Admin message - authoritative brass-like chord
     */
    playAdminMessage() {
        // Play a power chord
        const frequencies = [440, 554.37, 659.25]; // A4, C#5, E5
        frequencies.forEach((freq, i) => {
            setTimeout(() => {
                this.playNote(freq, 0.3, 'rich', {
                    attack: 0.02,
                    decay: 0.1,
                    sustain: 0.7,
                    release: 0.15,
                    volume: 0.5,
                    filterFreq: 1500
                });
            }, i * 50);
        });
    }

    /**
     * Command confirmed - quick positive blip
     */
    playCommandConfirm() {
        this.playNote(1000, 0.06, 'sine', {
            attack: 0.001,
            decay: 0.02,
            sustain: 0.3,
            release: 0.04,
            volume: 0.35,
            filterFreq: 3000
        });
    }

    /**
     * Error - descending alert with tension
     */
    playError() {
        this.playNote(600, 0.12, 'square', {
            attack: 0.01,
            decay: 0.05,
            sustain: 0.6,
            release: 0.08,
            volume: 0.5,
            filterFreq: 800
        });
        setTimeout(() => {
            this.playNote(400, 0.15, 'square', {
                attack: 0.01,
                decay: 0.05,
                sustain: 0.5,
                release: 0.1,
                volume: 0.45,
                filterFreq: 600
            });
        }, 100);
    }

    /**
     * Fleet movement - smooth swoosh with pitch bend
     */
    playFleetMove() {
        const osc = this.audioContext.createOscillator();
        const gain = this.audioContext.createGain();
        const filter = this.audioContext.createBiquadFilter();

        osc.type = 'sine';
        filter.type = 'bandpass';

        const now = this.audioContext.currentTime;

        // Swoosh from low to high
        osc.frequency.setValueAtTime(200, now);
        osc.frequency.exponentialRampToValueAtTime(800, now + 0.15);

        filter.frequency.setValueAtTime(400, now);
        filter.frequency.exponentialRampToValueAtTime(1600, now + 0.15);
        filter.Q.value = 2;

        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(this.masterVolume * 0.25, now + 0.03);
        gain.gain.linearRampToValueAtTime(0, now + 0.15);

        osc.connect(filter);
        filter.connect(gain);
        gain.connect(this.audioContext.destination);

        osc.start(now);
        osc.stop(now + 0.15);
    }

    /**
     * Battle - dramatic low rumble with tension
     */
    playBattle() {
        // Low dramatic hits
        this.playNote(110, 0.25, 'rich', {
            attack: 0.02,
            decay: 0.1,
            sustain: 0.6,
            release: 0.15,
            volume: 0.6,
            filterFreq: 400
        });
        setTimeout(() => {
            this.playNote(130.81, 0.25, 'rich', {
                attack: 0.02,
                decay: 0.1,
                sustain: 0.5,
                release: 0.15,
                volume: 0.55,
                filterFreq: 350
            });
        }, 150);
    }

    /**
     * World conquered - victorious fanfare
     */
    playWorldConquered() {
        const fanfare = [
            { frequency: 523.25, duration: 0.12, delay: 0 },     // C5
            { frequency: 659.25, duration: 0.12, delay: 0.08 },  // E5
            { frequency: 783.99, duration: 0.15, delay: 0.08 },  // G5
            { frequency: 1046.50, duration: 0.35, delay: 0.08 }  // C6
        ];

        fanfare.forEach(note => {
            setTimeout(() => {
                this.playNote(note.frequency, note.duration, 'rich', {
                    attack: 0.005,
                    decay: 0.08,
                    sustain: 0.7,
                    release: 0.2,
                    volume: 0.6,
                    reverb: true
                });
            }, note.delay * 1000);
        });
    }

    // ============================================================================
    // SETTINGS
    // ============================================================================

    setEnabled(enabled) {
        this.enabled = enabled;
        this.saveSettings();
    }

    setVolume(volume) {
        this.masterVolume = Math.max(0, Math.min(1, volume));
        this.saveSettings();
    }

    isEnabled() {
        return this.enabled;
    }

    getVolume() {
        return this.masterVolume;
    }

    saveSettings() {
        localStorage.setItem('starweb_audio_settings', JSON.stringify({
            enabled: this.enabled,
            volume: this.masterVolume
        }));
    }

    // Test all sounds
    testAllSounds() {
        console.log('Testing all sounds...');
        setTimeout(() => this.playTurnComplete(), 0);
        setTimeout(() => this.playChatMessage(), 1000);
        setTimeout(() => this.playAdminMessage(), 2000);
        setTimeout(() => this.playCommandConfirm(), 3200);
        setTimeout(() => this.playError(), 3800);
        setTimeout(() => this.playFleetMove(), 4600);
        setTimeout(() => this.playBattle(), 5200);
        setTimeout(() => this.playWorldConquered(), 6000);
    }
}

// Export singleton instance
window.audioManager = new AudioManager();
