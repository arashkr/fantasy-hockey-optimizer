#!/usr/bin/env python3
"""
Simple test script for Fantasy Hockey Roster Optimizer
Run this with your CSV file to test the optimization
"""

import sys
import os
from fantasy_roster_optimizer import RosterOptimizer

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_optimization.py <csv_file_path>")
        print("\nExample:")
        print("  python test_optimization.py 'your_file.csv'")
        print("\nOr drag and drop your CSV file onto this script.")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"Error: File '{csv_path}' not found.")
        print("Please provide a valid path to your CSV file.")
        sys.exit(1)
    
    print(f"Loading CSV file: {csv_path}")
    print("=" * 80)
    
    try:
        # Create optimizer and calculate results
        optimizer = RosterOptimizer(csv_path)
        
        print(f"\nFound {len(optimizer.teams)} teams in the CSV file.")
        print("Calculating optimal rosters...\n")
        
        # Calculate all teams
        results = optimizer.calculate_all_teams()
        
        # Print results
        optimizer.print_results(results)
        
        print("\n" + "=" * 80)
        print("Test completed successfully!")
        print("=" * 80)
        
    except FileNotFoundError:
        print(f"Error: File '{csv_path}' not found.")
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing required column in CSV: {e}")
        print("\nExpected columns: ID, Player, Team, Position, Status, Roster Status, FPts")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

