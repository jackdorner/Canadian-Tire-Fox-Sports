from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from pymongo import MongoClient
from datetime import datetime, timedelta
from django.shortcuts import render
import requests
import json
import threading
from time import sleep
from app.NFLEndpoints import NFLTeam


client = MongoClient(settings.MONGODB_URI)
db = client["FinalProjectPart2"]
games_col = db["Games"]
team_stats_col = db["TeamStats"]

def home(request):
    return render(request, "home.html")

def _get_stat_value(stats_list, names, default='-'):
    if isinstance(names, str):
        names = [names]

    for n in names:
        for stat in stats_list:
            if stat.get("name") == n:
                val = stat.get("displayValue")
                if val not in (None, ""):
                    return val
                val = stat.get("value")
                if val not in (None, ""):
                    return val
    return default


def _build_team_h2h_stats(team_abbr: str):
    """
    Given 'LV', 'DEN', etc, return offense/defense/special stats
    for the head-to-head page.
    """
    team_abbr = team_abbr.upper()
    print("H2H: building stats for", team_abbr)

    team_id = _get_team_id_from_abbr(team_abbr)
    if team_id is None:
        print("H2H: could not resolve team_id for", team_abbr)
        return None

    print("H2H:", team_abbr, "resolved team_id =", team_id)

    doc = team_stats_col.find_one({"team_id": team_id})
    if not doc:
        print("H2H: no TeamStats doc for team_id", team_id)
        return None

    stats_list = doc.get("stats", [])

    offense = {
        "total_yards":         _get_stat_value(stats_list, ["totalYards", "netTotalYards"]),
        "rushing_yards":       _get_stat_value(stats_list, "rushingYards"),
        "yards_per_reception": _get_stat_value(stats_list, "yardsPerReception"),
        "yards_per_rush":      _get_stat_value(stats_list, "yardsPerRushAttempt"),
        "passer_rating":       _get_stat_value(stats_list, ["QBRating", "quarterbackRating", "ESPNQBRating"]),
        "third_down_pct":      _get_stat_value(stats_list, "thirdDownConvPct"),
        "total_penalties":     _get_stat_value(stats_list, "totalPenalties"),
        "points_per_game":     _get_stat_value(stats_list, "totalPointsPerGame"),
    }

    defense = {
        "interceptions":     _get_stat_value(stats_list, "interceptions"),
        "tackles_for_loss":  _get_stat_value(stats_list, "tacklesForLoss"),
    }

    special = {
        "long_fg_made":      _get_stat_value(stats_list, "longFieldGoalMade"),
    }

    return {
        "offense": offense,
        "defense": defense,
        "special": special,
    }


def _get_team_id_from_abbr(abbr: str):
    """
    Find a team_id for a given abbreviation (e.g. 'GB', 'DEN')
    by looking at any game in the Games collection.
    """
    abbr = abbr.upper()

    doc = games_col.find_one({
        "$or": [
            {"home_team.abbreviation": abbr},
            {"away_team.abbreviation": abbr},
        ]
    })

    if not doc:
        print("H2H: no game found containing team", abbr)
        return None

    if doc["home_team"]["abbreviation"].upper() == abbr:
        raw_id = doc["home_team"]["team_id"]
    else:
        raw_id = doc["away_team"]["team_id"]

    try:
        return int(raw_id)
    except (TypeError, ValueError):
        return raw_id

def head_to_head(request, away_abbr, home_abbr):
    away_stats = _build_team_h2h_stats(away_abbr)
    home_stats = _build_team_h2h_stats(home_abbr)

    offense_rows = defense_rows = special_rows = []
    if away_stats and home_stats:
        offense_rows = _build_rows(
            away_stats["offense"],
            home_stats["offense"],
            [
                ("total_yards", "Total Yards", False),
                ("rushing_yards", "Rushing Yards", False),
                ("yards_per_reception", "Yards / Reception", False),
                ("yards_per_rush", "Yards / Rush Attempt", False),
                ("passer_rating", "Passer Rating", False),
                ("third_down_pct", "3rd Down %", False),
                ("total_penalties", "Total Penalties", True),
                ("points_per_game", "Points / Game", False),
            ]
        )
        defense_rows = _build_rows(
            away_stats["defense"],
            home_stats["defense"],
            [
                ("interceptions", "Interceptions", False),
                ("tackles_for_loss", "Tackles for Loss", False),
            ]
        )
        special_rows = _build_rows(
            away_stats["special"],
            home_stats["special"],
            [
                ("long_fg_made", "Long Field Goal Made", False),
            ]
        )

    context = {
        "away_team": away_abbr,
        "home_team": home_abbr,
        "away_stats": away_stats,
        "home_stats": home_stats,
        "offense_rows": offense_rows,
        "defense_rows": defense_rows,
        "special_rows": special_rows,
        "away_logo": _get_team_logo_from_abbr(away_abbr),
        "home_logo": _get_team_logo_from_abbr(home_abbr),
    }
    return render(request, "head_to_head.html", context)


