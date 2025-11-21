# Setup Checklist

Complete guide to get your NFL Game Center application running.

## ✅ Step-by-Step Setup

### 1. Prerequisites
- [ ] Python 3.8+ installed
- [ ] pip package manager available
- [ ] Git installed (optional, for version control)
- [ ] MongoDB installed OR MongoDB Atlas account

---

### 2. Install Python Dependencies

```bash
# Navigate to project directory
cd Canadian-Tire-Fox-Sports

# Install required packages
pip install -r requirements.txt
```

**Expected packages:**
- Django 5.2.5
- requests 2.31.0
- pymongo 4.6.1
- djongo 1.3.6
- sqlparse 0.2.4

**Troubleshooting:**
- If djongo fails: Try `pip install djongo==1.3.6 sqlparse==0.2.4`
- If errors persist: Consider using pymongo directly (see alternative setup below)

---

### 3. Setup MongoDB

#### Option A: Local MongoDB Installation

**Windows:**
1. Download: https://www.mongodb.com/try/download/community
2. Run installer (use default settings)
3. MongoDB runs automatically on `localhost:27017`
4. Verify: Open PowerShell and run `mongod --version`

**Mac:**
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongodb
```

#### Option B: MongoDB Atlas (Cloud)

1. Go to https://www.mongodb.com/atlas
2. Sign up for free account
3. Create a free cluster
4. Get connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)
5. Update `nfl_game_center/settings.py`:
   ```python
   'CLIENT': {
       'host': 'your-connection-string-here'
   }
   ```

---

### 4. Verify MongoDB Connection

**Check if MongoDB is running:**

```bash
# Windows PowerShell
Get-Process mongod

# Mac/Linux
ps aux | grep mongod
```

**Test connection with Python:**

```bash
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017/'); print('Connected:', client.server_info())"
```

---

### 5. Configure Django Settings

The settings are already configured in `nfl_game_center/settings.py`, but verify:

```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'nfl_game_center',
        'CLIENT': {
            'host': 'localhost',  # or your MongoDB Atlas connection string
            'port': 27017,
        }
    }
}
```

Make sure `'app'` is in `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    'app',
]
```

---

### 6. Run Django Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

**Note:** Djongo may show warnings - these are often safe to ignore for MongoDB.

**If migration fails:**
- Djongo can be finicky. Consider using raw pymongo (see alternative below)
- Or skip migrations and let MongoDB create collections automatically

---

### 7. Test the API Client

Before loading data, test the API client:

```bash
python demo_api_client.py
```

This will:
- Fetch sample data from ESPN APIs
- Display formatted output
- Show you what data looks like
- Verify your internet connection and API access

**Expected output:**
```
==================================================================
  DEMO: Fetching All NFL Teams
==================================================================

Found 32 NFL teams

1. Atlanta Falcons (ATL)
   Logo: https://a.espncdn.com/i/teamlogos/nfl/500/atl.png
   ...
```

Press Enter through each demo section.

---

### 8. Load Initial Data

Once API client works, load data into MongoDB:

```bash
python app/data_loader.py
```

This will:
1. Fetch all 32 NFL teams
2. Get team details and records
3. Load rosters for all teams
4. Get current week games
5. Load 2024 season schedule
6. Fetch team statistics

**Expected duration:** 5-10 minutes (respects API rate limits)

**Progress output:**
```
============================================================
LOADING INITIAL NFL DATA
============================================================

Step 1: Loading teams...
Fetching all teams...
✓ Teams loaded: 32 created, 0 updated

Step 2: Loading team details...
...
```

---

### 9. Verify Data in MongoDB

**Option A: Django Shell**

```bash
python manage.py shell
```

```python
from app.models import Team, Player, Game

# Check teams
print(f"Teams: {Team.objects.count()}")

# Check players
print(f"Players: {Player.objects.count()}")

# Check games
print(f"Games: {Game.objects.count()}")

# Show a team
packers = Team.objects.get(abbreviation='GB')
print(packers.display_name)
```

**Option B: MongoDB Shell**

```bash
mongosh  # or 'mongo' for older versions

use nfl_game_center

db.teams.countDocuments()      # Should be 32
db.players.countDocuments()    # Should be ~1700
db.games.countDocuments()      # Varies by current week

db.teams.findOne()  # View a team document
```

**Option C: MongoDB Compass (GUI)**

1. Download: https://www.mongodb.com/products/compass
2. Connect to `mongodb://localhost:27017`
3. Browse `nfl_game_center` database
4. View collections visually

---

### 10. Create Django Superuser (Optional)

```bash
python manage.py createsuperuser
```

Follow prompts to create admin account.

Access admin at: `http://localhost:8000/admin`

---

### 11. Run Development Server

```bash
python manage.py runserver
```

Visit: `http://localhost:8000`

