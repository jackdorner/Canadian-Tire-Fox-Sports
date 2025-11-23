# Example: Enum for NFL team endpoints
from enum import Enum


class NFLTeam(Enum):
    BEARS = 3
    BENGALS = 4
    BILLS = 2
    BRONCOS = 7
    BROWNS = 5
    BUCCANEERS = 27
    CARDINALS = 22
    CHARGERS = 24
    CHIEFS = 12
    COLTS = 11
    COMMANDERS = 28
    COWBOYS = 6
    DOLPHINS = 15
    EAGLES = 21
    FALCONS = 1
    NINERS = 25  # 49ers
    GIANTS = 19
    JAGUARS = 30
    JETS = 20
    LIONS = 8
    PACKERS = 9
    PANTHERS = 29
    PATRIOTS = 17
    RAIDERS = 13
    RAMS = 14
    RAVENS = 33
    SAINTS = 18
    SEAHAWKS = 26
    STEELERS = 23
    TEXANS = 34
    TITANS = 10
    VIKINGS = 16

class NFLEndpoints(Enum):
    TEAMS = "site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
    TEAM = "site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}"
    TEAM_ROSTER = "site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}/roster"
    DEPTH_CHART = "sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{YEAR}/teams/{TEAM_ID}/depthcharts"
    SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={date}" # 20251120 YYYYMMDD
    SCHEDULE = "https://cdn.espn.com/core/nfl/schedule?xhr=1&year={year}&week={week}"
    TEAM_STATS = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{year}/types/2/teams/{team_id}/statistics"
    