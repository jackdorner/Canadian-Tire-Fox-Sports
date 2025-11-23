class NFLGameCenter {
  constructor() {
    this.currentYear = 2025;
    this.currentWeek = 10;
    this.minYear = 2020;
    this.maxYear = 2025;
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
    // Season navigation
    document.getElementById('prevSeason').addEventListener('click', () => {
      if (this.currentYear > this.minYear) {
        this.currentYear--;
        this.updateDisplay();
        this.loadGames();
      }
    });

    document.getElementById('nextSeason').addEventListener('click', () => {
      if (this.currentYear < this.maxYear) {
        this.currentYear++;
        this.updateDisplay();
        this.loadGames();
      }
    });

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
  }

  updateDisplay() {
    // Update season display (25/26 format)
    const seasonDisplay = `${String(this.currentYear).slice(-2)}/${String(this.currentYear + 1).slice(-2)}`;
    document.getElementById('currentSeason').textContent = seasonDisplay;

    // Update week display
    document.getElementById('currentWeek').textContent = `Week ${this.currentWeek}`;

    // Enable/disable buttons based on boundaries
    document.getElementById('prevSeason').disabled = this.currentYear <= this.minYear;
    document.getElementById('nextSeason').disabled = this.currentYear >= this.maxYear;
    document.getElementById('prevWeek').disabled = this.currentWeek <= this.minWeek;
    document.getElementById('nextWeek').disabled = this.currentWeek >= this.maxWeek;
  }

  async loadGames() {
  const container = document.getElementById('gamesContainer');
  container.innerHTML = '<div class="loading">Loading games...</div>';

  try {
    const params = new URLSearchParams({
      week: this.currentWeek,
      season_start: this.currentYear,   // 2025 -> backend turns into "25/26"
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