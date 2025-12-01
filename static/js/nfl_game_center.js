class NFLGameCenter {
  constructor() {
    this.currentWeek = 10;
    this.minWeek = 1;
    this.maxWeek = 18; // Regular season weeks
    
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.updateDisplay();
    this.loadGames();
  }

  setupEventListeners() {
    // Week navigation
    document.getElementById('prevWeek').addEventListener('click', () => {
      if (this.currentWeek > this.minWeek) {
        this.currentWeek--;
        this.updateDisplay();
        this.loadGames();
      }
    });

    document.getElementById('nextWeek').addEventListener('click', () => {
      if (this.currentWeek < this.maxWeek) {
        this.currentWeek++;
        this.updateDisplay();
        this.loadGames();
      }
    });

    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', () => {
      this.refreshGames();
    });
  }

  updateDisplay() {
    // Update week display
    document.getElementById('currentWeek').textContent = `Week ${this.currentWeek}`;

    // Enable/disable buttons based on boundaries
    document.getElementById('prevWeek').disabled = this.currentWeek <= this.minWeek;
    document.getElementById('nextWeek').disabled = this.currentWeek >= this.maxWeek;
  }

  async loadGames() {
    const container = document.getElementById('gamesContainer');
    container.innerHTML = '<div class="loading">Loading games...</div>';

    try {
      const params = new URLSearchParams({
        week: this.currentWeek
      });

      const response = await fetch(`/api/games/?${params.toString()}`);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      this.displayGames(data.games);
    } catch (error) {
      console.error('Error loading games:', error);
      container.innerHTML = '<div class="error">Error loading games. Please try again.</div>';
    }
  }

  async refreshGames() {
    const refreshBtn = document.getElementById('refreshBtn');
    const originalContent = refreshBtn.innerHTML;
    
    // Disable button and show loading state
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = '<span class="refresh-icon spinning">&#x21bb;</span> Refreshing...';

    try {
      // Refresh games first (this is synchronous and returns updated data)
      const gamesResponse = await fetch('/api/refresh-games/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          week: this.currentWeek,
          season_start: '2025'
        })
      });

      if (!gamesResponse.ok) {
        throw new Error('Failed to refresh games');
      }

      const gamesData = await gamesResponse.json();
      
      // Trigger team stats refresh in background (fire and forget)
      fetch('/api/refresh-stats/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          season_start: '2025'
        })
      }).then(response => {
        if (response.ok) {
          console.log('Team stats refresh started in background');
        } else {
          console.warn('Failed to trigger stats refresh');
        }
      }).catch(error => {
        console.error('Error triggering stats refresh:', error);
      });
      
      // Show success message
      refreshBtn.innerHTML = '<span class="refresh-icon">&#x2713;</span> Updated!';
      
      // Reload games to show updated data
      await this.loadGames();
      
      // Reset button after 2 seconds
      setTimeout(() => {
        refreshBtn.innerHTML = originalContent;
        refreshBtn.disabled = false;
      }, 2000);
      
    } catch (error) {
      console.error('Error refreshing games:', error);
      refreshBtn.innerHTML = '<span class="refresh-icon">&#x2717;</span> Error';
      
      // Reset button after 2 seconds
      setTimeout(() => {
        refreshBtn.innerHTML = originalContent;
        refreshBtn.disabled = false;
      }, 2000);
    }
  }


  displayGames(games) {
    const container = document.getElementById('gamesContainer');
    
    if (!games || games.length === 0) {
      container.innerHTML = '<div class="loading">No games found for this week.</div>';
      return;
    }

    container.innerHTML = games.map(game => this.createGameCard(game)).join('');
  }

createGameCard(game) {
  // Look at the human-readable text: "Final", "In Progress", "Scheduled"
  const textRaw = (game.statusText || '').toLowerCase();

  let statusClass;
  if (textRaw.includes('final')) {
    statusClass = 'status-final';
  } else if (textRaw.includes('progress') || textRaw.includes('live')) {
    statusClass = 'status-live';
  } else {
    statusClass = 'status-scheduled';
  }

  const isFinal = textRaw.includes('final');

  const homeWinner = isFinal && game.homeScore > game.awayScore ? 'winner' : '';
  const awayWinner = isFinal && game.awayScore > game.homeScore ? 'winner' : '';

  console.log('status text:', game.statusText, 'class:', statusClass);

  return `
    <div class="game-card">
      <div class="game-date">${game.date}</div>
      <div class="game-status ${statusClass}">${game.statusText}</div>
      ${textRaw.includes('progress') || textRaw.includes('live') ? `<div class="game-detail">${game.shortDetail || ''}</div>` : ''}

      <div class="matchup">
        <div class="team">
          <div class="team-info">
            <img src="${game.awayTeam.logo}" alt="${game.awayTeam.name}" class="team-logo" onerror="this.style.display='none'">
            <div>
              <div class="team-name">${game.awayTeam.name}</div>
              <div class="team-record">${game.awayTeam.record}</div>
            </div>
          </div>
          ${textRaw.includes('scheduled') ? '' : `<div class="team-score ${awayWinner}">${game.awayScore}</div>`}
        </div>

        ${textRaw.includes('scheduled') ? '<div class="vs-separator">VS</div>' : ''}

        <div class="team">
          <div class="team-info">
            <img src="${game.homeTeam.logo}" alt="${game.homeTeam.name}" class="team-logo" onerror="this.style.display='none'">
            <div>
              <div class="team-name">${game.homeTeam.name}</div>
              <div class="team-record">${game.homeTeam.record}</div>
            </div>
          </div>
          ${textRaw.includes('scheduled') ? '' : `<div class="team-score ${homeWinner}">${game.homeScore}</div>`}
        </div>
      </div>
    </div>
  `;
}

}
// Initialize when DOM is loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new NFLGameCenter();
  });
} else {
  new NFLGameCenter();
}