/**
 * BaseLayer - Abstract base class for rendering layers
 */
class BaseLayer {
    constructor(name) {
        this.name = name;
        this.visible = true;
        this.alpha = 1.0;
    }

    /**
     * Render this layer
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {Camera} camera - Camera for transformations
     * @param {Object} gameState - Current game state
     * @param {Object} worldLayout - World positions
     */
    render(ctx, camera, gameState, worldLayout) {
        throw new Error('render() must be implemented by subclass');
    }

    /**
     * Set visibility
     */
    setVisible(visible) {
        this.visible = visible;
    }

    /**
     * Set alpha (transparency)
     */
    setAlpha(alpha) {
        this.alpha = Math.max(0, Math.min(1, alpha));
    }

    /**
     * Check if layer is visible
     */
    isVisible() {
        return this.visible;
    }
}
