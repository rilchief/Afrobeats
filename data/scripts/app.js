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

  const artistElements = {
    search: document.getElementById("artist-search"),
    options: document.getElementById("artist-options"),
    clear: document.getElementById("artist-clear"),
    empty: document.getElementById("artist-empty"),
    results: document.getElementById("artist-results"),
    name: document.getElementById("artist-name"),
    origin: document.getElementById("artist-origin"),
    flags: document.getElementById("artist-flags"),
    metricPlaylists: document.getElementById("artist-metric-playlists"),
    metricTracks: document.getElementById("artist-metric-tracks"),
    metricPopularity: document.getElementById("artist-metric-popularity"),
    metricPosition: document.getElementById("artist-metric-position"),
    metricFollowers: document.getElementById("artist-metric-followers"),
    playlistRows: document.getElementById("artist-playlist-rows"),
    trackRows: document.getElementById("artist-track-rows")
  };

  const regionElements = {
    search: document.getElementById("region-search"),
    clear: document.getElementById("region-clear"),
    tabs: document.getElementById("region-tabs"),
    empty: document.getElementById("region-empty"),
    content: document.getElementById("region-content"),
    name: document.getElementById("region-name"),
    summary: document.getElementById("region-summary"),
    flags: document.getElementById("region-flags"),
    metricTracks: document.getElementById("region-metric-tracks"),
    metricArtists: document.getElementById("region-metric-artists"),
    metricPlaylists: document.getElementById("region-metric-playlists"),
    metricPopularity: document.getElementById("region-metric-popularity"),
    metricDiaspora: document.getElementById("region-metric-diaspora"),
    metricFollowers: document.getElementById("region-metric-followers"),
    artistRows: document.getElementById("region-artist-rows"),
    playlistRows: document.getElementById("region-playlist-rows")
  };

  const chartTabButtons = Array.from(document.querySelectorAll("[data-chart-tab]"));
  const chartTabPanels = Array.from(document.querySelectorAll(".chart-tab-panel"));
  const chartTabContainer = document.querySelector("[data-tab-root]") || chartTabButtons[0]?.parentElement;
  const regionButtonMap = new Map();

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

  const dateFormatter = new Intl.DateTimeFormat(undefined, { day: "2-digit", month: "short", year: "numeric" });

  const artistIndex = buildArtistIndex(dataset.playlists);
  const regionIndex = buildRegionIndex(dataset.playlists);

  const state = {
    search: "",
    curatorTypes: new Set(uniqueCuratorTypes),
    minYear: minYearValue,
    maxYear: maxYearValue,
    diasporaOnly: false,
    selectedArtistId: null,
    artistQuery: "",
    selectedRegion: regionIndex.defaultRegion || regionIndex.list[0] || null,
    regionQuery: ""
  };

  let currentFilteredState = { playlists: [], tracks: [] };

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
      state.selectedArtistId = null;
      state.artistQuery = "";
      state.selectedRegion = regionIndex.defaultRegion || regionIndex.list[0] || null;
      state.regionQuery = "";

      elements.search.value = "";
      elements.minYear.value = minYearValue;
      elements.maxYear.value = maxYearValue;
      elements.diasporaOnly.checked = false;
      elements.curatorTypes.querySelectorAll("input[type=checkbox]").forEach((checkbox) => {
        checkbox.checked = true;
      });

      if (artistElements.search) {
        artistElements.search.value = "";
      }

      if (regionElements.search) {
        regionElements.search.value = "";
      }

      updateDashboard();
    });

    if (artistElements.search) {
      artistElements.search.addEventListener("input", (event) => {
        state.artistQuery = event.target.value;
        const resolvedId = resolveArtistId(event.target.value);
        state.selectedArtistId = resolvedId;
        updateArtistInspectorView();
      });

      artistElements.search.addEventListener("change", (event) => {
        state.artistQuery = event.target.value;
        const resolvedId = resolveArtistId(event.target.value);
        if (resolvedId) {
          state.selectedArtistId = resolvedId;
        }
        updateArtistInspectorView();
      });
    }

    if (artistElements.clear) {
      artistElements.clear.addEventListener("click", () => {
        state.selectedArtistId = null;
        state.artistQuery = "";
        if (artistElements.search) {
          artistElements.search.value = "";
        }
        updateArtistInspectorView();
      });
    }

    if (regionElements.search) {
      regionElements.search.addEventListener("input", (event) => {
        const value = event.target.value;
        state.regionQuery = value;
        const normalized = value.trim().toLowerCase();
        if (!normalized) {
          state.selectedRegion = regionIndex.defaultRegion || regionIndex.list[0] || null;
          updateRegionSpotlight();
          return;
        }
        const match = regionIndex.list.find((region) => region.toLowerCase().includes(normalized));
        state.selectedRegion = match || null;
        updateRegionSpotlight();
      });

      regionElements.search.addEventListener("change", (event) => {
        const value = event.target.value;
        state.regionQuery = value;
        const normalized = value.trim().toLowerCase();
        const exact = regionIndex.list.find((region) => region.toLowerCase() === normalized);
        if (exact) {
          state.selectedRegion = exact;
        }
        updateRegionSpotlight();
      });
    }

    if (regionElements.clear) {
      regionElements.clear.addEventListener("click", () => {
        state.regionQuery = "";
        state.selectedRegion = regionIndex.defaultRegion || regionIndex.list[0] || null;
        if (regionElements.search) {
          regionElements.search.value = "";
        }
        updateRegionSpotlight();
      });
    }
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

  function formatDate(value) {
    if (!value) return "--";
    const date = value instanceof Date ? value : new Date(value);
    if (Number.isNaN(date.getTime())) {
      return "--";
    }
    return dateFormatter.format(date);
  }

  function buildArtistIndex(playlists) {
    const map = new Map();

    playlists.forEach((playlist) => {
      (playlist.tracks || []).forEach((track) => {
        if (!track || !track.artistId) return;
        const id = track.artistId;
        const name = typeof track.artist === "string" ? track.artist.split(",")[0].trim() : "";

        if (!map.has(id)) {
          map.set(id, {
            id,
            name: name || "Unknown artist",
            defaultCountry: track.artistCountry || "Unknown",
            defaultRegion: track.regionGroup || "Unknown",
            diaspora: Boolean(track.diaspora),
            aliases: new Set()
          });
        }

        const entry = map.get(id);

        if (entry.defaultCountry === "Unknown" && track.artistCountry) {
          entry.defaultCountry = track.artistCountry;
        }

        if (entry.defaultRegion === "Unknown" && track.regionGroup) {
          entry.defaultRegion = track.regionGroup;
        }

        entry.diaspora = entry.diaspora || Boolean(track.diaspora);

        if (track.artist) {
          entry.aliases.add(track.artist);
        }
      });
    });

    const sorted = Array.from(map.values()).sort((a, b) => a.name.localeCompare(b.name));
    const nameToId = new Map();

    sorted.forEach((artist) => {
      nameToId.set(artist.name.toLowerCase(), artist.id);
      artist.aliases.forEach((alias) => {
        nameToId.set(alias.toLowerCase(), artist.id);
      });
    });

    return { map, sorted, nameToId };
  }

  function buildRegionIndex(playlists) {
    const counts = new Map();

    playlists.forEach((playlist) => {
      (playlist.tracks || []).forEach((track) => {
        const region = track?.regionGroup || "Unknown";
        counts.set(region, (counts.get(region) || 0) + 1);
      });
    });

    const list = Array.from(counts.keys()).sort((a, b) => a.localeCompare(b));
    let defaultRegion = null;
    let maxCount = -1;

    counts.forEach((value, region) => {
      if (value > maxCount) {
        maxCount = value;
        defaultRegion = region;
      }
    });

    return { list, counts, defaultRegion };
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

  function resolveArtistId(query) {
    if (!query) return null;
    const normalized = query.trim().toLowerCase();
    if (!normalized) return null;
    if (artistIndex.nameToId.has(normalized)) {
      return artistIndex.nameToId.get(normalized);
    }
    const partial = artistIndex.sorted.find((artist) => artist.name.toLowerCase().includes(normalized));
    return partial ? partial.id : null;
  }

  function showArtistPrompt(message) {
    if (!artistElements.empty || !artistElements.results) return;
    artistElements.empty.textContent = message;
    artistElements.empty.hidden = false;
    artistElements.results.hidden = true;
  }

  function renderArtistResults(artistMeta) {
    if (!artistElements.results || !artistElements.empty) return;

    const artistTracks = currentFilteredState.tracks.filter((track) => track.artistId === artistMeta.id);
    const playlistSummaries = new Map();

    artistTracks.forEach((track) => {
      if (!track.playlistId) {
        return;
      }

      if (!playlistSummaries.has(track.playlistId)) {
        playlistSummaries.set(track.playlistId, {
          playlistId: track.playlistId,
          playlistName: track.playlistName,
          curator: track.playlistCurator,
          curatorType: track.playlistCuratorType,
          followerCount: track.playlistFollowers || 0,
          launchYear: track.playlistLaunchYear || null,
          trackCount: 0,
          positions: [],
          addedAtDates: []
        });
      }

      const summary = playlistSummaries.get(track.playlistId);
      summary.trackCount += 1;
      if (typeof track.playlistPosition === "number") {
        summary.positions.push(track.playlistPosition);
      }
      if (track.addedAt) {
        summary.addedAtDates.push(track.addedAt);
      }
    });

    const playlistRows = Array.from(playlistSummaries.values()).map((summary) => {
      const medianPosition = summary.positions.length ? median(summary.positions) : null;
      const firstAdded = summary.addedAtDates
        .map((value) => new Date(value))
        .filter((date) => !Number.isNaN(date.getTime()))
        .sort((a, b) => a - b)[0];

      return {
        ...summary,
        medianPosition,
        firstAdded: firstAdded || null
      };
    });

    playlistRows.sort((a, b) => (b.followerCount || 0) - (a.followerCount || 0));

    const popularityValues = artistTracks
      .map((track) => track.trackPopularity)
      .filter((value) => typeof value === "number");
    const positionValues = artistTracks
      .map((track) => track.playlistPosition)
      .filter((value) => typeof value === "number");

    const avgPopularity = popularityValues.length ? average(popularityValues) : null;
    const medianPosition = positionValues.length ? median(positionValues) : null;
    const followerReach = playlistRows.reduce((total, row) => total + (row.followerCount || 0), 0);

    artistElements.empty.hidden = true;
    artistElements.results.hidden = false;

    artistElements.name.textContent = artistMeta.name;
    const originParts = [];
    if (artistMeta.defaultCountry && artistMeta.defaultCountry !== "Unknown") {
      originParts.push(artistMeta.defaultCountry);
    }
    if (artistMeta.defaultRegion && artistMeta.defaultRegion !== "Unknown") {
      originParts.push(artistMeta.defaultRegion);
    }
    artistElements.origin.textContent = originParts.length ? originParts.join(" • ") : "Origin unknown";

    const flagBadges = [];
    if (artistMeta.defaultCountry && artistMeta.defaultCountry !== "Unknown") {
      flagBadges.push(`<span class="tag">${artistMeta.defaultCountry}</span>`);
    }
    if (artistMeta.defaultRegion && artistMeta.defaultRegion !== "Unknown") {
      flagBadges.push(`<span class="tag">${artistMeta.defaultRegion}</span>`);
    }
    if (artistMeta.diaspora) {
      flagBadges.push('<span class="tag">Diaspora artist</span>');
    }
    if (artistElements.flags) {
      artistElements.flags.innerHTML = flagBadges.join(" ");
    }

    if (artistElements.metricPlaylists) {
      artistElements.metricPlaylists.textContent = String(playlistRows.length);
    }
    if (artistElements.metricTracks) {
      artistElements.metricTracks.textContent = String(artistTracks.length);
    }
    if (artistElements.metricPopularity) {
      artistElements.metricPopularity.textContent = avgPopularity !== null ? avgPopularity.toFixed(1) : "--";
    }
    if (artistElements.metricPosition) {
      artistElements.metricPosition.textContent = medianPosition !== null ? medianPosition.toFixed(0) : "--";
    }
    if (artistElements.metricFollowers) {
      artistElements.metricFollowers.textContent = formatNumber(followerReach);
    }

    if (artistElements.playlistRows) {
      if (!playlistRows.length) {
        artistElements.playlistRows.innerHTML = '<tr><td colspan="6">No placements within the current filters.</td></tr>';
      } else {
        artistElements.playlistRows.innerHTML = playlistRows
          .map((row) => {
            const launchTag = row.launchYear ? `<span class="tag">Launched ${row.launchYear}</span>` : "";
            const medianDisplay = row.medianPosition !== null ? row.medianPosition.toFixed(0) : "--";
            const firstAddedDisplay = row.firstAdded ? formatDate(row.firstAdded) : "--";
            return `
              <tr>
                <td>
                  <div class="table-stack">
                    <strong>${row.playlistName}</strong>
                    ${launchTag}
                  </div>
                </td>
                <td>
                  <div class="table-stack">
                    <span>${row.curator || "--"}</span>
                    <span class="tag">${row.curatorType || "Unknown"}</span>
                  </div>
                </td>
                <td>${row.trackCount}</td>
                <td>${medianDisplay}</td>
                <td>${formatNumber(row.followerCount || 0)}</td>
                <td>${firstAddedDisplay}</td>
              </tr>
            `;
          })
          .join("");
      }
    }

    if (artistElements.trackRows) {
      if (!artistTracks.length) {
        artistElements.trackRows.innerHTML = '<tr><td colspan="5">No placements within the current filters.</td></tr>';
      } else {
        const trackRows = artistTracks
          .slice()
          .sort((a, b) => {
            const aTime = new Date(a.addedAt || 0).getTime();
            const bTime = new Date(b.addedAt || 0).getTime();
            return bTime - aTime;
          })
          .map((track) => {
            const positionDisplay = typeof track.playlistPosition === "number" ? track.playlistPosition : "--";
            const popularityDisplay = typeof track.trackPopularity === "number" ? track.trackPopularity : "--";
            return `
              <tr>
                <td>${track.title || "--"}</td>
                <td>
                  <div class="table-stack">
                    <span>${track.playlistName || "--"}</span>
                    <span class="tag">${track.playlistCuratorType || "Unknown"}</span>
                  </div>
                </td>
                <td>${positionDisplay}</td>
                <td>${popularityDisplay}</td>
                <td>${track.addedAt ? formatDate(track.addedAt) : "--"}</td>
              </tr>
            `;
          });

        artistElements.trackRows.innerHTML = trackRows.join("");
      }
    }
  }

  function updateArtistInspectorView() {
    if (!artistElements.empty || !artistElements.results) return;

    if (!state.selectedArtistId) {
      if (state.artistQuery.trim()) {
        showArtistPrompt("No artist matches that name. Try another search.");
      } else {
        showArtistPrompt("Start typing an artist's name to surface their placements.");
      }
      if (artistElements.flags) {
        artistElements.flags.innerHTML = "";
      }
      return;
    }

    const artistMeta = artistIndex.map.get(state.selectedArtistId);
    if (!artistMeta) {
      showArtistPrompt("No artist matches that name. Try another search.");
      if (artistElements.flags) {
        artistElements.flags.innerHTML = "";
      }
      return;
    }

    renderArtistResults(artistMeta);
  }

  function initArtistLookup() {
    if (artistElements.options && artistIndex.sorted.length) {
      artistElements.options.innerHTML = artistIndex.sorted.map((artist) => `<option value="${artist.name}"></option>`).join("");
    }

    updateArtistInspectorView();
  }

  function showRegionPrompt(message) {
    if (!regionElements.empty || !regionElements.content) return;
    regionElements.empty.textContent = message;
    regionElements.empty.hidden = false;
    regionElements.content.hidden = true;
    if (regionElements.flags) {
      regionElements.flags.innerHTML = "";
    }
  }

  function updateRegionTabButtons(availableRegions) {
    regionButtonMap.forEach((button, region) => {
      const hasData = availableRegions.has(region);
      const isActive = hasData && state.selectedRegion === region;
      button.disabled = !hasData;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-selected", String(isActive));
      button.setAttribute("tabindex", isActive ? "0" : "-1");
    });
  }

  function renderRegionDetails(regionName) {
    if (!regionElements.content || !regionElements.empty) return;

    const normalizedRegion = regionName || "Unknown";
    const regionTracks = currentFilteredState.tracks.filter((track) => (track.regionGroup || "Unknown") === normalizedRegion);

    if (!regionTracks.length) {
      showRegionPrompt("This region has no placements under the current filters.");
      return;
    }

    const artistSummaries = new Map();
    const playlistSummaries = new Map();
    const uniquePlaylistFollowers = new Map();

    let diasporaCount = 0;

    regionTracks.forEach((track) => {
      if (track.diaspora) {
        diasporaCount += 1;
      }

      const artistKey = track.artistId || track.artist || "Unknown";
      const artistName = typeof track.artist === "string" ? track.artist.split(",")[0].trim() : track.artist || "Unknown artist";

      if (!artistSummaries.has(artistKey)) {
        artistSummaries.set(artistKey, {
          name: artistName || "Unknown artist",
          trackCount: 0,
          playlists: new Set(),
          popularity: [],
          positions: [],
          diasporaPlacements: 0
        });
      }

      const artistEntry = artistSummaries.get(artistKey);
      artistEntry.trackCount += 1;
      artistEntry.playlists.add(track.playlistId || track.playlistName || "Unknown playlist");
      if (typeof track.trackPopularity === "number") {
        artistEntry.popularity.push(track.trackPopularity);
      }
      if (typeof track.playlistPosition === "number") {
        artistEntry.positions.push(track.playlistPosition);
      }
      if (track.diaspora) {
        artistEntry.diasporaPlacements += 1;
      }

      const playlistKey = track.playlistId || `${track.playlistName || "Unknown playlist"}-${track.playlistCurator || ""}`;
      if (!playlistSummaries.has(playlistKey)) {
        playlistSummaries.set(playlistKey, {
          name: track.playlistName || "Unknown playlist",
          curator: track.playlistCurator || "Unknown",
          curatorType: track.playlistCuratorType || "Unknown",
          trackCount: 0,
          positions: [],
          artists: new Set(),
          followers: track.playlistFollowers || 0,
          launchYear: track.playlistLaunchYear || null
        });
      }

      const playlistEntry = playlistSummaries.get(playlistKey);
      playlistEntry.trackCount += 1;
      playlistEntry.artists.add(artistName || "Unknown artist");
      if (typeof track.playlistPosition === "number") {
        playlistEntry.positions.push(track.playlistPosition);
      }
      if (typeof track.playlistFollowers === "number") {
        playlistEntry.followers = track.playlistFollowers;
      }

      if (track.playlistId) {
        uniquePlaylistFollowers.set(track.playlistId, track.playlistFollowers || 0);
      }
    });

    const trackCount = regionTracks.length;
    const uniqueArtists = artistSummaries.size;
    const uniquePlaylists = playlistSummaries.size;
    const popularityValues = regionTracks
      .map((track) => track.trackPopularity)
      .filter((value) => typeof value === "number");
    const avgPopularity = popularityValues.length ? average(popularityValues) : null;
    const followerReach = Array.from(uniquePlaylistFollowers.values()).reduce((total, value) => total + (value || 0), 0);
    const diasporaShare = formatPercent(diasporaCount, trackCount);

    regionElements.empty.hidden = true;
    regionElements.content.hidden = false;

    if (regionElements.name) {
      regionElements.name.textContent = normalizedRegion;
    }
    if (regionElements.summary) {
      regionElements.summary.textContent = `${trackCount} tracks across ${uniquePlaylists} playlists within the active filters.`;
    }
    if (regionElements.flags) {
      const tags = [`<span class="tag">${uniqueArtists} artists</span>`, `<span class="tag">${diasporaShare} diaspora</span>`];
      regionElements.flags.innerHTML = tags.join(" ");
    }

    if (regionElements.metricTracks) {
      regionElements.metricTracks.textContent = String(trackCount);
    }
    if (regionElements.metricArtists) {
      regionElements.metricArtists.textContent = String(uniqueArtists);
    }
    if (regionElements.metricPlaylists) {
      regionElements.metricPlaylists.textContent = String(uniquePlaylists);
    }
    if (regionElements.metricPopularity) {
      regionElements.metricPopularity.textContent = avgPopularity !== null ? avgPopularity.toFixed(1) : "--";
    }
    if (regionElements.metricDiaspora) {
      regionElements.metricDiaspora.textContent = diasporaShare;
    }
    if (regionElements.metricFollowers) {
      regionElements.metricFollowers.textContent = formatNumber(followerReach);
    }

    if (regionElements.artistRows) {
      const artistRows = Array.from(artistSummaries.values())
        .sort((a, b) => b.trackCount - a.trackCount || a.name.localeCompare(b.name))
        .slice(0, 20)
        .map((artist) => {
          const avgArtistPopularity = artist.popularity.length ? average(artist.popularity) : null;
          const medianArtistPosition = artist.positions.length ? median(artist.positions) : null;
          const diasporaArtistShare = formatPercent(artist.diasporaPlacements, artist.trackCount);
          return `
            <tr>
              <td>${artist.name}</td>
              <td>${artist.trackCount}</td>
              <td>${artist.playlists.size}</td>
              <td>${avgArtistPopularity !== null ? avgArtistPopularity.toFixed(1) : "--"}</td>
              <td>${medianArtistPosition !== null ? medianArtistPosition.toFixed(0) : "--"}</td>
              <td>${diasporaArtistShare}</td>
            </tr>
          `;
        });

      regionElements.artistRows.innerHTML = artistRows.length
        ? artistRows.join("")
        : '<tr><td colspan="6">No artist placements for this region within the filters.</td></tr>';
    }

    if (regionElements.playlistRows) {
      const playlistRows = Array.from(playlistSummaries.values())
        .sort((a, b) => b.trackCount - a.trackCount || a.name.localeCompare(b.name))
        .slice(0, 20)
        .map((playlist) => {
          const medianPlaylistPosition = playlist.positions.length ? median(playlist.positions) : null;
          const launchTag = playlist.launchYear ? `<span class="tag">Launched ${playlist.launchYear}</span>` : "";
          return `
            <tr>
              <td>
                <div class="table-stack">
                  <strong>${playlist.name}</strong>
                  ${launchTag}
                </div>
              </td>
              <td>
                <div class="table-stack">
                  <span>${playlist.curator}</span>
                  <span class="tag">${playlist.curatorType}</span>
                </div>
              </td>
              <td>${playlist.trackCount}</td>
              <td>${playlist.artists.size}</td>
              <td>${medianPlaylistPosition !== null ? medianPlaylistPosition.toFixed(0) : "--"}</td>
              <td>${formatNumber(playlist.followers || 0)}</td>
            </tr>
          `;
        });

      regionElements.playlistRows.innerHTML = playlistRows.length
        ? playlistRows.join("")
        : '<tr><td colspan="6">No playlists surface this region within the filters.</td></tr>';
    }
  }

  function updateRegionSpotlight() {
    if (!regionElements.tabs) return;

    const availableRegions = new Set(currentFilteredState.tracks.map((track) => track.regionGroup || "Unknown"));
    updateRegionTabButtons(availableRegions);

    if (!currentFilteredState.tracks.length) {
      showRegionPrompt("No regions within the current filters.");
      return;
    }

    if (state.regionQuery.trim() && (!state.selectedRegion || !availableRegions.has(state.selectedRegion))) {
      showRegionPrompt("No region matches that search within the current filters.");
      return;
    }

    if (!state.selectedRegion || !availableRegions.has(state.selectedRegion)) {
      const sortedAvailable = Array.from(availableRegions).sort((a, b) => a.localeCompare(b));
      state.selectedRegion = sortedAvailable[0] || null;
    }

    if (!state.selectedRegion) {
      showRegionPrompt("No regions available within the current filters.");
      return;
    }

    renderRegionDetails(state.selectedRegion);
  }

  function initRegionSpotlight() {
    if (!regionElements.tabs || !regionIndex.list.length) {
      if (regionElements.empty) {
        regionElements.empty.textContent = "No regions available in the dataset.";
      }
      return;
    }

    if (!state.selectedRegion) {
      state.selectedRegion = regionIndex.defaultRegion || regionIndex.list[0] || null;
    }

    regionElements.tabs.innerHTML = regionIndex.list
      .map((region) => {
        const isActive = state.selectedRegion === region;
        return `<button type="button" data-region-tab="${region}" role="tab" aria-selected="${isActive}" tabindex="${isActive ? "0" : "-1"}">${region}</button>`;
      })
      .join("");

    regionButtonMap.clear();
    regionElements.tabs.querySelectorAll("button[data-region-tab]").forEach((button) => {
      regionButtonMap.set(button.dataset.regionTab, button);
    });

    regionElements.tabs.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-region-tab]");
      if (!button || button.disabled) return;
      const { regionTab } = button.dataset;
      if (!regionTab) return;
      state.selectedRegion = regionTab;
      state.regionQuery = "";
      if (regionElements.search) {
        regionElements.search.value = "";
      }
      updateRegionSpotlight();
    });

    updateRegionSpotlight();
  }

  function updateDashboard() {
    const filteredPlaylists = filterPlaylists();
    const filteredTracks = filteredPlaylists.flatMap((playlist) =>
      playlist.filteredTracks.map((track) => ({
        ...track,
        playlistId: playlist.id,
        playlistName: playlist.name,
        playlistCurator: playlist.curator,
        playlistCuratorType: playlist.curatorType,
        playlistFollowers: playlist.followerCount,
        playlistLaunchYear: playlist.launchYear
      }))
    );

    currentFilteredState = { playlists: filteredPlaylists, tracks: filteredTracks };

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
      updateArtistInspectorView();
      updateRegionSpotlight();
      return;
    }

    updateCards(filteredPlaylists, filteredTracks);
    updateCharts(filteredTracks, filteredPlaylists);
    renderPlaylistTable(filteredPlaylists);
    updateArtistInspectorView();
    updateRegionSpotlight();
  }

  initFilters();
  initArtistLookup();
  initRegionSpotlight();
  attachListeners();
  initMetadata();
  updateDashboard();
  initChartTabs();
})();
