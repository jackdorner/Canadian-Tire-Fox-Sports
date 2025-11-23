from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.conf import settings
from pymongo import MongoClient
from datetime import datetime
from django.shortcuts import render


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

