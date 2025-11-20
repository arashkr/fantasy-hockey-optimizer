#!/usr/bin/env python3
"""
Streamlit Web App for Fantasy Hockey Roster Optimizer
"""

import streamlit as st
import pandas as pd
import io
from collections import defaultdict
from typing import List, Dict, Set, Tuple, Optional
import content

class Player:
    def __init__(self, row: Dict[str, str]):
        self.id = row['ID']
        self.name = row['Player']
        self.team = row['Team']
        self.positions = set(pos.strip() for pos in row['Position'].split(','))
        self.status = row['Status']
        self.roster_status = row['Roster Status']
        try:
            self.fpts = int(float(row['FPts'])) if row['FPts'] else 0
        except ValueError:
            self.fpts = 0
    
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


# Streamlit App
st.set_page_config(
    page_title="Fantasy Hockey Roster Optimizer",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Header
st.markdown(f"""
<div class="main-header">
    <h1>{content.APP_TITLE}</h1>
</div>
""", unsafe_allow_html=True)

# File upload
uploaded_file = st.file_uploader(
    content.UPLOAD_LABEL,
    type=['csv'],
    help=content.UPLOAD_HELP
)

if uploaded_file is not None:
    try:
        # Read CSV content
        csv_content = uploaded_file.read().decode('utf-8')
        
        # Show loading spinner with progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text(content.LOADING_MSG)
        optimizer = RosterOptimizer(csv_content)
        
        # Calculate with progress updates
        teams = sorted(optimizer.teams.keys())
        results = {}
        total_teams = len(teams)
        
        for idx, team_name in enumerate(teams):
            status_text.text(content.OPTIMIZING_MSG.format(team=team_name, current=idx+1, total=total_teams))
            progress_bar.progress((idx + 1) / total_teams)
            roster, total_fpts = optimizer.optimize_roster(optimizer.teams[team_name])
            results[team_name] = (roster, total_fpts)
        
        status_text.text(content.COMPLETE_MSG)
        progress_bar.progress(1.0)
        
        # Sort results by total FPts
        sorted_results = sorted(results.items(), key=lambda x: x[1][1], reverse=True)
        
        # Summary section with metrics
        st.markdown("---")
        st.markdown(content.SUMMARY_HEADER)
        
        # Create summary dataframe with styling
        summary_data = []
        for rank, (team_name, (roster, total_fpts)) in enumerate(sorted_results, 1):
            pos_points = defaultdict(int)
            for player, pos in roster:
                pos_points[pos] += player.fpts
            summary_data.append({
                'Rank': rank,
                'Team': team_name,
                'Total FPts': int(total_fpts),
                'C': pos_points['C'],
                'RW': pos_points['RW'],
                'LW': pos_points['LW'],
                'D': pos_points['D'],
                'G': pos_points['G']
            })
        
        df_summary = pd.DataFrame(summary_data)
        
        # Style the dataframe
        def highlight_ranks(row):
            if row['Rank'] <= 3:
                return ['background-color: #003300; color: #00ff00'] * len(row)
            elif row['Rank'] <= 5:
                return ['background-color: #001a00; color: #00cc00'] * len(row)
            return [''] * len(row)
        
        styled_df = df_summary.style.apply(highlight_ranks, axis=1)
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Detailed breakdown
        st.markdown("---")
        st.markdown(content.DETAILED_HEADER)
        
        # Team selector with rank
        team_names = [team for team, _ in sorted_results]
        team_with_ranks = [f"#{idx+1} - {team} ({results[team][1]:.2f} FPts)" 
                          for idx, team in enumerate(team_names)]
        
        selected_index = st.selectbox(
            content.SELECT_TEAM_LABEL,
            range(len(team_names)),
            format_func=lambda x: team_with_ranks[x],
            index=0
        )
        
        selected_team = team_names[selected_index]
        
        # Display selected team's roster
        roster, total_fpts = results[selected_team]
        
        # Group by position
        by_position = defaultdict(list)
        for player, assigned_pos in roster:
            by_position[assigned_pos].append((player, assigned_pos))
        
        position_order = ['C', 'RW', 'LW', 'D', 'G']
        position_names = {
            'C': 'Centers',
            'RW': 'Right Wingers',
            'LW': 'Left Wingers',
            'D': 'Defensemen',
            'G': 'Goalies'
        }
        
        for pos in position_order:
            players_in_pos = by_position[pos]
            if players_in_pos:
                # Sort players by points
                sorted_players = sorted(players_in_pos, key=lambda x: x[0].fpts, reverse=True)
                
                st.markdown(f"""
                <div style="margin-bottom: 0.5rem; font-family: 'VT323', monospace;">
                    <div style="color: #00ff00; border-bottom: 1px dashed #00ff00; margin-bottom: 0.25rem; font-size: 1rem; font-weight: bold;">{position_names[pos]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                for p, _ in sorted_players:
                    eligible = ",".join(sorted(p.positions))
                    st.markdown(f"""
                    <div style="margin-left: 1rem; margin-bottom: 0.25rem; font-size: 1rem;">
                        <span style="color: #00cc00;">{p.name}</span> 
                        <span style="color: #008800; font-size: 1rem;">({eligible})</span> 
                        <span style="float: right; color: #00ff00;">{int(p.fpts)}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Download results as CSV
        st.markdown("---")
        st.markdown(content.EXPORT_HEADER)
        
        # Create export data
        export_data = []
        for rank, (team_name, (roster, total_fpts)) in enumerate(sorted_results, 1):
            for player, assigned_pos in roster:
                export_data.append({
                    'Rank': rank,
                    'Team': team_name,
                    'Player': player.name,
                    'Assigned Position': assigned_pos,
                    'Eligible Positions': ','.join(sorted(player.positions)),
                    'FPts': player.fpts,
                    'Total Team FPts': total_fpts
                })
        
        df_export = pd.DataFrame(export_data)
        csv_export = df_export.to_csv(index=False)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label=content.DOWNLOAD_BUTTON_LABEL,
                data=csv_export,
                file_name=f"optimal_rosters_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.exception(e)


