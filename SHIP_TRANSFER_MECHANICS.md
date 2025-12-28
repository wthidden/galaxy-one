# Ship Transfer Mechanics

## Overview
When transferring ships between fleets, cargo is automatically transferred with the ships. Character class differences between fleet owners may cause cargo to be jettisoned.

**IMPORTANT**: Transfer commands transfer SHIPS, not cargo. The only requirement is that the source fleet has enough ships. Cargo is transferred automatically and proportionally with the ships.

## Command Syntax
- **F5T10F7** - Transfer 10 ships from fleet 5 to fleet 7
- **F5T10I** - Transfer 10 ships from fleet 5 to garrison (I-ships)
- **F5T10P** - Transfer 10 ships from fleet 5 to garrison (P-ships)

## Requirements
- Source fleet must have enough **ships** (not cargo)
- For fleet-to-fleet transfers: both fleets must be at the same world
- Fleet ownership is checked (must own the source fleet)

## Cargo Transfer Rules

### Fleet-to-Fleet Transfers
When transferring ships between fleets, cargo is handled as follows:

1. **Proportional Transfer**: Cargo is transferred proportionally with the ships
   - If fleet has 10 ships with 15 cargo and you transfer 5 ships
   - Cargo transferred = 5 × (15 ÷ 10) = 7.5 → rounded down to 7 cargo

2. **Character Class Capacity**:
   - **Merchants**: 2 cargo per ship
   - **All others**: 1 cargo per ship

3. **Capacity Checking**:
   - Target fleet capacity is calculated based on owner's character class
   - If transferred cargo exceeds available capacity, excess is jettisoned
   - Player is notified of any cargo loss

### Example Scenarios

#### Scenario 1: Merchant to Merchant
- Source: Merchant fleet with 10 ships, 20 cargo (full capacity)
- Transfer: 5 ships to Merchant fleet
- Result: 5 ships + 10 cargo transferred, all fits (target has 5×2=10 capacity)

#### Scenario 2: Merchant to Non-Merchant (Jettison)
- Source: Merchant fleet with 10 ships, 20 cargo
- Transfer: 5 ships to Pirate fleet with 0 existing cargo
- Cargo to transfer: 5 × (20÷10) = 10 cargo
- Target capacity: 5 ships × 1 = 5 cargo
- Result: 5 ships + 5 cargo transferred, **5 cargo jettisoned**
- Player receives notification: "Transfer F5→F7: 5 cargo jettisoned due to capacity limits"

#### Scenario 3: Non-Merchant to Merchant
- Source: Pirate fleet with 10 ships, 10 cargo (full capacity)
- Transfer: 5 ships to Merchant fleet with 5 existing cargo
- Cargo to transfer: 5 × (10÷10) = 5 cargo
- Target capacity: (5+5) ships × 2 = 20, available = 20-5 = 15
- Result: 5 ships + 5 cargo transferred, all fits

#### Scenario 4: Partial Fleet Capacity
- Source: Empire Builder fleet with 10 ships, 5 cargo
- Transfer: 3 ships to another Empire Builder fleet
- Cargo to transfer: 3 × (5÷10) = 1.5 → rounds to 1 cargo
- Result: 3 ships + 1 cargo transferred

### Fleet-to-Garrison Transfers
When transferring to world garrisons (I-ships or P-ships):
- Ships are transferred but cargo remains in fleet
- No cargo is jettisoned

## Cross-Player Transfers
Ships can be transferred to fleets owned by other players (e.g., allies). The same cargo and capacity rules apply:
- Cargo transfers with ships
- Target player's character class determines capacity
- Excess cargo is jettisoned if capacity insufficient
- Both players are notified of the transfer

## Implementation Details

### File: `server/game/mechanics/production.py`
Function: `execute_transfer_order()`

### Processing Order
Ship transfers are processed in turn step #1 (before builds, combat, or movement).