**Current status:** Basic home page (you'll need to build views)

---

## 🔧 Alternative Setup: Raw PyMongo

If djongo causes issues, use raw pymongo instead:

### Update settings.py:

```python
# Keep Django's default database for admin/auth
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Add MongoDB connection
from pymongo import MongoClient
MONGO_CLIENT = MongoClient('mongodb://localhost:27017/')
MONGO_DB = MONGO_CLIENT['nfl_game_center']
```

### Update data_loader.py:

```python
from nfl_game_center.settings import MONGO_DB

# Instead of:
Team.objects.update_or_create(...)

# Use:
MONGO_DB.teams.update_one(
    {'team_id': team_data['team_id']},
    {'$set': team_data},
    upsert=True
)
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'djongo'"
**Solution:**
```bash
pip install djongo==1.3.6 sqlparse==0.2.4
```

### Issue: MongoDB connection refused
**Solution:**
- Check MongoDB is running: `mongod --version`
- Start MongoDB service:
  - Windows: Services → MongoDB → Start
  - Mac: `brew services start mongodb-community`
  - Linux: `sudo systemctl start mongodb`

### Issue: API requests failing
**Solution:**
- Check internet connection
- Verify ESPN URLs in browser
- Add delays between requests
- Some endpoints may be temporarily down - try later

### Issue: Djongo migration errors
**Solution:**
- Use raw pymongo approach (see alternative setup)
- Or skip migrations: MongoDB creates collections automatically
- Collections will be created when you first insert data

### Issue: Data loader script hangs
**Solution:**
- Normal - loading all data takes 5-10 minutes
- Check progress messages
- Can interrupt (Ctrl+C) and resume later
- Load data incrementally:
  ```python
  loader = NFLDataLoader()
  loader.load_all_teams()  # Just teams first
  ```

---

## 📋 Post-Setup Tasks

Once setup is complete:

### 1. Schedule Data Updates

Create a task/cron job to update data:

**Daily (during season):**
```bash
# Update current week scores
python -c "from app.data_loader import NFLDataLoader; NFLDataLoader().load_current_week_games()"
```

**Weekly (Tuesday after games):**
```bash
# Update standings and stats
python -c "from app.data_loader import NFLDataLoader; loader = NFLDataLoader(); loader.load_all_team_details(); loader.load_all_team_stats(2024)"
```

### 2. Build Django Views

Start creating views in `app/views.py`:

```python
from django.shortcuts import render
from app.models import Team, Game, TeamDetails
from datetime import datetime

def home(request):
    # Get current week games
    games = Game.objects.filter(season=2024, week=10).order_by('date')
    return render(request, 'home.html', {'games': games})

def teams_list(request):
    teams = Team.objects.all().order_by('display_name')
    return render(request, 'teams.html', {'teams': teams})

def scoreboard(request):
    today = datetime.now().strftime('%Y%m%d')
    games = Game.objects.filter(date__startswith=today[:8])
    return render(request, 'scoreboard.html', {'games': games})
```

### 3. Create Templates

Build HTML templates in `templates/`:
- `home.html` - Homepage with featured games
- `teams.html` - All teams listing
- `team_detail.html` - Team page with roster
- `scoreboard.html` - Live scores
- `schedule.html` - Weekly schedule
- `standings.html` - Standings table

### 4. Add Static Assets

Enhance `static/css/styles.css` with:
- Team color schemes
- Responsive design
- Score displays
- Stat tables

---

## ✨ Quick Commands Reference

```bash
# Start MongoDB
mongod  # or: brew services start mongodb-community

# Start Django server
python manage.py runserver

# Django shell
python manage.py shell

# Load data
python app/data_loader.py

# Demo API
python demo_api_client.py

# Update migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

---

## 📚 Next Steps

1. **Review Documentation:**
   - [ ] Read `NFL_API_CLIENT_GUIDE.md`
   - [ ] Review `DATA_STORAGE_GUIDE.md`
   - [ ] Check `DATA_STRUCTURE_REFERENCE.md`

2. **Explore Data:**
   - [ ] Run demo script
   - [ ] Browse MongoDB collections
   - [ ] Test queries in Django shell

3. **Build Features:**
   - [ ] Create homepage view
   - [ ] Add scoreboard page
   - [ ] Build team listing
   - [ ] Design templates

4. **Enhance:**
   - [ ] Add real-time updates
   - [ ] Implement search
   - [ ] Create player pages
   - [ ] Add favorites/bookmarks

---

## 🎉 Success Criteria

Your setup is complete when:

✅ MongoDB is running  
✅ Python dependencies installed  
✅ Django server starts without errors  
✅ Data loaded successfully (32 teams, ~1700 players)  
✅ Can query data in Django shell  
✅ Home page displays at localhost:8000  

---

## 🆘 Need Help?

- **Django Issues:** https://docs.djangoproject.com/
- **MongoDB Issues:** https://docs.mongodb.com/
- **API Issues:** Check ESPN API status, try different endpoints
- **Python Issues:** Verify Python 3.8+, check virtualenv

**Common gotcha:** Make sure you're in the project directory when running commands!

---

**Ready to build your NFL Game Center? Start with Step 1! 🏈**
