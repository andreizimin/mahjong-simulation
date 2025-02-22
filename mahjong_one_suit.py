import numpy as np
import random

# Constants
NUM_PLAYERS = 4
TILES_PER_PLAYER = 3  # Except dealer, who gets 4
TOTAL_TILES = 36  # Only values (1,1) to (1,9), four copies each

# Generate the tile set (suit 1, values 1-9, four copies each)
tile_set = [(1, value) for value in range(1, 10) for _ in range(4)]  # (suit, value) pairs
np.random.shuffle(tile_set)

# Deal initial hands
players = {i: [] for i in range(NUM_PLAYERS)}
dealer = 0
discard_pile = []

# Distribute tiles
index = 0
for player in range(NUM_PLAYERS):
    num_tiles = 4 if player == dealer else 3  # Dealer gets 4, others get 3
    players[player] = tile_set[index:index + num_tiles]
    index += num_tiles

# Remaining tiles (the "wall")
wall = tile_set[index:]

def is_winning_hand(hand):
    """Check if a hand contains at least one valid Chi or Peng."""
    for tile in hand:
        if check_peng(hand, tile) or check_chi(hand, tile):
            return True
    return False

def check_peng(hand, tile):
    """Check if a tile can form a Peng (three of a kind) with the player's hand."""
    return hand.count(tile) == 3

def check_chi(hand, tile):
    """Check if a tile can form a Chi (sequence) with the player's hand."""
    suit, value = tile
    return ((suit, value - 1) in hand and (suit, value - 2) in hand) or \
           ((suit, value - 1) in hand and (suit, value + 1) in hand) or \
           ((suit, value + 1) in hand and (suit, value + 2) in hand)

def calculate_peng_probability(player_hand, wall, discard_pile):
    """Calculate actual and estimated probability of forming a Peng."""
    from math import comb
    
    wall_counts = {tile: wall.count(tile) for tile in set(wall)}
    discard_counts = {tile: discard_pile.count(tile) for tile in set(discard_pile)}
    
    total_wall_tiles = len(wall)
    known_tiles = total_wall_tiles + sum(discard_counts.values())
    unknown_tiles = TOTAL_TILES - known_tiles  # Tiles held by other players
    
    peng_prob_actual = 0.0
    peng_prob_estimated = 0.0
    
    for tile in set(player_hand):
        if player_hand.count(tile) == 2:
            actual_prob = wall_counts.get(tile, 0) / total_wall_tiles if total_wall_tiles > 0 else 0
            
            # Compute probability of 0, 1, or 2 copies in the wall
            if unknown_tiles >= 2:
                prob_0_in_wall = comb(unknown_tiles - 2, 2) / comb(unknown_tiles, 2)
                prob_1_in_wall = (comb(unknown_tiles - 1, 1) * comb(total_wall_tiles, 1)) / comb(unknown_tiles, 2)
                prob_2_in_wall = comb(total_wall_tiles, 2) / comb(unknown_tiles, 2)
            else:
                prob_0_in_wall = 0
                prob_1_in_wall = 0
                prob_2_in_wall = 0
            
            # Compute expected probability of drawing the tile
            estimated_prob = (
                prob_1_in_wall * (1 / total_wall_tiles) +
                prob_2_in_wall * (2 / total_wall_tiles)
            ) if total_wall_tiles > 0 else 0
            
            peng_prob_actual = max(peng_prob_actual, actual_prob)
            peng_prob_estimated = max(peng_prob_estimated, estimated_prob)
    
    return peng_prob_actual, peng_prob_estimated

def calculate_chi_probability(player_hand, wall, discard_pile):
    """Calculate actual and estimated probability of forming a Chi."""
    wall_counts = {tile: wall.count(tile) for tile in set(wall)}
    discard_counts = {tile: discard_pile.count(tile) for tile in set(discard_pile)}
    
    total_wall_tiles = len(wall)
    known_tiles = total_wall_tiles + sum(discard_counts.values())
    unknown_tiles = TOTAL_TILES - known_tiles
    
    chi_prob_actual = 0.0
    chi_prob_estimated = 0.0
    
    for tile in player_hand:
        suit, value = tile
        chi_needed = [
            (suit, value - 1), (suit, value + 1),
            (suit, value - 2), (suit, value + 2)
        ]
        chi_needed = [t for t in chi_needed if 1 <= t[1] <= 9]
        
        for needed_tile in chi_needed:
            actual_prob = wall_counts.get(needed_tile, 0) / total_wall_tiles if total_wall_tiles > 0 else 0
            missing_tiles = 4 - player_hand.count(needed_tile) - discard_counts.get(needed_tile, 0)
            estimated_prob = missing_tiles / unknown_tiles if unknown_tiles > 0 else 0
            
            chi_prob_actual = max(chi_prob_actual, actual_prob)
            chi_prob_estimated = max(chi_prob_estimated, estimated_prob)
    
    return chi_prob_actual, chi_prob_estimated

def print_game_state(turn, discard_tile, turn_number):
    peng_prob_actual, peng_prob_estimated = calculate_peng_probability(players[turn], wall, discard_pile)
    chi_prob_actual, chi_prob_estimated = calculate_chi_probability(players[turn], wall, discard_pile)
    
    print(f"\n--- Turn {turn_number} ---")
    print(f"Tiles left in wall: {len(wall)}")
    for p in range(NUM_PLAYERS):
        print(f"Player {p}: {sorted(players[p])}")
    print(f"Discard Pile: {discard_pile}")
    print(f"Current Discard: {discard_tile}")
    print(f"Player {turn}'s turn")
    print(f"Peng Probability for Player {turn} | Actual: {peng_prob_actual:.2%}, Estimated: {peng_prob_estimated:.2%}")
    print(f"Chi Probability for Player {turn} | Actual: {chi_prob_actual:.2%}, Estimated: {chi_prob_estimated:.2%}")

# Game loop
turn = dealer
winner = None
discard_tile = None
turn_number = 1

while wall:
    print_game_state(turn, discard_tile, turn_number)
    
    if len(players[turn]) < 4 and wall:
        new_tile = wall.pop(0)
        players[turn].append(new_tile)
        
        if is_winning_hand(players[turn]):
            winner = turn
            break
    
    if players[turn]:
        discard_tile = random.choice(players[turn])
        players[turn].remove(discard_tile)
        discard_pile.append(discard_tile)
        
        if is_winning_hand(players[turn]):
            winner = turn
            break
    else:
        discard_tile = None

    turn = (turn + 1) % NUM_PLAYERS
    turn_number += 1

    if not wall:
        break

if winner is not None:
    winning_type = "Peng" if any(check_peng(players[winner], tile) for tile in players[winner]) else "Chi"
    result = f"Player {winner} won with {winning_type}: {sorted(players[winner])}"
else:
    result = "Game ended without a winner (wall exhausted)."

print(result)
