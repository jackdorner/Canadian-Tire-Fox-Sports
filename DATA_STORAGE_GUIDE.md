# NFL Data Storage Recommendations

## Quick Reference: What Data to Store

Based on ESPN API analysis, here's what you should store for an NFL Fox Sports-like application.

---

## 📊 Priority 1: Essential Data (Must Have)

### Teams Collection (~32 records)
```json
{
  "team_id": 9,
  "abbreviation": "GB",
  "display_name": "Green Bay Packers",
  "logo_url": "https://...",
  "color": "203731",
  "venue": {
    "name": "Lambeau Field",
    "city": "Green Bay",
    "state": "Wisconsin"
  }
}
```
**Why:** Foundation for all other data. Small dataset, rarely changes.

---

### Players Collection (~1,700 records)
```json
{
  "player_id": 12345,
  "display_name": "Aaron Rodgers",
  "jersey": "8",
  "team_id": 20,
  "position": {
    "abbreviation": "QB",
    "name": "Quarterback"
  },
  "headshot_url": "https://...",
  "height": "6'2\"",
  "weight": "225 lbs",
  "college": "California"
}
```
**Why:** Core content for roster pages, player profiles, stat leaders.

---

### Games Collection (~270 games/season)
```json
{
  "game_id": "401547417",
  "date": "2024-11-03T17:00Z",
  "week": 9,
  "season": 2024,
  "home_team": {
    "team_id": 9,
    "abbreviation": "GB",
    "display_name": "Green Bay Packers",
    "score": 24,
    "linescores": [7, 3, 7, 7]
  },
  "away_team": {
    "team_id": 8,
    "abbreviation": "DET",
    "display_name": "Detroit Lions",
    "score": 14,
    "linescores": [0, 7, 7, 0]
  },
  "status": {
    "completed": true,
    "description": "Final"
  },
  "broadcasts": ["FOX"],
  "stat_leaders": {
    "passing": [...],
    "rushing": [...],
    "receiving": [...]
  }
}
```
**Why:** Core feature - live scores, game results, weekly schedules. Includes stat leaders for quick access.

---

## 📈 Priority 2: Important Data (Should Have)

### Team Details Collection (~32 records)
```json
{
  "team_id": 9,
  "record_summary": "7-2",
  "standing_summary": "1st in NFC North",
  "record": {
    "overall": {
      "wins": 7,
      "losses": 2,
      "ties": 0,
      "win_percent": 0.778
    },
    "home": {"wins": 4, "losses": 1},
    "road": {"wins": 3, "losses": 1}
  },
  "next_game": {
    "id": "401547420",
    "name": "Packers vs Bears",
    "date": "2024-11-10T13:00Z"
  }
}
```
**Why:** Current standings, win-loss records, next game info for team pages.

---

### Team Season Stats Collection (~32 records/season)
```json
{
  "team_id": 9,
  "season": 2024,
  "key_stats": {
    "offensive": {
      "passing_yards": {
        "value": 2845,
        "display_value": "2,845",
        "rank": 5,
        "per_game_value": 316.1
      },
      "rushing_yards": {...},
      "total_yards": {...}
    },
    "defensive": {
      "points_allowed": {...},
      "sacks": {...}
    }
  }
}
```
**Why:** Team performance metrics, rankings, offensive/defensive stats for comparison.

---

### Schedule Collection (~18 records/season)
```json
{
  "year": 2024,
  "week": 10,
  "calendar": [...],
  "games": [
    {
      "game_id": "401547420",
      "date": "2024-11-10T13:00Z",
      "home_team": {...},
      "away_team": {...},
      "broadcasts": ["CBS"]
    }
  ]
}
```
**Why:** Weekly schedule view, TV listings, upcoming games.

---

## ⚡ Priority 3: Optional Data (Nice to Have)

### Depth Charts
- Position-by-position depth (1st string, 2nd string, etc.)
- **When to add:** If building detailed roster/lineup features
- **Frequency:** Weekly updates

### Play-by-Play Data
- Individual plays, drive summaries
- **When to add:** For advanced game analysis features
- **Storage:** Large dataset, consider on-demand fetching

### Historical Seasons
- Multiple years of data
- **When to add:** For trends, records, historical comparison
- **Storage:** Grows significantly with each season

### Player Game Logs
- Individual player statistics per game
- **When to add:** For detailed player stat pages
- **API:** Separate endpoint needed

---

## 💾 Storage Size Estimates

| Collection | Records | Size (est.) | Update Frequency |
|------------|---------|-------------|------------------|
| Teams | 32 | ~100 KB | Rarely |
| Players | ~1,700 | ~5 MB | Weekly |
| Games (1 season) | ~270 | ~20 MB | Live during games |
| Team Details | 32 | ~50 KB | Weekly |
| Team Stats | 32 | ~500 KB | Weekly |
| Schedule | 18 | ~2 MB | Pre-season |
| **TOTAL** | | **~28 MB/season** | |

