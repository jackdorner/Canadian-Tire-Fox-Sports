import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

def load_weeks():
    """Load the weeks data from weeks.json"""
    weeks_file = Path(__file__).parent / "nfl_data" / "weeks.json"
    with open(weeks_file, 'r') as f:
        return json.load(f)

def parse_date_range(start_date_str, end_date_str):
    """Parse date range and return list of dates in YYYYMMDD format"""
    start = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
    end = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
    
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime('%Y%m%d'))
        current += timedelta(days=1)
    
    return dates

def fetch_games_for_date(date_str):
    """Fetch games for a specific date"""
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={date_str}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('events', [])
        else:
            print(f"Error fetching data for {date_str}: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception fetching data for {date_str}: {e}")
        return []

def extract_game_info(event, week_num, season):
    """Extract and format game information according to specified structure"""
    competition = event['competitions'][0]
    competitors = competition['competitors']
    status = competition['status']
    
    # Find home and away teams
    home_team = None
    away_team = None
    for competitor in competitors:
        if competitor['homeAway'] == 'home':
            home_team = competitor
        else:
            away_team = competitor
    
    # Extract linescores
    def get_linescores(team):
        linescores = []
        if 'linescores' in team:
            for ls in team['linescores']:
                linescores.append(int(ls.get('value', 0)))
        return linescores
    
    # Get broadcast info
    broadcast = competition.get('broadcast', '')
    if not broadcast and 'broadcasts' in competition and len(competition['broadcasts']) > 0:
        broadcast_names = competition['broadcasts'][0].get('names', [])
        broadcast = broadcast_names[0] if broadcast_names else ''
    
    # Get venue info
    venue_data = competition.get('venue', {})
    venue = {
        "name": venue_data.get('fullName', ''),
        "city": venue_data.get('address', {}).get('city', ''),
        "state": venue_data.get('address', {}).get('state', '')
    }
    
    # Get overall record
    def get_record(team):
        records = team.get('records', [])
        for record in records:
            if record.get('type') == 'total' or record.get('name') == 'overall':
                return record.get('summary', '')
        return ''
    
    # Format the game data
    game = {
        "id": event['id'],
        "week": week_num,
        "season": season,
        "name": event['name'],
        "home_team": {
            "team_id": home_team['id'],
            "abbreviation": home_team['team']['abbreviation'],
            "display_name": home_team['team']['displayName'],
            "logo": home_team['team'].get('logo', ''),
            "score": int(home_team.get('score', 0)),
            "linescores": get_linescores(home_team),
            "winner": home_team.get('winner', False),
            "record": get_record(home_team)
        },
        "away_team": {
            "team_id": away_team['id'],
            "abbreviation": away_team['team']['abbreviation'],
            "display_name": away_team['team']['displayName'],
            "logo": away_team['team'].get('logo', ''),
            "score": int(away_team.get('score', 0)),
            "linescores": get_linescores(away_team),
            "winner": away_team.get('winner', False),
            "record": get_record(away_team)
        },
        "time": event.get('date', ''),
        "broadcast": broadcast,
        "status": {
            "completed": status['type'].get('completed', False),
            "description": status['type'].get('description', ''),
            "detail": status['type'].get('detail', ''),
            "short_detail": status['type'].get('shortDetail', ''),
            "state": status['type'].get('state', ''),
            "period": status.get('period', 0),
            "display_clock": status.get('displayClock', '0:00')
        },
        "venue": venue
    }
    
    return game

def fetch_all_games():
    """Fetch all games for the 2025 NFL season"""
    weeks = load_weeks()
    all_games = []
    
    # Filter to regular season and playoffs (skip preseason)
    # Regular season weeks have integer values 1-18
    # Playoff weeks also have values but different labels
    regular_and_playoff_weeks = [w for w in weeks if 
                                  ('Week' in w['label'] and 'Preseason' not in w['label']) or
                                  'Wild Card' in w['label'] or
                                  'Divisional' in w['label'] or
                                  'Conference' in w['label'] or
                                  'Super Bowl' in w['label']]
    
    print(f"Fetching games for {len(regular_and_playoff_weeks)} weeks...")
    
    for week_data in regular_and_playoff_weeks:
        week_label = week_data['label']
        week_value = week_data['value']
        
        print(f"\nProcessing {week_label}...")
        
        # Get date range for the week
        dates = parse_date_range(week_data['startDate'], week_data['endDate'])
        
        week_games = []
        for date_str in dates:
            games = fetch_games_for_date(date_str)
            week_games.extend(games)
        
        # Extract and format game info
        for game_event in week_games:
            try:
                game_info = extract_game_info(game_event, week_value, "2025/2026")
                all_games.append(game_info)
                print(f"  - {game_info['name']}")
            except Exception as e:
                print(f"  Error processing game {game_event.get('id', 'unknown')}: {e}")
        
        print(f"  Found {len(week_games)} games for {week_label}")
    
    return all_games

def main():
    """Main function to fetch and save all NFL games"""
    print("Starting NFL 2025 season game data collection...")
    
    all_games = fetch_all_games()
    
    # Save to JSON file
    output_file = Path(__file__).parent / "nfl_data" / "all_games_2025.json"
    with open(output_file, 'w') as f:
        json.dump(all_games, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Total games collected: {len(all_games)}")
    print(f"Data saved to: {output_file}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
