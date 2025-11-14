#!/usr/bin/env python3
"""
Fantasy Hockey Roster Optimizer
Calculates the best possible roster for each team based on FPts.
"""

import csv
import sys
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Optional


class Player:
    def __init__(self, row: Dict[str, str]):
        self.id = row['ID']
        self.name = row['Player']
        self.team = row['Team']
        self.positions = set(pos.strip() for pos in row['Position'].split(','))
        self.status = row['Status']
        self.roster_status = row['Roster Status']
        try:
            self.fpts = float(row['FPts']) if row['FPts'] else 0.0
        except ValueError:
            self.fpts = 0.0
    
    def can_play(self, position: str) -> bool:
        """Check if player can play a specific position."""
        return position in self.positions


class RosterOptimizer:
    def __init__(self, csv_path: str):
        self.players = []
        self.teams = defaultdict(list)
        self.load_data(csv_path)
    
    def load_data(self, csv_path: str):
        """Load player data from CSV file."""
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                player = Player(row)
                self.players.append(player)
                if player.status:  # Only include players with a team
                    self.teams[player.status].append(player)
    
    def optimize_roster(self, team_players: List[Player]) -> Tuple[List[Tuple[Player, str]], float]:
        """
        Find the best possible roster for a team.
        Requirements: 3 C, 3 RW, 3 LW, 4 D, 3 G
        Returns: (list of (player, assigned_position), total FPts)
        Uses backtracking algorithm to find optimal solution.
        """
        # Sort players by FPts (descending) for better pruning
        sorted_players = sorted(team_players, key=lambda p: p.fpts, reverse=True)
        
        # Use backtracking algorithm to find optimal solution
        selected, total_fpts = self._backtrack_optimize(
            sorted_players, {'C': 3, 'RW': 3, 'LW': 3, 'D': 4, 'G': 3}
        )
        
        return selected, total_fpts
    
    def _backtrack_optimize(
        self, 
        players: List[Player], 
        positions_needed: Dict[str, int]
    ) -> Tuple[List[Tuple[Player, str]], float]:
        """
        Backtracking algorithm to find the optimal roster assignment.
        Considers all possible position assignments for multi-position players.
        Uses pruning to avoid exploring suboptimal paths.
        """
        best_solution = []
        best_score = -1.0
        total_slots = sum(positions_needed.values())  # Total players needed (16)
        
        def backtrack(
            player_idx: int,
            current_assignment: List[Tuple[Player, str]],
            remaining: Dict[str, int],
            current_score: float
        ):
            nonlocal best_solution, best_score
            
            # Pruning: calculate upper bound of remaining score
            # We can use at most (total_slots - len(current_assignment)) more players
            slots_remaining = total_slots - len(current_assignment)
            if slots_remaining > 0 and player_idx < len(players):
                # Sum top remaining players we could potentially use
                max_remaining_score = sum(
                    p.fpts for p in players[player_idx:player_idx + slots_remaining]
                )
                if current_score + max_remaining_score <= best_score:
                    return
            
            # Check if all positions are filled
            if all(count == 0 for count in remaining.values()):
                if current_score > best_score:
                    best_score = current_score
                    best_solution = current_assignment.copy()
                return
            
            # If we've processed all players but positions aren't filled, this is invalid
            if player_idx >= len(players):
                return
            
            player = players[player_idx]
            
            # Try assigning this player to each eligible position
            for pos in sorted(player.positions):  # Sort for consistency
                if remaining.get(pos, 0) > 0:
                    # Make assignment
                    new_assignment = current_assignment + [(player, pos)]
                    new_remaining = remaining.copy()
                    new_remaining[pos] -= 1
                    new_score = current_score + player.fpts
                    
                    # Recursively try next player
                    backtrack(player_idx + 1, new_assignment, new_remaining, new_score)
            
            # Also try skipping this player (in case we need to save them for later)
            backtrack(player_idx + 1, current_assignment, remaining, current_score)
        
        # Start backtracking
        backtrack(0, [], positions_needed.copy(), 0.0)
        
        # If no solution found (shouldn't happen with valid data), fall back to greedy
        if not best_solution:
            return self._optimized_greedy(players, positions_needed)
        
        return best_solution, best_score
    
    def _optimized_greedy(
        self, 
        players: List[Player], 
        positions_needed: Dict[str, int]
    ) -> Tuple[List[Tuple[Player, str]], float]:
        """
        Fallback greedy algorithm (kept for edge cases).
        """
        selected = []
        used = set()
        remaining = positions_needed.copy()
        
        for player in players:
            if player.id in used:
                continue
            
            # Find best position to assign this player
            best_pos = None
            best_priority = float('inf')
            
            for pos in player.positions:
                if remaining.get(pos, 0) > 0:
                    priority = remaining[pos]
                    if priority < best_priority:
                        best_priority = priority
                        best_pos = pos
            
            if best_pos:
                selected.append((player, best_pos))
                used.add(player.id)
                remaining[best_pos] -= 1
        
        # Fill remaining positions
        if sum(remaining.values()) > 0:
            for player in players:
                if player.id in used:
                    continue
                
                for pos in player.positions:
                    if remaining.get(pos, 0) > 0:
                        selected.append((player, pos))
                        used.add(player.id)
                        remaining[pos] -= 1
                        break
        
        total = sum(p.fpts for p, _ in selected)
        return selected, total
    
    def _greedy_fill(
        self, 
        players: List[Player], 
        positions_needed: Dict[str, int]
    ) -> Tuple[List[Player], float]:
        """Greedy fallback algorithm."""
        selected = []
        used = set()
        remaining = positions_needed.copy()
        
        for player in players:
            if player.id in used:
                continue
            
            for pos in sorted(player.positions, key=lambda p: remaining.get(p, 0), reverse=True):
                if remaining.get(pos, 0) > 0:
                    selected.append(player)
                    used.add(player.id)
                    remaining[pos] -= 1
                    break
        
        total = sum(p.fpts for p in selected)
        return selected, total
    
    def calculate_all_teams(self) -> Dict[str, Tuple[List[Tuple[Player, str]], float]]:
        """Calculate optimal roster for all teams."""
        results = {}
        for team_name, team_players in sorted(self.teams.items()):
            roster, total_fpts = self.optimize_roster(team_players)
            results[team_name] = (roster, total_fpts)
        return results
    
    def print_results(self, results: Dict[str, Tuple[List[Tuple[Player, str]], float]]):
        """Print formatted results."""
        print("\n" + "="*80)
        print("FANTASY HOCKEY ROSTER OPTIMIZATION RESULTS")
        print("="*80)
        print(f"\n{'Team':<8} {'Total FPts':<12} {'Players Selected':<60}")
        print("-"*80)
        
        # Sort by total FPts (descending)
        sorted_results = sorted(results.items(), key=lambda x: x[1][1], reverse=True)
        
        for team_name, (roster, total_fpts) in sorted_results:
            player_count = len(roster)
            # Verify position counts
            pos_counts = defaultdict(int)
            for _, pos in roster:
                pos_counts[pos] += 1
            pos_str = f"C:{pos_counts['C']} RW:{pos_counts['RW']} LW:{pos_counts['LW']} D:{pos_counts['D']} G:{pos_counts['G']}"
            print(f"{team_name:<8} {total_fpts:<12.2f} {pos_str}")
        
        print("\n" + "="*80)
        print("DETAILED BREAKDOWN BY TEAM")
        print("="*80)
        
        for team_name, (roster, total_fpts) in sorted_results:
            print(f"\n{team_name} - Total FPts: {total_fpts:.2f}")
            print("-" * 60)
            
            # Group by assigned position
            by_position = defaultdict(list)
            for player, assigned_pos in roster:
                by_position[assigned_pos].append((player, assigned_pos))
            
            for pos in ['C', 'RW', 'LW', 'D', 'G']:
                players_in_pos = by_position[pos]
                if players_in_pos:
                    print(f"  {pos} ({len(players_in_pos)}):")
                    for p, assigned_pos in sorted(players_in_pos, key=lambda x: x[0].fpts, reverse=True):
                        eligible_pos = ','.join(sorted(p.positions))
                        print(f"    - {p.name:<30} (eligible: {eligible_pos:<10}) {p.fpts:>6.2f} FPts")


def main():
    if len(sys.argv) < 2:
        print("Usage: python fantasy_roster_optimizer.py <csv_file_path>")
        print("\nExample:")
        print("  python fantasy_roster_optimizer.py 'Fantrax-Players-The Conos League (6).csv'")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    try:
        optimizer = RosterOptimizer(csv_path)
        results = optimizer.calculate_all_teams()
        optimizer.print_results(results)
    except FileNotFoundError:
        print(f"Error: File '{csv_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

