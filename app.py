#!/usr/bin/env python3
"""
Streamlit Web App for Fantasy Hockey Roster Optimizer
"""

import streamlit as st
import pandas as pd
import io
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
    def __init__(self, csv_data: str):
        self.players = []
        self.teams = defaultdict(list)
        self.load_data(csv_data)
    
    def load_data(self, csv_data: str):
        """Load player data from CSV string."""
        df = pd.read_csv(io.StringIO(csv_data))
        for _, row in df.iterrows():
            player = Player(row.to_dict())
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


# Streamlit App
st.set_page_config(
    page_title="Fantasy Hockey Roster Optimizer",
    page_icon="🏒",
    layout="wide"
)

st.title("🏒 Fantasy Hockey Roster Optimizer")
st.markdown("""
Upload a Fantrax CSV export to calculate the optimal roster for each team.
Each team's optimal roster includes: **3 Centers, 3 Right Wingers, 3 Left Wingers, 4 Defensemen, and 3 Goalies**.
""")

# File upload
uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=['csv'],
    help="Upload your Fantrax league export CSV file"
)

if uploaded_file is not None:
    try:
        # Read CSV content
        csv_content = uploaded_file.read().decode('utf-8')
        
        # Show loading spinner
        with st.spinner('Calculating optimal rosters...'):
            optimizer = RosterOptimizer(csv_content)
            results = optimizer.calculate_all_teams()
        
        # Sort results by total FPts
        sorted_results = sorted(results.items(), key=lambda x: x[1][1], reverse=True)
        
        # Summary section
        st.header("📊 Summary Results")
        
        # Create summary dataframe
        summary_data = []
        for team_name, (roster, total_fpts) in sorted_results:
            pos_counts = defaultdict(int)
            for _, pos in roster:
                pos_counts[pos] += 1
            summary_data.append({
                'Team': team_name,
                'Total FPts': f"{total_fpts:.2f}",
                'C': pos_counts['C'],
                'RW': pos_counts['RW'],
                'LW': pos_counts['LW'],
                'D': pos_counts['D'],
                'G': pos_counts['G']
            })
        
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True, hide_index=True)
        
        # Detailed breakdown
        st.header("📋 Detailed Breakdown by Team")
        
        # Team selector
        team_names = [team for team, _ in sorted_results]
        selected_team = st.selectbox(
            "Select a team to view detailed roster:",
            team_names,
            index=0
        )
        
        # Display selected team's roster
        roster, total_fpts = results[selected_team]
        
        st.subheader(f"{selected_team} - Total FPts: {total_fpts:.2f}")
        
        # Group by position
        by_position = defaultdict(list)
        for player, assigned_pos in roster:
            by_position[assigned_pos].append((player, assigned_pos))
        
        # Create columns for better layout
        cols = st.columns(5)
        position_order = ['C', 'RW', 'LW', 'D', 'G']
        position_names = {
            'C': 'Centers',
            'RW': 'Right Wingers',
            'LW': 'Left Wingers',
            'D': 'Defensemen',
            'G': 'Goalies'
        }
        
        for idx, pos in enumerate(position_order):
            with cols[idx]:
                players_in_pos = by_position[pos]
                if players_in_pos:
                    st.markdown(f"**{position_names[pos]} ({len(players_in_pos)})**")
                    for p, assigned_pos in sorted(players_in_pos, key=lambda x: x[0].fpts, reverse=True):
                        eligible_pos = ','.join(sorted(p.positions))
                        st.markdown(f"""
                        **{p.name}**  
                        *{eligible_pos}* - {p.fpts:.2f} FPts
                        """)
        
        # Download results as CSV
        st.header("💾 Export Results")
        
        # Create export data
        export_data = []
        for team_name, (roster, total_fpts) in sorted_results:
            for player, assigned_pos in roster:
                export_data.append({
                    'Team': team_name,
                    'Player': player.name,
                    'Assigned Position': assigned_pos,
                    'Eligible Positions': ','.join(sorted(player.positions)),
                    'FPts': player.fpts,
                    'Total Team FPts': total_fpts
                })
        
        df_export = pd.DataFrame(export_data)
        csv_export = df_export.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv_export,
            file_name="optimal_rosters.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.exception(e)
else:
    st.info("👆 Please upload a CSV file to get started.")
    
    # Show example format
    with st.expander("📝 Expected CSV Format"):
        st.markdown("""
        The CSV file should have the following columns:
        - `ID`: Player ID
        - `Player`: Player name
        - `Team`: NHL team abbreviation
        - `Position`: Player position(s) - can be single (e.g., "C") or multiple (e.g., "C,RW")
        - `Status`: Fantasy team abbreviation (2-3 letters)
        - `Roster Status`: Active or Reserve
        - `FPts`: Fantasy points
        """)

