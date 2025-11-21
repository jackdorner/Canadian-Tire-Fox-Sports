# Quick Reference Card

## 🏈 NFL Game Center - Essential Commands & Info

---

## 🚀 Getting Started (First Time)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start MongoDB (choose one)
mongod                                    # Windows/Linux
brew services start mongodb-community     # Mac

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Test API client
python demo_api_client.py

# 5. Load all data (takes 5-10 min)
python app/data_loader.py

# 6. Start server
python manage.py runserver
```

---

## 📊 Data Collections

| Collection | Count | What It Stores |
|------------|-------|----------------|
| **teams** | 32 | Team info, logos, colors, venues |
| **players** | ~1,700 | Roster with positions & photos |
| **games** | ~270/season | Scores, schedules, stat leaders |
| **team_details** | 32 | Records, standings, next game |
| **team_season_stats** | 32/season | Offensive/defensive statistics |
| **schedules** | 18/season | Weekly schedules with TV info |

**Total Size:** ~28 MB per season

---

## 🔧 Common Commands

### Django Management

```bash
python manage.py runserver              # Start dev server
python manage.py shell                  # Django shell
python manage.py createsuperuser        # Create admin
python manage.py makemigrations         # Create migrations
python manage.py migrate                # Apply migrations
```

### Data Loading

```python
from app.data_loader import NFLDataLoader
loader = NFLDataLoader()

# Load everything
loader.load_initial_data()

# Or load specific data
loader.load_all_teams()
loader.load_team_roster(9)              # Packers
loader.load_scoreboard('20241103')      # Specific date
loader.load_schedule(2024, 10)          # Week 10
loader.load_team_stats(9, 2024)         # Packers 2024
```

### API Client

```python
from app.nfl_api_client import NFLAPIClient
from app.NFLEndpoints import NFLTeam

client = NFLAPIClient()

teams = client.fetch_all_teams()
details = client.fetch_team_details(NFLTeam.PACKERS.value)
roster = client.fetch_team_roster(NFLTeam.CHIEFS.value)
games = client.fetch_scoreboard('20241103')
schedule = client.fetch_schedule(2024, 10)
stats = client.fetch_team_stats(NFLTeam.BILLS.value, 2024)
```

---

## 🔍 Common Queries

### Django ORM (if using Djongo)

```python
from app.models import Team, Player, Game, TeamDetails

# Get all teams
Team.objects.all()

# Get specific team
Team.objects.get(team_id=9)
Team.objects.get(abbreviation='GB')

# Get team roster
Player.objects.filter(team_id=9)

# Get QBs only
Player.objects.filter(position__abbreviation='QB')

# Get current week games
Game.objects.filter(season=2024, week=10).order_by('date')

# Get completed games
Game.objects.filter(status__completed=True)

# Get standings
TeamDetails.objects.all().order_by('-record__overall__win_percent')

# Get team's games (home or away)
from django.db.models import Q
Game.objects.filter(
    Q(home_team__team_id=9) | Q(away_team__team_id=9)
).order_by('-date')
```

### Raw PyMongo

```python
from nfl_game_center.settings import MONGO_DB

# Get all teams
MONGO_DB.teams.find()

# Get specific team
MONGO_DB.teams.find_one({'team_id': 9})

# Get team roster
MONGO_DB.players.find({'team_id': 9})

# Get current week games
MONGO_DB.games.find({'season': 2024, 'week': 10})

# Get standings (sorted by wins)
MONGO_DB.team_details.find().sort('record.overall.wins', -1)
```

---

## 📁 File Structure

```
Canadian-Tire-Fox-Sports/
├── app/
│   ├── nfl_api_client.py          # API client with filtering
│   ├── data_loader.py              # Batch data loading
│   ├── NFLEndpoints.py             # API endpoints & team IDs
│   ├── models.py                   # MongoDB models
│   ├── views.py                    # Django views
│   └── admin.py                    # Admin configuration
├── nfl_game_center/
│   ├── settings.py                 # Django settings
│   ├── urls.py                     # URL routing
│   └── wsgi.py                     # WSGI config
├── templates/                      # HTML templates
├── static/                         # CSS, JS, images
├── demo_api_client.py             # API demo script
├── requirements.txt                # Dependencies
├── README.md                       # Main documentation
├── NFL_API_CLIENT_GUIDE.md        # API documentation
├── DATA_STORAGE_GUIDE.md          # Storage recommendations
├── DATA_STRUCTURE_REFERENCE.md    # Data structure details
└── SETUP_CHECKLIST.md             # Setup instructions
```

---

## 🏈 NFL Team IDs (Quick Reference)

```python
from app.NFLEndpoints import NFLTeam

