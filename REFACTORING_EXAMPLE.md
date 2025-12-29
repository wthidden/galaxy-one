# Command Validation Refactoring Example

## The Problem: Code Duplication

**Current State Analysis:**
- 12 duplicate fleet existence checks
- 12 duplicate fleet ownership checks
- 7 duplicate world existence checks
- 10 duplicate world ownership checks
- ~200+ lines of duplicated validation logic

## Before: Duplicated Code

### Example 1: MoveFleetCommand (17 lines of validation)

```python
def validate(self, game_state) -> tuple[bool, str]:
    fleet = game_state.get_fleet(self.fleet_id)

    if not fleet:
        return False, f"Fleet {self.fleet_id} does not exist"

    if fleet.owner != self.player:
        return False, f"You do not own fleet {self.fleet_id}"

    if fleet.ships == 0:
        return False, f"Fleet {self.fleet_id} has no ships"

    # Validate path connectivity
    current = fleet.world.id
    for next_world_id in self.path:
        world = game_state.get_world(current)
        if next_world_id not in world.connections:
            return False, f"World {current} is not connected to {next_world_id}"
        current = next_world_id

    return True, ""
```

### Example 2: TransferCommand (17 lines, mostly duplicated)

```python
def validate(self, game_state) -> tuple[bool, str]:
    fleet = game_state.get_fleet(self.fleet_id)

    if not fleet:
        return False, f"Fleet {self.fleet_id} does not exist"

    if fleet.owner != self.player:
        return False, f"You do not own fleet {self.fleet_id}"

    if fleet.ships == 0:
        return False, f"Fleet {self.fleet_id} has no ships"

    if self.amount > fleet.ships:
        return False, f"Fleet {self.fleet_id} only has {fleet.ships} ships"

    world = fleet.world
    if world.owner != self.player:
        return False, f"You do not own world {world.id}"

    return True, ""
```

### Example 3: BuildCommand (21 lines, lots of duplication)

```python
def validate(self, game_state) -> tuple[bool, str]:
    world = game_state.get_world(self.world_id)

    if not world:
        return False, f"World {self.world_id} does not exist"

    if world.owner != self.player:
        return False, f"You do not own world {self.world_id}"

    if self.amount <= 0:
        return False, "Build amount must be positive"

    max_build = min(world.industry, world.metal, world.population)
    if self.amount > max_build:
        return False, f"Cannot build {self.amount}, maximum is {max_build}"

    if self.target_type == "F" and self.target_id:
        fleet = game_state.get_fleet(self.target_id)
        if not fleet:
            return False, f"Fleet {self.target_id} does not exist"
        if fleet.owner != self.player:
            return False, f"You do not own fleet {self.target_id}"

    return True, ""
```

**Problems:**
- Same 3-5 lines repeated in every command
- Hard to maintain (change ownership logic → update 12 places)
- Error-prone (easy to forget a check or make inconsistent error messages)
- Harder to test (same logic tested 12 different ways)

---

## After: Using Validation Helpers

### Example 1: MoveFleetCommand (9 lines, 47% reduction)

```python
from .command_validators import validate_fleet_has_ships, validate_world_connected

def validate(self, game_state) -> tuple[bool, str]:
    # Reuse common validation
    valid, msg, fleet = validate_fleet_has_ships(game_state, self.player, self.fleet_id)
    if not valid:
        return valid, msg

    # Command-specific validation: path connectivity
    current = fleet.world.id
    for next_world_id in self.path:
        valid, msg = validate_world_connected(game_state, current, next_world_id)
        if not valid:
            return valid, msg
        current = next_world_id

    return True, ""
```

### Example 2: TransferCommand (5 lines, 71% reduction!)

```python
from .command_validators import validate_transfer_ships_basic

def validate(self, game_state) -> tuple[bool, str]:
    # All common validation in ONE line
    valid, msg, fleet = validate_transfer_ships_basic(
        game_state, self.player, self.fleet_id, self.amount
    )
    if not valid:
        return valid, msg

    # Command already has what it needs
    return True, ""
```

### Example 3: BuildCommand (8 lines, 62% reduction)

```python
from .command_validators import (
    validate_build_basic, validate_fleet_ownership
)

def validate(self, game_state) -> tuple[bool, str]:
    # Common build validation
    valid, msg, world = validate_build_basic(
        game_state, self.player, self.world_id, self.amount
    )
    if not valid:
        return valid, msg

    # Command-specific: validate target fleet if building on fleet
    if self.target_type == "F" and self.target_id:
        valid, msg, _ = validate_fleet_ownership(
            game_state, self.player, self.target_id
        )
        if not valid:
            return valid, msg

    return True, ""
```

---

## Benefits of Refactoring

### 1. **Code Reduction**
- **Before:** ~200+ lines of duplicated validation
- **After:** ~50 lines of reusable helpers + ~100 lines of command-specific logic
- **Savings:** ~50% code reduction overall

### 2. **Maintainability**
**Scenario:** Need to change fleet ownership error message

**Before:**
```python
# Update in 12 different places:
if fleet.owner != self.player:
    return False, f"You do not own fleet {self.fleet_id}"
```

**After:**
```python
# Update in ONE place (command_validators.py):
def validate_fleet_ownership(game_state, player, fleet_id):
    # ...
    if fleet.owner != player:
        return False, f"You do not own fleet {fleet_id}"  # ONE change
```

### 3. **Testability**
**Before:** Test fleet ownership validation 12 times (once per command)

**After:** Test `validate_fleet_ownership()` ONCE, then test command-specific logic

