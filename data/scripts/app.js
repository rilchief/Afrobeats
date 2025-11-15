(() => {
  const dataset = window.AFROBEATS_DATA;
  if (!dataset || !Array.isArray(dataset.playlists)) {
    console.error("Afrobeats dataset missing or malformed.");
    return;
  }

  const elements = {
    search: document.getElementById("search"),
    curatorTypes: document.getElementById("curator-types"),
    minYear: document.getElementById("min-year"),
    maxYear: document.getElementById("max-year"),
    diasporaOnly: document.getElementById("diaspora-only"),
    reset: document.getElementById("reset-filters"),
    playlistCount: document.getElementById("playlist-count"),
    trackCount: document.getElementById("track-count"),
    nigeriaShare: document.getElementById("nigeria-share"),
    diasporaShare: document.getElementById("diaspora-share"),
    diversityScore: document.getElementById("diversity-score"),
    playlistTable: document.getElementById("playlist-table"),
    emptyState: document.getElementById("empty-state"),
    regionChart: document.getElementById("region-chart"),
    releaseChart: document.getElementById("release-chart"),
    popularityChart: document.getElementById("popularity-chart"),
    curatorChart: document.getElementById("curator-chart"),
    exposureChart: document.getElementById("exposure-chart")
  };

  const chartTabButtons = Array.from(document.querySelectorAll("[data-chart-tab]"));
              ticks: { color: "#f7f8fa" },
              title: {
                display: true,
                text: "Spotify popularity (0-100)",
                color: "#f7f8fa",
                font: { weight: "600" }
              },
  const chartTabContainer = document.querySelector("[data-tab-root]") || chartTabButtons[0]?.parentElement;

  const allTracks = dataset.playlists.flatMap((playlist) => playlist.tracks || []);
  const trackYears = allTracks.map((track) => track.releaseYear).filter((year) => typeof year === "number");
  const minYearValue = Math.min(...trackYears);
  const maxYearValue = Math.max(...trackYears);

  const uniqueCuratorTypes = Array.from(new Set(dataset.playlists.map((p) => p.curatorType))).sort();

  const metadataElements = {
    generated: document.getElementById("data-generated"),
    started: document.getElementById("data-started"),
    playlistTotal: document.getElementById("dataset-playlist-count"),
    missingCount: document.getElementById("dataset-missing-count"),
    audioStatus: document.getElementById("audio-feature-status")
  };

  const state = {
    search: "",
    curatorTypes: new Set(uniqueCuratorTypes),
    minYear: minYearValue,
    maxYear: maxYearValue,
    diasporaOnly: false
  };

  function initFilters() {
    elements.curatorTypes.innerHTML = uniqueCuratorTypes
      .map(
        (type, index) => `
          <label>
            <input type="checkbox" value="${type}" data-index="${index}" checked />
            <span>${type}</span>
          </label>
        `
      )
      .join("");

    elements.minYear.value = state.minYear;
    elements.minYear.min = String(minYearValue);
    elements.minYear.max = String(maxYearValue);

    elements.maxYear.value = state.maxYear;
    elements.maxYear.min = String(minYearValue);
    elements.maxYear.max = String(maxYearValue);
  }

  function initChartTabs() {
    if (!chartTabButtons.length || !chartTabPanels.length) {
      return;
    }

    function activateTab(targetId, options = {}) {
      if (!targetId) return;
      const shouldScroll = Boolean(options.scrollIntoView);

      chartTabButtons.forEach((button) => {
        const isActive = button.dataset.chartTab === targetId;
        button.setAttribute("aria-selected", String(isActive));
        button.setAttribute("tabindex", isActive ? "0" : "-1");
        button.classList.toggle("is-active", isActive);
      });

      chartTabPanels.forEach((panel) => {
        const isActive = panel.id === targetId;
        panel.classList.toggle("is-hidden", !isActive);
        panel.setAttribute("aria-hidden", String(!isActive));
        panel.setAttribute("tabindex", isActive ? "0" : "-1");
        if (isActive) {
          requestAnimationFrame(() => {
            switch (targetId) {
              case "overview-panel":
                charts.region?.resize();
                charts.region?.update();
                break;
              case "release-panel":
                charts.release?.resize();
                charts.release?.update();
                break;
              case "popularity-panel":
                charts.popularity?.resize();
                charts.popularity?.update();
                break;
              case "curator-panel":
                charts.curator?.resize();
                charts.curator?.update();
                break;
              case "exposure-panel":
                charts.exposure?.resize();
                charts.exposure?.update();
                break;
              default:
                break;
            }
            if (shouldScroll && chartTabContainer && typeof chartTabContainer.scrollIntoView === "function") {
              chartTabContainer.scrollIntoView({ behavior: "smooth", block: "start" });
            }
          });
        }
      });
    }

    const defaultButton = chartTabButtons.find((button) => button.hasAttribute("data-default-tab")) || chartTabButtons[0];
    if (defaultButton) {
      activateTab(defaultButton.dataset.chartTab, { scrollIntoView: false });
    }

    chartTabButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const { chartTab } = button.dataset;
        if (!chartTab) return;
        activateTab(chartTab, { scrollIntoView: true });
      });
    });
  }

  function attachListeners() {
    elements.search.addEventListener("input", (event) => {
      state.search = event.target.value.trim().toLowerCase();
      updateDashboard();
    });

    elements.curatorTypes.querySelectorAll("input[type=checkbox]").forEach((checkbox) => {
      checkbox.addEventListener("change", (event) => {
        const value = event.target.value;
        if (event.target.checked) {
          state.curatorTypes.add(value);
        } else {
          state.curatorTypes.delete(value);
        }
        if (state.curatorTypes.size === 0) {
          state.curatorTypes.add(value);
          event.target.checked = true;
          return;
        }
        updateDashboard();
      });
    });

    elements.minYear.addEventListener("change", (event) => {
      const value = Number(event.target.value) || minYearValue;
      state.minYear = Math.max(minYearValue, Math.min(value, state.maxYear));
      event.target.value = state.minYear;
      updateDashboard();
    });

    elements.maxYear.addEventListener("change", (event) => {
      const value = Number(event.target.value) || maxYearValue;
      state.maxYear = Math.min(maxYearValue, Math.max(value, state.minYear));
      event.target.value = state.maxYear;
      updateDashboard();
    });

    elements.diasporaOnly.addEventListener("change", (event) => {
      state.diasporaOnly = event.target.checked;
      updateDashboard();
    });

    elements.reset.addEventListener("click", () => {
      state.search = "";
      state.curatorTypes = new Set(uniqueCuratorTypes);
      state.minYear = minYearValue;
      state.maxYear = maxYearValue;
      state.diasporaOnly = false;

      elements.search.value = "";
      elements.minYear.value = minYearValue;
      elements.maxYear.value = maxYearValue;
      elements.diasporaOnly.checked = false;
      elements.curatorTypes.querySelectorAll("input[type=checkbox]").forEach((checkbox) => {
        checkbox.checked = true;
      });

      updateDashboard();
    });
  }

  function filterTracks(playlist) {
    const tracks = playlist.tracks || [];
    return tracks.filter((track) => {
      if (!track) return false;
      if (typeof track.releaseYear !== "number") return false;
      if (track.releaseYear < state.minYear || track.releaseYear > state.maxYear) return false;
      if (state.diasporaOnly && !track.diaspora) return false;
      return true;
    });
  }

  function filterPlaylists() {
    return dataset.playlists
      .filter((playlist) => state.curatorTypes.has(playlist.curatorType))
      .filter((playlist) => playlist.name.toLowerCase().includes(state.search))
      .map((playlist) => ({
        ...playlist,
        filteredTracks: filterTracks(playlist)
      }))
      .filter((playlist) => playlist.filteredTracks.length > 0);
  }

  function average(numbers) {
    if (!numbers.length) return 0;
    const total = numbers.reduce((sum, value) => sum + value, 0);
    return total / numbers.length;
  }

  function sumCounts(tracks, accessor) {
    return tracks.reduce((acc, track) => {
      const key = accessor(track) || "Unknown";
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {});
  }

  function median(numbers) {
    if (!numbers.length) return 0;
    const sorted = [...numbers].sort((a, b) => a - b);
    const midpoint = Math.floor(sorted.length / 2);
    if (sorted.length % 2 === 0) {
      return (sorted[midpoint - 1] + sorted[midpoint]) / 2;
    }
    return sorted[midpoint];
  }

  function formatNumber(value) {
    if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
    if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
    return String(value);
  }

  function formatPercent(part, total) {
    if (!total) return "0%";
    return `${Math.round((part / total) * 100)}%`;
  }

  function formatTimestamp(value) {
    if (!value) return "Unknown";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }
    return date.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
  }

  let charts = {
    region: null,
    release: null,
    popularity: null,
    curator: null,
    exposure: null
  };

  function initMetadata() {
    const runMetadata = dataset.runMetadata || {};
    if (metadataElements.generated) {
      metadataElements.generated.textContent = formatTimestamp(runMetadata.generatedAt);
    }
    if (metadataElements.started) {
      metadataElements.started.textContent = formatTimestamp(runMetadata.startedAt);
    }
    if (metadataElements.playlistTotal) {
      const runCount = typeof runMetadata.playlistCount === "number" ? runMetadata.playlistCount : dataset.playlists.length;
      metadataElements.playlistTotal.textContent = String(runCount);
    }
    if (metadataElements.missingCount) {
      const missing = Array.isArray(runMetadata.missingArtists) ? runMetadata.missingArtists.length : 0;
      metadataElements.missingCount.textContent = String(missing);
    }

    const tracksWithAudio = allTracks.filter((track) => {
      if (!track?.features) return false;
      return Object.values(track.features).some((value) => typeof value === "number" && value > 0);
    }).length;
    const coverage = allTracks.length ? Math.round((tracksWithAudio / allTracks.length) * 100) : 0;

    if (metadataElements.audioStatus) {
      if (coverage === 0) {
        metadataElements.audioStatus.textContent = "Optional: Spotify audio features currently blocked";
        metadataElements.audioStatus.classList.add("is-warning");
        metadataElements.audioStatus.classList.remove("is-success");
      } else {
        metadataElements.audioStatus.textContent = `${coverage}% optional audio feature coverage`;
        metadataElements.audioStatus.classList.add("is-success");
        metadataElements.audioStatus.classList.remove("is-warning");
      }
    }
  }

  function ensureCharts() {
    if (!charts.region) {
      charts.region = new Chart(elements.regionChart, {
        type: "bar",
        data: {
          labels: [],
          datasets: [
            {
              label: "Tracks",
              data: [],
              backgroundColor: "rgba(255, 180, 0, 0.75)",
              borderRadius: 8
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { ticks: { color: "#f7f8fa" }, grid: { color: "rgba(255,255,255,0.06)" } },
            y: { ticks: { color: "#f7f8fa" }, grid: { color: "rgba(255,255,255,0.06)" } }
          },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (context) => `${context.parsed.y} tracks`
              }
            }
          }
        }
      });
    }

    if (!charts.release) {
      charts.release = new Chart(elements.releaseChart, {
        type: "bar",
        data: {
          labels: [],
          datasets: [
            {
              label: "Tracks",
              data: [],
              backgroundColor: "rgba(108, 99, 255, 0.75)",
              borderRadius: 8
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { ticks: { color: "#f7f8fa" }, grid: { color: "rgba(255,255,255,0.06)" } },
            y: { ticks: { color: "#f7f8fa" }, beginAtZero: true }
          },
          plugins: {
            legend: { display: false }
          }
        }
      });
    }

    if (!charts.popularity) {
      charts.popularity = new Chart(elements.popularityChart, {
        type: "bar",
        data: {
          labels: [],
          datasets: [
            {
              label: "Average popularity",
              data: [],
              backgroundColor: "rgba(255, 180, 0, 0.75)",
              borderRadius: 8
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              ticks: { color: "#f7f8fa" },
              title: {
                display: true,
                text: "Spotify popularity (0-100)",
                color: "#f7f8fa",
                font: { weight: "600" }
              },
              grid: { color: "rgba(255,255,255,0.06)" }
            },
            x: { ticks: { color: "#f7f8fa", autoSkip: false }, grid: { display: false } }
          },
          plugins: {
            legend: { display: false }
          }
        }
      });
    }

    if (!charts.curator) {
      charts.curator = new Chart(elements.curatorChart, {
        type: "bar",
        data: {
          labels: [],
          datasets: [
            {
              label: "% of tracks featuring Nigerian artists",
              data: [],
              backgroundColor: "rgba(108, 99, 255, 0.75)",
              borderRadius: 8
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              ticks: { color: "#f7f8fa", callback: (value) => `${value}%` },
              grid: { color: "rgba(255,255,255,0.06)" }
            },
            x: {
              ticks: { color: "#f7f8fa", autoSkip: false },
              grid: { display: false }
            }
          },
          plugins: {
            legend: { display: false }
          }
        }
      });
    }

    if (!charts.exposure) {
      charts.exposure = new Chart(elements.exposureChart, {
        type: "bar",
        data: {
          labels: [],
          datasets: [
            {
              label: "Track placements",
              data: [],
              backgroundColor: "rgba(46, 204, 113, 0.7)",
              borderRadius: 8
            }
          ]
        },
        options: {
          indexAxis: "y",
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { beginAtZero: true, ticks: { color: "#f7f8fa" }, grid: { color: "rgba(255,255,255,0.06)" } },
            y: { ticks: { color: "#f7f8fa" }, grid: { display: false } }
          },
          plugins: {
            legend: { display: false }
          }
        }
      });
    }
  }

  function updateCharts(allTracks, playlists) {
    ensureCharts();

    const regionCounts = sumCounts(allTracks, (track) => track.regionGroup);
    const regionLabels = Object.keys(regionCounts).sort();
    const regionValues = regionLabels.map((key) => regionCounts[key]);
    charts.region.data.labels = regionLabels;
    charts.region.data.datasets[0].data = regionValues;
    charts.region.update();

    const releaseCounts = sumCounts(allTracks, (track) => track.releaseYear);
    const releaseLabels = Object.keys(releaseCounts)
      .map((year) => Number(year))
      .filter((year) => !Number.isNaN(year))
      .sort((a, b) => a - b);
    const releaseValues = releaseLabels.map((year) => releaseCounts[String(year)]);
    charts.release.data.labels = releaseLabels;
    charts.release.data.datasets[0].data = releaseValues;
    charts.release.update();

    const popularityByRegion = playlists.reduce((acc, playlist) => {
      playlist.filteredTracks.forEach((track) => {
        const key = track.regionGroup || "Unknown";
        if (!acc[key]) {
          acc[key] = { total: 0, count: 0 };
        }
        if (typeof track.trackPopularity === "number") {
          acc[key].total += track.trackPopularity;
          acc[key].count += 1;
        }
      });
      return acc;
    }, {});

    const popularityEntries = Object.entries(popularityByRegion).map(([region, stats]) => {
      const averagePopularity = stats.count ? Math.round(stats.total / stats.count) : 0;
      return { region, averagePopularity };
    });

    popularityEntries.sort((a, b) => b.averagePopularity - a.averagePopularity);
    charts.popularity.data.labels = popularityEntries.map((entry) => entry.region);
    charts.popularity.data.datasets[0].data = popularityEntries.map((entry) => entry.averagePopularity);
    charts.popularity.update();

    const curatorGroups = playlists.reduce((acc, playlist) => {
      const key = playlist.curatorType;
      if (!acc[key]) {
        acc[key] = { nigeria: 0, total: 0 };
      }
      playlist.filteredTracks.forEach((track) => {
        if (track.artistCountry === "Nigeria") acc[key].nigeria += 1;
        acc[key].total += 1;
      });
      return acc;
    }, {});

    const curatorLabels = Object.keys(curatorGroups);
    const curatorValues = curatorLabels.map((label) => {
      const group = curatorGroups[label];
      if (!group.total) return 0;
      return Math.round((group.nigeria / group.total) * 100);
    });
    charts.curator.data.labels = curatorLabels;
    charts.curator.data.datasets[0].data = curatorValues;
    charts.curator.update();

    const artistExposure = playlists.reduce((acc, playlist) => {
      playlist.filteredTracks.forEach((track) => {
        const key = track.artistId || track.artist;
        if (!key) return;
        if (!acc[key]) {
          const primaryName = typeof track.artist === "string" ? track.artist.split(",")[0].trim() : "Unknown";
          acc[key] = { name: primaryName || "Unknown", count: 0 };
        }
        acc[key].count += 1;
      });
      return acc;
    }, {});

    const topArtists = Object.values(artistExposure)
      .sort((a, b) => b.count - a.count)
      .slice(0, 8);
    charts.exposure.data.labels = topArtists.map((artist) => artist.name);
    charts.exposure.data.datasets[0].data = topArtists.map((artist) => artist.count);
    charts.exposure.update();
  }

  function updateCards(playlists, tracks) {
    elements.playlistCount.textContent = playlists.length;
    elements.trackCount.textContent = tracks.length;

    const nigeriaTracks = tracks.filter((track) => track.artistCountry === "Nigeria").length;
    const diasporaTracks = tracks.filter((track) => track.diaspora).length;
    elements.nigeriaShare.textContent = formatPercent(nigeriaTracks, tracks.length);
    elements.diasporaShare.textContent = formatPercent(diasporaTracks, tracks.length);

    const diversityScores = playlists.map((playlist) => new Set(playlist.filteredTracks.map((track) => track.regionGroup)).size);
    const avgDiversity = diversityScores.length ? average(diversityScores).toFixed(1) : "0";
    elements.diversityScore.textContent = avgDiversity;
  }

  function renderPlaylistTable(playlists) {
    if (!playlists.length) {
      elements.playlistTable.innerHTML = "";
      elements.emptyState.hidden = false;
      return;
    }

    elements.emptyState.hidden = true;

    const rows = playlists
      .map((playlist) => {
        const totalTracks = playlist.filteredTracks.length;
        const diasporaCount = playlist.filteredTracks.filter((track) => track.diaspora).length;
        const nigeriaCount = playlist.filteredTracks.filter((track) => track.artistCountry === "Nigeria").length;
        const uniqueRegions = new Set(playlist.filteredTracks.map((track) => track.regionGroup)).size;
        const popularityValues = playlist.filteredTracks
          .map((track) => track.trackPopularity)
          .filter((value) => typeof value === "number");
        const avgPopularity = popularityValues.length ? average(popularityValues).toFixed(0) : "0";

        const positionValues = playlist.filteredTracks
          .map((track) => track.playlistPosition)
          .filter((value) => typeof value === "number");
        const medianPosition = positionValues.length ? median(positionValues).toFixed(0) : "--";

        return `
          <tr>
            <td>
              <div style="display:flex; flex-direction:column; gap:0.35rem;">
                <strong>${playlist.name}</strong>
                <span class="tag">Launched ${playlist.launchYear}</span>
              </div>
            </td>
            <td>${playlist.curator}</td>
            <td>${formatNumber(playlist.followerCount)}</td>
            <td>${uniqueRegions}</td>
            <td>${formatPercent(diasporaCount, totalTracks)}</td>
            <td>${formatPercent(nigeriaCount, totalTracks)}</td>
            <td>${avgPopularity}</td>
            <td>${medianPosition}</td>
          </tr>
        `;
      })
      .join("");

    elements.playlistTable.innerHTML = rows;
  }

  function updateDashboard() {
    const filteredPlaylists = filterPlaylists();
    const filteredTracks = filteredPlaylists.flatMap((playlist) => playlist.filteredTracks.map((track) => ({ ...track })));

    if (!filteredTracks.length) {
      ensureCharts();
      charts.region.data.labels = [];
      charts.region.data.datasets[0].data = [];
      charts.region.update();

      charts.release.data.labels = [];
      charts.release.data.datasets[0].data = [];
      charts.release.update();

      charts.popularity.data.labels = [];
      charts.popularity.data.datasets[0].data = [];
      charts.popularity.update();

      charts.curator.data.labels = [];
      charts.curator.data.datasets[0].data = [];
      charts.curator.update();

      charts.exposure.data.labels = [];
      charts.exposure.data.datasets[0].data = [];
      charts.exposure.update();

      renderPlaylistTable([]);
      updateCards(filteredPlaylists, filteredTracks);
      return;
    }

    updateCards(filteredPlaylists, filteredTracks);
    updateCharts(filteredTracks, filteredPlaylists);
    renderPlaylistTable(filteredPlaylists);
  }

  initFilters();
  attachListeners();
  initMetadata();
  updateDashboard();
  initChartTabs();
})();