**Note:** Includes rich data (stat leaders, linescores, etc.). Very manageable for MongoDB.

---

## 🔄 Update Schedule Recommendations

### Live (During Games)
- **Games collection:** Score updates every 30-60 seconds
- **Stat leaders:** Updated with scores

### Daily
- **Games collection:** Finalize scores/stats after games complete

### Weekly (Tuesday after MNF)
- **Team Details:** Updated records and standings
- **Team Stats:** Season statistics and rankings
- **Players:** Roster changes (injuries, trades, practice squad)

### Seasonally
- **Teams:** New team info (rare)
- **Schedule:** Pre-season schedule release

### One-time
- **Initial load:** All teams, current rosters, season schedule

---

## 🎯 Data Filtering Strategy

### From ESPN Teams Endpoint
**Keep:**
- Team ID, abbreviation, display names
- Logo URL (500px version)
- Primary/alternate colors
- Venue name and location

**Skip:**
- Detailed venue capacity/dimensions
- Social media links
- Alternative logo sizes
- Team ownership info

### From ESPN Scoreboard Endpoint
**Keep:**
- Game ID, date, week, teams
- Final scores + quarter scores
- Game status (completed/live/scheduled)
- Venue, broadcast network
- Top 3 stat leaders (QB, RB, WR)

**Skip:**
- Betting odds/lines
- Game recap text
- Full play sequences
- Weather conditions
- Referee information

### From ESPN Roster Endpoint
**Keep:**
- Player ID, name, jersey
- Position (abbreviation)
- Headshot photo
- Height, weight, age, experience
- College

**Skip:**
- Player birthplace details
- Contract information
- Social media handles
- Detailed injury history

### From ESPN Stats Endpoint
**Keep:**
- Key offensive stats (pass/rush/receive yards, TDs)
- Key defensive stats (tackles, sacks, INTs)
- Special teams (FG%, punt avg)
- Rankings for each stat

**Skip:**
- Extremely granular stats (3rd down left hash at night, etc.)
- Historical comparisons (provided by ESPN)
- Advanced metrics you won't display

---

## 🏗️ Building Your Application

### Phase 1: Foundation
1. Set up Teams, Players, Games collections
2. Load current season data
3. Build basic views: teams list, scores, schedule

### Phase 2: Enhancement
1. Add Team Details and Stats
2. Build standings page
3. Add stat leaders and rankings

### Phase 3: Advanced
1. Real-time score updates
2. Player profile pages
3. Historical data and trends

### Phase 4: Polish
1. Depth charts
2. Advanced analytics
3. Notifications and alerts

---

## 🔍 Query Examples

### Most Common Queries

```python
# Get current week games
Game.objects.filter(season=2024, week=10).order_by('date')

# Get team roster
Player.objects.filter(team_id=9).order_by('position', 'jersey')

# Get standings (all team details)
TeamDetails.objects.all().order_by('-record__overall__win_percent')

# Get live games
Game.objects.filter(status__completed=False, date__gte=today)

# Get team upcoming games
Game.objects.filter(
    Q(home_team__team_id=9) | Q(away_team__team_id=9),
    date__gte=now
).order_by('date')[:5]

# Get stat leaders for a game
game = Game.objects.get(game_id='401547417')
passing_leaders = game.stat_leaders['passing']
```

---

## 💡 Tips for Success

1. **Start Small:** Load one team's data first, verify it looks good, then scale to all teams

2. **Use Indexes:** Add indexes on frequently queried fields (team_id, date, week, season)

3. **Cache Aggressively:** Team info, rosters change infrequently - cache them

4. **Batch Updates:** Update all team stats together, not individually

5. **Monitor API:** Be respectful of ESPN's API - add delays between requests

6. **Validate Data:** Check for None/null values before storing

7. **Keep It Simple:** Start with core features, add complexity later

---

## ✅ Recommended Storage Checklist

For an MVP Fox Sports-like NFL app, store:

- [x] All 32 teams with logos, colors, venues
- [x] Current season rosters (all players)
- [x] Current week games with scores
- [x] Season schedule (all weeks)
- [x] Team records and standings
- [x] Team season statistics
- [x] Game stat leaders (passing, rushing, receiving)
- [ ] Player individual stats (add later if needed)
- [ ] Historical seasons (add later if needed)
- [ ] Depth charts (add later if needed)

**Result:** Comprehensive NFL app with ~28MB of data, updated weekly + live scores.

---

## 🚀 Quick Start

```python
from app.data_loader import NFLDataLoader

# One command to load everything essential
loader = NFLDataLoader()
loader.load_initial_data()
```

This loads teams, rosters, games, schedule, and stats - everything needed for your application!
