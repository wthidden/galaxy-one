/**
 * Scoreboard - Displays player rankings
 */
class Scoreboard {
    constructor(elementId) {
        this.element = document.getElementById(elementId);
    }

    /**
     * Update scoreboard with current game state
     */
    update(gameState) {
        if (!this.element) return;

        // If no players data, show placeholder
        if (!gameState.players || Object.keys(gameState.players).length === 0) {
            this.element.innerHTML = '<div class="empty-message">No player data available</div>';
            return;
        }

        // Get players sorted by score
        const players = Object.values(gameState.players).sort((a, b) => b.score - a.score);

        // Build HTML
        let html = '<div class="scoreboard-list">';

        players.forEach((player, index) => {
            const rank = index + 1;
            const isMe = player.name === gameState.player_name;
            const readyIndicator = player.ready ? '✓' : '○';
            const characterIcon = this._getCharacterIcon(player.character_type);

            html += `
                <div class="scoreboard-entry ${isMe ? 'me' : ''}">
                    <span class="rank">#${rank}</span>
                    <span class="ready-indicator">${readyIndicator}</span>
                    <span class="player-name">${player.name}</span>
                    <span class="character-icon" title="${player.character_type}">${characterIcon}</span>
                    <span class="score">${player.score}</span>
                </div>
            `;
        });

        html += '</div>';
        this.element.innerHTML = html;
    }

    /**
     * Get icon for character type
     */
    _getCharacterIcon(characterType) {
        const icons = {
            'Empire Builder': '👑',
            'Merchant': '💰',
            'Pirate': '🏴‍☠️',
            'Artifact Collector': '💎',
            'Berserker': '⚔️',
            'Apostle': '✨'
        };
        return icons[characterType] || '❓';
    }
}
