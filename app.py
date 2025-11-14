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

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
    }
    
    /* Card styling */
    .team-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .position-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 3px solid #667eea;
    }
    
    .player-item {
        background: white;
        padding: 0.75rem;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .player-item:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transform: translateX(5px);
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    .dataframe thead {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    .dataframe tbody tr:hover {
        background-color: #e9ecef;
    }
    
    /* Button styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* File uploader styling */
    .uploadedFile {
        border: 2px dashed #667eea;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Section headers */
    h2 {
        color: #667eea;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    
    h3 {
        color: #764ba2;
        margin-top: 1.5rem;
    }
    
    /* Info box styling */
    .stInfo {
        background: linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%);
        border-left: 4px solid #26a69a;
        border-radius: 6px;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🏒 Fantasy Hockey Roster Optimizer</h1>
    <p>Calculate the optimal fantasy roster for each team based on fantasy points</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;">
    <h3 style="color: #667eea; margin-top: 0;">📋 Roster Requirements</h3>
    <p style="margin-bottom: 0.5rem;">Each team's optimal roster includes:</p>
    <ul style="margin: 0;">
        <li><strong>3 Centers (C)</strong></li>
        <li><strong>3 Right Wingers (RW)</strong></li>
        <li><strong>3 Left Wingers (LW)</strong></li>
        <li><strong>4 Defensemen (D)</strong></li>
        <li><strong>3 Goalies (G)</strong></li>
    </ul>
</div>
""", unsafe_allow_html=True)

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
        
        # Show loading spinner with progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text('Loading CSV data...')
        optimizer = RosterOptimizer(csv_content)
        
        # Calculate with progress updates
        teams = sorted(optimizer.teams.keys())
        results = {}
        total_teams = len(teams)
        
        for idx, team_name in enumerate(teams):
            status_text.text(f'Optimizing roster for {team_name} ({idx+1}/{total_teams})...')
            progress_bar.progress((idx + 1) / total_teams)
            roster, total_fpts = optimizer.optimize_roster(optimizer.teams[team_name])
            results[team_name] = (roster, total_fpts)
        
        status_text.text('Complete!')
        progress_bar.progress(1.0)
        
        # Sort results by total FPts
        sorted_results = sorted(results.items(), key=lambda x: x[1][1], reverse=True)
        
        # Summary section with metrics
        st.markdown("---")
        st.markdown("## 📊 Summary Results")
        
        # Top 3 teams as metrics
        top_3_cols = st.columns(3)
        for idx, (team_name, (roster, total_fpts)) in enumerate(sorted_results[:3]):
            with top_3_cols[idx]:
                st.metric(
                    label=f"🥇 #{idx+1} - {team_name}" if idx == 0 else f"🥈 #{idx+1} - {team_name}" if idx == 1 else f"🥉 #{idx+1} - {team_name}",
                    value=f"{total_fpts:.2f}",
                    delta=None
                )
        
        # Create summary dataframe with styling
        summary_data = []
        for rank, (team_name, (roster, total_fpts)) in enumerate(sorted_results, 1):
            pos_counts = defaultdict(int)
            for _, pos in roster:
                pos_counts[pos] += 1
            summary_data.append({
                'Rank': rank,
                'Team': team_name,
                'Total FPts': total_fpts,
                'C': pos_counts['C'],
                'RW': pos_counts['RW'],
                'LW': pos_counts['LW'],
                'D': pos_counts['D'],
                'G': pos_counts['G']
            })
        
        df_summary = pd.DataFrame(summary_data)
        
        # Style the dataframe
        def highlight_top3(row):
            if row['Rank'] <= 3:
                return ['background-color: #fff3cd'] * len(row)
            return [''] * len(row)
        
        styled_df = df_summary.style.apply(highlight_top3, axis=1).format({
            'Total FPts': '{:.2f}'
        })
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Detailed breakdown
        st.markdown("---")
        st.markdown("## 📋 Detailed Breakdown by Team")
        
        # Team selector with rank
        team_names = [team for team, _ in sorted_results]
        team_with_ranks = [f"#{idx+1} - {team} ({results[team][1]:.2f} FPts)" 
                          for idx, team in enumerate(team_names)]
        
        selected_index = st.selectbox(
            "Select a team to view detailed roster:",
            range(len(team_names)),
            format_func=lambda x: team_with_ranks[x],
            index=0
        )
        
        selected_team = team_names[selected_index]
        
        # Display selected team's roster
        roster, total_fpts = results[selected_team]
        rank = selected_index + 1
        
        # Team header card
        st.markdown(f"""
        <div class="team-card">
            <h2 style="color: #667eea; margin-top: 0;">
                {'🥇' if rank == 1 else '🥈' if rank == 2 else '🥉' if rank == 3 else '🏒'} 
                Rank #{rank}: {selected_team}
            </h2>
            <div style="font-size: 1.5rem; color: #764ba2; font-weight: bold;">
                Total Fantasy Points: {total_fpts:.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
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
        position_icons = {
            'C': '🎯',
            'RW': '➡️',
            'LW': '⬅️',
            'D': '🛡️',
            'G': '🥅'
        }
        
        for idx, pos in enumerate(position_order):
            with cols[idx]:
                players_in_pos = by_position[pos]
                if players_in_pos:
                    st.markdown(f"""
                    <div class="position-card">
                        <h3 style="color: #667eea; margin-top: 0;">
                            {position_icons[pos]} {position_names[pos]} ({len(players_in_pos)})
                        </h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for p, assigned_pos in sorted(players_in_pos, key=lambda x: x[0].fpts, reverse=True):
                        eligible_pos = ','.join(sorted(p.positions))
                        st.markdown(f"""
                        <div class="player-item">
                            <strong style="color: #333; font-size: 0.95rem;">{p.name}</strong><br>
                            <span style="color: #666; font-size: 0.85rem;">{eligible_pos}</span> | 
                            <span style="color: #667eea; font-weight: bold;">{p.fpts:.2f} FPts</span>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Download results as CSV
        st.markdown("---")
        st.markdown("## 💾 Export Results")
        
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
                label="📥 Download Results as CSV",
                data=csv_export,
                file_name=f"optimal_rosters_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.exception(e)
else:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%); 
                padding: 2rem; border-radius: 10px; border-left: 4px solid #26a69a; 
                margin: 2rem 0;">
        <h3 style="color: #26a69a; margin-top: 0;">👆 Ready to Get Started?</h3>
        <p style="font-size: 1.1rem; margin-bottom: 0;">
            Upload your Fantrax CSV export file above to calculate optimal rosters for all teams.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show example format in a nicer expander
    with st.expander("📝 Expected CSV Format", expanded=False):
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 6px;">
            <p>The CSV file should have the following columns:</p>
            <ul>
                <li><strong>ID</strong>: Player ID</li>
                <li><strong>Player</strong>: Player name</li>
                <li><strong>Team</strong>: NHL team abbreviation</li>
                <li><strong>Position</strong>: Player position(s) - can be single (e.g., "C") or multiple (e.g., "C,RW")</li>
                <li><strong>Status</strong>: Fantasy team abbreviation (2-3 letters)</li>
                <li><strong>Roster Status</strong>: Active or Reserve</li>
                <li><strong>FPts</strong>: Fantasy points</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