NFLTeam.PACKERS.value      # 9
NFLTeam.CHIEFS.value       # 12
NFLTeam.BILLS.value        # 2
NFLTeam.COWBOYS.value      # 6
NFLTeam.PATRIOTS.value     # 17
NFLTeam.EAGLES.value       # 21
NFLTeam.STEELERS.value     # 23
NFLTeam.NINERS.value       # 25 (49ers)
NFLTeam.RAVENS.value       # 33
```

**See `app/NFLEndpoints.py` for all 32 teams**

---

## 🌐 API Endpoints

| Endpoint | URL Pattern | Returns |
|----------|-------------|---------|
| **Teams** | `/teams` | All 32 teams |
| **Team** | `/teams/{id}` | Team details & record |
| **Roster** | `/teams/{id}/roster` | Team roster |
| **Scoreboard** | `/scoreboard?dates={YYYYMMDD}` | Games for date |
| **Schedule** | `/schedule?year={Y}&week={W}` | Week schedule |
| **Stats** | `/statistics` | Team statistics |

**Base URL:** `https://site.api.espn.com/apis/site/v2/sports/football/nfl`

---

## 📋 Update Schedule

| Data | Frequency | When |
|------|-----------|------|
| **Scores (live)** | 30-60 sec | During games |
| **Scores (final)** | Daily | After games end |
| **Rosters** | Weekly | Wednesday |
| **Standings** | Weekly | Tuesday (after MNF) |
| **Team Stats** | Weekly | Tuesday |
| **Schedule** | Once | Pre-season |

---

## 🐛 Quick Troubleshooting

### MongoDB not starting?
```bash
# Check if running
mongod --version

# Start service
# Windows: Services → MongoDB → Start
# Mac: brew services start mongodb-community
# Linux: sudo systemctl start mongodb
```

### Import errors?
```bash
pip install -r requirements.txt
pip install djongo==1.3.6 sqlparse==0.2.4
```

### API failing?
- Check internet connection
- Try in browser first
- Add delays between requests
- ESPN may have rate limits

### Djongo issues?
- Use raw pymongo instead (see docs)
- Or keep SQLite for Django, use pymongo for NFL data

---

## 🎯 Next Steps

### Phase 1: Foundation ✓
- [x] API client created
- [x] Models defined
- [x] Data loader built
- [ ] Load initial data
- [ ] Create basic views

### Phase 2: Core Features
- [ ] Homepage with scores
- [ ] Team listing page
- [ ] Scoreboard view
- [ ] Schedule view
- [ ] Standings table

### Phase 3: Enhanced
- [ ] Team detail pages
- [ ] Player profiles
- [ ] Search functionality
- [ ] Real-time updates

---

## 📚 Documentation Links

- **Main README:** `README.md`
- **API Guide:** `NFL_API_CLIENT_GUIDE.md`
- **Storage Guide:** `DATA_STORAGE_GUIDE.md`
- **Data Reference:** `DATA_STRUCTURE_REFERENCE.md`
- **Setup Guide:** `SETUP_CHECKLIST.md`

---

## 💡 Pro Tips

1. **Test incrementally:** Load one team before loading all 32
2. **Use demo script:** Run `demo_api_client.py` to see data first
3. **Monitor API:** Don't spam requests, add delays
4. **Cache data:** Store responses, don't refetch unnecessarily
5. **Index queries:** Add database indexes on frequently queried fields
6. **Handle errors:** Check for None/null before using data

---

## 🆘 Getting Help

- **Django:** https://docs.djangoproject.com/
- **MongoDB:** https://docs.mongodb.com/
- **Djongo:** https://www.djongomapper.com/
- **ESPN API:** Test endpoints in browser

---

## ✅ Health Check

Run this to verify everything works:

```python
# In Django shell (python manage.py shell)
from app.models import Team, Player, Game
from app.nfl_api_client import NFLAPIClient

# Check data
print(f"Teams: {Team.objects.count()}")       # Should be 32
print(f"Players: {Player.objects.count()}")   # Should be ~1700
print(f"Games: {Game.objects.count()}")       # Varies

# Test API
client = NFLAPIClient()
teams = client.fetch_all_teams()
print(f"API working: {len(teams) == 32}")     # Should be True
```

**All good?** Start building your views! 🎉

---

**Print this card or keep it open while developing!**
