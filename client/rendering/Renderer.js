/**
 * Renderer - Coordinates all rendering layers
 */
class Renderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.camera = null;
        this.worldLayout = null;
        this.layers = [];
        this.gameState = null;
        this.animationId = null;
        this.isAnimating = false;

        // Handle canvas resize
        this._setupResizeHandler();
    }

    /**
     * Set camera for viewport transformations
     */
    setCamera(camera) {
        this.camera = camera;
    }

    /**
     * Set world layout for position calculations
     */
    setWorldLayout(worldLayout) {
        this.worldLayout = worldLayout;
    }

    /**
     * Add a rendering layer
     */
    addLayer(layer) {
        this.layers.push(layer);
    }

    /**
     * Get layer by name
     */
    getLayer(name) {
        return this.layers.find(layer => layer.name === name);
    }

    /**
     * Main render loop
     */
    render(gameState) {
        if (!this.camera || !this.worldLayout) {
            console.warn('Renderer: camera or worldLayout not set');
            return;
        }

        this.gameState = gameState;

        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Save context state
        this.ctx.save();

        // Apply camera transformation
        this.camera.applyTransform(this.ctx, this.canvas);

        // Render each layer in order
        for (const layer of this.layers) {
            if (!layer.isVisible()) continue;

            this.ctx.save();

            // Apply layer alpha
            if (layer.alpha < 1.0) {
                this.ctx.globalAlpha = layer.alpha;
            }

            // Render the layer
            try {
                layer.render(this.ctx, this.camera, gameState, this.worldLayout);
            } catch (error) {
                console.error(`Error rendering layer ${layer.name}:`, error);
            }

            this.ctx.restore();
        }

        // Restore context state
        this.ctx.restore();

        // Check if we need continuous animation
        this._updateAnimationState(gameState);
    }

    /**
     * Check if animation should be running and start/stop accordingly
     */
    _updateAnimationState(gameState) {
        const needsAnimation = this._hasMovingFleets(gameState);

        if (needsAnimation && !this.isAnimating) {
            this.startAnimation();
        } else if (!needsAnimation && this.isAnimating) {
            this.stopAnimation();
        }
    }

    /**
     * Check if there are moving fleets or order indicators that need animation
     */
    _hasMovingFleets(gameState) {
        if (!gameState || !gameState.orders) return false;
        // Animate if there are moves or ambushes (ambush has pulsing effect)
        return gameState.orders.some(order =>
            order.includes('Move F') || order.includes('Ambush')
        );
    }

    /**
     * Start continuous animation
     */
    startAnimation() {
        if (this.isAnimating) return;

        this.isAnimating = true;
        const animate = () => {
            if (!this.isAnimating) return;

            if (this.gameState) {
                this.render(this.gameState);
            }

            this.animationId = requestAnimationFrame(animate);
        };

        this.animationId = requestAnimationFrame(animate);
    }

    /**
     * Stop continuous animation
     */
    stopAnimation() {
        this.isAnimating = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    /**
     * Resize canvas to fill container
     */
    resize() {
        const container = this.canvas.parentElement;
        const rect = container.getBoundingClientRect();

        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
    }

    /**
     * Setup automatic resize handling
     */
    _setupResizeHandler() {
        this.resize();

        window.addEventListener('resize', () => {
            this.resize();
        });
    }

    /**
     * Convert screen coordinates to world coordinates
     */
    screenToWorld(screenX, screenY) {
        if (!this.camera) return { x: 0, y: 0 };
        return this.camera.screenToWorld(screenX, screenY, this.canvas);
    }

    /**
     * Convert world coordinates to screen coordinates
     */
    worldToScreen(worldX, worldY) {
        if (!this.camera) return { x: 0, y: 0 };
        return this.camera.worldToScreen(worldX, worldY, this.canvas);
    }

    /**
     * Find world at screen position
     */
    findWorldAtScreen(screenX, screenY) {
        if (!this.worldLayout) return null;

        const worldPos = this.screenToWorld(screenX, screenY);
        return this.worldLayout.findWorldAt(worldPos.x, worldPos.y);
    }

    /**
     * Find fleet at screen position
     */
    findFleetAtScreen(screenX, screenY) {
        if (!this.gameState || !this.gameState.fleets || !this.worldLayout) return null;

        const worldPos = this.screenToWorld(screenX, screenY);
        const mouseX = worldPos.x;
        const mouseY = worldPos.y;

        // Get fleet layer to access orbit calculations
        const fleetLayer = this.getLayer('fleets');
        if (!fleetLayer) return null;

        const myPlayerName = fleetLayer.myPlayerName;

        // Check moving fleets first (they're more prominent)
        const movingFleets = fleetLayer._getMovingFleets(this.gameState);
        for (const fleetId in movingFleets) {
            const fleet = this.gameState.fleets[fleetId];
            if (!fleet) continue;

            const move = movingFleets[fleetId];
            const originPos = this.worldLayout.getPosition(move.origin);
            const destPos = this.worldLayout.getPosition(move.dest);
            if (!originPos || !destPos) continue;

            // Calculate current position
            const time = Date.now() / 1000;
            const progress = (Math.sin(time * 2) + 1) / 2;
            const fleetX = originPos.x + (destPos.x - originPos.x) * progress;
            const fleetY = originPos.y + (destPos.y - originPos.y) * progress;

            const size = Math.max(8, 16 / this.camera.zoom);
            const dx = mouseX - fleetX;
            const dy = mouseY - fleetY;
            if (dx * dx + dy * dy <= size * size) {
                return parseInt(fleetId);
            }
        }

        // Check stationary fleets
        const stationaryFleets = fleetLayer._groupStationaryFleets(this.gameState, movingFleets);

        for (const worldId in stationaryFleets) {
            const worldPos = this.worldLayout.getPosition(worldId);
            if (!worldPos) continue;

            const fleets = stationaryFleets[worldId];
            const friendlyFleets = fleets.filter(f => f.owner === myPlayerName);
            const hostileFleets = fleets.filter(f => f.owner !== myPlayerName);

            const iconSize = Math.max(8, 14 / this.camera.zoom);

            // Check friendly fleets (closer orbit)
            const friendlyOrbit = worldPos.radius + 12;
            for (let i = 0; i < friendlyFleets.length; i++) {
                const fleet = friendlyFleets[i];
                const angle = (i / friendlyFleets.length) * 2 * Math.PI;
                const fleetX = worldPos.x + Math.cos(angle) * friendlyOrbit;
                const fleetY = worldPos.y + Math.sin(angle) * friendlyOrbit;

                const dx = mouseX - fleetX;
                const dy = mouseY - fleetY;
                if (dx * dx + dy * dy <= iconSize * iconSize) {
                    return fleet.id;
                }
            }

            // Check hostile fleets (farther orbit)
            const hostileOrbit = worldPos.radius + 22;
            for (let i = 0; i < hostileFleets.length; i++) {
                const fleet = hostileFleets[i];
                const angle = (i / hostileFleets.length) * 2 * Math.PI;
                const fleetX = worldPos.x + Math.cos(angle) * hostileOrbit;
                const fleetY = worldPos.y + Math.sin(angle) * hostileOrbit;

                const dx = mouseX - fleetX;
                const dy = mouseY - fleetY;
                if (dx * dx + dy * dy <= iconSize * iconSize) {
                    return fleet.id;
                }
            }
        }

        return null;
    }
}
