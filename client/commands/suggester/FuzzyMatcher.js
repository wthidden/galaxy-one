/**
 * FuzzyMatcher - Fuzzy string matching utilities
 */
class FuzzyMatcher {
    /**
     * Check if query matches target (case-insensitive prefix match)
     */
    matches(query, target) {
        if (!query || query.length === 0) return true;
        return target.toUpperCase().startsWith(query.toUpperCase());
    }

    /**
     * Score a match (higher is better)
     */
    score(query, target) {
        if (!query || query.length === 0) return 1;

        const q = query.toUpperCase();
        const t = target.toUpperCase();

        // Exact match
        if (q === t) return 1000;

        // Prefix match
        if (t.startsWith(q)) return 500 + (100 - q.length);

        // Contains match
        if (t.includes(q)) return 100;

        return 0;
    }

    /**
     * Filter and sort items by match quality
     */
    filter(query, items, getText = (item) => item) {
        if (!query || query.length === 0) return items;

        return items
            .map(item => ({
                item,
                score: this.score(query, getText(item))
            }))
            .filter(({ score }) => score > 0)
            .sort((a, b) => b.score - a.score)
            .map(({ item }) => item);
    }
}
