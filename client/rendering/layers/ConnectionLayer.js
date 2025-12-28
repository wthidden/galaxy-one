/**
 * ConnectionLayer - Renders connections between worlds
 */
class ConnectionLayer extends BaseLayer {
    constructor() {
        super('connections');
        this.selectedWorldId = null;
    }

    setSelectedWorld(worldId) {
        this.selectedWorldId = worldId;
    }

    render(ctx, camera, gameState, worldLayout) {
        if (!this.visible || !gameState || !gameState.worlds) return;

        const drawnConnections = new Set();

        // First pass: Draw all normal connections
        ctx.strokeStyle = '#444';
        ctx.lineWidth = 1 / camera.zoom;

        for (const worldId in gameState.worlds) {
            const world = gameState.worlds[worldId];
            const pos1 = worldLayout.getPosition(worldId);
            if (!pos1) continue;

            world.connections.forEach(targetId => {
                const pos2 = worldLayout.getPosition(targetId);
                if (!pos2) return;

                const connectionKey = [worldId, targetId].sort((a, b) => a - b).join('-');

                // Skip if already drawn or if this is a highlighted connection
                const isHighlighted = this.selectedWorldId &&
                    (worldId == this.selectedWorldId || targetId == this.selectedWorldId);

                if (!drawnConnections.has(connectionKey) && !isHighlighted) {
                    ctx.beginPath();
                    ctx.moveTo(pos1.x, pos1.y);
                    ctx.lineTo(pos2.x, pos2.y);
                    ctx.stroke();
                    drawnConnections.add(connectionKey);
                }
            });
        }

        // Second pass: Draw highlighted connections for selected world
        if (this.selectedWorldId) {
            const selectedWorld = gameState.worlds[this.selectedWorldId];
            if (selectedWorld) {
                const pos1 = worldLayout.getPosition(this.selectedWorldId);
                if (pos1) {
                    // Emphasized connections
                    ctx.strokeStyle = '#ffcc00';
                    ctx.lineWidth = 3 / camera.zoom;

                    selectedWorld.connections.forEach(targetId => {
                        const pos2 = worldLayout.getPosition(targetId);
                        if (!pos2) return;

                        const connectionKey = [this.selectedWorldId, targetId].sort((a, b) => a - b).join('-');

                        if (!drawnConnections.has(connectionKey)) {
                            ctx.beginPath();
                            ctx.moveTo(pos1.x, pos1.y);
                            ctx.lineTo(pos2.x, pos2.y);
                            ctx.stroke();
                            drawnConnections.add(connectionKey);
                        }
                    });
                }
            }
        }
    }
}
