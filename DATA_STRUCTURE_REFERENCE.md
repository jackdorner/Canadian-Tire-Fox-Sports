# NFL Data Collection Summary

## What Data Gets Stored in MongoDB

This document provides a quick visual reference of exactly what data your application stores from the ESPN NFL API.

---

## 🏈 1. TEAMS Collection

**Source:** `NFLEndpoints.TEAMS`  
**Count:** 32 teams  
**Update Frequency:** Rarely (only when teams rebrand)

### Stored Fields:

```
Team {
  team_id: 9
  abbreviation: "GB"
  display_name: "Green Bay Packers"
  short_display_name: "Packers"
  name: "Packers"
  location: "Green Bay"
  
  color: "203731"           # Hex color (primary)
  alternate_color: "FFB612" # Hex color (secondary)
  logo_url: "https://a.espncdn.com/i/teamlogos/nfl/500/gb.png"
  
  venue: {
    name: "Lambeau Field"
    city: "Green Bay"
    state: "Wisconsin"
    capacity: 81441
  }
  
  links: {
    clubhouse: "https://..."
    roster: "https://..."
    stats: "https://..."
  }
}
```

### Example Query:
```python
Team.objects.all()  # Get all teams
Team.objects.get(team_id=9)  # Get Packers
```

---

## 👤 2. PLAYERS Collection

**Source:** `NFLEndpoints.TEAM_ROSTER`  
**Count:** ~1,700 players (53 per team)  
**Update Frequency:** Weekly (roster changes)

### Stored Fields:

```
Player {
  player_id: 12345
  team_id: 9
  
  display_name: "Jordan Love"
  full_name: "Jordan Alexander Love"
  short_name: "J. Love"
  jersey: "10"
  
  position: {
    name: "Quarterback"
    abbreviation: "QB"
    display_name: "Quarterback"
  }
  
  headshot_url: "https://a.espncdn.com/i/headshots/nfl/players/full/12345.png"
  
  age: 25
  height: "6'4\""
  weight: "224 lbs"
  experience: 4          # Years in NFL
  college: "Utah State"
  status: "Active"
}
```

### Example Queries:
```python
Player.objects.filter(team_id=9)  # Packers roster
Player.objects.filter(position__abbreviation='QB')  # All QBs
```

---

## 🏟️ 3. GAMES Collection

**Source:** `NFLEndpoints.SCOREBOARD`  
**Count:** ~270 games per season  
**Update Frequency:** Live during games, final after completion

### Stored Fields:

```
Game {
  game_id: "401547417"
  date: "2024-11-03T17:00:00Z"
  week: 9
  season: 2024
  season_type: 2  # 1=preseason, 2=regular, 3=postseason
  
  name: "Detroit Lions at Green Bay Packers"
  short_name: "DET @ GB"
  
  home_team: {
    team_id: 9
    abbreviation: "GB"
    display_name: "Green Bay Packers"
    logo: "https://..."
    score: 24
    linescores: [7, 3, 7, 7]  # Quarter by quarter
    winner: true
    record: "7-2"
  }
  
  away_team: {
    team_id: 8
    abbreviation: "DET"
    display_name: "Detroit Lions"
    logo: "https://..."
    score: 14
    linescores: [0, 7, 7, 0]
    winner: false
    record: "6-3"
  }
  
  status: {
    completed: true
    description: "Final"
    detail: "Final"
    short_detail: "Final"
    state: "post"
    period: 4
    display_clock: "0:00"
  }
  
  venue: {
    name: "Lambeau Field"
    city: "Green Bay"
    state: "Wisconsin"
  }
  
  broadcasts: ["FOX"]
  
  stat_leaders: {
    passing: [
      {
        player_id: 12345
        player_name: "Jordan Love"
        team_id: 9
        headshot_url: "https://..."
        value: "295 YDS, 3 TD"
        stat: 295
      }
    ],
    rushing: [...],
    receiving: [...]
  }
  
  attendance: 78128
}
```

