/**
 * FleetLayer - Renders fleets (stationary and moving)
 */
class FleetLayer extends BaseLayer {
    constructor() {
        super('fleets');
        this.selectedFleetId = null;
        this.myPlayerName = null;
    }

    setSelectedFleet(fleetId) {
        this.selectedFleetId = fleetId;
    }

    setMyPlayerName(name) {
        this.myPlayerName = name;
    }

    render(ctx, camera, gameState, worldLayout) {
        if (!this.visible || !gameState) return;

        const movingFleets = this._getMovingFleets(gameState);
        const stationaryFleets = this._groupStationaryFleets(gameState, movingFleets);

        this._renderStationaryFleets(ctx, camera, stationaryFleets, worldLayout);
        this._renderMovingFleets(ctx, camera, movingFleets, gameState, worldLayout);
    }

    _getMovingFleets(gameState) {
        const moving = {};
        if (!gameState.orders) return moving;

        gameState.orders.forEach(orderText => {
            const match = orderText.match(/^Move F(\d+) -> W(\d+)$/);
            if (!match) return;

            const fleetId = parseInt(match[1]);
            const destId = parseInt(match[2]);
            const fleet = gameState.fleets?.[fleetId];
            if (!fleet) return;

            moving[fleetId] = {
                origin: fleet.world,
                dest: destId
            };
        });

        return moving;
    }

    _groupStationaryFleets(gameState, movingFleets) {
        const grouped = {};
        if (!gameState.fleets) return grouped;

        // Handle fleets as object
        const fleetsArray = Object.values(gameState.fleets);
        fleetsArray.forEach(fleet => {
            if (movingFleets[fleet.id]) return;

            if (!grouped[fleet.world]) {
                grouped[fleet.world] = [];
            }
            grouped[fleet.world].push(fleet);
        });

        return grouped;
    }

    _renderStationaryFleets(ctx, camera, fleetsByWorld, worldLayout) {
        for (const worldId in fleetsByWorld) {
            const worldPos = worldLayout.getPosition(worldId);
            if (!worldPos) continue;

            const fleets = fleetsByWorld[worldId];
            const friendlyFleets = fleets.filter(f => f.owner === this.myPlayerName);
            const hostileFleets = fleets.filter(f => f.owner !== this.myPlayerName);

            const fleetIconSize = Math.max(8, 14 / camera.zoom);

            // Render friendly fleets closer to world (clear of defense ring at radius+5)
            this._renderFleetRing(
                ctx,
                friendlyFleets,
                worldPos,
                worldPos.radius + 12,
                fleetIconSize,
                true
            );

            // Render hostile fleets further out (clear of artifacts at radius+8)
            this._renderFleetRing(
                ctx,
                hostileFleets,
                worldPos,
                worldPos.radius + 22,
                fleetIconSize,
                false
            );
        }
    }

