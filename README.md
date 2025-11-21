# NFL Game Center - Fox Sports Clone

A Django-based NFL sports application similar to Fox Sports, using MongoDB for data storage and ESPN's NFL API for live data.

## 🎯 Project Overview

This application provides:
- Live NFL scores and game results
- Team information, rosters, and statistics
- Season schedules and standings
- Player profiles and stat leaders
- Real-time game updates

## 📁 Project Structure

```
Canadian-Tire-Fox-Sports/
├── app/
│   ├── nfl_api_client.py      # ESPN API client with data filtering
│   ├── data_loader.py          # Batch data loading utility
│   ├── NFLEndpoints.py         # API endpoints and team IDs
│   ├── models.py               # MongoDB/Djongo models
│   ├── views.py                # Django views
│   └── admin.py                # Django admin config
├── nfl_game_center/
│   ├── settings.py             # Django settings (MongoDB config)
│   ├── urls.py                 # URL routing
│   └── wsgi.py                 # WSGI config
├── templates/                  # HTML templates
├── static/                     # CSS, JS, images
├── demo_api_client.py         # API demonstration script
├── requirements.txt            # Python dependencies
├── NFL_API_CLIENT_GUIDE.md    # Comprehensive API documentation
└── DATA_STORAGE_GUIDE.md      # Data storage recommendations
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and Start MongoDB

Download MongoDB Community Edition from [mongodb.com](https://www.mongodb.com/try/download/community)

Or use MongoDB Atlas (cloud):
- Create free account at [mongodb.com/atlas](https://www.mongodb.com/atlas)
- Get connection string
- Update `settings.py` with your connection string

### 3. Configure Database

MongoDB is already configured in `nfl_game_center/settings.py`:

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

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Load NFL Data

```bash
# Demo the API client (see what data looks like)
python demo_api_client.py

# Load all initial data into MongoDB
python app/data_loader.py
```

### 6. Start Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000`

## 📊 Data Models

### Core Collections

- **Teams** (32 records) - Team info, logos, colors, venues
- **Players** (~1,700 records) - Rosters with positions, photos, stats
- **Games** (~270/season) - Scores, schedules, stat leaders
- **TeamDetails** (32 records) - Current records, standings
- **TeamSeasonStats** (32/season) - Offensive/defensive statistics
- **Schedule** (18/season) - Weekly schedule with TV info

## 🔧 API Client Usage

### Fetch Teams

```python
from app.nfl_api_client import NFLAPIClient

client = NFLAPIClient()
teams = client.fetch_all_teams()
```

### Fetch Roster

```python
from app.NFLEndpoints import NFLTeam

roster = client.fetch_team_roster(NFLTeam.PACKERS.value)
```

### Fetch Live Scores

```python
# Get games for a specific date (YYYYMMDD format)
games = client.fetch_scoreboard('20241103')
```

### Fetch Team Stats

```python
stats = client.fetch_team_stats(NFLTeam.CHIEFS.value, 2024)
```

See **NFL_API_CLIENT_GUIDE.md** for complete documentation.

## 📚 Documentation

- **[NFL_API_CLIENT_GUIDE.md](NFL_API_CLIENT_GUIDE.md)** - Complete API client documentation with examples
- **[DATA_STORAGE_GUIDE.md](DATA_STORAGE_GUIDE.md)** - Data storage recommendations and best practices

## 🎨 Features to Implement

### Phase 1 (MVP)
- [x] API client with data filtering
- [x] MongoDB models and storage
- [x] Data loading utilities
- [ ] Home page with current week games
- [ ] Team listing page
- [ ] Live scoreboard view
- [ ] Schedule view

### Phase 2 (Enhanced)
- [ ] Team detail pages with rosters
- [ ] Player profile pages
- [ ] Standings table
- [ ] Team statistics pages
- [ ] Search functionality

### Phase 3 (Advanced)
- [ ] Real-time score updates (WebSocket)
- [ ] Game detail pages with play-by-play
- [ ] Historical data and trends
- [ ] User favorites and notifications
- [ ] Mobile responsive design

## 🏗️ Tech Stack

- **Backend:** Django 5.2.5
- **Database:** MongoDB (via Djongo)
- **Data Source:** ESPN NFL API
- **Frontend:** HTML, CSS, JavaScript (templates provided)

## 📦 Dependencies

```
Django==5.2.5
requests==2.31.0
pymongo==4.6.1
djongo==1.3.6
sqlparse==0.2.4
```

## 🔑 Key Features of the API Client

### Data Filtering
The API client automatically filters ESPN's verbose responses to extract only essential data:

✅ **Teams:** Names, logos, colors, venues  
✅ **Players:** Names, positions, jerseys, photos, physical stats  
✅ **Games:** Scores, quarter-by-quarter, status, venues, broadcasts  
✅ **Stats:** Key offensive/defensive/special teams metrics with rankings  

❌ **Excluded:** Betting odds, detailed play-by-play, social links, excessive metadata

### Storage Optimization
- ~28 MB per season of filtered data
- Efficient JSON storage in MongoDB
- Indexed fields for fast queries

## 🔄 Data Update Strategy

| Data Type | Frequency | Method |
|-----------|-----------|--------|
| Teams | Rarely | Manual update |
| Rosters | Weekly | `load_all_rosters()` |
| Games (Live) | 30-60 sec | `load_scoreboard(date)` |
| Games (Final) | Daily | `load_scoreboard(date)` |
| Schedule | Pre-season | `load_season_schedule()` |
| Team Stats | Weekly | `load_all_team_stats()` |
| Standings | Weekly | `load_all_team_details()` |

## 🎯 ESPN API Endpoints Used

1. **Teams** - `/teams` - All NFL teams
2. **Team Details** - `/teams/{id}` - Records and standings
3. **Roster** - `/teams/{id}/roster` - Player rosters
4. **Scoreboard** - `/scoreboard?dates={date}` - Live scores
5. **Schedule** - `/schedule?year={y}&week={w}` - Season schedule
6. **Team Stats** - `/statistics` - Season statistics

## 🧪 Testing the API Client

Run the demo script to see live API responses:

```bash
python demo_api_client.py
```

This will:
- Fetch and display sample data from each endpoint
- Show the structure of filtered data
- Demonstrate all API client methods
- Help you understand what data is available

## 💡 Development Tips

1. **Start with Demo:** Run `demo_api_client.py` first to see data structures
2. **Load Incrementally:** Test with one team before loading all 32
3. **Monitor API Calls:** ESPN APIs are free but don't abuse them
4. **Use Indexes:** Add database indexes for frequently queried fields
5. **Cache Data:** Store API responses; don't refetch unnecessarily

## 🐛 Troubleshooting

### MongoDB Connection Error
```
Check MongoDB is running: mongod --version
Update connection string in settings.py
```

### API Request Failures
```
Check internet connection
Verify ESPN API endpoints are accessible
Add delays between bulk requests
```

### Import Errors
```
Ensure all dependencies installed: pip install -r requirements.txt
Check Python version: 3.8+ required
```

## 📖 Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Djongo Documentation](https://www.djongomapper.com/)
- [ESPN API Guide](https://gist.github.com/nntrn/ee26cb2a0716de0947a0a4e9a157bc1c)

## 🤝 Contributing

This is a class project. Contributions and suggestions welcome!

## 📝 License

Educational project - use as needed for learning purposes.

## 🏈 About

Built for Database course at Milwaukee School of Engineering.  
An NFL-focused sports center application demonstrating:
- RESTful API consumption
- NoSQL database design
- Real-time data handling
- Django web framework

---

**Ready to get started?** Run `python demo_api_client.py` to see the API in action!
