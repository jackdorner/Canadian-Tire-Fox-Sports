from djongo import models


class Team(models.Model):
    """NFL Team model."""
    team_id = models.IntegerField(primary_key=True)
    uid = models.CharField(max_length=100)
    slug = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)
    display_name = models.CharField(max_length=100)
    short_display_name = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    color = models.CharField(max_length=10, null=True, blank=True)
    alternate_color = models.CharField(max_length=10, null=True, blank=True)
    logo_url = models.URLField(max_length=500, null=True, blank=True)
    
    # Venue information stored as JSON
    venue = models.JSONField(default=dict)
    
    # Links stored as JSON
    links = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teams'
        ordering = ['display_name']
    
    def __str__(self):
        return f"{self.display_name} ({self.abbreviation})"


class TeamDetails(models.Model):
    """Extended team details including current season record."""
    team_id = models.IntegerField(primary_key=True)
    display_name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    record_summary = models.CharField(max_length=50, null=True, blank=True)
    standing_summary = models.CharField(max_length=200, null=True, blank=True)
    
    # Record data stored as JSON
    record = models.JSONField(default=dict)
    
    # Next game stored as JSON
    next_game = models.JSONField(default=dict, null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'team_details'
    
    def __str__(self):
        return f"{self.display_name} - {self.record_summary}"


class Player(models.Model):
    """NFL Player model."""
    player_id = models.IntegerField(primary_key=True)
    uid = models.CharField(max_length=100)
    team_id = models.IntegerField(db_index=True)
    jersey = models.CharField(max_length=5, null=True, blank=True)
    display_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    short_name = models.CharField(max_length=50, null=True, blank=True)
    
    # Position stored as JSON
    position = models.JSONField(default=dict)
    
    headshot_url = models.URLField(max_length=500, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    height = models.CharField(max_length=10, null=True, blank=True)
    weight = models.CharField(max_length=10, null=True, blank=True)
    experience = models.IntegerField(default=0)
    college = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'players'
        ordering = ['display_name']
        indexes = [
            models.Index(fields=['team_id']),
            models.Index(fields=['position']),
        ]
    
    def __str__(self):
        pos = self.position.get('abbreviation', '') if isinstance(self.position, dict) else ''
        return f"{self.display_name} - {pos} #{self.jersey}"


class Game(models.Model):
    """NFL Game model."""
    game_id = models.CharField(max_length=50, primary_key=True)
    uid = models.CharField(max_length=100)
    date = models.DateTimeField(db_index=True)
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100)
    week = models.IntegerField(db_index=True)
    season = models.IntegerField(db_index=True)
    season_type = models.IntegerField(default=2)  # 1=preseason, 2=regular, 3=postseason
    
    # Team data stored as JSON
    home_team = models.JSONField(default=dict)
    away_team = models.JSONField(default=dict)
    
    # Game status stored as JSON
    status = models.JSONField(default=dict)
    
    # Venue stored as JSON
    venue = models.JSONField(default=dict)
    
    # Broadcasts stored as list
    broadcasts = models.JSONField(default=list)
    
    # Stat leaders stored as JSON
    stat_leaders = models.JSONField(default=dict)
    
    attendance = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'games'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['season', 'week']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.short_name} - Week {self.week}"
    
    @property
    def is_completed(self):
        """Check if game is completed."""
        return self.status.get('completed', False) if isinstance(self.status, dict) else False
    
    @property
    def home_score(self):
        """Get home team score."""
        return self.home_team.get('score', 0) if isinstance(self.home_team, dict) else 0
    
    @property
    def away_score(self):
        """Get away team score."""
        return self.away_team.get('score', 0) if isinstance(self.away_team, dict) else 0


class TeamSeasonStats(models.Model):
    """Team statistics for a season."""
    id = models.AutoField(primary_key=True)
    team_id = models.IntegerField(db_index=True)
    season = models.IntegerField(db_index=True)
    season_type = models.IntegerField(default=2)
    
    # All statistics stored as nested JSON
    all_stats = models.JSONField(default=dict)
    
    # Key statistics for quick access stored as JSON
    key_stats = models.JSONField(default=dict)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'team_season_stats'
        unique_together = ('team_id', 'season', 'season_type')
        ordering = ['-season', 'team_id']
        indexes = [
            models.Index(fields=['team_id', 'season']),
        ]
    
    def __str__(self):
        return f"Team {self.team_id} - {self.season} Stats"


class Schedule(models.Model):
    """NFL Schedule and calendar model."""
    id = models.AutoField(primary_key=True)
    year = models.IntegerField(db_index=True)
    week = models.IntegerField(db_index=True)
    
    # Calendar information stored as JSON
    calendar = models.JSONField(default=list)
    
    # Games list stored as JSON
    games = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'schedules'
        unique_together = ('year', 'week')
        ordering = ['-year', 'week']
    
    def __str__(self):
        return f"{self.year} - Week {self.week}"
