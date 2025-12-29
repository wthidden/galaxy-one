# Test Coverage Report

**Generated:** 2025-12-29
**Overall Coverage:** 35% (778/2231 statements)
**Test Suite:** 99 tests (92 passing, 7 failing)

## Summary by Module

| Module | Statements | Covered | Coverage | Status |
|--------|-----------|---------|----------|--------|
| **Command Parser Registry** | 169 | 164 | **97%** | ✅ Excellent |
| **Entities** | 73 | 50 | **68%** | ✅ Good |
| **Movement Mechanics** | 114 | 63 | **55%** | ⚠️ Moderate |
| **Commands** | 561 | 304 | **54%** | ⚠️ Moderate |
| **Combat Mechanics** | 131 | 47 | **36%** | ⚠️ Low |
| **Game State** | 132 | 39 | **30%** | ⚠️ Low |
| **Production Mechanics** | 522 | 111 | **21%** | ❌ Very Low |
| **Turn Processor** | 101 | 0 | **0%** | ❌ Not Tested |
| **Ownership Mechanics** | 78 | 0 | **0%** | ❌ Not Tested |
| **Persistence** | 105 | 0 | **0%** | ❌ Not Tested |
| **Command Handlers** | 196 | 0 | **0%** | ❌ Not Tested |
| **Help Content** | 49 | 0 | **0%** | ❌ Not Tested |

## Detailed Analysis

### Excellent Coverage (90-100%)

#### Command Parser Registry (97%)
**Coverage:** 164/169 statements tested

**What's Tested:**
- ✅ All 17+ command parsers (move, build, transfer, fire, etc.)
- ✅ Pattern matching and regex parsing
- ✅ Parameter extraction and conversion

**What's NOT Tested (5 lines):**
- Lines 207-211: Migrate command parser (not fully implemented yet)

**Recommendation:** Complete migrate command implementation and add tests.

---

### Good Coverage (60-89%)

#### Entities (68%)
**Coverage:** 50/73 statements tested

**What's Tested:**
- ✅ Player, World, Fleet, Artifact creation
- ✅ Basic entity methods and properties
- ✅ Dictionary serialization (to_dict)

**What's NOT Tested (23 lines):**
- Visibility/ownership checks in to_dict methods
- Some edge cases in entity relationships
- World production calculations

**Recommendation:** Add tests for entity visibility and ownership logic.

---

### Moderate Coverage (40-59%)

#### Movement Mechanics (55%)
**Coverage:** 63/114 statements tested

**What's Tested:**
- ✅ Fleet movement execution
- ✅ Probe order execution
- ✅ Basic movement validation

**What's NOT Tested (51 lines):**
- Ambush mechanics (handle_ambush function)
- Multi-hop movement paths
- Edge cases in probe execution

**Recommendation:** Add tests for ambush scenarios and complex movement paths.

#### Commands (54%)
**Coverage:** 304/561 statements tested

**What's Tested:**
- ✅ All command class constructors
- ✅ Basic validation logic (ownership, existence checks)
- ✅ to_order() and get_description() methods

**What's NOT Tested (257 lines):**
- Many edge case validations
- Complex validation scenarios (resource limits, etc.)
- Some command-specific validation logic (Migration, etc.)

**Recommendation:** Add more validation tests for edge cases and resource constraints.

---

### Low Coverage (20-39%)

#### Combat Mechanics (36%)
**Coverage:** 47/131 statements tested

**What's Tested:**
- ✅ Basic fire order structure
- ✅ Some damage calculations

