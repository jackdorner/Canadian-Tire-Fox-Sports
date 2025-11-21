"""
NFL API Client for ESPN NFL Data
Fetches and filters data from ESPN NFL endpoints for storage in MongoDB.
"""

import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from .NFLEndpoints import NFLTeam, NFLEndpoints


class NFLAPIClient:
    """Client for fetching and filtering NFL data from ESPN APIs."""
    
    def __init__(self):
        self.base_timeout = 10  # seconds
        
    def _make_request(self, url: str) -> Optional[Dict]:
        """
        Make HTTP GET request to the API endpoint.
        
        Args:
            url: Full URL to fetch
            
        Returns:
            JSON response as dictionary, or None if request fails
        """
        try:
            # Add https:// if not present
            if not url.startswith('http'):
                url = f'https://{url}'
                
            response = requests.get(url, timeout=self.base_timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return None
    
    def fetch_all_teams(self) -> List[Dict]:
        """
        Fetch all NFL teams with filtered essential information.
        
        Returns:
            List of team dictionaries with filtered data
        """
        url = NFLEndpoints.TEAMS.value
        data = self._make_request(url)
        
        if not data or 'sports' not in data:
            return []
        
        teams = []
        for sport in data.get('sports', []):
            for league in sport.get('leagues', []):
                for team in league.get('teams', []):
                    team_data = team.get('team', {})
                    
                    # Extract logo URL (prefer 500px version)
                    logo_url = None
                    for logo in team_data.get('logos', []):
                        if logo.get('width') == 500:
                            logo_url = logo.get('href')
                            break
                    if not logo_url and team_data.get('logos'):
                        logo_url = team_data['logos'][0].get('href')
                    
                    # Extract venue information
                    venue = team_data.get('venue', {})
                    venue_info = {
                        'name': venue.get('fullName'),
                        'city': venue.get('address', {}).get('city'),
                        'state': venue.get('address', {}).get('state'),
                        'capacity': venue.get('capacity')
                    }
                    
                    filtered_team = {
                        'team_id': team_data.get('id'),
                        'uid': team_data.get('uid'),
                        'slug': team_data.get('slug'),
                        'abbreviation': team_data.get('abbreviation'),
                        'display_name': team_data.get('displayName'),
                        'short_display_name': team_data.get('shortDisplayName'),
                        'name': team_data.get('name'),
                        'location': team_data.get('location'),
                        'color': team_data.get('color'),
                        'alternate_color': team_data.get('alternateColor'),
                        'logo_url': logo_url,
                        'venue': venue_info,
                        'links': {
                            'clubhouse': next((link['href'] for link in team_data.get('links', []) if link.get('rel', []) and 'clubhouse' in link['rel']), None),
                            'roster': next((link['href'] for link in team_data.get('links', []) if link.get('rel', []) and 'roster' in link['rel']), None),
                            'stats': next((link['href'] for link in team_data.get('links', []) if link.get('rel', []) and 'stats' in link['rel']), None),
                        }
                    }
                    teams.append(filtered_team)
        
        return teams
    
    def fetch_team_details(self, team_id: int) -> Optional[Dict]:
        """
        Fetch detailed information for a specific team including current record.
        
        Args:
            team_id: NFL team ID
            
        Returns:
            Dictionary with filtered team details and current record
        """
        url = NFLEndpoints.TEAM.value.format(team_id=team_id)
        data = self._make_request(url)
        
        if not data or 'team' not in data:
            return None
        
        team = data['team']
        
        # Extract current record
        record_summary = team.get('recordSummary', '')
        record_data = team.get('record', {})
        record_items = record_data.get('items', [])
        
        overall_record = next((item for item in record_items if item.get('type') == 'total'), {})
        home_record = next((item for item in record_items if item.get('type') == 'home'), {})
        road_record = next((item for item in record_items if item.get('type') == 'road'), {})
        
        # Extract next event
        next_event = team.get('nextEvent', [{}])[0] if team.get('nextEvent') else {}
        next_game = None
        if next_event:
            next_game = {
                'id': next_event.get('id'),
                'name': next_event.get('name'),
                'short_name': next_event.get('shortName'),
                'date': next_event.get('date')
            }
        
        filtered_details = {
            'team_id': team.get('id'),
            'display_name': team.get('displayName'),
            'abbreviation': team.get('abbreviation'),
            'record_summary': record_summary,
            'standing_summary': team.get('standingSummary'),
            'record': {
                'overall': {
                    'wins': overall_record.get('wins', 0),
                    'losses': overall_record.get('losses', 0),
                    'ties': overall_record.get('ties', 0),
                    'win_percent': overall_record.get('winPercent', 0),
                    'games_played': overall_record.get('gamesPlayed', 0)
                },
                'home': {
                    'wins': home_record.get('wins', 0),
                    'losses': home_record.get('losses', 0),
                    'summary': home_record.get('summary', '')
                },
                'road': {
                    'wins': road_record.get('wins', 0),
                    'losses': road_record.get('losses', 0),
                    'summary': road_record.get('summary', '')
                }
            },
            'next_game': next_game,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        return filtered_details
    
    def fetch_team_roster(self, team_id: int) -> List[Dict]:
        """
        Fetch team roster with filtered player information.
        
        Args:
            team_id: NFL team ID
            
        Returns:
            List of player dictionaries with filtered data
        """
        url = NFLEndpoints.TEAM_ROSTER.value.format(team_id=team_id)
        data = self._make_request(url)
        
        if not data:
            return []
        
        players = []
        
        # Process athletes from roster
        for athlete in data.get('athletes', []):
            # Extract headshot URL
            headshot_url = athlete.get('headshot', {}).get('href')
            
            # Extract position info
            position = athlete.get('position', {})
            position_info = {
                'name': position.get('name'),
                'abbreviation': position.get('abbreviation'),
                'display_name': position.get('displayName')
            }
            
            # Extract college info
            college = athlete.get('college', {})
            college_name = college.get('name') if college else None
            
            filtered_player = {
                'player_id': athlete.get('id'),
                'uid': athlete.get('uid'),
                'team_id': team_id,
                'jersey': athlete.get('jersey'),
                'display_name': athlete.get('displayName'),
                'full_name': athlete.get('fullName'),
                'short_name': athlete.get('shortName'),
                'position': position_info,
                'headshot_url': headshot_url,
                'age': athlete.get('age'),
                'height': athlete.get('displayHeight'),
                'weight': athlete.get('displayWeight'),
                'experience': athlete.get('experience', {}).get('years', 0),
                'college': college_name,
                'status': athlete.get('status', {}).get('name'),
                'updated_at': datetime.utcnow().isoformat()
            }
            players.append(filtered_player)
        
        return players
    
    def fetch_scoreboard(self, date: str) -> List[Dict]:
        """
        Fetch games and scores for a specific date.
        
        Args:
            date: Date string in YYYYMMDD format (e.g., '20241103')
            
        Returns:
            List of game dictionaries with filtered data
        """
        url = NFLEndpoints.SCOREBOARD.value.format(date=date)
        data = self._make_request(url)
        
        if not data or 'events' not in data:
            return []
        
        games = []
        
        for event in data.get('events', []):
            # Extract game basic info
            game_id = event.get('id')
            competition = event.get('competitions', [{}])[0]
            status = event.get('status', {})
            
            # Extract competitors (teams)
            competitors = competition.get('competitors', [])
            home_team = next((c for c in competitors if c.get('homeAway') == 'home'), {})
            away_team = next((c for c in competitors if c.get('homeAway') == 'away'), {})
            
            # Extract scores
            home_score = int(home_team.get('score', 0))
            away_score = int(away_team.get('score', 0))
            
            # Extract linescores (quarter by quarter)
            home_linescores = [ls.get('value', 0) for ls in home_team.get('linescores', [])]
            away_linescores = [ls.get('value', 0) for ls in away_team.get('linescores', [])]
            
            # Extract venue
            venue = competition.get('venue', {})
            venue_info = {
                'name': venue.get('fullName'),
                'city': venue.get('address', {}).get('city'),
                'state': venue.get('address', {}).get('state')
            }
            
            # Extract broadcast info
            broadcasts = competition.get('broadcasts', [])
            broadcast_networks = [b.get('names', [''])[0] for b in broadcasts if b.get('names')]
            
            # Extract stat leaders
            leaders = competition.get('leaders', [])
            stat_leaders = {}
            for leader_category in leaders:
                category_name = leader_category.get('name', '').lower()
                category_leaders = []
                for leader in leader_category.get('leaders', []):
                    athlete = leader.get('athlete', {})
                    category_leaders.append({
                        'player_id': athlete.get('id'),
                        'player_name': athlete.get('displayName'),
                        'team_id': athlete.get('team', {}).get('id'),
                        'headshot_url': athlete.get('headshot'),
                        'value': leader.get('displayValue'),
                        'stat': leader.get('value')
                    })
                stat_leaders[category_name] = category_leaders
            
            # Extract game status details
            status_info = {
                'completed': status.get('type', {}).get('completed', False),
                'description': status.get('type', {}).get('description'),
                'detail': status.get('type', {}).get('detail'),
                'short_detail': status.get('type', {}).get('shortDetail'),
                'state': status.get('type', {}).get('state'),
                'period': status.get('period'),
                'display_clock': status.get('displayClock')
            }
            
            filtered_game = {
                'game_id': game_id,
                'uid': event.get('uid'),
                'date': event.get('date'),
                'name': event.get('name'),
                'short_name': event.get('shortName'),
                'week': event.get('week', {}).get('number'),
                'season': event.get('season', {}).get('year'),
                'season_type': event.get('season', {}).get('type'),
                'home_team': {
                    'team_id': home_team.get('team', {}).get('id'),
                    'abbreviation': home_team.get('team', {}).get('abbreviation'),
                    'display_name': home_team.get('team', {}).get('displayName'),
                    'logo': home_team.get('team', {}).get('logo'),
                    'score': home_score,
                    'linescores': home_linescores,
                    'winner': home_team.get('winner', False),
                    'record': home_team.get('records', [{}])[0].get('summary', '') if home_team.get('records') else ''
                },
                'away_team': {
                    'team_id': away_team.get('team', {}).get('id'),
                    'abbreviation': away_team.get('team', {}).get('abbreviation'),
                    'display_name': away_team.get('team', {}).get('displayName'),
                    'logo': away_team.get('team', {}).get('logo'),
                    'score': away_score,
                    'linescores': away_linescores,
                    'winner': away_team.get('winner', False),
                    'record': away_team.get('records', [{}])[0].get('summary', '') if away_team.get('records') else ''
                },
                'status': status_info,
                'venue': venue_info,
                'broadcasts': broadcast_networks,
                'stat_leaders': stat_leaders,
                'attendance': competition.get('attendance'),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            games.append(filtered_game)
        
        return games
    
    def fetch_schedule(self, year: int, week: int) -> Dict:
        """
        Fetch schedule for a specific week.
        
        Args:
            year: Season year
            week: Week number
            
        Returns:
            Dictionary with calendar info and list of games
        """
        url = NFLEndpoints.SCHEDULE.value.format(year=year, week=week)
        data = self._make_request(url)
        
        if not data or 'content' not in data:
            return {'calendar': [], 'games': []}
        
        # Extract calendar information
        calendar = []
        for entry in data.get('content', {}).get('calendar', []):
            calendar.append({
                'label': entry.get('label'),
                'value': entry.get('value'),
                'start_date': entry.get('startDate'),
                'end_date': entry.get('endDate'),
                'entries': [
                    {
                        'label': e.get('label'),
                        'alternate_label': e.get('alternateLabel'),
                        'detail': e.get('detail'),
                        'value': e.get('value'),
                        'start_date': e.get('startDate'),
                        'end_date': e.get('endDate')
                    }
                    for e in entry.get('entries', [])
                ]
            })
        
        # Extract games from schedule
        games = []
        schedule_data = data.get('content', {}).get('schedule', {})
        
        for date_key, date_games in schedule_data.items():
            for game in date_games.get('games', []):
                competitions = game.get('competitions', [{}])[0]
                competitors = competitions.get('competitors', [])
                
                home_team = next((c for c in competitors if c.get('homeAway') == 'home'), {})
                away_team = next((c for c in competitors if c.get('homeAway') == 'away'), {})
                
                filtered_game = {
                    'game_id': game.get('id'),
                    'uid': game.get('uid'),
                    'date': game.get('date'),
                    'name': game.get('name'),
                    'short_name': game.get('shortName'),
                    'week': game.get('week', {}).get('number'),
                    'season_type': game.get('seasonType', {}).get('type'),
                    'home_team': {
                        'team_id': home_team.get('id'),
                        'abbreviation': home_team.get('abbreviation'),
                        'display_name': home_team.get('displayName'),
                        'logo': home_team.get('logo'),
                        'record': home_team.get('record', '')
                    },
                    'away_team': {
                        'team_id': away_team.get('id'),
                        'abbreviation': away_team.get('abbreviation'),
                        'display_name': away_team.get('displayName'),
                        'logo': away_team.get('logo'),
                        'record': away_team.get('record', '')
                    },
                    'venue': {
                        'name': competitions.get('venue', {}).get('fullName')
                    },
                    'broadcasts': [b.get('name') for b in competitions.get('broadcasts', [])]
                }
                games.append(filtered_game)
        
        return {
            'year': year,
            'week': week,
            'calendar': calendar,
            'games': games
        }
    
    def fetch_team_stats(self, team_id: int, year: int) -> Optional[Dict]:
        """
        Fetch comprehensive team statistics for a season.
        
        Args:
            team_id: NFL team ID
            year: Season year
            
        Returns:
            Dictionary with filtered team statistics
        """
        url = NFLEndpoints.TEAM_STATS.value.format(year=year, team_id=team_id)
        data = self._make_request(url)
        
        if not data or 'splits' not in data:
            return None
        
        # Extract statistics from splits
        stats = {}
        categories = data.get('splits', {}).get('categories', [])
        
        for category in categories:
            category_name = category.get('name', '').lower().replace(' ', '_')
            category_stats = {}
            
            for stat in category.get('stats', []):
                stat_name = stat.get('name', '').lower().replace(' ', '_').replace('.', '')
                category_stats[stat_name] = {
                    'value': stat.get('value'),
                    'display_value': stat.get('displayValue'),
                    'rank': stat.get('rank'),
                    'per_game_value': stat.get('perGameValue'),
                    'per_game_display_value': stat.get('perGameDisplayValue')
                }
            
            stats[category_name] = category_stats
        
        # Create a summary of key stats for easy access
        key_stats = {
            'offensive': {},
            'defensive': {},
            'special_teams': {}
        }
        
        # Extract key offensive stats
        if 'passing' in stats:
            key_stats['offensive']['passing_yards'] = stats['passing'].get('net_passing_yards', {})
            key_stats['offensive']['passing_tds'] = stats['passing'].get('passing_touchdowns', {})
            key_stats['offensive']['interceptions'] = stats['passing'].get('interceptions', {})
            key_stats['offensive']['qb_rating'] = stats['passing'].get('qb_rating', {})
        
        if 'rushing' in stats:
            key_stats['offensive']['rushing_yards'] = stats['rushing'].get('rushing_yards', {})
            key_stats['offensive']['rushing_tds'] = stats['rushing'].get('rushing_touchdowns', {})
        
        if 'receiving' in stats:
            key_stats['offensive']['receiving_yards'] = stats['receiving'].get('receiving_yards', {})
            key_stats['offensive']['receiving_tds'] = stats['receiving'].get('receiving_touchdowns', {})
        
        # Extract key defensive stats (if available in response)
        if 'defensive' in stats:
            key_stats['defensive']['total_tackles'] = stats['defensive'].get('total_tackles', {})
            key_stats['defensive']['sacks'] = stats['defensive'].get('sacks', {})
            key_stats['defensive']['interceptions'] = stats['defensive'].get('interceptions', {})
        
        # Extract special teams stats
        if 'kicking' in stats:
            key_stats['special_teams']['field_goal_pct'] = stats['kicking'].get('field_goal_pct', {})
            key_stats['special_teams']['extra_point_pct'] = stats['kicking'].get('extra_point_pct', {})
        
        if 'punting' in stats:
            key_stats['special_teams']['punt_avg'] = stats['punting'].get('yards_per_punt', {})
        
        filtered_stats = {
            'team_id': team_id,
            'season': year,
            'season_type': 2,  # Regular season
            'all_stats': stats,
            'key_stats': key_stats,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        return filtered_stats
    
    def fetch_team_by_enum(self, nfl_team: NFLTeam) -> Optional[Dict]:
        """
        Convenience method to fetch team details using the NFLTeam enum.
        
        Args:
            nfl_team: NFLTeam enum value
            
        Returns:
            Dictionary with team details
        """
        return self.fetch_team_details(nfl_team.value)
    
    def fetch_roster_by_enum(self, nfl_team: NFLTeam) -> List[Dict]:
        """
        Convenience method to fetch team roster using the NFLTeam enum.
        
        Args:
            nfl_team: NFLTeam enum value
            
        Returns:
            List of player dictionaries
        """
        return self.fetch_team_roster(nfl_team.value)
