# StarWeb Command Test Suite

This test suite verifies all game commands are parsed, validated, and executed correctly.

## Test Structure

The test suite is organized into three main categories:

### 1. Command Parsing Tests (`test_command_parsing.py`)
Tests that command syntax is correctly parsed into command objects.

**Coverage:**
- All 17+ command types with various syntax variations
- Movement: `F5W10`, `F5W1W3W10`
- Building: `W3B25I`, `W3B10P`, `W3B15F7`, `W3B2INDUSTRY`, `W3B5LIMIT`, `W3B10ROBOT`
- Transfers: `F5T10I`, `F5T10P`, `F5T10F7`, `I5T10F7`, `P5T10I`
- Artifacts: `F5TA3F7`, `F5TA3W`, `W5TA3F7`, `V3`, `V3F5`, `V3W`
- Cargo: `F5L`, `F5L10`, `F5U`, `F5U10`, `F5J`, `F5N`
- Combat: `F5AF10`, `F5AP`, `F5AI`, `F5AH`, `I5AF10`, `P5AC`, `F5A`
- Probing: `F5P10`, `I5P10`, `P5P10`
- Economy: `W5S3`, `W5X`
- Diplomacy: `F5Q10`, `F5X10`
- Invalid/empty commands

### 2. Command Validation Tests (`test_command_validation.py`)
Tests that commands properly validate game state constraints.

**Coverage:**
- Ownership validation (can't use other players' fleets/worlds)
- Resource validation (enough ships, cargo, population, etc.)
- Existence validation (fleets/worlds/artifacts exist)
- Special rules (Empire Builder scrap bonus, Merchant-only consumer goods)
- Combat rules (can't fire at own fleets, need ships to fire)
- Movement constraints (connected worlds only)
- Edge cases (empty fleets, no resources, invalid targets)

### 3. Command Execution Tests (`test_command_execution.py`)
Tests that commands produce correct game state changes when executed.

**Coverage:**
- Movement execution (fleets change worlds)
- Build execution (resources consumed, ships created)
- Transfer execution (ships move between fleets/defenses)
- Cargo operations (load/unload/jettison)
- Combat execution (damage calculation, fleet destruction)
- Economy execution (scrap ships, plunder, consumer goods)
- Diplomacy execution (relation tracking)
- Probing (ship cost, information gathering)
- Edge cases (fleet destruction, resource depletion)

## Running Tests

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test Suite
```bash
python run_tests.py parsing
python run_tests.py validation
python run_tests.py execution
```

### Verbose Output
```bash
python run_tests.py -v
python run_tests.py parsing -v
```

### Run Individual Test File
```bash
python -m unittest tests.test_command_parsing
python -m unittest tests.test_command_validation
python -m unittest tests.test_command_execution
```

### Run Specific Test Class or Method
```bash
python -m unittest tests.test_command_parsing.TestCommandParsing
python -m unittest tests.test_command_parsing.TestCommandParsing.test_move_command_single_hop
```

## Test Fixtures

`fixtures.py` provides helper functions to create test game states:

- `create_basic_game_state()` - 2 players, 3 worlds, 3 fleets
- `create_combat_game_state()` - Set up for combat testing with defenses
- `create_artifact_game_state()` - Includes artifacts on fleets/worlds
- `create_economy_game_state()` - Rich resources for production testing

Individual entity creators:
- `create_test_player(id, name, character_type)`
- `create_test_world(id, owner)`
- `create_test_fleet(id, owner, world, ships)`
- `create_test_artifact(id, name)`

## Adding New Tests

When adding a new command:

1. **Add parsing test** in `test_command_parsing.py`:
   - Test command syntax is correctly parsed
   - Test all variations of the command

2. **Add validation tests** in `test_command_validation.py`:
   - Test all validation rules (ownership, resources, constraints)
   - Test failure cases with appropriate error messages
   - Test at least one successful validation

3. **Add execution test** in `test_command_execution.py`:
   - Test command produces correct game state changes
   - Test edge cases (resource depletion, destruction, etc.)
   - Use appropriate fixture for test setup

## Test Coverage

Current coverage: **17+ command types, 100+ test cases**

### Commands Tested:
- ✅ Movement (F#W#)
- ✅ Building (W#B#I/P/F#/INDUSTRY/LIMIT/ROBOT)
- ✅ Fleet transfers (F#T#I/P/F#)
- ✅ Defense transfers (I#T#F#/P, P#T#F#/I)
- ✅ Artifact transfers (F#TA#F#/W, W#TA#F#)
- ✅ Cargo operations (F#L/U/J, F#N)
- ✅ Combat (F#AF#/P/I/H, I#AF#/C, P#AF#/C)
- ✅ Ambush (F#A)
- ✅ Probing (F#P#, I#P#, P#P#)
- ✅ Scrap ships (W#S#)
- ✅ Plunder (W#X)
- ✅ View artifacts (V#, V#F#, V#W)
- ✅ Diplomacy (F#Q#, F#X#)

### Character-Specific Features:
- ✅ Empire Builder scrap bonus (4 ships/industry)
- ✅ Merchant consumer goods scoring (10/8/5/3/1 points)

## CI/CD Integration

To integrate tests into CI/CD pipeline:

```yaml
# .github/workflows/test.yml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Run tests
        run: python run_tests.py -v
```

## Known Limitations

- Tests use mocked message sender (no actual WebSocket messages sent)
- Tests don't cover turn processor orchestration (see `turn_processor.py`)
- Tests don't cover concurrent order execution
- No performance/load testing included

## Future Improvements

- [ ] Add integration tests for full turn processing
- [ ] Add tests for migration commands (W#M#W#)
- [ ] Add tests for exclusive order conflicts (MOVE/FIRE/AMBUSH)
- [ ] Add coverage reporting
- [ ] Add performance benchmarks
- [ ] Mock WebSocket message sending for verification
