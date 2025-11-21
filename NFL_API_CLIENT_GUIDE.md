# NFL API Client Documentation

## Overview

This module provides a comprehensive API client for fetching NFL data from ESPN endpoints and storing it in MongoDB. The system is designed for building an NFL-focused sports application similar to Fox Sports.

## Architecture

### Components

1. **NFLAPIClient** (`app/nfl_api_client.py`) - Handles API requests and data filtering
2. **Models** (`app/models.py`) - Django/Djongo models for MongoDB collections
3. **NFLDataLoader** (`app/data_loader.py`) - Utility for batch data loading
4. **NFLEndpoints** (`app/NFLEndpoints.py`) - API endpoint definitions and team IDs

## Data Models

### Team
Stores basic team information:
- Team ID, name, abbreviation, display names
- Logo URL and team colors (hex codes)
- Venue information (stadium name, city, state, capacity)
- Links to related resources

### TeamDetails
Stores extended team information:
- Current season record (overall, home, road)
- Win-loss-tie statistics
- Division/conference standings
- Next scheduled game information

### Player
Stores player roster information:
- Player ID, name, jersey number
- Team association
- Position (name, abbreviation, display name)
- Physical stats (height, weight, age)
- Headshot photo URL
- College and experience level

### Game
Stores game information and scores:
- Game ID, date, week, season
- Home and away team data (IDs, scores, quarter-by-quarter scoring)
- Game status (scheduled, in-progress, final)
- Venue information
- Broadcast networks
- Stat leaders (passing, rushing, receiving)
- Attendance

### TeamSeasonStats
Stores comprehensive team statistics:
- Offensive stats (passing, rushing, receiving yards/TDs)
- Defensive stats (tackles, sacks, interceptions)
- Special teams stats (FG%, punt average)
- Rankings for each statistic
- Per-game averages

### Schedule
Stores season schedule information:
- Week-by-week calendar
- Season structure (preseason, regular season, postseason)
- Game listings with dates and broadcast info

## API Methods

### NFLAPIClient Methods

#### `fetch_all_teams()` → List[Dict]
Fetches all 32 NFL teams with basic information.

**Returns:** List of team dictionaries with:
- `team_id`, `abbreviation`, `display_name`
- `logo_url`, `color`, `alternate_color`
- `venue` (stadium details)
- `links` (clubhouse, roster, stats URLs)

**Example:**
```python
from app.nfl_api_client import NFLAPIClient

client = NFLAPIClient()
teams = client.fetch_all_teams()

for team in teams:
    print(f"{team['display_name']} - {team['abbreviation']}")
```

---

#### `fetch_team_details(team_id: int)` → Dict
Fetches detailed information for a specific team.

**Parameters:**
- `team_id` (int): NFL team ID from NFLTeam enum

**Returns:** Dictionary with:
- `record` (overall, home, road wins-losses)
- `standing_summary` (e.g., "1st in NFC North")
- `next_game` (upcoming game details)

**Example:**
```python
from app.NFLEndpoints import NFLTeam

# Get Green Bay Packers details
details = client.fetch_team_details(NFLTeam.PACKERS.value)
print(f"Record: {details['record_summary']}")
print(f"Standings: {details['standing_summary']}")
```

---

#### `fetch_team_roster(team_id: int)` → List[Dict]
Fetches complete roster for a team.

**Returns:** List of player dictionaries with:
- `player_id`, `display_name`, `jersey`
- `position` (name, abbreviation)
- `headshot_url`, `height`, `weight`
- `experience`, `college`

**Example:**
```python
roster = client.fetch_team_roster(NFLTeam.CHIEFS.value)

for player in roster:
    pos = player['position']['abbreviation']
    print(f"#{player['jersey']} {player['display_name']} - {pos}")
```

---

#### `fetch_scoreboard(date: str)` → List[Dict]
Fetches games and live scores for a specific date.

**Parameters:**
- `date` (str): Date in YYYYMMDD format (e.g., '20241103')

**Returns:** List of game dictionaries with:
- `game_id`, `date`, `week`, `season`
- `home_team` / `away_team` (IDs, scores, linescores)
- `status` (completed, in-progress, scheduled)
- `stat_leaders` (top performers)
- `broadcasts` (TV networks)

**Example:**
```python
# Get games from November 3, 2024
games = client.fetch_scoreboard('20241103')

for game in games:
    home = game['home_team']
    away = game['away_team']
    print(f"{away['display_name']} {away['score']} @ {home['display_name']} {home['score']}")
```

---

#### `fetch_schedule(year: int, week: int)` → Dict
Fetches schedule for a specific week.

**Parameters:**
- `year` (int): Season year (e.g., 2024)
- `week` (int): Week number (1-18 for regular season)

**Returns:** Dictionary with:
- `calendar` (season structure, date ranges)
- `games` (list of scheduled games)

**Example:**
```python
schedule = client.fetch_schedule(2024, 10)

for game in schedule['games']:
    print(f"Week {game['week']}: {game['name']} on {game['date']}")
```

---

#### `fetch_team_stats(team_id: int, year: int)` → Dict
Fetches comprehensive team statistics.

**Parameters:**
- `team_id` (int): NFL team ID
- `year` (int): Season year

**Returns:** Dictionary with:
- `all_stats` (complete statistics by category)
- `key_stats` (summary of important metrics)
- Each stat includes: value, display_value, rank, per_game_value

