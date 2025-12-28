/**
 * BackgroundLayer - Renders the starfield background
 */
class BackgroundLayer extends BaseLayer {
    constructor() {
        super('background');
    }

    render(ctx, camera, gameState, worldLayout) {
        if (!this.visible) return;

        // Simple black background
        ctx.fillStyle = '#050505';
        ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);

        // Could add stars here in the future
    }
}