### Example Queries:
```python
Game.objects.filter(season=2024, week=9)  # Week 9 games
Game.objects.filter(status__completed=True)  # Completed games
Game.objects.filter(date__gte=today)  # Upcoming games
```

---

## 📊 4. TEAM_DETAILS Collection

**Source:** `NFLEndpoints.TEAM` (individual team endpoint)  
**Count:** 32 records  
**Update Frequency:** Weekly (after games)

### Stored Fields:

```
TeamDetails {
  team_id: 9
  display_name: "Green Bay Packers"
  abbreviation: "GB"
  
  record_summary: "7-2"
  standing_summary: "1st in NFC North"
  
  record: {
    overall: {
      wins: 7
      losses: 2
      ties: 0
      win_percent: 0.778
      games_played: 9
    }
    home: {
      wins: 4
      losses: 1
      summary: "4-1"
    }
    road: {
      wins: 3
      losses: 1
      summary: "3-1"
    }
  }
  
  next_game: {
    id: "401547420"
    name: "Chicago Bears at Green Bay Packers"
    short_name: "CHI @ GB"
    date: "2024-11-10T13:00:00Z"
  }
}
```

### Example Queries:
```python
TeamDetails.objects.all().order_by('-record__overall__win_percent')  # Standings
TeamDetails.objects.get(team_id=9)  # Packers details
```

---

## 📈 5. TEAM_SEASON_STATS Collection

**Source:** `NFLEndpoints.TEAM_STATS`  
**Count:** 32 records per season  
**Update Frequency:** Weekly (after games)

### Stored Fields:

```
TeamSeasonStats {
  team_id: 9
  season: 2024
  season_type: 2  # Regular season
  
  key_stats: {
    offensive: {
      passing_yards: {
        value: 2845
        display_value: "2,845"
        rank: 5
        per_game_value: 316.1
        per_game_display_value: "316.1"
      }
      rushing_yards: {
        value: 1230
        display_value: "1,230"
        rank: 12
        per_game_value: 136.7
      }
      passing_tds: {...}
      rushing_tds: {...}
      receiving_yards: {...}
      receiving_tds: {...}
      qb_rating: {...}
    }
    
    defensive: {
      total_tackles: {...}
      sacks: {...}
      interceptions: {...}
    }
    
    special_teams: {
      field_goal_pct: {...}
      extra_point_pct: {...}
      punt_avg: {...}
    }
  }
  
  all_stats: {
    passing: {
      completions: {...}
      attempts: {...}
      completion_pct: {...}
      yards: {...}
      touchdowns: {...}
      interceptions: {...}
      ... (many more detailed stats)
    }
    rushing: {...}
    receiving: {...}
    defensive: {...}
    kicking: {...}
    punting: {...}
  }
}
```

### Example Queries:
```python
TeamSeasonStats.objects.filter(season=2024)  # All 2024 stats
TeamSeasonStats.objects.get(team_id=9, season=2024)  # Packers 2024
```

---

## 📅 6. SCHEDULE Collection

**Source:** `NFLEndpoints.SCHEDULE`  
**Count:** 18 records per season (one per week)  
**Update Frequency:** Pre-season (then rarely)

### Stored Fields:

```
Schedule {
  year: 2024
  week: 10
  
  calendar: [
    {
      label: "Regular Season"
      value: "2"
      start_date: "2024-09-05"
      end_date: "2025-01-05"
      entries: [
        {
          label: "Week 10"
          alternate_label: "10"
          detail: "Nov 10-11"
          value: "10"
          start_date: "2024-11-10"
          end_date: "2024-11-11"
        }
        ... (other weeks)
      ]
    }
  ]
  
  games: [
    {
      game_id: "401547420"
      date: "2024-11-10T13:00:00Z"
      name: "Chicago Bears at Green Bay Packers"
      short_name: "CHI @ GB"
      week: 10
      season_type: 2
      
      home_team: {
        team_id: 9
        abbreviation: "GB"
        display_name: "Green Bay Packers"
        logo: "https://..."
        record: "7-2"
      }
      
      away_team: {
        team_id: 3
        abbreviation: "CHI"
        display_name: "Chicago Bears"
        logo: "https://..."
        record: "4-5"
      }
      
      venue: {
        name: "Lambeau Field"
      }
      
      broadcasts: ["FOX", "FOX Deportes"]
    }
    ... (other games this week)
  ]
}
```