**Example:**
```python
stats = client.fetch_team_stats(NFLTeam.BILLS.value, 2024)

passing = stats['key_stats']['offensive']['passing_yards']
print(f"Passing yards: {passing['display_value']} (Rank: {passing['rank']})")
```

---

## Data Loading Utility

The `NFLDataLoader` class provides methods to fetch and store data in MongoDB.

### Usage Examples

#### Load All Initial Data
```python
from app.data_loader import NFLDataLoader

loader = NFLDataLoader()
loader.load_initial_data()  # Loads teams, rosters, games, schedules, stats
```

#### Load Specific Data
```python
# Load all teams
loader.load_all_teams()

# Load roster for a specific team
from app.NFLEndpoints import NFLTeam
loader.load_team_roster(NFLTeam.PACKERS.value)

# Load games for a specific date
loader.load_scoreboard('20241103')

# Load schedule for a week
loader.load_schedule(2024, 10)

# Load team statistics
loader.load_team_stats(NFLTeam.CHIEFS.value, 2024)
```

#### Run from Command Line
```bash
python app/data_loader.py
```

---

## Database Schema

### Collections

1. **teams** - 32 NFL teams
2. **team_details** - Current season records and standings
3. **players** - All player rosters (~1700 players)
4. **games** - Game results and scores
5. **team_season_stats** - Team statistics by season
6. **schedules** - Season schedules by week

### Storage Considerations

**Recommended Data to Store:**

✅ **Essential (Priority 1):**
- All teams (small dataset, ~32 records)
- Current season rosters (medium, ~1700 players)
- Current week games (small, ~16 games/week)
- Current season schedule (medium, ~270 games)
- Team season statistics (small, ~32 records)

✅ **Important (Priority 2):**
- Team details with records (updated weekly)
- Game stat leaders (included in games)
- Historical game results (grows over time)

⚠️ **Optional (Priority 3):**
- Depth charts (can be fetched on-demand)
- Historical statistics (multiple seasons)
- Play-by-play data (if needed later)

### Update Frequency

- **Teams/Rosters:** Weekly or after trades
- **Games/Scores:** Live during games, final after completion
- **Schedules:** Once per season (pre-season)
- **Team Stats:** Weekly after games complete
- **Team Details:** Weekly for updated records

---

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install and Start MongoDB
```bash
# Windows (if using MongoDB Community Edition)
# Download from: https://www.mongodb.com/try/download/community
# Default installation runs MongoDB on localhost:27017
```

### 3. Configure Database
Edit `nfl_game_center/settings.py` if needed:
```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'nfl_game_center',
        'CLIENT': {
            'host': 'localhost',
            'port': 27017,
        }
    }
}
```

### 4. Create Collections (Run Migrations)
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Load Initial Data
```bash
python app/data_loader.py
```

---

## ESPN API Endpoints Reference

| Endpoint | Purpose | Update Frequency |
|----------|---------|------------------|
| `/teams` | All NFL teams | Rarely (roster changes) |
| `/teams/{id}` | Team details & records | Weekly |
| `/teams/{id}/roster` | Team rosters | Weekly |
| `/scoreboard?dates={date}` | Games & scores | Live/Final |
| `/schedule?year={y}&week={w}` | Season schedule | Pre-season |
| `/statistics` | Team statistics | Weekly |

---

## Best Practices

### 1. Rate Limiting
- Add delays between bulk requests to avoid overwhelming the API
- Cache frequently accessed data

### 2. Error Handling
- All API methods return `None` or empty lists on failure
- Check return values before processing

### 3. Data Updates
- Update live games every 30-60 seconds during games
- Update team stats/records weekly (Tuesday after Monday Night Football)
- Refresh rosters weekly during season

### 4. Querying Data
```python
from app.models import Team, Player, Game

# Get all teams
teams = Team.objects.all()

# Get players for a team
packers_players = Player.objects.filter(team_id=9)

# Get games for a specific week
week_10_games = Game.objects.filter(season=2024, week=10)

# Get completed games
completed = Game.objects.filter(status__completed=True)
```

---

## Data Filtering Decisions

### What We Store
✅ Team names, logos, colors, venues  
✅ Player names, positions, jerseys, photos  
✅ Game scores (final and by quarter)  
✅ Game status, dates, times, venues  
✅ Broadcast networks  
✅ Top stat leaders per game  
✅ Team season statistics with rankings  

### What We Don't Store
❌ Play-by-play details  
❌ Individual player game logs (can add later)  
❌ Betting odds (available but not essential)  
❌ Detailed venue information (capacity, location sufficient)  
❌ Full game narratives/recaps  
❌ Team/player social media links  

This keeps the database lean while maintaining all information needed for a sports center application focused on scores, standings, schedules, and key statistics.

---

## Future Enhancements

1. **Real-time Updates:** WebSocket integration for live score updates
2. **Player Stats:** Individual player game logs and career statistics
3. **Advanced Analytics:** Drive summaries, efficiency metrics
4. **Historical Data:** Multiple seasons for trending analysis
5. **Depth Charts:** Position-by-position depth information
6. **Injuries:** Player injury reports and status

---

## Support

For ESPN API documentation and data structures, examine the actual API responses:
- Teams: https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams
- Scoreboard: https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard

For Django/Djongo documentation:
- Django: https://docs.djangoproject.com/
- Djongo: https://www.djongomapper.com/
