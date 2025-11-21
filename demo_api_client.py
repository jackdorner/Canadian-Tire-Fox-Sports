"""
Quick demonstration of the NFL API Client.
Shows how to fetch and examine data from ESPN NFL endpoints.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.nfl_api_client import NFLAPIClient
from app.NFLEndpoints import NFLTeam
import json


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def demo_teams():
    """Demonstrate fetching all teams."""
    print_section("DEMO: Fetching All NFL Teams")
    
    client = NFLAPIClient()
    teams = client.fetch_all_teams()
    
    print(f"Found {len(teams)} NFL teams\n")
    
    # Show first 3 teams as examples
    for i, team in enumerate(teams[:3], 1):
        print(f"{i}. {team['display_name']} ({team['abbreviation']})")
        print(f"   Logo: {team['logo_url'][:50]}..." if team['logo_url'] else "   Logo: N/A")
        print(f"   Colors: #{team['color']}, #{team['alternate_color']}")
        print(f"   Venue: {team['venue']['name']}, {team['venue']['city']}, {team['venue']['state']}")
        print()
    
    print(f"... and {len(teams) - 3} more teams")


def demo_team_details():
    """Demonstrate fetching team details."""
    print_section("DEMO: Fetching Team Details (Green Bay Packers)")
    
    client = NFLAPIClient()
    details = client.fetch_team_details(NFLTeam.PACKERS.value)
    
    if details:
        print(f"Team: {details['display_name']}")
        print(f"Record: {details['record_summary']}")
        print(f"Standing: {details['standing_summary']}")
        print(f"\nDetailed Record:")
        print(f"  Overall: {details['record']['overall']['wins']}-{details['record']['overall']['losses']}-{details['record']['overall']['ties']}")
        print(f"  Home: {details['record']['home']['wins']}-{details['record']['home']['losses']}")
        print(f"  Road: {details['record']['road']['wins']}-{details['record']['road']['losses']}")
        
        if details.get('next_game'):
            print(f"\nNext Game:")
            print(f"  {details['next_game']['name']}")
            print(f"  Date: {details['next_game']['date']}")
    else:
        print("Failed to fetch team details")


def demo_roster():
    """Demonstrate fetching team roster."""
    print_section("DEMO: Fetching Team Roster (Kansas City Chiefs)")
    
    client = NFLAPIClient()
    roster = client.fetch_team_roster(NFLTeam.CHIEFS.value)
    
    print(f"Found {len(roster)} players on roster\n")
    
    # Group by position for display
    positions = {}
    for player in roster:
        pos = player['position']['abbreviation']
        if pos not in positions:
            positions[pos] = []
        positions[pos].append(player)
    
    # Show QBs as example
    if 'QB' in positions:
        print("Quarterbacks:")
        for player in positions['QB']:
            print(f"  #{player['jersey']} {player['display_name']}")
            print(f"     {player['height']}, {player['weight']} - {player['college']}")
            print(f"     Experience: {player['experience']} years")
            print()
    
    print(f"Other positions: {', '.join(sorted(positions.keys()))}")


def demo_scoreboard():
    """Demonstrate fetching scoreboard."""
    print_section("DEMO: Fetching Scoreboard (Recent Date)")
    
    client = NFLAPIClient()
    # Try a recent date - adjust this to a date with actual games
    games = client.fetch_scoreboard('20241103')
    
    if games:
        print(f"Found {len(games)} games\n")
        
        for i, game in enumerate(games[:3], 1):
            home = game['home_team']
            away = game['away_team']
            status = game['status']
            
            print(f"Game {i}: Week {game['week']}")
            print(f"  {away['display_name']:<25} {away['score']:>3}")
            print(f"  {home['display_name']:<25} {home['score']:>3}")
            print(f"  Status: {status['short_detail']}")
            print(f"  Venue: {game['venue']['name']}")
            print(f"  Network: {', '.join(game['broadcasts'])}")
            
            # Show stat leaders if available
            if game.get('stat_leaders'):
                print(f"  Leaders:")
                for stat_type, leaders in game['stat_leaders'].items():
                    if leaders:
                        leader = leaders[0]
                        print(f"    {stat_type.title()}: {leader['player_name']} - {leader['value']}")
            print()
        
        if len(games) > 3:
            print(f"... and {len(games) - 3} more games")
    else:
        print("No games found for this date")


def demo_schedule():
    """Demonstrate fetching schedule."""
    print_section("DEMO: Fetching Schedule (2024 Week 10)")
    
    client = NFLAPIClient()
    schedule = client.fetch_schedule(2024, 10)
    
    print(f"Season: {schedule['year']}, Week: {schedule['week']}")
    print(f"Found {len(schedule['games'])} games scheduled\n")
    
    for i, game in enumerate(schedule['games'][:5], 1):
        print(f"{i}. {game['name']}")
        print(f"   Date: {game['date']}")
        print(f"   Venue: {game['venue']['name']}")
        print(f"   TV: {', '.join(game['broadcasts'])}")
        print()
    
    if len(schedule['games']) > 5:
        print(f"... and {len(schedule['games']) - 5} more games")


def demo_team_stats():
    """Demonstrate fetching team statistics."""
    print_section("DEMO: Fetching Team Statistics (Buffalo Bills 2024)")
    
    client = NFLAPIClient()
    stats = client.fetch_team_stats(NFLTeam.BILLS.value, 2024)
    
    if stats:
        print("Key Offensive Statistics:\n")
        
        offensive = stats['key_stats'].get('offensive', {})
        for stat_name, stat_data in offensive.items():
            if stat_data:
                name = stat_name.replace('_', ' ').title()
                print(f"  {name}:")
                print(f"    Value: {stat_data.get('display_value', 'N/A')}")
                print(f"    Rank: #{stat_data.get('rank', 'N/A')}")
                if stat_data.get('per_game_value'):
                    print(f"    Per Game: {stat_data.get('per_game_display_value', 'N/A')}")
                print()
        
        print("\nKey Defensive Statistics:\n")
        defensive = stats['key_stats'].get('defensive', {})
        for stat_name, stat_data in defensive.items():
            if stat_data:
                name = stat_name.replace('_', ' ').title()
                print(f"  {name}:")
                print(f"    Value: {stat_data.get('display_value', 'N/A')}")
                print(f"    Rank: #{stat_data.get('rank', 'N/A')}")
                print()
    else:
        print("Failed to fetch team statistics")


def demo_filtered_data_structure():
    """Show the structure of filtered data."""
    print_section("DEMO: Data Structure Overview")
    
    client = NFLAPIClient()
    
    print("Fetching sample data to show structure...\n")
    
    # Get one team
    teams = client.fetch_all_teams()
    if teams:
        print("TEAM DATA STRUCTURE:")
        print(json.dumps(teams[0], indent=2, default=str)[:500] + "...")
    
    print("\n" + "-"*70 + "\n")
    
    # Get one player
    roster = client.fetch_team_roster(NFLTeam.PACKERS.value)
    if roster:
        print("PLAYER DATA STRUCTURE:")
        print(json.dumps(roster[0], indent=2, default=str)[:500] + "...")


def main():
    """Run all demonstrations."""
    print("\n" + "*"*70)
    print("*" + " "*68 + "*")
    print("*" + "  NFL API CLIENT DEMONSTRATION".center(68) + "*")
    print("*" + " "*68 + "*")
    print("*"*70)
    
    try:
        # Run each demo
        demo_teams()
        input("\nPress Enter to continue...")
        
        demo_team_details()
        input("\nPress Enter to continue...")
        
        demo_roster()
        input("\nPress Enter to continue...")
        
        demo_scoreboard()
        input("\nPress Enter to continue...")
        
        demo_schedule()
        input("\nPress Enter to continue...")
        
        demo_team_stats()
        input("\nPress Enter to continue...")
        
        demo_filtered_data_structure()
        
        print("\n" + "*"*70)
        print("*" + " "*68 + "*")
        print("*" + "  DEMONSTRATION COMPLETE".center(68) + "*")
        print("*" + " "*68 + "*")
        print("*"*70 + "\n")
        
        print("Next steps:")
        print("1. Install MongoDB and start the service")
        print("2. Run: python app/data_loader.py")
        print("3. Build your Django views to display this data")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
