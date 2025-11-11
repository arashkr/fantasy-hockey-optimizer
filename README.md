# Fantasy Hockey Roster Optimizer

A Python application that calculates the optimal fantasy hockey roster for each team in a Fantrax league export. The optimizer finds the best possible combination of players that maximizes total fantasy points (FPts) while meeting position requirements.

Available as both a **command-line tool** and a **web application** with CSV upload functionality.

## Requirements

### Command-Line Tool
- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

### Web Application
- Python 3.7 or higher
- Streamlit and Pandas (see `requirements.txt`)

## Position Requirements

Each team's optimal roster must include:
- **3 Centers (C)**
- **3 Right Wingers (RW)**
- **3 Left Wingers (LW)**
- **4 Defensemen (D)**
- **3 Goalies (G)**

Players eligible for multiple positions can be assigned to any of their eligible positions to maximize the total FPts.

## Usage

### Web Application (Recommended)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the web app:**
   ```bash
   streamlit run app.py
   ```

3. **Open your browser** to `http://localhost:8501`

4. **Upload your CSV file** using the file uploader

The web app provides:
- Interactive team selection
- Visual summary tables
- Detailed roster breakdowns
- CSV export functionality

### Command-Line Tool

```bash
python3 fantasy_roster_optimizer.py <path_to_csv_file>
```

**Example:**
```bash
python3 fantasy_roster_optimizer.py "Fantrax-Players-The Conos League (6).csv"
```

## CSV File Format

The application expects a CSV file exported from Fantrax with the following columns:
- `ID`: Player ID
- `Player`: Player name
- `Team`: NHL team abbreviation
- `Position`: Player position(s) - can be single (e.g., "C") or multiple (e.g., "C,RW")
- `Status`: Fantasy team abbreviation (2-3 letters)
- `Roster Status`: Active or Reserve
- `FPts`: Fantasy points (the value to maximize)

## Output

The application provides two levels of output:

1. **Summary Table**: Shows each team's total optimal FPts and position breakdown
2. **Detailed Breakdown**: Lists all selected players for each team, grouped by position, showing:
   - Player name
   - Eligible positions
   - Fantasy points

## Algorithm

The optimizer uses a backtracking algorithm to find the optimal roster assignment:
1. Players are sorted by FPts (descending)
2. The algorithm explores all possible position assignments for multi-position players
3. Pruning is used to avoid exploring suboptimal paths
4. The solution with the highest total FPts is selected

## Example Output

```
================================================================================
FANTASY HOCKEY ROSTER OPTIMIZATION RESULTS
================================================================================

Team     Total FPts   Players Selected                                            
--------------------------------------------------------------------------------
JS       238.00       C:3 RW:3 LW:3 D:4 G:3
UPI      221.00       C:3 RW:3 LW:3 D:4 G:3
...
```

## Deployment

The web application can be deployed to:
- **Streamlit Cloud** (free, recommended) - See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Heroku** - See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Docker** - See [DEPLOYMENT.md](DEPLOYMENT.md)
- **AWS/Azure/GCP** - See [DEPLOYMENT.md](DEPLOYMENT.md)

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Notes

- The optimizer considers all players assigned to each team (both Active and Reserve status)
- Multi-position players are intelligently assigned to maximize total FPts
- The algorithm ensures strict adherence to position requirements
- Results are sorted by total FPts (descending)
- The web app supports real-time CSV upload and processing

