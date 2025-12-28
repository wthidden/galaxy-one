/**
 * WorldLayer - Renders worlds
 */
class WorldLayer extends BaseLayer {
    constructor() {
        super('worlds');
        this.hoveredWorldId = null;
        this.selectedWorldId = null;
        this.myPlayerName = null;
    }

    setHoveredWorld(worldId) {
        this.hoveredWorldId = worldId;
    }

    setSelectedWorld(worldId) {
        this.selectedWorldId = worldId;
    }

    setMyPlayerName(name) {
        this.myPlayerName = name;
    }

    render(ctx, camera, gameState, worldLayout) {
        if (!this.visible || !gameState || !gameState.worlds) return;

        for (const worldId in gameState.worlds) {
            const world = gameState.worlds[worldId];
            const pos = worldLayout.getPosition(worldId);
            if (!pos) continue;

            this._renderWorldDefenses(ctx, world, pos, camera);
            this._renderWorldCircle(ctx, worldId, world, pos, camera);
            this._renderArtifactIndicator(ctx, world, pos, camera);
            this._renderWorldLabel(ctx, worldId, pos, camera);
        }
    }

    _renderWorldDefenses(ctx, world, pos, camera) {
        if (world.iships <= 0 && world.pships <= 0) return;

        ctx.beginPath();
        ctx.arc(pos.x, pos.y, pos.radius + 5, 0, 2 * Math.PI);

        if (world.iships > 0 && world.pships > 0) {
            ctx.strokeStyle = '#00ffff'; // Cyan for both
        } else if (world.iships > 0) {
            ctx.strokeStyle = '#4da6ff'; // Blue for IShips
        } else {
            ctx.strokeStyle = '#4caf50'; // Green for PShips
        }

        ctx.lineWidth = 3 / camera.zoom;
        ctx.stroke();
    }

    _renderWorldCircle(ctx, worldId, world, pos, camera) {
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, pos.radius, 0, 2 * Math.PI);

        // Fill color based on owner
        const isMyHomeworld = world.key && world.owner === this.myPlayerName;

        if (world.owner) {
            if (isMyHomeworld) {
                // Gold gradient for player's homeworld
                const gradient = ctx.createRadialGradient(
                    pos.x - pos.radius / 3,
                    pos.y - pos.radius / 3,
                    0,
                    pos.x,
                    pos.y,
                    pos.radius
                );
                gradient.addColorStop(0, '#FFD700');
                gradient.addColorStop(1, '#FFA500');
                ctx.fillStyle = gradient;
            } else {
                ctx.fillStyle = world.owner === this.myPlayerName ? '#4da6ff' : '#ff5722';
            }
        } else {
            ctx.fillStyle = '#666';
        }

        // Hover highlight
        if (String(this.hoveredWorldId) === String(worldId)) {
            ctx.fillStyle = '#88ccee';
        }

        ctx.fill();

        // Border
        if (String(this.selectedWorldId) === String(worldId)) {
            ctx.strokeStyle = '#ffff00';
            ctx.lineWidth = 4 / camera.zoom;
        } else if (isMyHomeworld) {
            // Thicker gold border for homeworld
            ctx.strokeStyle = '#FFD700';
            ctx.lineWidth = 3 / camera.zoom;
        } else {
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2 / camera.zoom;
        }

        ctx.stroke();

        // Draw key icon for homeworld
        if (isMyHomeworld) {
            const fontSize = Math.max(12, 16 / camera.zoom);
            ctx.fillStyle = '#FFD700';
            ctx.font = `bold ${fontSize}px Arial`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            // Draw key emoji slightly above the world ID
            ctx.fillText('🔑', pos.x, pos.y - pos.radius - 8);
        }
    }

    _renderArtifactIndicator(ctx, world, pos, camera) {
        // Only show simple artifact count badge if world has been seen and has artifacts
        if (!world.artifacts || !Array.isArray(world.artifacts) || world.artifacts.length === 0) return;

        const badgeSize = Math.max(10, 14 / camera.zoom);
        const badgeX = pos.x + pos.radius + 8;
        const badgeY = pos.y;

        // Draw gold badge with artifact count
        ctx.fillStyle = '#ffd700';
        ctx.beginPath();
        ctx.arc(badgeX, badgeY, badgeSize / 2, 0, 2 * Math.PI);
        ctx.fill();

        // Draw count
        ctx.fillStyle = '#000';
        ctx.font = `bold ${Math.max(8, badgeSize * 0.7)}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(world.artifacts.length, badgeX, badgeY);
    }

    _renderWorldLabel(ctx, worldId, pos, camera) {
        const fontSize = Math.max(10, 14 / camera.zoom);
        ctx.fillStyle = '#fff';
        ctx.font = `bold ${fontSize}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(worldId, pos.x, pos.y);
    }
}
