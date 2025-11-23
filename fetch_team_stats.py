"""
Script to fetch NFL team statistics from ESPN API and save to JSON file.
"""
import requests
import json
from app.NFLEndpoints import NFLTeam
from time import sleep


def fetch_team_stats(team_id, year=2025):
    """
    Fetch statistics for a specific team.
    
    Args:
        team_id: The ESPN team ID
        year: The season year (default: 2025)
    
    Returns:
        dict: Team statistics in the specified format, or None if error
    """
    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{year}/types/2/teams/{team_id}/statistics"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract all stats from all categories
        all_stats = []
        
        if 'splits' in data and 'categories' in data['splits']:
            for category in data['splits']['categories']:
                if 'stats' in category:
                    for stat in category['stats']:
                        # Build the stat object according to the specified structure
                        stat_obj = {
                            "name": stat.get("name", ""),
                            "displayName": stat.get("displayName", ""),
                            "shortDisplayName": stat.get("shortDisplayName", ""),
                            "description": stat.get("description", ""),
                            "abbreviation": stat.get("abbreviation", ""),
                            "value": stat.get("value", 0),
                            "displayValue": stat.get("displayValue", "0"),
                        }
                        
                        # Add optional fields if they exist
                        if "perGameValue" in stat:
                            stat_obj["perGameValue"] = stat["perGameValue"]
                        if "perGameDisplayValue" in stat:
                            stat_obj["perGameDisplayValue"] = stat["perGameDisplayValue"]
                        if "rank" in stat:
                            stat_obj["rank"] = stat["rank"]
                        if "rankDisplayValue" in stat:
                            stat_obj["rankDisplayValue"] = stat["rankDisplayValue"]
                        
                        all_stats.append(stat_obj)
        
        # Return in the specified format
        return {
            "team_id": team_id,
            "stats": all_stats
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stats for team {team_id}: {e}")
        return None


def fetch_all_team_stats(output_file="nfl_data/team_stats.json", year=2025):
    """
    Fetch statistics for all NFL teams and save to JSON file.
    
    Args:
        output_file: Path to output JSON file
        year: The season year (default: 2025)
    """
    print(f"Fetching statistics for all NFL teams (season {year})...")
    
    all_team_stats = []
    
    # Iterate through all teams in the NFLTeam enum
    for team in NFLTeam:
        team_id = team.value
        team_name = team.name
        
        print(f"Fetching stats for {team_name} (ID: {team_id})...", end=" ")
        
        team_stats = fetch_team_stats(team_id, year)
        
        if team_stats:
            all_team_stats.append(team_stats)
            print(f"✓ ({len(team_stats['stats'])} stats)")
        else:
            print("✗ Failed")
        
        # Be nice to the API - small delay between requests
        sleep(0.5)
    
    # Save to JSON file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_team_stats, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Successfully saved statistics for {len(all_team_stats)} teams to {output_file}")
        print(f"  Total stats collected: {sum(len(team['stats']) for team in all_team_stats)}")
        
    except IOError as e:
        print(f"\n✗ Error saving to file: {e}")


def main():
    """Main entry point for the script."""
    fetch_all_team_stats()


if __name__ == "__main__":
    main()
