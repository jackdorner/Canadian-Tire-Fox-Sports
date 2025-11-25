from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from pymongo import MongoClient
from datetime import datetime, timedelta
from django.shortcuts import render
import requests
import json


client = MongoClient(settings.MONGODB_URI)
db = client["FinalProjectPart2"]   # DB name
games_col = db["GameWeeks"]     #collection name

def home(request):
    return render(request, "home.html")

client = MongoClient(settings.MONGODB_URI)
db = client["FinalProjectPart2"]
games_col = db["Games"]


@require_GET
def games_for_week(request):
    week = request.GET.get("week")    # "1", "10", etc.
    season_start = request.GET.get("season_start", "2025")  # Default to 2025 if not provided

    if not week:
        return JsonResponse({"games": []})

    # Your docs use "2025/2026"
    season_str = f"{season_start}/{int(season_start) + 1}"

    # NOTE: week is stored as a string in Mongo, so cast to str
    mongo_query = {
        "week": str(week),
        "season": season_str,
    }

    docs = list(games_col.find(mongo_query))

    games = []
    for d in docs:
        home = d["home_team"]
        away = d["away_team"]
        status = d.get("status", {})

        iso_time = d.get("time")  # e.g. "2025-08-01T00:00:00Z"
        try:
            dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
            date_str = dt.strftime("%A, %b %d, %Y")
        except Exception:
            date_str = iso_time or ""

        games.append({
            "date": date_str,
            "status": status.get("type", "scheduled"),         # "final"/"in"/"scheduled"
            "statusText": status.get("description", "Scheduled"),
            "shortDetail": status.get("short_detail", ""),

            "homeTeam": {
                "name": home["display_name"],
                "abbreviation": home["abbreviation"],
                "logo": home["logo"],
                "record": home.get("record", ""),
            },
            "awayTeam": {
                "name": away["display_name"],
                "abbreviation": away["abbreviation"],
                "logo": away["logo"],
                "record": away.get("record", ""),
            },
            "homeScore": home.get("score", 0),
            "awayScore": away.get("score", 0),
        })

    return JsonResponse({"games": games})


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
    """Fetch games for a specific date from ESPN API"""
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={date_str}"
    
    try:
        response = requests.get(url, timeout=10)
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
    """Extract and format game information from ESPN API response"""
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
        "week": str(week_num),
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


@csrf_exempt
@require_POST
def refresh_week_games(request):
    """Refresh games for a specific week from ESPN API"""
    try:
        data = json.loads(request.body)
        week = data.get('week')
        season_start = data.get('season_start', '2025')
        
        if not week:
            return JsonResponse({'error': 'Week parameter is required'}, status=400)
        
        season_str = f"{season_start}/{int(season_start) + 1}"
        
        # Load weeks data to get date range
        from pathlib import Path
        weeks_file = Path(settings.BASE_DIR) / "nfl_data" / "weeks.json"
        with open(weeks_file, 'r') as f:
            weeks_data = json.load(f)
        
        # Find the week data
        week_data = None
        for w in weeks_data:
            if str(w['value']) == str(week):
                week_data = w
                break
        
        if not week_data:
            return JsonResponse({'error': f'Week {week} not found in weeks data'}, status=404)
        
        # Get date range for the week
        dates = parse_date_range(week_data['startDate'], week_data['endDate'])
        
        # Fetch games for all dates in the week
        week_games = []
        for date_str in dates:
            games = fetch_games_for_date(date_str)
            week_games.extend(games)
        
        if not week_games:
            return JsonResponse({
                'message': f'No games found for week {week}',
                'games_updated': 0
            })
        
        # Process and update games in MongoDB
        updated_count = 0
        for game_event in week_games:
            try:
                game_info = extract_game_info(game_event, week, season_str)
                
                # Update or insert game in MongoDB
                games_col.update_one(
                    {'id': game_info['id']},
                    {'$set': game_info},
                    upsert=True
                )
                updated_count += 1
            except Exception as e:
                print(f"Error processing game {game_event.get('id', 'unknown')}: {e}")
        
        return JsonResponse({
            'message': f'Successfully refreshed {updated_count} games for week {week}',
            'games_updated': updated_count
        })
        
    except Exception as e:
        print(f"Error refreshing games: {e}")
        return JsonResponse({'error': str(e)}, status=500)

