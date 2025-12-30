/**
 * Audio Manager - Handles sound effects for game events
 *
 * Generates tones programmatically using Web Audio API for:
 * - Turn completion
 * - New chat message
 * - Admin message
 * - Command confirmation
 * - Error notification
 */

class AudioManager {
    constructor() {
        this.enabled = true;
        this.audioContext = null;
        this.masterVolume = 0.3;

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
        // Create audio context lazily to avoid browser autoplay restrictions
        if (!this.audioContext) {
            try {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            } catch (e) {
                console.warn('Web Audio API not supported:', e);
            }
        }
    }

    /**
     * Play a tone with specific frequency and duration
     */
    playTone(frequency, duration, type = 'sine', volume = 1.0) {
        if (!this.enabled || !this.audioContext) return;

        // Resume context if suspended (browser autoplay policy)
        if (this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }

        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        oscillator.type = type;
        oscillator.frequency.value = frequency;

        // Set volume with envelope (fade in/out to avoid clicks)
        const now = this.audioContext.currentTime;
        const adjustedVolume = this.masterVolume * volume;
        gainNode.gain.setValueAtTime(0, now);
        gainNode.gain.linearRampToValueAtTime(adjustedVolume, now + 0.01);
        gainNode.gain.linearRampToValueAtTime(adjustedVolume, now + duration - 0.05);
        gainNode.gain.linearRampToValueAtTime(0, now + duration);

        oscillator.start(now);
        oscillator.stop(now + duration);
    }

    /**
     * Play a sequence of tones (melody)
     */
    playSequence(notes) {
        if (!this.enabled || !this.audioContext) return;

        let currentTime = this.audioContext.currentTime;

        notes.forEach(note => {
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);

            oscillator.type = note.type || 'sine';
            oscillator.frequency.value = note.frequency;

            const adjustedVolume = this.masterVolume * (note.volume || 1.0);
            gainNode.gain.setValueAtTime(0, currentTime);
            gainNode.gain.linearRampToValueAtTime(adjustedVolume, currentTime + 0.01);
            gainNode.gain.linearRampToValueAtTime(adjustedVolume, currentTime + note.duration - 0.05);
            gainNode.gain.linearRampToValueAtTime(0, currentTime + note.duration);

            oscillator.start(currentTime);
            oscillator.stop(currentTime + note.duration);

            currentTime += note.duration;
        });
    }

    // ============================================================================
    // GAME EVENT SOUNDS
    // ============================================================================

    /**
     * Turn complete - triumphant ascending chime
     */
    playTurnComplete() {
        this.playSequence([
            { frequency: 523.25, duration: 0.15, type: 'sine', volume: 0.6 },  // C5
            { frequency: 659.25, duration: 0.15, type: 'sine', volume: 0.7 },  // E5
            { frequency: 783.99, duration: 0.3, type: 'sine', volume: 0.8 }    // G5
        ]);
    }

    /**
     * New chat message - gentle notification
     */
    playChatMessage() {
        this.playSequence([
            { frequency: 800, duration: 0.1, type: 'sine', volume: 0.5 },
            { frequency: 1000, duration: 0.15, type: 'sine', volume: 0.4 }
        ]);
    }

    /**
     * Admin message - authoritative dual tone
     */
    playAdminMessage() {
        this.playSequence([
            { frequency: 440, duration: 0.15, type: 'square', volume: 0.6 },   // A4
            { frequency: 554.37, duration: 0.15, type: 'square', volume: 0.6 }, // C#5
            { frequency: 659.25, duration: 0.3, type: 'square', volume: 0.7 }   // E5
        ]);
    }

    /**
     * Command confirmed - quick positive beep
     */
    playCommandConfirm() {
        this.playTone(800, 0.08, 'sine', 0.4);
    }

    /**
     * Error - descending alert tone
     */
    playError() {
        this.playSequence([
            { frequency: 400, duration: 0.15, type: 'square', volume: 0.6 },
            { frequency: 300, duration: 0.2, type: 'square', volume: 0.5 }
        ]);
    }

    /**
     * Fleet movement - quick swoosh
     */
    playFleetMove() {
        this.playSequence([
            { frequency: 200, duration: 0.05, type: 'sine', volume: 0.3 },
            { frequency: 400, duration: 0.05, type: 'sine', volume: 0.3 },
            { frequency: 600, duration: 0.05, type: 'sine', volume: 0.2 }
        ]);
    }

    /**
     * Battle - dramatic low tone
     */
    playBattle() {
        this.playSequence([
            { frequency: 110, duration: 0.2, type: 'sawtooth', volume: 0.6 },
            { frequency: 130.81, duration: 0.2, type: 'sawtooth', volume: 0.5 }
        ]);
    }

    /**
     * World conquered - victorious fanfare
     */
    playWorldConquered() {
        this.playSequence([
            { frequency: 523.25, duration: 0.1, type: 'square', volume: 0.5 },  // C5
            { frequency: 659.25, duration: 0.1, type: 'square', volume: 0.6 },  // E5
            { frequency: 783.99, duration: 0.15, type: 'square', volume: 0.7 }, // G5
            { frequency: 1046.50, duration: 0.25, type: 'square', volume: 0.8 } // C6
        ]);
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
        setTimeout(() => this.playChatMessage(), 800);
        setTimeout(() => this.playAdminMessage(), 1600);
        setTimeout(() => this.playCommandConfirm(), 2400);
        setTimeout(() => this.playError(), 3000);
        setTimeout(() => this.playFleetMove(), 3600);
        setTimeout(() => this.playBattle(), 4200);
        setTimeout(() => this.playWorldConquered(), 4800);
    }
}

// Export singleton instance
window.audioManager = new AudioManager();
