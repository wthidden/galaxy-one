/**
 * Camera - Handles viewport transformation and controls
 */
class Camera {
    constructor() {
        this.x = 0;
        this.y = 0;
        this.zoom = 1.0;

        // Zoom limits
        this.minZoom = 0.1;
        this.maxZoom = 5.0;

        // Dragging state
        this.isDragging = false;
        this.dragStartX = 0;
        this.dragStartY = 0;
        this.lastMouseX = 0;
        this.lastMouseY = 0;
    }

    /**
     * Apply camera transformation to canvas context
     */
    applyTransform(ctx, canvas) {
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.scale(this.zoom, this.zoom);
        ctx.translate(-this.x, -this.y);
    }

    /**
     * Convert screen coordinates to world coordinates
     */
    screenToWorld(screenX, screenY, canvas) {
        const x = (screenX - canvas.width / 2) / this.zoom + this.x;
        const y = (screenY - canvas.height / 2) / this.zoom + this.y;
        return { x, y };
    }

    /**
     * Convert world coordinates to screen coordinates
     */
    worldToScreen(worldX, worldY, canvas) {
        const x = (worldX - this.x) * this.zoom + canvas.width / 2;
        const y = (worldY - this.y) * this.zoom + canvas.height / 2;
        return { x, y };
    }

    /**
     * Move camera to position
     */
    moveTo(x, y) {
        this.x = x;
        this.y = y;
    }

    /**
     * Pan camera by delta
     */
    pan(dx, dy) {
        this.x += dx;
        this.y += dy;
    }

    /**
     * Set zoom level
     */
    setZoom(zoom) {
        this.zoom = Math.max(this.minZoom, Math.min(this.maxZoom, zoom));
    }

    /**
     * Zoom at a specific point (usually mouse position)
     */
    zoomAt(worldX, worldY, zoomDelta) {
        const newZoom = Math.max(
            this.minZoom,
            Math.min(this.maxZoom, this.zoom + zoomDelta)
        );

        // Adjust camera position to zoom at point
        this.x = worldX - (worldX - this.x) * (newZoom / this.zoom);
        this.y = worldY - (worldY - this.y) * (newZoom / this.zoom);
        this.zoom = newZoom;
    }

    /**
     * Focus camera on a specific world position
     */
    focusOn(worldX, worldY, zoom = 1.0) {
        this.x = worldX;
        this.y = worldY;
        this.setZoom(zoom);
    }

    /**
     * Start dragging
     */
    startDrag(screenX, screenY) {
        this.isDragging = true;
        this.dragStartX = screenX;
        this.dragStartY = screenY;
        this.lastMouseX = screenX;
        this.lastMouseY = screenY;
    }

    /**
     * Update drag
     */
    updateDrag(screenX, screenY) {
        if (!this.isDragging) return false;

        const dx = screenX - this.lastMouseX;
        const dy = screenY - this.lastMouseY;

        this.x -= dx / this.zoom;
        this.y -= dy / this.zoom;

        this.lastMouseX = screenX;
        this.lastMouseY = screenY;

        return true;
    }

    /**
     * End dragging
     */
    endDrag() {
        this.isDragging = false;
    }

    /**
     * Check if drag was significant (not a click)
     */
    wasSignificantDrag(screenX, screenY, threshold = 5) {
        const dx = screenX - this.dragStartX;
        const dy = screenY - this.dragStartY;
        return Math.sqrt(dx * dx + dy * dy) > threshold;
    }
}
