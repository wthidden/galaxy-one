/**
 * WorldLayout - Calculates world positions on the map
 */
class WorldLayout {
    constructor() {
        this.positions = {};
        this.mapSize = 255;
        this.mapRadius = 1000;
        this.minDistance = 50; // Minimum distance between world centers
    }

    /**
     * Calculate positions for all worlds with collision avoidance
     */
    calculateLayout(worlds) {
        this.positions = {};

        if (!worlds) return;

        const worldIds = Object.keys(worlds).map(id => parseInt(id)).sort((a, b) => a - b);

        // First pass: Initial placement using Vogel's method (sunflower spiral)
        // This distributes points more evenly than simple circular arrangement
        const goldenAngle = Math.PI * (3 - Math.sqrt(5)); // ~137.5 degrees

        worldIds.forEach((worldId, index) => {
            const world = worlds[worldId];

            // Vogel's method for even distribution
            const angle = index * goldenAngle;
            const radius = Math.sqrt(index) * 50; // Spiral outward

            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;

            // Calculate world radius based on population
            const pop = (typeof world.population === 'number') ? world.population : 0;
            const worldRadius = Math.min(15 + pop * 0.1, 30);

            this.positions[worldId] = {
                x: x,
                y: y,
                radius: worldRadius,
                id: worldId
            };
        });

        // Second pass: Resolve collisions using iterative relaxation
        this.resolveCollisions(worldIds, 50); // 50 iterations max
    }

    /**
     * Resolve overlapping worlds by pushing them apart
     */
    resolveCollisions(worldIds, maxIterations = 50) {
        for (let iteration = 0; iteration < maxIterations; iteration++) {
            let hadCollision = false;

            // Check all pairs of worlds
            for (let i = 0; i < worldIds.length; i++) {
                const id1 = worldIds[i];
                const pos1 = this.positions[id1];

                for (let j = i + 1; j < worldIds.length; j++) {
                    const id2 = worldIds[j];
                    const pos2 = this.positions[id2];

                    // Calculate distance between centers
                    const dx = pos2.x - pos1.x;
                    const dy = pos2.y - pos1.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    // Minimum required distance (sum of radii + padding)
                    const minDist = pos1.radius + pos2.radius + this.minDistance;

                    if (distance < minDist && distance > 0.01) {
                        hadCollision = true;

                        // Calculate push force
                        const overlap = minDist - distance;
                        const pushX = (dx / distance) * overlap * 0.5;
                        const pushY = (dy / distance) * overlap * 0.5;

                        // Push both worlds apart
                        pos1.x -= pushX;
                        pos1.y -= pushY;
                        pos2.x += pushX;
                        pos2.y += pushY;
                    }
                }
            }

            // If no collisions this iteration, we're done
            if (!hadCollision) {
                console.log(`World layout converged after ${iteration + 1} iterations`);
                break;
            }
        }
    }

    /**
     * Get position for a world
     */
    getPosition(worldId) {
        return this.positions[worldId];
    }

    /**
     * Get all positions
     */
    getAllPositions() {
        return this.positions;
    }

    /**
     * Find world at a position
     */
    findWorldAt(x, y) {
        for (const worldId in this.positions) {
            const pos = this.positions[worldId];
            const dx = x - pos.x;
            const dy = y - pos.y;
            const distSq = dx * dx + dy * dy;

            if (distSq < pos.radius * pos.radius) {
                return worldId;
            }
        }
        return null;
    }

    /**
     * Clear layout
     */
    clear() {
        this.positions = {};
    }
}
