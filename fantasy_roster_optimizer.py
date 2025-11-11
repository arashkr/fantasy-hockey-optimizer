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
        """
        # Sort players by FPts (descending) for better pruning
        sorted_players = sorted(team_players, key=lambda p: p.fpts, reverse=True)
        
        # Always use backtracking for optimal results
        selected, total_fpts = self._optimize_with_backtracking(
            sorted_players, {'C': 3, 'RW': 3, 'LW': 3, 'D': 4, 'G': 3}
        )
        
        return selected, total_fpts
    
    def _optimize_with_backtracking(
        self, 
        players: List[Player], 
        positions_needed: Dict[str, int]
    ) -> Tuple[List[Tuple[Player, str]], float]:
        """
        Use backtracking to find optimal roster assignment.
        This handles multi-position players more intelligently.
        """
        # Reset positions needed to original requirements
        positions_needed = {'C': 3, 'RW': 3, 'LW': 3, 'D': 4, 'G': 3}
        
        best_roster = []
        best_score = 0.0
        
        def backtrack(remaining_players: List[Player], current_roster: List[Tuple[Player, str]], 
                     remaining_positions: Dict[str, int], used_ids: Set[str]):
            nonlocal best_roster, best_score
            
            # Check if all positions are filled
            if all(count == 0 for count in remaining_positions.values()):
                total = sum(p.fpts for p, _ in current_roster)
                if total > best_score:
                    best_score = total
                    best_roster = current_roster.copy()
                return
            
            # Check if we can still fill remaining positions
            total_needed = sum(remaining_positions.values())
            if len(remaining_players) < total_needed:
                return
            
            # Pruning: if current roster + best possible remaining players can't beat best_score
            remaining_fpts = sum(p.fpts for p in remaining_players[:total_needed])
            current_fpts = sum(p.fpts for p, _ in current_roster)
            if current_fpts + remaining_fpts <= best_score:
                return
            
            # Try next player
            if not remaining_players:
                return
            
            player = remaining_players[0]
            rest_players = remaining_players[1:]
            
            # Option 1: Don't use this player
            backtrack(rest_players, current_roster, remaining_positions, used_ids)
            
            # Option 2: Use this player in one of their eligible positions
            if player.id not in used_ids:
                for pos in player.positions:
                    if remaining_positions.get(pos, 0) > 0:
                        # Try assigning player to this position
                        new_remaining = remaining_positions.copy()
                        new_remaining[pos] -= 1
                        new_roster = current_roster + [(player, pos)]
                        new_used = used_ids | {player.id}
                        
                        backtrack(rest_players, new_roster, new_remaining, new_used)
        
        backtrack(players, [], positions_needed.copy(), set())
        
        if best_roster:
            return best_roster, best_score
        else:
            # Fallback to greedy if backtracking fails
            roster, score = self._greedy_fill(players, positions_needed)
            # Convert to (player, position) format
            result = []
            remaining = positions_needed.copy()
            for player in roster:
                for pos in player.positions:
                    if remaining.get(pos, 0) > 0:
                        result.append((player, pos))
                        remaining[pos] -= 1
                        break
            return result, score
    
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