**What's NOT Tested (84 lines):**
- Defense fire execution
- Fire at world defenses (F#AH)
- Combat damage to ISHIPS/PSHIPS
- World neutralization
- Most combat mechanics execution

**Recommendation:** Add comprehensive combat execution tests.

#### Game State (30%)
**Coverage:** 39/132 statements tested

**What's Tested:**
- ✅ get_game_state() function
- ✅ set_game_state() function
- ✅ Basic state initialization

**What's NOT Tested (93 lines):**
- Map generation and initialization
- Fleet/world lookup optimizations
- Player management functions
- State modification methods

**Recommendation:** Add integration tests for game state management.

#### Production Mechanics (21%)
**Coverage:** 111/522 statements tested

**What's Tested:**
- ✅ Some basic order execution structure
- ✅ Consumer goods scoring logic (partial)

**What's NOT Tested (411 lines):**
- Build order execution
- Transfer execution details
- Scrap ships execution
- Plunder execution
- Load/unload cargo details
- World production calculations
- Player score calculation

**Recommendation:** This is the biggest gap - add comprehensive production/economy tests.

---

### Not Tested (0%)

#### Turn Processor (0%)
**Coverage:** 0/101 statements

**Why Not Tested:**
- Turn processor orchestrates async execution
- Requires complex game state setup
- Integration test rather than unit test

**Recommendation:** Add integration tests that process full turns.

#### Ownership Mechanics (0%)
**Coverage:** 0/78 statements

**Functions Not Tested:**
- check_world_ownership()
- handle_fleet_captures()
- ownership transfer logic

**Recommendation:** Add tests for world capture and fleet capture scenarios.

#### Persistence (0%)
**Coverage:** 0/105 statements

**Why Not Tested:**
- Requires file I/O mocking
- JSON serialization/deserialization
- Game save/load logic

**Recommendation:** Add tests with temporary test files.

#### Command Handlers (0%)
**Coverage:** 0/196 statements

**Why Not Tested:**
- WebSocket integration layer
- Requires async WebSocket mocking
- Server-side request handling

**Recommendation:** Add integration tests with mocked WebSocket connections.

#### Help Content (0%)
**Coverage:** 0/49 statements

**Why Not Tested:**
- Static help text content
- Low priority for testing

**Recommendation:** Optional - add smoke tests to verify help text loads.

---

## Coverage by Test Type

### Parsing Tests (44 tests)
**Coverage Contribution:** ~15%
- Command parser registry: 97%
- Basic command validation: partial
- Command constructors: 100%

### Validation Tests (39 tests)
**Coverage Contribution:** ~15%
- Command validation logic: 54%
- Game state queries: 30%
- Entity lookups: 68%

### Execution Tests (16 tests)
**Coverage Contribution:** ~5%
- Movement execution: 55%
- Combat execution: 36%
- Production execution: 21%

---

## Improvement Roadmap

### Quick Wins (High Impact, Low Effort)
1. **Add execution tests for production mechanics** (+20% coverage)
   - Build, transfer, load/unload, scrap, plunder
   - Currently only 21% covered, easy to test

2. **Add combat execution tests** (+15% coverage)
   - Defense fire, world attacks, neutralization
   - Currently only 36% covered

3. **Add ownership/capture tests** (+3% coverage)
   - World ownership changes
   - Fleet captures
   - Currently 0% covered

### Medium Wins (Medium Impact, Medium Effort)
4. **Add movement edge case tests** (+10% coverage)
   - Ambush mechanics
   - Multi-hop paths
   - Currently 55% covered

5. **Add command validation edge cases** (+15% coverage)
   - Resource constraints
   - Complex scenarios
   - Currently 54% covered

### Long-Term Goals (High Impact, High Effort)
6. **Add turn processor integration tests** (+5% coverage)
   - Full turn execution
   - Order priority
   - Currently 0% covered

7. **Add persistence tests** (+5% coverage)
   - Save/load game state
   - Currently 0% covered

8. **Add WebSocket handler tests** (+9% coverage)
   - Command handling
   - Event broadcasting
   - Currently 0% covered

---

## Recommendations

### Priority 1: Get to 60% Coverage
Focus on production mechanics and combat execution tests. These are:
- High-value (complex game logic)
- Low-hanging fruit (easy to mock)
- Currently very low coverage (21-36%)

**Estimated Effort:** 2-3 hours
**Coverage Gain:** +35% → **70% total**

### Priority 2: Edge Cases
Add edge case tests for existing modules:
- Command validation edge cases
- Movement ambush scenarios
- Combat with empty fleets

**Estimated Effort:** 1-2 hours
**Coverage Gain:** +10% → **80% total**

### Priority 3: Integration Tests
Add integration tests for:
- Turn processor
- Ownership mechanics
- Persistence

**Estimated Effort:** 4-6 hours
**Coverage Gain:** +13% → **93% total**

---

## How to View Coverage

### Terminal Report
```bash
coverage report
coverage report -m  # Show missing lines
coverage report --sort=cover  # Sort by coverage
```

### HTML Report
```bash
coverage html
open htmlcov/index.html  # Opens in browser
```

### Re-run with Coverage
```bash
coverage run --source=server/game run_tests.py
coverage report
```

### Focus on Specific Module
```bash
coverage report --include="server/game/mechanics/production.py" -m
```

---

## Known Test Failures

**7 tests currently failing (execution tests):**
- `test_build_iships_execution` - Build not consuming resources properly
- `test_fire_at_fleet_execution` - Missing mock setup
- `test_scrap_ships_execution` - Missing mock setup
- `test_scrap_ships_empire_builder_execution` - Missing mock setup
- `test_plunder_execution` - Missing mock setup
- `test_consumer_goods_execution` - Missing mock setup
- `test_declare_peace_execution` - Missing mock setup

**Root Cause:** Incomplete mocking of message sender and event bus.

**Fix:** Complete the mock setup in test fixtures for async dependencies.

---

## Next Steps

1. ✅ Coverage report generated
2. ⬜ Fix 7 failing execution tests
3. ⬜ Add production mechanics execution tests
4. ⬜ Add combat execution tests
5. ⬜ Add ownership/capture tests
6. ⬜ Add turn processor integration tests
7. ⬜ Target: 80%+ coverage

---

**Report Generated:** `coverage html` creates detailed line-by-line HTML report
**View Report:** Open `htmlcov/index.html` in your browser for interactive coverage exploration
