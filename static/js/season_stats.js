class SeasonStatsPage {
  constructor() {
    this.currentStat = "OFFPointsPerGame";
    this.selector = document.getElementById("statSelector");
    this.container = document.getElementById("rankingsContainer");
    this.headerTitle = document.querySelector(".stat-header-title");
    this.leagueAverageSpan = document.getElementById("leagueAverage");
    
    this.init();
  }

  init() {
    // Set up event listener for dropdown
    this.selector.addEventListener("change", (e) => {
      this.currentStat = e.target.value;
      this.loadStats(this.currentStat);
    });

    // Load default stat
    this.loadStats(this.currentStat);
  }

  async loadStats(statKey) {
    // Show loading state
    this.container.innerHTML = '<div class="loading">Loading statistics...</div>';

    try {
      const response = await fetch(`/api/season-stats/?stat=${encodeURIComponent(statKey)}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.error) {
        this.showError(data.error);
        return;
      }

      this.displayStats(data);
    } catch (error) {
      console.error("Error loading stats:", error);
      this.showError("Failed to load statistics. Please try again.");
    }
  }

  displayStats(data) {
    // Update header
    this.headerTitle.textContent = data.stat_display_name;
    this.leagueAverageSpan.textContent = data.league_average_display;

    // Calculate color intensities based on percentage distance from average
    const teams = data.teams;
    const average = data.league_average;
    const preferLow = data.prefer_low;

    // Calculate percentage distances from average
    teams.forEach(team => {
      if (average === 0) {
        // Handle zero average - use absolute distance
        team.percentDistance = team.value;
      } else {
        // Calculate percentage distance: (value - average) / average * 100
        team.percentDistance = ((team.value - average) / Math.abs(average)) * 100;
      }
    });

    // Find max absolute percentage distance for normalization
    const maxAbsDistance = Math.max(...teams.map(t => Math.abs(t.percentDistance)));

    // Assign color classes to each team
    teams.forEach(team => {
      team.colorClass = this.getColorClass(team.percentDistance, maxAbsDistance, preferLow);
    });

    // Generate HTML for all teams
    const html = teams.map(team => this.createTeamRow(team)).join('');
    this.container.innerHTML = html;
  }

  getColorClass(percentDistance, maxAbsDistance, preferLow) {
    // Determine if this value is "good" or "bad"
    // For prefer_low stats (like interceptions), negative distance is good
    // For normal stats (like points), positive distance is good
    
    const isGood = preferLow ? (percentDistance < 0) : (percentDistance > 0);
    
    // If at average (or very close), return neutral
    if (Math.abs(percentDistance) < 0.01) {
      return "stat-average";
    }

    // Normalize the distance to 0-1 range
    const normalizedDistance = Math.abs(percentDistance) / maxAbsDistance;
    
    // Map to intensity 1-16 (linear scale)
    // 0-6.25% -> 1, 6.25-12.5% -> 2, ..., 93.75-100% -> 16
    let intensity = Math.ceil(normalizedDistance * 16);
    intensity = Math.max(1, Math.min(16, intensity)); // Clamp to 1-16

    // Return appropriate class
    if (isGood) {
      return `stat-above-${intensity}`;
    } else {
      return `stat-below-${intensity}`;
    }
  }

  createTeamRow(team) {
    return `
      <div class="stats-rank-row">
        <div class="rank-number">${team.rank}</div>
        <div class="team-info-cell">
          <img src="${team.logo}" alt="${team.display_name}" class="team-logo" onerror="this.style.display='none'">
          <div class="team-name">${team.display_name}</div>
        </div>
        <div class="stat-value-cell ${team.colorClass}">${team.displayValue}</div>
      </div>
    `;
  }

  showError(message) {
    this.container.innerHTML = `<div class="error">${message}</div>`;
  }
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new SeasonStatsPage();
  });
} else {
  new SeasonStatsPage();
}
