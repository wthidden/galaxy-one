/**
 * QueuedOrders - Displays player's orders for this turn
 */
class QueuedOrders {
    constructor(elementId) {
        this.element = document.getElementById(elementId);
        this.onCancelOrder = null;
    }

    /**
     * Update queued orders with current game state
     */
    update(gameState) {
        if (!this.element || !gameState.orders) return;

        const orders = gameState.orders;

        // Build HTML
        let html = '<div class="orders-list">';

        if (orders.length === 0) {
            html += '<div class="empty-message">No orders queued</div>';
        } else {
            orders.forEach((order, index) => {
                const description = this._formatOrderDescription(order);
                const orderInfo = this._getOrderType(order);

                html += `
                    <div class="order-entry order-${orderInfo.type.toLowerCase().replace(/\s+/g, '-')}" data-order-index="${index}">
                        <div class="order-header">
                            <span class="order-type">${orderInfo.type}</span>
                            <button class="cancel-btn" data-order-index="${index}">✕</button>
                        </div>
                        <div class="order-description">${description}</div>
                    </div>
                `;
            });
        }

        html += '</div>';
        this.element.innerHTML = html;

        // Add cancel listeners
        this.element.querySelectorAll('.cancel-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const orderIndex = parseInt(btn.dataset.orderIndex);
                if (this.onCancelOrder) {
                    this.onCancelOrder(orderIndex);
                }
            });
        });
    }

    /**
     * Get order type and icon from order text
     */
    _getOrderType(order) {
        // Server sends formatted strings like:
        // "Move F5 -> W10"
        // "Build 25 IShips at W3"
        // "Build 25 PShips at W3"
        // "Build 2 Industry at W3"
        // "Build 1 Pop Limit at W3"
        // "Build 10 Robots at W3"
        // "Migrate 5 population from W3 to W10"
        // "Transfer 10 from F5 to I"
        // "F5 Fire at F10"
        // "F5 Ambush"

        if (typeof order === 'string') {
            if (order.includes('Move F')) return { type: 'MOVE', icon: '🚀' };
            if (order.includes('Migrate')) return { type: 'MIGRATE', icon: '👥' };
            if (order.includes('Load')) return { type: 'LOAD', icon: '📥' };
            if (order.includes('Unload')) return { type: 'UNLOAD', icon: '📤' };
            if (order.includes('Build') && order.includes('IShips')) return { type: 'BUILD ISHIPS', icon: '🔵' };
            if (order.includes('Build') && order.includes('PShips')) return { type: 'BUILD PSHIPS', icon: '🟢' };
            if (order.includes('Build') && order.includes('Industry')) return { type: 'BUILD INDUSTRY', icon: '🏭' };
            if (order.includes('Build') && order.includes('Pop Limit')) return { type: 'BUILD LIMIT', icon: '📈' };
            if (order.includes('Build') && order.includes('Robots')) return { type: 'BUILD ROBOTS', icon: '🤖' };
            if (order.includes('Build')) return { type: 'BUILD', icon: '🏗️' };
            if (order.includes('Transfer')) return { type: 'TRANSFER', icon: '📦' };
            if (order.includes('Fire at F')) return { type: 'FIRE FLEET', icon: '⚔️' };
            if (order.includes('Fire at World')) return { type: 'FIRE WORLD', icon: '💥' };
            if (order.includes('Ambush')) return { type: 'AMBUSH', icon: '🎯' };
        }

        return { type: 'ORDER', icon: '📋' };
    }

    /**
     * Format order description with color coding and icons
     */
    _formatOrderDescription(order) {
        if (typeof order !== 'string') return JSON.stringify(order);

        // Parse different order types and add formatting
        const orderInfo = this._getOrderType(order);

        // Color code important elements
        let formatted = order;

        // Highlight fleet IDs
        formatted = formatted.replace(/F(\d+)/g, '<span class="fleet-ref">F$1</span>');

        // Highlight world IDs
        formatted = formatted.replace(/W(\d+)/g, '<span class="world-ref">W$1</span>');

        // Highlight numbers (amounts)
        formatted = formatted.replace(/(\d+)\s+(I|P|ships?)/gi, '<span class="amount">$1</span> <span class="resource-type">$2</span>');

        // Highlight targets
        formatted = formatted.replace(/(Industry|Population|I|P)(?!\d)/g, '<span class="target-type">$1</span>');

        return `<span class="order-icon">${orderInfo.icon}</span> ${formatted}`;
    }

    /**
     * Set callback for cancel order events
     */
    setOnCancelOrder(callback) {
        this.onCancelOrder = callback;
    }
}
