/**
 * OrderIndicatorsLayer - Shows visual indicators for queued orders on the map
 */
class OrderIndicatorsLayer extends BaseLayer {
    constructor() {
        super('order-indicators');
        this.myPlayerName = null;
    }

    setMyPlayerName(name) {
        this.myPlayerName = name;
    }

    render(ctx, camera, gameState, worldLayout) {
        if (!this.visible || !gameState || !gameState.orders) return;

        const orders = this._parseOrders(gameState.orders);

        // Render order indicators
        orders.forEach(order => {
            switch (order.type) {
                case 'MOVE':
                    this._renderMoveIndicator(ctx, camera, order, gameState, worldLayout);
                    break;
                case 'AMBUSH':
                    this._renderAmbushIndicator(ctx, camera, order, gameState, worldLayout);
                    break;
                case 'FIRE_WORLD':
                    this._renderFireWorldIndicator(ctx, camera, order, gameState, worldLayout);
                    break;
                case 'FIRE_FLEET':
                    this._renderFireFleetIndicator(ctx, camera, order, gameState, worldLayout);
                    break;
                case 'BUILD':
                    this._renderBuildIndicator(ctx, camera, order, gameState, worldLayout);
                    break;
                case 'TRANSFER':
                    this._renderTransferIndicator(ctx, camera, order, gameState, worldLayout);
                    break;
                case 'MIGRATE':
                    this._renderMigrateIndicator(ctx, camera, order, gameState, worldLayout);
                    break;
            }
        });
    }

    /**
     * Parse order strings into structured data
     */
    _parseOrders(orderStrings) {
        const orders = [];

        orderStrings.forEach(orderStr => {
            // "Move F5 -> W10"
            const moveMatch = orderStr.match(/Move F(\d+) -> W(\d+)/);
            if (moveMatch) {
                orders.push({
                    type: 'MOVE',
                    fleetId: parseInt(moveMatch[1]),
                    destWorld: parseInt(moveMatch[2])
                });
                return;
            }

            // "F5 Ambush"
            const ambushMatch = orderStr.match(/F(\d+) Ambush/);
            if (ambushMatch) {
                orders.push({
                    type: 'AMBUSH',
                    fleetId: parseInt(ambushMatch[1])
                });
                return;
            }

            // "F5 Fire at World P" or "F5 Fire at World I"
            const fireWorldMatch = orderStr.match(/F(\d+) Fire at World (P|I)/);
            if (fireWorldMatch) {
                orders.push({
                    type: 'FIRE_WORLD',
                    fleetId: parseInt(fireWorldMatch[1]),
                    target: fireWorldMatch[2]
                });
                return;
            }

            // "F5 Fire at F10"
            const fireFleetMatch = orderStr.match(/F(\d+) Fire at F(\d+)/);
            if (fireFleetMatch) {
                orders.push({
                    type: 'FIRE_FLEET',
                    fleetId: parseInt(fireFleetMatch[1]),
                    targetFleet: parseInt(fireFleetMatch[2])
                });
                return;
            }

            // "Build 25 IShips at W3", "Build 2 Industry at W3", etc.
            const buildMatch = orderStr.match(/Build (\d+) (IShips|PShips|Industry|Pop Limit|Robots|F\d+) at W(\d+)/);
            if (buildMatch) {
                orders.push({
                    type: 'BUILD',
                    amount: parseInt(buildMatch[1]),
                    target: buildMatch[2],
                    worldId: parseInt(buildMatch[3])
                });
                return;
            }

            // "Migrate 5 population from W3 to W10"
            const migrateMatch = orderStr.match(/Migrate (\d+) population from W(\d+) to W(\d+)/);
            if (migrateMatch) {
                orders.push({
                    type: 'MIGRATE',
                    amount: parseInt(migrateMatch[1]),
                    worldId: parseInt(migrateMatch[2]),
                    destWorld: parseInt(migrateMatch[3])
                });
                return;
            }

            // "Transfer 10 from F5 to I"
            const transferMatch = orderStr.match(/Transfer (\d+) from F(\d+) to (I|P|F\d+)/);
            if (transferMatch) {
                orders.push({
                    type: 'TRANSFER',
                    amount: parseInt(transferMatch[1]),
                    fleetId: parseInt(transferMatch[2]),
                    target: transferMatch[3]
                });
                return;
            }
        });

        return orders;
    }