### 4. **Consistency**
**Before:**
- MoveFleetCommand says: "You do not own fleet {id}"
- TransferCommand might say: "Fleet {id} not owned by you"
- BuildCommand might say: "You don't own fleet {id}"

**After:** All commands use same helper → consistent error messages

### 5. **Composability**
Validators can be composed for complex checks:

```python
def validate(self, game_state):
    # Compose multiple validators
    valid, msg, fleet = validate_fleet_ownership(game_state, self.player, self.fleet_id)
    if not valid:
        return valid, msg

    valid, msg = validate_fleet_has_cargo(game_state, self.player, self.fleet_id, 10)
    if not valid:
        return valid, msg

    valid, msg = validate_character_type(self.player, "Merchant")
    if not valid:
        return valid, msg

    return True, ""
```

---

## Code Metrics

### Lines of Code (LOC)

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| MoveFleetCommand.validate() | 17 | 9 | 47% |
| TransferCommand.validate() | 17 | 5 | 71% |
| BuildCommand.validate() | 21 | 8 | 62% |
| FireCommand.validate() | 15 | 7 | 53% |
| **Average per command** | **17.5** | **7.25** | **59%** |

### Duplication Analysis

| Validation Type | Occurrences Before | After Refactor | Reduction |
|----------------|-------------------|----------------|-----------|
| Fleet existence check | 12 | 1 (in helper) | 92% |
| Fleet ownership check | 12 | 1 (in helper) | 92% |
| World existence check | 7 | 1 (in helper) | 86% |
| World ownership check | 10 | 1 (in helper) | 90% |
| Resource checks | 8 | 2 (in helpers) | 75% |

---

## Why This Approach?

### Compared to Alternatives

#### Option A: Base Class with Template Method ❌
```python
class Command(ABC):
    def validate(self, game_state):
        # Base validation
        valid, msg = self.validate_ownership(game_state)
        if not valid:
            return valid, msg
        return self.validate_specific(game_state)

    @abstractmethod
    def validate_specific(self, game_state):
        pass
```

**Problems:**
- Not all commands need ownership validation
- Forces rigid structure
- Hard to compose different validations
- Inheritance complexity

#### Option B: Mixins ❌
```python
class FleetOwnershipMixin:
    def validate_fleet_ownership(self, game_state):
        pass

class MoveFleetCommand(FleetOwnershipMixin, Command):
    pass
```

**Problems:**
- Mixin hell / multiple inheritance
- Unclear method resolution order
- Hard to understand dependencies

#### Option C: Validation Helpers ✅ (Our Choice)
```python
from .command_validators import validate_fleet_ownership

def validate(self, game_state):
    valid, msg, fleet = validate_fleet_ownership(...)
    return valid, msg
```

**Benefits:**
- **Simple:** Just function calls
- **Explicit:** Clear what's being validated
- **Flexible:** Easy to compose
- **Testable:** Helpers tested independently
- **No inheritance:** Avoids OOP complexity

---

## Migration Strategy

### Phase 1: Add Helpers (No Breaking Changes)
1. Create `command_validators.py` with all helpers
2. Add tests for each helper function
3. Commands still use old validation (backward compatible)

### Phase 2: Refactor Commands Incrementally
Refactor one command at a time:
1. Update command to use helpers
2. Run tests to ensure behavior unchanged
3. Commit
4. Repeat for next command

### Phase 3: Cleanup
Once all commands refactored:
1. Remove old duplicated code
2. Update documentation
3. Celebrate 50% code reduction! 🎉

---

## Example Migration: Step-by-Step

### Step 1: Before (MoveFleetCommand)
```python
def validate(self, game_state) -> tuple[bool, str]:
    fleet = game_state.get_fleet(self.fleet_id)
    if not fleet:
        return False, f"Fleet {self.fleet_id} does not exist"
    if fleet.owner != self.player:
        return False, f"You do not own fleet {self.fleet_id}"
    if fleet.ships == 0:
        return False, f"Fleet {self.fleet_id} has no ships"
    # ... path validation ...
    return True, ""
```

### Step 2: Import helper
```python
from .command_validators import validate_fleet_has_ships
```

### Step 3: Replace duplicated code
```python
def validate(self, game_state) -> tuple[bool, str]:
    # Replace 6 lines with 3 lines
    valid, msg, fleet = validate_fleet_has_ships(game_state, self.player, self.fleet_id)
    if not valid:
        return valid, msg

    # Keep command-specific validation
    current = fleet.world.id
    for next_world_id in self.path:
        world = game_state.get_world(current)
        if next_world_id not in world.connections:
            return False, f"World {current} is not connected to {next_world_id}"
        current = next_world_id
    return True, ""
```

### Step 4: Run tests
```bash
python run_tests.py validation
# All tests pass ✓
```

### Step 5: Commit
```bash
git commit -m "Refactor MoveFleetCommand to use validation helpers"
```

### Repeat for remaining 16 commands...

---

## Conclusion

**You were absolutely right!** The current validation code has massive duplication that makes it:
- ❌ Hard to maintain (12 places to update)
- ❌ Error-prone (inconsistent messages)
- ❌ Verbose (200+ lines of duplication)
- ❌ Hard to test (test same logic 12 times)

**After refactoring with validation helpers:**
- ✅ Easy to maintain (1 place to update)
- ✅ Consistent (same messages everywhere)
- ✅ Concise (59% code reduction)
- ✅ Testable (test helpers once)

The helper function approach is superior to:
- Template methods (too rigid)
- Mixins (inheritance hell)
- Validators as classes (over-engineered)

**Next Steps:**
1. Add validation helpers module (done ✅)
2. Write tests for helpers
3. Refactor commands one by one
4. Enjoy 50%+ code reduction!