# this is to normalize numbers for comparison (removes %, commas, etc)
def _parse_number_for_compare(value):
    if value in (None, "", "-"):
        return None
    if isinstance(value, (int, float)):
        return float(value)

    s = str(value).replace(",", "").strip()
    if s.endswith("%"):
        s = s[:-1]
    try:
        return float(s)
    except ValueError:
        return None


def _build_rows(away_section, home_section, field_specs):
    """
    field_specs = [
        ("total_yards", "Total Yards", False),   # False => higher is better
        ("total_penalties", "Total Penalties", True),  # True => lower is better
        ...
    ]
    """
    rows = []
    for key, label, prefer_low in field_specs:
        a_display = away_section.get(key, "-")
        h_display = home_section.get(key, "-")

        a_num = _parse_number_for_compare(a_display)
        h_num = _parse_number_for_compare(h_display)

        leader = "tie"
        if a_num is not None and h_num is not None and a_num != h_num:
            if prefer_low:
                leader = "away" if a_num < h_num else "home"
            else:
                leader = "away" if a_num > h_num else "home"

        if leader == "away":
            away_class = "leader"
            home_class = "faded"
        elif leader == "home":
            away_class = "faded"
            home_class = "leader"
        else:
            away_class = ""
            home_class = ""

        rows.append({
            "label": label,
            "away_display": a_display,
            "home_display": h_display,
            "away_class": away_class,
            "home_class": home_class,
        })
    return rows

def _find_team_doc_for_abbr(abbr: str):
    abbr = abbr.upper()
    doc = games_col.find_one({
        "$or": [
            {"home_team.abbreviation": abbr},
            {"away_team.abbreviation": abbr},
        ]
    })
    if not doc:
        return None

    if doc["home_team"]["abbreviation"].upper() == abbr:
        return doc["home_team"]
    return doc["away_team"]


def _get_team_logo_from_abbr(abbr: str):
    team_doc = _find_team_doc_for_abbr(abbr)
    if not team_doc:
        return ""
    return team_doc.get("logo", "")


def season_stats(request):
    return render(request, "season_stats.html")


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


def fetch_team_stats(team_id, year=2025):
    """Fetch statistics for a specific team from ESPN API"""
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
                        # Build the stat object
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


def refresh_all_team_stats_async(year=2025):
    """Background task to fetch all team stats and update MongoDB"""
    print(f"Starting async team stats refresh for season {year}...")
    
    try:
        # Clear existing stats
        result = team_stats_col.delete_many({})
        print(f"Deleted {result.deleted_count} existing team stats documents")
        
        updated_count = 0
        failed_count = 0
        
        # Fetch stats for each team
        for team in NFLTeam:
            team_id = team.value
            team_name = team.name
            
            print(f"Fetching stats for {team_name} (ID: {team_id})...")
            
            team_stats = fetch_team_stats(team_id, year)
            
            if team_stats:
                # Insert the new stats
                team_stats_col.insert_one(team_stats)
                updated_count += 1
                print(f"  ✓ Updated {team_name} with {len(team_stats['stats'])} stats")
            else:
                failed_count += 1
                print(f"  ✗ Failed to fetch stats for {team_name}")
            
            # Be nice to the API
            sleep(0.5)
        
        print(f"\nTeam stats refresh completed:")
        print(f"  - Successfully updated: {updated_count} teams")
        print(f"  - Failed: {failed_count} teams")
        
    except Exception as e:
        print(f"Error in async team stats refresh: {e}")


@csrf_exempt
@require_POST
def trigger_stats_refresh(request):
    """Trigger async refresh of team statistics"""
    try:
        data = json.loads(request.body)
        season_start = data.get('season_start', '2025')
        year = int(season_start)
        
        # Start the refresh in a background thread
        thread = threading.Thread(target=refresh_all_team_stats_async, args=(year,))
        thread.daemon = True
        thread.start()
        
        return JsonResponse({
            'message': 'Team stats refresh started in background',
            'status': 'started'
        })
        
    except Exception as e:
        print(f"Error triggering stats refresh: {e}")
        return JsonResponse({'error': str(e)}, status=500)