    /**
     * Render move order indicator (arrow from origin to destination)
     */
    _renderMoveIndicator(ctx, camera, order, gameState, worldLayout) {
        const fleet = gameState.fleets?.[order.fleetId];
        if (!fleet) return;

        const originPos = worldLayout.getPosition(fleet.world);
        const destPos = worldLayout.getPosition(order.destWorld);
        if (!originPos || !destPos) return;

        // Draw curved arrow
        ctx.strokeStyle = '#2196F3';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);

        ctx.beginPath();
        ctx.moveTo(originPos.x, originPos.y);
        ctx.lineTo(destPos.x, destPos.y);
        ctx.stroke();
        ctx.setLineDash([]);

        // Draw arrowhead at destination
        const angle = Math.atan2(destPos.y - originPos.y, destPos.x - originPos.x);
        const arrowSize = 10;

        ctx.fillStyle = '#2196F3';
        ctx.beginPath();
        ctx.moveTo(
            destPos.x - arrowSize * Math.cos(angle - Math.PI / 6),
            destPos.y - arrowSize * Math.sin(angle - Math.PI / 6)
        );
        ctx.lineTo(destPos.x, destPos.y);
        ctx.lineTo(
            destPos.x - arrowSize * Math.cos(angle + Math.PI / 6),
            destPos.y - arrowSize * Math.sin(angle + Math.PI / 6)
        );
        ctx.fill();
    }

    /**
     * Render ambush indicator (pulsing circle at fleet location)
     */
    _renderAmbushIndicator(ctx, camera, order, gameState, worldLayout) {
        const fleet = gameState.fleets?.[order.fleetId];
        if (!fleet) return;

        const worldPos = worldLayout.getPosition(fleet.world);
        if (!worldPos) return;

        // Pulsing effect
        const time = Date.now() / 1000;
        const pulseScale = 0.8 + Math.sin(time * 3) * 0.2;

        ctx.strokeStyle = '#9C27B0';
        ctx.lineWidth = 2;
        ctx.setLineDash([3, 3]);
        ctx.beginPath();
        ctx.arc(worldPos.x, worldPos.y, 25 * pulseScale, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);

        // Draw ambush icon
        ctx.fillStyle = '#9C27B0';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('🎯', worldPos.x, worldPos.y - 30);
    }

    /**
     * Render fire at world indicator
     */
    _renderFireWorldIndicator(ctx, camera, order, gameState, worldLayout) {
        const fleet = gameState.fleets?.[order.fleetId];
        if (!fleet) return;

        const worldPos = worldLayout.getPosition(fleet.world);
        if (!worldPos) return;

        // Draw crosshairs
        ctx.strokeStyle = '#F44336';
        ctx.lineWidth = 2;

        const size = 20;
        ctx.beginPath();
        ctx.moveTo(worldPos.x - size, worldPos.y);
        ctx.lineTo(worldPos.x + size, worldPos.y);
        ctx.moveTo(worldPos.x, worldPos.y - size);
        ctx.lineTo(worldPos.x, worldPos.y + size);
        ctx.stroke();

        // Draw target icon
        ctx.strokeStyle = '#F44336';
        ctx.beginPath();
        ctx.arc(worldPos.x, worldPos.y, 15, 0, Math.PI * 2);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(worldPos.x, worldPos.y, 8, 0, Math.PI * 2);
        ctx.stroke();

        // Label (P or I)
        ctx.fillStyle = '#F44336';
        ctx.font = 'bold 12px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(order.target, worldPos.x, worldPos.y + 30);
    }

    /**
     * Render fire at fleet indicator
     */
    _renderFireFleetIndicator(ctx, camera, order, gameState, worldLayout) {
        const fleet = gameState.fleets?.[order.fleetId];
        const targetFleet = gameState.fleets?.[order.targetFleet];
        if (!fleet || !targetFleet) return;

        const worldPos = worldLayout.getPosition(fleet.world);
        if (!worldPos) return;

        // Draw combat indicator
        ctx.fillStyle = '#F44336';
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('⚔️', worldPos.x + 25, worldPos.y - 25);
    }

    /**
     * Render build indicator
     */
    _renderBuildIndicator(ctx, camera, order, gameState, worldLayout) {
        const worldPos = worldLayout.getPosition(order.worldId);
        if (!worldPos) return;

        // Draw construction icon
        ctx.fillStyle = '#4CAF50';
        ctx.font = 'bold 18px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('🏗️', worldPos.x - 25, worldPos.y - 25);

        // Draw amount badge
        ctx.fillStyle = '#4CAF50';
        ctx.fillRect(worldPos.x - 35, worldPos.y - 35, 20, 12);
        ctx.fillStyle = '#000';
        ctx.font = 'bold 10px Arial';
        ctx.fillText(order.amount, worldPos.x - 25, worldPos.y - 29);
    }

    /**
     * Render transfer indicator
     */
    _renderTransferIndicator(ctx, camera, order, gameState, worldLayout) {
        const fleet = gameState.fleets?.[order.fleetId];
        if (!fleet) return;

        const worldPos = worldLayout.getPosition(fleet.world);
        if (!worldPos) return;

        // Draw transfer icon
        ctx.fillStyle = '#FF9800';
        ctx.font = 'bold 18px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('📦', worldPos.x + 25, worldPos.y + 25);

        // Draw amount
        ctx.fillStyle = '#FF9800';
        ctx.font = 'bold 10px Arial';
        ctx.fillText(order.amount, worldPos.x + 25, worldPos.y + 40);
    }

    /**
     * Render migration indicator (arrow from source to destination world)
     */
    _renderMigrateIndicator(ctx, camera, order, gameState, worldLayout) {
        const originPos = worldLayout.getPosition(order.worldId);
        const destPos = worldLayout.getPosition(order.destWorld);
        if (!originPos || !destPos) return;

        // Draw curved arrow
        ctx.strokeStyle = '#00BCD4';
        ctx.lineWidth = 2;
        ctx.setLineDash([3, 3]);

        ctx.beginPath();
        ctx.moveTo(originPos.x, originPos.y);
        ctx.lineTo(destPos.x, destPos.y);
        ctx.stroke();
        ctx.setLineDash([]);

        // Draw arrowhead at destination
        const angle = Math.atan2(destPos.y - originPos.y, destPos.x - originPos.x);
        const arrowSize = 8;

        ctx.fillStyle = '#00BCD4';
        ctx.beginPath();
        ctx.moveTo(
            destPos.x - arrowSize * Math.cos(angle - Math.PI / 6),
            destPos.y - arrowSize * Math.sin(angle - Math.PI / 6)
        );
        ctx.lineTo(destPos.x, destPos.y);
        ctx.lineTo(
            destPos.x - arrowSize * Math.cos(angle + Math.PI / 6),
            destPos.y - arrowSize * Math.sin(angle + Math.PI / 6)
        );
        ctx.fill();

        // Draw migration icon at midpoint
        const midX = (originPos.x + destPos.x) / 2;
        const midY = (originPos.y + destPos.y) / 2;

        ctx.fillStyle = '#00BCD4';
        ctx.font = 'bold 18px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('👥', midX, midY);

        // Draw amount
        ctx.fillStyle = '#00BCD4';
        ctx.font = 'bold 10px Arial';
        ctx.fillText(order.amount, midX, midY + 15);
    }
}
