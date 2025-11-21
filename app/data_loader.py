"""
Data loader utility for fetching and storing NFL data.
Demonstrates how to use the NFLAPIClient to populate the database.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nfl_game_center.settings')
django.setup()

from app.nfl_api_client import NFLAPIClient
from app.models import Team, TeamDetails, Player, Game, TeamSeasonStats, Schedule
from app.NFLEndpoints import NFLTeam


class NFLDataLoader:
    """Utility class for loading NFL data into MongoDB."""
    
    def __init__(self):
        self.client = NFLAPIClient()
    
    def load_all_teams(self):
        """Fetch and store all NFL teams."""
        print("Fetching all teams...")
        teams_data = self.client.fetch_all_teams()
        
        created_count = 0
        updated_count = 0
        
        for team_data in teams_data:
            team, created = Team.objects.update_or_create(
                team_id=team_data['team_id'],
                defaults=team_data
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        print(f"✓ Teams loaded: {created_count} created, {updated_count} updated")
        return teams_data
    
    def load_team_details(self, team_id: int):
        """Fetch and store detailed information for a specific team."""
        print(f"Fetching details for team {team_id}...")
        details_data = self.client.fetch_team_details(team_id)
        
        if details_data:
            team_details, created = TeamDetails.objects.update_or_create(
                team_id=details_data['team_id'],
                defaults=details_data
            )
            action = "created" if created else "updated"
            print(f"✓ Team details {action}: {details_data['display_name']}")
            return team_details
        else:
            print(f"✗ Failed to fetch team details for team {team_id}")
            return None
    
    def load_all_team_details(self):
        """Fetch and store details for all teams."""
        print("Fetching details for all teams...")
        teams = Team.objects.all()
        
        for team in teams:
            self.load_team_details(team.team_id)
        
        print(f"✓ All team details loaded")
    
    def load_team_roster(self, team_id: int):
        """Fetch and store roster for a specific team."""
        print(f"Fetching roster for team {team_id}...")
        roster_data = self.client.fetch_team_roster(team_id)
        
        created_count = 0
        updated_count = 0
        
        for player_data in roster_data:
            player, created = Player.objects.update_or_create(
                player_id=player_data['player_id'],
                defaults=player_data
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        print(f"✓ Roster loaded: {created_count} created, {updated_count} updated")
        return roster_data
    
    def load_all_rosters(self):
        """Fetch and store rosters for all teams."""
        print("Fetching rosters for all teams...")
        teams = Team.objects.all()
        
        total_created = 0
        total_updated = 0
        
        for team in teams:
            print(f"  Loading roster for {team.abbreviation}...")
            roster_data = self.client.fetch_team_roster(team.team_id)
            
            for player_data in roster_data:
                player, created = Player.objects.update_or_create(
                    player_id=player_data['player_id'],
                    defaults=player_data
                )
                if created:
                    total_created += 1
                else:
                    total_updated += 1
        
        print(f"✓ All rosters loaded: {total_created} created, {total_updated} updated")
    
    def load_scoreboard(self, date: str):
        """
        Fetch and store games for a specific date.
        
        Args:
            date: Date string in YYYYMMDD format (e.g., '20241103')
        """
        print(f"Fetching scoreboard for {date}...")
        games_data = self.client.fetch_scoreboard(date)
        
        created_count = 0
        updated_count = 0
        
        for game_data in games_data:
            game, created = Game.objects.update_or_create(
                game_id=game_data['game_id'],
                defaults=game_data
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        print(f"✓ Scoreboard loaded: {created_count} created, {updated_count} updated")
        return games_data
    
    def load_current_week_games(self):
        """Fetch and store games for the current week."""
        # Get current date
        today = datetime.now()
        date_str = today.strftime('%Y%m%d')
        
        print(f"Loading games for current week (date: {date_str})...")
        return self.load_scoreboard(date_str)
    
    def load_schedule(self, year: int, week: int):
        """
        Fetch and store schedule for a specific week.
        
        Args:
            year: Season year
            week: Week number
        """
        print(f"Fetching schedule for {year} Week {week}...")
        schedule_data = self.client.fetch_schedule(year, week)
        
        schedule, created = Schedule.objects.update_or_create(
            year=year,
            week=week,
            defaults=schedule_data
        )
        
        action = "created" if created else "updated"
        print(f"✓ Schedule {action}: {year} Week {week}")
        return schedule
    
    def load_season_schedule(self, year: int, num_weeks: int = 18):
        """
        Fetch and store schedule for an entire season.
        
        Args:
            year: Season year
            num_weeks: Number of weeks (default 18 for regular season)
        """
        print(f"Loading schedule for {year} season ({num_weeks} weeks)...")
        
        for week in range(1, num_weeks + 1):
            self.load_schedule(year, week)
        
        print(f"✓ Full season schedule loaded")
    
    def load_team_stats(self, team_id: int, year: int):
        """
        Fetch and store team statistics for a season.
        
        Args:
            team_id: NFL team ID
            year: Season year
        """
        print(f"Fetching stats for team {team_id} in {year}...")
        stats_data = self.client.fetch_team_stats(team_id, year)
        
        if stats_data:
            stats, created = TeamSeasonStats.objects.update_or_create(
                team_id=team_id,
                season=year,
                season_type=2,
                defaults=stats_data
            )
            action = "created" if created else "updated"
            print(f"✓ Team stats {action}")
            return stats
        else:
            print(f"✗ Failed to fetch stats for team {team_id}")
            return None
    
    def load_all_team_stats(self, year: int = 2024):
        """
        Fetch and store statistics for all teams for a season.
        
        Args:
            year: Season year (default 2024)
        """
        print(f"Loading stats for all teams in {year}...")
        teams = Team.objects.all()
        
        success_count = 0
        fail_count = 0
        
        for team in teams:
            stats = self.load_team_stats(team.team_id, year)
            if stats:
                success_count += 1
            else:
                fail_count += 1
        
        print(f"✓ All team stats loaded: {success_count} successful, {fail_count} failed")
    
    def load_initial_data(self):
        """Load initial dataset - teams, rosters, and current season data."""
        print("\n" + "="*60)
        print("LOADING INITIAL NFL DATA")
        print("="*60 + "\n")
        
        # 1. Load all teams
        print("Step 1: Loading teams...")
        self.load_all_teams()
        
        # 2. Load team details
        print("\nStep 2: Loading team details...")
        self.load_all_team_details()
        
        # 3. Load rosters
        print("\nStep 3: Loading rosters...")
        self.load_all_rosters()
        
        # 4. Load current week games
        print("\nStep 4: Loading current week games...")
        self.load_current_week_games()
        
        # 5. Load current season schedule (2024)
        print("\nStep 5: Loading 2024 season schedule...")
        self.load_season_schedule(2024)
        
        # 6. Load team stats for 2024
        print("\nStep 6: Loading 2024 team statistics...")
        self.load_all_team_stats(2024)
        
        print("\n" + "="*60)
        print("INITIAL DATA LOAD COMPLETE!")
        print("="*60 + "\n")


def main():
    """Main execution function."""
    loader = NFLDataLoader()
    
    # Example usage - uncomment the operations you want to perform:
    
    # Load all initial data
    loader.load_initial_data()
    
    # Or load specific data:
    # loader.load_all_teams()
    # loader.load_team_roster(NFLTeam.PACKERS.value)
    # loader.load_scoreboard('20241103')
    # loader.load_schedule(2024, 10)
    # loader.load_team_stats(NFLTeam.CHIEFS.value, 2024)


if __name__ == '__main__':
    main()