### Example Queries:
```python
Schedule.objects.get(year=2024, week=10)  # Week 10 schedule
Schedule.objects.filter(year=2024)  # All 2024 schedules
```

---

## 📐 Data Size Estimates

| Collection | Records | Avg Size | Total Size |
|------------|---------|----------|------------|
| Teams | 32 | ~3 KB | ~100 KB |
| Players | 1,700 | ~3 KB | ~5 MB |
| Games (1 season) | 270 | ~70 KB | ~20 MB |
| TeamDetails | 32 | ~2 KB | ~64 KB |
| TeamSeasonStats | 32 | ~15 KB | ~500 KB |
| Schedule | 18 | ~100 KB | ~2 MB |
| **TOTAL** | | | **~28 MB** |

**Per Season Storage:** Approximately 28 MB of well-structured, filtered data

---

## 🔄 Data Relationships

```
Team (32)
  ├─> Players (53 per team = 1,700 total)
  ├─> TeamDetails (1:1 relationship)
  ├─> TeamSeasonStats (1 per season)
  └─> Games (home or away)
      └─> Stat Leaders (players)

Schedule (18 weeks)
  └─> Games (references)
```

---

## 🎯 What Makes This Data "Filtered"?

### What We KEEP:
✅ Essential identifiers (IDs, names, abbreviations)  
✅ Visual elements (logos, colors, photos)  
✅ Core stats (scores, yards, TDs, rankings)  
✅ Schedule info (dates, times, TV networks)  
✅ Key game details (status, venue, leaders)  

### What We SKIP:
❌ Betting odds and gambling lines  
❌ Detailed play-by-play narratives  
❌ Social media links and handles  
❌ Marketing content and descriptions  
❌ Redundant or computed fields  
❌ Alternative image sizes (keep one)  
❌ Historical comparison data (ESPN calculates)  

**Result:** Clean, focused data that's perfect for a sports application without the bloat!

---

## 💾 MongoDB Storage Benefits

- **Flexible Schema:** JSON structure allows nested data (teams, positions, stats)
- **Fast Queries:** Indexes on common fields (team_id, date, week)
- **Easy Updates:** Update entire game object with latest scores
- **Natural Fit:** ESPN returns JSON → store JSON → serve JSON to frontend

---

## 🔍 Common Queries You'll Use

```python
# Current week games
Game.objects.filter(season=2024, week=CURRENT_WEEK)

# Team roster with specific position
Player.objects.filter(team_id=9, position__abbreviation='WR')

# Standings (sorted by win percentage)
TeamDetails.objects.all().order_by('-record__overall__win_percent')

# Live games
Game.objects.filter(status__completed=False, date__lte=now)

# Team's recent games
Game.objects.filter(
    Q(home_team__team_id=9) | Q(away_team__team_id=9),
    status__completed=True
).order_by('-date')[:5]

# Top passing teams
TeamSeasonStats.objects.filter(season=2024).order_by(
    'key_stats__offensive__passing_yards__rank'
)
```

---

## 🚀 Next Steps

1. **Explore the data:** Run `python demo_api_client.py`
2. **Load the database:** Run `python app/data_loader.py`
3. **Query in Django shell:**
   ```bash
   python manage.py shell
   >>> from app.models import *
   >>> Team.objects.all()
   ```
4. **Build views:** Create Django views to display this data
5. **Create templates:** Design HTML pages to show scores, rosters, etc.

---

**Remember:** This filtered data gives you everything needed for an NFL sports app without unnecessary bloat. Each collection is optimized for the queries you'll actually run!