    _renderFleetRing(ctx, fleets, worldPos, orbitRadius, iconSize, isFriendly) {
        fleets.forEach((fleet, index) => {
            const angle = (index / fleets.length) * 2 * Math.PI;
            const drawX = worldPos.x + Math.cos(angle) * orbitRadius;
            const drawY = worldPos.y + Math.sin(angle) * orbitRadius;

            // Selection highlight
            if (isFriendly && this.selectedFleetId == fleet.id) {
                ctx.strokeStyle = '#ffff00';
                ctx.lineWidth = 2 / 1; // Don't scale with zoom
                ctx.strokeRect(
                    drawX - iconSize / 2 - 1,
                    drawY - iconSize / 2 - 1,
                    iconSize + 2,
                    iconSize + 2
                );
            }

            // Check if fleet is empty (no ships)
            const isEmpty = !fleet.ships || fleet.ships <= 0;
            const hasCargo = fleet.cargo && fleet.cargo > 0;

            // Determine fleet color
            let fillColor;
            if (isEmpty) {
                fillColor = '#666666'; // Gray for empty fleets
            } else {
                fillColor = isFriendly ? '#4caf50' : '#f44336';
            }

            if (hasCargo) {
                // Diamond shape for fleets with cargo
                ctx.fillStyle = fillColor;
                ctx.beginPath();
                ctx.moveTo(drawX, drawY - iconSize / 2);
                ctx.lineTo(drawX + iconSize / 2, drawY);
                ctx.lineTo(drawX, drawY + iconSize / 2);
                ctx.lineTo(drawX - iconSize / 2, drawY);
                ctx.closePath();
                ctx.fill();

                // Cargo indicator
                ctx.strokeStyle = '#FFD700';
                ctx.lineWidth = 1;
                ctx.stroke();
            } else {
                // Square for fleets without cargo
                ctx.fillStyle = fillColor;
                ctx.fillRect(
                    drawX - iconSize / 2,
                    drawY - iconSize / 2,
                    iconSize,
                    iconSize
                );
            }

            // Fleet ID label
            if (iconSize > 4) {
                ctx.fillStyle = isEmpty ? '#999999' : '#fff';
                ctx.font = `bold ${Math.max(10, iconSize * 0.9)}px Arial`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(fleet.id, drawX, drawY);
            }

            // Artifact indicators (small gold badges)
            if (fleet.artifacts && Array.isArray(fleet.artifacts) && fleet.artifacts.length > 0) {
                const badgeSize = Math.max(8, iconSize * 0.4);
                const badgeX = drawX + iconSize / 2 + 2;
                const badgeY = drawY - iconSize / 2 - 2;

                // Draw gold badge with artifact count
                ctx.fillStyle = '#ffd700';
                ctx.beginPath();
                ctx.arc(badgeX, badgeY, badgeSize / 2, 0, 2 * Math.PI);
                ctx.fill();

                // Draw count
                ctx.fillStyle = '#000';
                ctx.font = `bold ${Math.max(6, badgeSize * 0.7)}px Arial`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(fleet.artifacts.length, badgeX, badgeY);
            }
        });
    }

    _renderMovingFleets(ctx, camera, movingFleets, gameState, worldLayout) {
        if (!gameState.fleets) return;

        for (const fleetId in movingFleets) {
            const move = movingFleets[fleetId];
            const originPos = worldLayout.getPosition(move.origin);
            const destPos = worldLayout.getPosition(move.dest);
            if (!originPos || !destPos) continue;

            const fleet = gameState.fleets[fleetId];
            if (!fleet) continue;

            // Animate position based on time (simple oscillation for now)
            const time = Date.now() / 1000;
            const progress = (Math.sin(time * 2) + 1) / 2; // Oscillate between 0 and 1

            // Draw connection line
            ctx.strokeStyle = fleet.owner === this.myPlayerName ? 'rgba(76, 175, 80, 0.3)' : 'rgba(244, 67, 54, 0.3)';
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.moveTo(originPos.x, originPos.y);
            ctx.lineTo(destPos.x, destPos.y);
            ctx.stroke();
            ctx.setLineDash([]);

            // Calculate fleet position along the line
            const fleetX = originPos.x + (destPos.x - originPos.x) * progress;
            const fleetY = originPos.y + (destPos.y - originPos.y) * progress;

            const size = Math.max(8, 16 / camera.zoom);
            const color = fleet.owner === this.myPlayerName ? '#4caf50' : '#f44336';

            // Calculate angle for rotation
            const angle = Math.atan2(destPos.y - originPos.y, destPos.x - originPos.x);

            // Draw triangle pointing in movement direction
            ctx.save();
            ctx.translate(fleetX, fleetY);
            ctx.rotate(angle);

            ctx.beginPath();
            ctx.moveTo(size / 2, 0);
            ctx.lineTo(-size / 2, -size / 2);
            ctx.lineTo(-size / 2, size / 2);
            ctx.closePath();
            ctx.fillStyle = color;
            ctx.fill();

            // Add outline for visibility
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 1;
            ctx.stroke();

            ctx.restore();

            // Fleet ID label
            if (size > 4) {
                ctx.fillStyle = '#fff';
                ctx.strokeStyle = '#000';
                ctx.lineWidth = 2;
                ctx.font = `bold ${size * 0.8}px Arial`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.strokeText(`F${fleet.id}`, fleetX, fleetY + size + 8);
                ctx.fillText(`F${fleet.id}`, fleetX, fleetY + size + 8);
            }
        }
    }
}
