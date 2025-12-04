"""
Script to load teams from teams.json into MongoDB Teams collection
"""
import json
from pathlib import Path
from pymongo import MongoClient
from django.conf import settings
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nfl_game_center.settings')
django.setup()

def load_teams():
    """Load teams from teams.json into MongoDB"""
    client = MongoClient(settings.MONGODB_URI)
    db = client["FinalProjectPart2"]
    teams_col = db["Teams"]
    
    # Load teams.json
    teams_file = Path(__file__).parent / "nfl_data" / "teams.json"
    
    with open(teams_file, 'r') as f:
        teams_data = json.load(f)
    
    # Clear existing teams
    result = teams_col.delete_many({})
    print(f"Deleted {result.deleted_count} existing teams")
    
    # Insert all teams
    if teams_data:
        teams_col.insert_many(teams_data)
        print(f"Successfully loaded {len(teams_data)} teams into MongoDB")
    else:
        print("No teams data found")

if __name__ == "__main__":
    load_teams()
