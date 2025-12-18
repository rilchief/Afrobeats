const SPOTIFY_PLAYLIST_IDS = {
  "afrobeats-hits": "25Y75ozl2aI0NylFToefO5",
  "afrobeats-2026": "5myeBzohhCVewaK2Thqmo5",
  "ginja": "4XtoXt98uSrnUbMz7JtWZk",
  "viral-afrobeats": "6ebiO5veMmbIWL5aGvalgQ",
  "top-afrobeats-hits": "0RChPss4CYl5LTfK0CRgOZ",
  "afrobeats-gold": "1UFBYLsMwB2q0EypxWdBLO",
  "top-picks-afrobeats": "1ynsIf7ZgpEFxIvuDBlUcK",
  "afrobeats-hits-indie": "2DfNaw9Z1nuddjI6NczTXS",
  "afro-nation-united": "0tbbV39e1yP4GsJ3HXSXgG",
  "hits-radio-afrobeats": "62Hmju3toBooBrDAHTQxg5",
  "afro-fusion-afrikan-radar": "3zCyA7HZGqHvAhzqVuclMu",
  "afrobeats-central-hypetribe": "7jVpY2zB7NXUwlYHNVFc2g",
  "feel-good-afrobeats": "7MPu2vwkQJDnIS4hAOu2Q6",
  "afrobeats-now": "3yyH2cPh5dctpFwsns9B2Z"
};

(() => {
  const toggle = document.getElementById("nav-toggle");
  const menu = document.querySelector("[data-nav-menu]");
  const backdrop = document.querySelector("[data-nav-backdrop]");
  if (!toggle || !menu) {
    return;
  }

  function setOpen(isOpen) {
    toggle.setAttribute("aria-expanded", String(isOpen));
    menu.classList.toggle("is-open", isOpen);
    document.body.classList.toggle("nav-open", isOpen);
    if (backdrop) {
      backdrop.hidden = !isOpen;
    }
  }

  toggle.addEventListener("click", () => {
    const willOpen = !menu.classList.contains("is-open");
    setOpen(willOpen);
  });

  if (backdrop) {
    backdrop.addEventListener("click", () => setOpen(false));
  }

  menu.addEventListener("click", (event) => {
    const target = event.target;
    if (target instanceof HTMLElement && target.tagName === "A") {
      setOpen(false);
    }
  });
})();

(() => {
  const toggle = document.getElementById("filters-toggle");
  const panel = document.getElementById("filters");
  const backdrop = document.querySelector("[data-filters-backdrop]");
  if (!toggle || !panel) {
    return;
  }

  function setOpen(isOpen) {
    panel.classList.toggle("is-open", isOpen);
    toggle.setAttribute("aria-expanded", String(isOpen));
    document.body.classList.toggle("filters-open", isOpen);
    if (backdrop) {
      backdrop.hidden = !isOpen;
    }
  }

  toggle.addEventListener("click", () => {
    const willOpen = !panel.classList.contains("is-open");
    setOpen(willOpen);
  });

  if (backdrop) {
    backdrop.addEventListener("click", () => setOpen(false));
  }

  const mq = window.matchMedia("(min-width: 901px)");
  const handleBreakpoint = (event) => {
    if (event.matches) {
      setOpen(false);
    }
  };
  mq.addEventListener("change", handleBreakpoint);
})();

(async () => {
  const dataset = window.AFROBEATS_DATA;
  if (!dataset || !Array.isArray(dataset.playlists)) {
    console.error("Afrobeats dataset missing or malformed.");
    return;
  }

  let artistMetadataMap = new Map();
  try {
    artistMetadataMap = await fetchArtistMetadata();
  } catch (error) {
    console.warn("Failed to load artist metadata CSV; falling back to embedded values.", error);
  }
  applyArtistMetadataInPlace(dataset, artistMetadataMap);

  const MIN_REGION_TRACK_COUNT = 2;
  const MIN_COUNTRY_TRACK_COUNT = 2;

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
    filterSummary: document.getElementById("filter-summary"),
    playlistTable: document.getElementById("playlist-table"),
    emptyState: document.getElementById("empty-state"),
    regionChart: document.getElementById("region-chart"),
    releaseChart: document.getElementById("release-chart"),
    popularityChart: document.getElementById("popularity-chart"),
    curatorChart: document.getElementById("curator-chart"),
    exposureChart: document.getElementById("exposure-chart")
  };

  const playlistTracksPanel = document.getElementById("playlist-tracks-panel");
  const playlistTracksRows = document.getElementById("playlist-tracks-rows");

  const loadingOverlay = document.getElementById("dashboard-loading");
  const quickViewStatus = document.getElementById("quick-view-status");
  const quickViewButtons = Array.from(document.querySelectorAll("[data-quick-view]"));

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
    metricSpotifyFollowers: document.getElementById("artist-metric-spotify-followers"),
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

  const countryElements = {
    search: document.getElementById("country-search"),
    clear: document.getElementById("country-clear"),
    tabs: document.getElementById("country-tabs"),
    empty: document.getElementById("country-empty"),
    content: document.getElementById("country-content"),
    name: document.getElementById("country-name"),
    summary: document.getElementById("country-summary"),
    flags: document.getElementById("country-flags"),
    metricTracks: document.getElementById("country-metric-tracks"),
    metricArtists: document.getElementById("country-metric-artists"),
    metricPlaylists: document.getElementById("country-metric-playlists"),
    metricPopularity: document.getElementById("country-metric-popularity"),
    metricDiaspora: document.getElementById("country-metric-diaspora"),
    metricFollowers: document.getElementById("country-metric-followers"),
    artistRows: document.getElementById("country-artist-rows"),
    playlistRows: document.getElementById("country-playlist-rows")
  };

  const chartTabButtons = Array.from(document.querySelectorAll("[data-chart-tab]"));
  const chartTabPanels = Array.from(document.querySelectorAll(".chart-tab-panel"));
  const chartTabContainer = document.querySelector("[data-tab-root]") || chartTabButtons[0]?.parentElement;
  const regionButtonMap = new Map();
  const countryButtonMap = new Map();

  const quickViewSelect = document.getElementById("quick-view-select");

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

  const QUICK_VIEW_DEFAULT_ID = "all-placements";
  const quickViewPresets = [
    {
      id: QUICK_VIEW_DEFAULT_ID,
      label: "All placements",
      summary: "Full dataset across every curator, region, and release year.",
      apply: () => {
        resetFilters();
      }
    },
    {
      id: "current-cycle",
      label: "Current cycle",
      summary: "Focus on the most recent five release years to study current rotations.",
      apply: () => {
        resetFilters();
        state.minYear = Math.max(maxYearValue - 5, minYearValue);
        state.maxYear = maxYearValue;
      }
    },
    {
      id: "diaspora-wave",
      label: "Diaspora wave",
      summary: "Diaspora-only lens anchored to the freshest six-year window.",
      apply: () => {
        resetFilters();
        state.diasporaOnly = true;
        state.minYear = Math.max(maxYearValue - 6, minYearValue);
        state.maxYear = maxYearValue;
      }
    },
    {
      id: "archive-dig",
      label: "Archive dig",
      summary: "Lean into the earliest catalogue years to inspect historical gatekeeping.",
      apply: () => {
        resetFilters();
        const legacyCeiling = Math.min(minYearValue + 8, maxYearValue);
        state.maxYear = Math.max(legacyCeiling, state.minYear);
      }
    }
  ];
  const quickViewRegistry = new Map();

  const artistIndex = buildArtistIndex(dataset.playlists);
  const regionIndex = buildRegionIndex(dataset.playlists);
  const countryIndex = buildCountryIndex(dataset.playlists);

  const playlistEmbedElements = {
    dashboardIframe: document.getElementById("playlist-embed-iframe-dashboard"),
    dashboardContainer: document.getElementById("playlist-embed-dashboard")
  };

  const dashboardPlaylistElements = {
    input: document.getElementById("dashboard-playlist-search"),
    options: document.getElementById("dashboard-playlist-options"),
    clear: document.getElementById("dashboard-playlist-clear"),
    status: document.getElementById("dashboard-playlist-status"),
    metrics: document.getElementById("playlist-breakdown-metrics"),
    prompt: document.getElementById("playlist-breakdown-prompt"),
    empty: document.getElementById("empty-state")
  };

  function setEmbedForPlaylistInternalId(internalId) {
    const spotifyId = internalId ? SPOTIFY_PLAYLIST_IDS[internalId] : undefined;
    if (!spotifyId) {
      if (playlistEmbedElements.dashboardContainer) {
        playlistEmbedElements.dashboardContainer.hidden = true;
      }
      return;
    }

    const url = `https://open.spotify.com/embed/playlist/${spotifyId}?utm_source=generator`;

    if (playlistEmbedElements.dashboardIframe) {
      playlistEmbedElements.dashboardIframe.src = url;
    }
    if (playlistEmbedElements.dashboardContainer) {
      playlistEmbedElements.dashboardContainer.hidden = false;
    }
  }

  function clearDashboardPlaylistSelection() {
    selectedPlaylistId = null;
    if (dashboardPlaylistElements.input) {
      dashboardPlaylistElements.input.value = "";
    }
    if (dashboardPlaylistElements.status) {
      dashboardPlaylistElements.status.textContent = "Type a playlist name to see its breakdown.";
    }
    if (dashboardPlaylistElements.metrics) {
      dashboardPlaylistElements.metrics.hidden = true;
      dashboardPlaylistElements.metrics.innerHTML = "";
    }
    if (dashboardPlaylistElements.prompt) {
      dashboardPlaylistElements.prompt.hidden = false;
    }
    renderPlaylistTracks(null);
    if (playlistEmbedElements.dashboardContainer) {
      playlistEmbedElements.dashboardContainer.hidden = true;
    }
    if (playlistEmbedElements.dashboardIframe) {
      playlistEmbedElements.dashboardIframe.src = "";
    }
  }

  function renderDashboardPlaylistMetrics(playlist) {
    if (!dashboardPlaylistElements.metrics || !dashboardPlaylistElements.prompt) return;
    if (!playlist) {
      dashboardPlaylistElements.metrics.hidden = true;
      dashboardPlaylistElements.metrics.innerHTML = "";
      dashboardPlaylistElements.prompt.hidden = false;
      return;
    }

    const tracks = playlist.filteredTracks || [];
    const totalTracks = tracks.length;
    const diasporaCount = tracks.filter((track) => track.diaspora).length;
    const nigeriaCount = tracks.filter((track) => track.artistCountry === "Nigeria").length;
    const uniqueRegions = new Set(tracks.map((track) => track.regionGroup || "Unknown")).size;

    const popularityValues = tracks
      .map((track) => track.trackPopularity)
      .filter((value) => typeof value === "number");
    const avgPopularity = popularityValues.length ? average(popularityValues).toFixed(0) : "--";

    const positionValues = tracks
      .map((track) => track.playlistPosition)
      .filter((value) => typeof value === "number");
    const medianPosition = positionValues.length ? median(positionValues).toFixed(0) : "--";

    dashboardPlaylistElements.metrics.innerHTML = `
      <div class="breakdown-card">
        <span class="label">Playlist</span>
        <span class="value">${playlist.name}</span>
        <span class="subvalue">${playlist.curator}</span>
      </div>
      <div class="breakdown-card">
        <span class="label">Followers</span>
        <span class="value">${formatNumber(playlist.followerCount)}</span>
        <span class="subvalue">Launched ${playlist.launchYear ?? "--"}</span>
      </div>
      <div class="breakdown-card">
        <span class="label">Unique regions</span>
        <span class="value">${uniqueRegions}</span>
        <span class="subvalue">Across ${totalTracks} track${totalTracks === 1 ? "" : "s"}</span>
      </div>
      <div class="breakdown-card">
        <span class="label">Diaspora share</span>
        <span class="value">${formatPercent(diasporaCount, totalTracks)}</span>
        <span class="subvalue">Nigeria share ${formatPercent(nigeriaCount, totalTracks)}</span>
      </div>
      <div class="breakdown-card">
        <span class="label">Avg popularity</span>
        <span class="value">${avgPopularity}</span>
        <span class="subvalue">Median position ${medianPosition}</span>
      </div>
    `;
    dashboardPlaylistElements.metrics.hidden = false;
    dashboardPlaylistElements.prompt.hidden = true;
  }

  function resolvePlaylistByName(query, playlists) {
    if (!query) return null;
    const normalized = query.trim().toLowerCase();
    if (!normalized) return null;
    const exact = playlists.find((p) => String(p.name || "").trim().toLowerCase() === normalized);
    if (exact) return exact;
    const partial = playlists.find((p) => String(p.name || "").toLowerCase().includes(normalized));
    return partial || null;
  }

  function populateDashboardPlaylistOptions(playlists) {
    if (!dashboardPlaylistElements.options) return;
    dashboardPlaylistElements.options.innerHTML = "";
    const names = playlists
      .map((p) => p && p.name)
      .filter(Boolean)
      .map((name) => String(name))
      .sort((a, b) => a.localeCompare(b));

    names.forEach((name) => {
      const option = document.createElement("option");
      option.value = name;
      dashboardPlaylistElements.options.appendChild(option);
    });
  }

  function applyDashboardPlaylistSelection(playlists, rawName) {
    const playlist = resolvePlaylistByName(rawName, playlists);
    if (!playlist) {
      if (dashboardPlaylistElements.status) {
        dashboardPlaylistElements.status.textContent = "No matching playlist in the current filters.";
      }
      renderDashboardPlaylistMetrics(null);
      renderPlaylistTracks(null);
      if (playlistEmbedElements.dashboardContainer) {
        playlistEmbedElements.dashboardContainer.hidden = true;
      }
      return;
    }

    selectedPlaylistId = playlist.id;
    if (dashboardPlaylistElements.input) {
      dashboardPlaylistElements.input.value = playlist.name;
    }
    if (dashboardPlaylistElements.status) {
      dashboardPlaylistElements.status.textContent = `Selected: ${playlist.name}`;
    }
    renderDashboardPlaylistMetrics(playlist);
    renderPlaylistTracks(playlist);
    setEmbedForPlaylistInternalId(playlist.id);
  }

  function renderDashboardPlaylistSection(playlists) {
    if (dashboardPlaylistElements.empty) {
      dashboardPlaylistElements.empty.hidden = playlists.length > 0;
    }

    populateDashboardPlaylistOptions(playlists);

    if (!playlists.length) {
      clearDashboardPlaylistSelection();
      if (dashboardPlaylistElements.status) {
        dashboardPlaylistElements.status.textContent = "No playlists match the current filters.";
      }
      return;
    }

    if (!selectedPlaylistId) {
      renderDashboardPlaylistMetrics(null);
      renderPlaylistTracks(null);
      if (playlistEmbedElements.dashboardContainer) {
        playlistEmbedElements.dashboardContainer.hidden = true;
      }
      return;
    }

    const playlist = playlists.find((p) => p.id === selectedPlaylistId) || null;
    if (!playlist) {
      clearDashboardPlaylistSelection();
      return;
    }

    renderDashboardPlaylistMetrics(playlist);
    renderPlaylistTracks(playlist);
    setEmbedForPlaylistInternalId(playlist.id);
  }

  if (dashboardPlaylistElements.clear) {
    dashboardPlaylistElements.clear.addEventListener("click", () => {
      clearDashboardPlaylistSelection();
    });
  }

  if (dashboardPlaylistElements.input) {
    dashboardPlaylistElements.input.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        applyDashboardPlaylistSelection(currentFilteredState?.playlists || [], dashboardPlaylistElements.input.value);
      }
    });
    dashboardPlaylistElements.input.addEventListener("change", () => {
      applyDashboardPlaylistSelection(currentFilteredState?.playlists || [], dashboardPlaylistElements.input.value);
    });
  }

  const state = {
    search: "",
    curatorTypes: new Set(uniqueCuratorTypes),
    minYear: minYearValue,
    maxYear: maxYearValue,
    diasporaOnly: false,
    selectedArtistId: null,
    artistQuery: "",
    selectedRegion: regionIndex.defaultRegion || regionIndex.list[0] || null,
    regionQuery: "",
    selectedCountry: countryIndex.defaultCountry || countryIndex.list[0] || null,
    countryQuery: "",
    activeQuickView: null
  };

  function syncFilterControls() {
    if (elements.search) {
      elements.search.value = state.search;
    }
    if (elements.minYear) {
      elements.minYear.value = state.minYear;
    }
    if (elements.maxYear) {
      elements.maxYear.value = state.maxYear;
    }
    if (elements.diasporaOnly) {
      elements.diasporaOnly.checked = state.diasporaOnly;
    }
  }

  function resetFilters() {
    state.search = "";
    state.curatorTypes = new Set(uniqueCuratorTypes);
    state.minYear = minYearValue;
    state.maxYear = maxYearValue;
    state.diasporaOnly = false;
    state.selectedArtistId = null;
    state.artistQuery = "";
    state.selectedRegion = regionIndex.defaultRegion || regionIndex.list[0] || null;
    state.regionQuery = "";
    state.selectedCountry = countryIndex.defaultCountry || countryIndex.list[0] || null;
    state.countryQuery = "";
    syncFilterControls();
    if (elements.curatorTypes) {
      elements.curatorTypes.querySelectorAll("input[type=checkbox]").forEach((checkbox) => {
        checkbox.checked = true;
      });
    }
    if (artistElements.search) {
      artistElements.search.value = "";
    }
    if (regionElements.search) {
      regionElements.search.value = "";
    }
    if (countryElements.search) {
      countryElements.search.value = "";
    }
  }

  function updateQuickViewStatus() {
    if (!quickViewStatus) return;
    if (state.activeQuickView && quickViewRegistry.has(state.activeQuickView)) {
      quickViewStatus.textContent = quickViewRegistry.get(state.activeQuickView).summary;
    } else {
      quickViewStatus.textContent = "Custom view active — mix filters freely.";
    }
  }

  function syncQuickViewSelect(value) {
    if (!quickViewSelect) return;
    quickViewSelect.value = value || "custom";
  }

  function setActiveQuickView(id) {
    state.activeQuickView = id;
    if (!quickViewButtons.length) {
      updateQuickViewStatus();
      syncQuickViewSelect(id);
      return;
    }
    quickViewButtons.forEach((button) => {
      const isActive = button.dataset.quickView === id;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });
    updateQuickViewStatus();
    syncQuickViewSelect(id);
  }

  function clearActiveQuickView() {
    state.activeQuickView = null;
    quickViewButtons.forEach((button) => {
      button.classList.remove("is-active");
      button.setAttribute("aria-pressed", "false");
    });
    updateQuickViewStatus();
    syncQuickViewSelect("custom");
  }

  function initQuickViewPresets() {
    if (!quickViewButtons.length) {
      if (quickViewSelect) {
        quickViewSelect.innerHTML = [
          '<option value="custom">Custom view</option>',
          ...quickViewPresets.map((preset) => `<option value="${preset.id}">${preset.label}</option>`)
        ].join("");
      }
      return;
    }
    quickViewRegistry.clear();
    quickViewPresets.forEach((preset) => {
      quickViewRegistry.set(preset.id, preset);
    });

    if (quickViewSelect) {
      quickViewSelect.innerHTML = [
        '<option value="custom">Custom view</option>',
        ...quickViewPresets.map((preset) => `<option value="${preset.id}">${preset.label}</option>`)
      ].join("");
      quickViewSelect.addEventListener("change", (event) => {
        const selectedId = event.target.value;
        if (selectedId === "custom") {
          clearActiveQuickView();
          return;
        }
        const preset = quickViewRegistry.get(selectedId);
        if (!preset) {
          clearActiveQuickView();
          return;
        }
        preset.apply();
        syncFilterControls();
        setActiveQuickView(preset.id);
        updateDashboard();
      });
    }

    quickViewButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const { quickView } = button.dataset;
        const preset = quickViewRegistry.get(quickView);
        if (!preset) {
          return;
        }
        preset.apply();
        syncFilterControls();
        setActiveQuickView(preset.id);
        updateDashboard();
      });
    });

    setActiveQuickView(QUICK_VIEW_DEFAULT_ID);
  }

  let hasRenderedInitialView = false;

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
      clearActiveQuickView();
      state.search = event.target.value.trim().toLowerCase();
      updateDashboard();
    });

    elements.curatorTypes.querySelectorAll("input[type=checkbox]").forEach((checkbox) => {
      checkbox.addEventListener("change", (event) => {
        clearActiveQuickView();
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
      clearActiveQuickView();
      const value = Number(event.target.value) || minYearValue;
      state.minYear = Math.max(minYearValue, Math.min(value, state.maxYear));
      event.target.value = state.minYear;
      updateDashboard();
    });

    elements.maxYear.addEventListener("change", (event) => {
      clearActiveQuickView();
      const value = Number(event.target.value) || maxYearValue;
      state.maxYear = Math.min(maxYearValue, Math.max(value, state.minYear));
      event.target.value = state.maxYear;
      updateDashboard();
    });

    elements.diasporaOnly.addEventListener("change", (event) => {
      clearActiveQuickView();
      state.diasporaOnly = event.target.checked;
      updateDashboard();
    });

    elements.reset.addEventListener("click", () => {
      resetFilters();
      setActiveQuickView(QUICK_VIEW_DEFAULT_ID);
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

    if (countryElements.search) {
      countryElements.search.addEventListener("input", (event) => {
        const value = event.target.value;
        state.countryQuery = value;
        const normalized = value.trim().toLowerCase();
        if (!normalized) {
          state.selectedCountry = countryIndex.defaultCountry || countryIndex.list[0] || null;
          updateCountrySpotlight();
          return;
        }
        const match = countryIndex.list.find((country) => country.toLowerCase().includes(normalized));
        state.selectedCountry = match || null;
        updateCountrySpotlight();
      });

      countryElements.search.addEventListener("change", (event) => {
        const value = event.target.value;
        state.countryQuery = value;
        const normalized = value.trim().toLowerCase();
        const exact = countryIndex.list.find((country) => country.toLowerCase() === normalized);
        if (exact) {
          state.selectedCountry = exact;
        }
        updateCountrySpotlight();
      });
    }

    if (countryElements.clear) {
      countryElements.clear.addEventListener("click", () => {
        state.countryQuery = "";
        state.selectedCountry = countryIndex.defaultCountry || countryIndex.list[0] || null;
        if (countryElements.search) {
          countryElements.search.value = "";
        }
        updateCountrySpotlight();
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
            followers: typeof track.artistFollowers === "number" ? track.artistFollowers : null,
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

        if (typeof track.artistFollowers === "number" && track.artistFollowers > 0) {
          entry.followers = track.artistFollowers;
        }

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

    const list = Array.from(counts.entries())
      .filter(([, count]) => count >= MIN_REGION_TRACK_COUNT)
      .map(([region]) => region)
      .sort((a, b) => a.localeCompare(b));
    let defaultRegion = null;
    let maxCount = -1;

    counts.forEach((value, region) => {
      if (value < MIN_REGION_TRACK_COUNT) {
        return;
      }
      if (value > maxCount) {
        maxCount = value;
        defaultRegion = region;
      }
    });

    return { list, counts, defaultRegion };
  }

  function buildCountryIndex(playlists) {
    const counts = new Map();

    playlists.forEach((playlist) => {
      (playlist.tracks || []).forEach((track) => {
        const country = track?.artistCountry || "Unknown";
        counts.set(country, (counts.get(country) || 0) + 1);
      });
    });

    const list = Array.from(counts.entries())
      .filter(([, count]) => count >= MIN_COUNTRY_TRACK_COUNT)
      .map(([country]) => country)
      .sort((a, b) => a.localeCompare(b));

    let defaultCountry = null;
    let maxCount = -1;

    counts.forEach((value, country) => {
      if (value < MIN_COUNTRY_TRACK_COUNT) {
        return;
      }
      if (value > maxCount) {
        maxCount = value;
        defaultCountry = country;
      }
    });

    return { list, counts, defaultCountry };
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
      // Check if features object has any valid numeric values (including 0)
      return Object.values(track.features).some((value) => typeof value === "number" && !isNaN(value));
    }).length;
    const coverage = allTracks.length ? Math.round((tracksWithAudio / allTracks.length) * 100) : 0;

    if (metadataElements.audioStatus) {
      if (coverage === 0) {
        metadataElements.audioStatus.textContent = "Optional: Spotify audio features currently blocked";
        metadataElements.audioStatus.classList.add("is-warning");
        metadataElements.audioStatus.classList.remove("is-success");
      } else {
        metadataElements.audioStatus.textContent = `${coverage}% audio feature coverage (n=${tracksWithAudio})`;
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

    if (elements.filterSummary) {
      if (!tracks.length) {
        elements.filterSummary.textContent = "No playlists match the current filters. Reset or pick another quick view.";
      } else {
        const taggedRegions = tracks
          .map((track) => track.regionGroup || "Unknown")
          .filter((region) => region && region !== "Unknown");
        const uniqueRegionCount = new Set(taggedRegions).size;
        const regionCopy = uniqueRegionCount
          ? `${uniqueRegionCount} region${uniqueRegionCount === 1 ? "" : "s"}`
          : "no tagged regions";
        const releaseYears = tracks
          .map((track) => track.releaseYear)
          .filter((year) => typeof year === "number");
        let releaseCopy = "across unknown release years";
        if (releaseYears.length) {
          const minRelease = Math.min(...releaseYears);
          const maxRelease = Math.max(...releaseYears);
          releaseCopy = minRelease === maxRelease ? `from ${minRelease}` : `from ${minRelease} to ${maxRelease}`;
        }
        const playlistLabel = playlists.length === 1 ? "playlist" : "playlists";
        const trackLabel = tracks.length === 1 ? "track" : "tracks";
        elements.filterSummary.textContent = `Showing ${playlists.length} ${playlistLabel} spanning ${regionCopy} with ${tracks.length} ${trackLabel} ${releaseCopy}.`;
      }
    }
  }

  let selectedPlaylistId = null;

  function renderPlaylistTracks(playlist) {
    if (!playlistTracksPanel || !playlistTracksRows) return;
    if (!playlist) {
      playlistTracksPanel.hidden = true;
      playlistTracksRows.innerHTML = "";
      return;
    }
    const rows = playlist.filteredTracks
      .map((track) => {
        return `
          <tr>
            <td>${track.title}</td>
            <td>${track.artist}</td>
            <td>${track.playlistPosition ?? "--"}</td>
            <td>${typeof track.trackPopularity === "number" ? track.trackPopularity : "--"}</td>
            <td>${track.regionGroup || "Unknown"}</td>
          </tr>
        `;
      })
      .join("");
    playlistTracksRows.innerHTML = rows;
    playlistTracksPanel.hidden = !rows;
  }

  function renderPlaylistTable(playlists) {
    if (!playlists.length) {
      elements.playlistTable.innerHTML = "";
      elements.emptyState.hidden = false;
      renderPlaylistTracks(null);
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
          <tr data-playlist-id="${playlist.id}">
            <td data-label="Playlist">
              <div style="display:flex; flex-direction:column; gap:0.35rem;">
                <strong>${playlist.name}</strong>
                <span class="tag">Launched ${playlist.launchYear}</span>
              </div>
            </td>
            <td data-label="Curator">${playlist.curator}</td>
            <td data-label="Followers">${formatNumber(playlist.followerCount)}</td>
            <td data-label="Unique regions">${uniqueRegions}</td>
            <td data-label="Diaspora share">${formatPercent(diasporaCount, totalTracks)}</td>
            <td data-label="Nigeria share">${formatPercent(nigeriaCount, totalTracks)}</td>
            <td data-label="Avg popularity">${avgPopularity}</td>
            <td data-label="Median position">${medianPosition}</td>
          </tr>
        `;
      })
      .join("");

    elements.playlistTable.innerHTML = rows;

    // Attach click handler to each playlist row
    elements.playlistTable.querySelectorAll("tr[data-playlist-id]").forEach((row) => {
      row.addEventListener("click", () => {
        const playlistId = row.getAttribute("data-playlist-id");
        selectedPlaylistId = playlistId;
        const playlist = playlists.find((p) => p.id === playlistId);
        renderPlaylistTracks(playlist || null);
        if (playlist && playlist.id) {
          setEmbedForPlaylistInternalId(playlist.id);
        }
      });
    });
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
    const followerValueFromTracks = artistTracks.find((track) => typeof track.artistFollowers === "number");
    const spotifyFollowers =
      typeof artistMeta.followers === "number"
        ? artistMeta.followers
        : followerValueFromTracks && typeof followerValueFromTracks.artistFollowers === "number"
          ? followerValueFromTracks.artistFollowers
          : null;

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
    if (artistElements.metricSpotifyFollowers) {
      artistElements.metricSpotifyFollowers.textContent =
        typeof spotifyFollowers === "number" ? formatNumber(spotifyFollowers) : "--";
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
                <td data-label="Playlist">
                  <div class="table-stack">
                    <strong>${row.playlistName}</strong>
                    ${launchTag}
                  </div>
                </td>
                <td data-label="Curator">
                  <div class="table-stack">
                    <span>${row.curator || "--"}</span>
                    <span class="tag">${row.curatorType || "Unknown"}</span>
                  </div>
                </td>
                <td data-label="Tracks">${row.trackCount}</td>
                <td data-label="Median position">${medianDisplay}</td>
                <td data-label="Followers">${formatNumber(row.followerCount || 0)}</td>
                <td data-label="First added">${firstAddedDisplay}</td>
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
                <td data-label="Track">${track.title || "--"}</td>
                <td data-label="Playlist">
                  <div class="table-stack">
                    <span>${track.playlistName || "--"}</span>
                    <span class="tag">${track.playlistCuratorType || "Unknown"}</span>
                  </div>
                </td>
                <td data-label="Position">${positionDisplay}</td>
                <td data-label="Popularity">${popularityDisplay}</td>
                <td data-label="Added">${track.addedAt ? formatDate(track.addedAt) : "--"}</td>
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

  function showCountryPrompt(message) {
    if (!countryElements.empty || !countryElements.content) return;
    countryElements.empty.textContent = message;
    countryElements.empty.hidden = false;
    countryElements.content.hidden = true;
    if (countryElements.flags) {
      countryElements.flags.innerHTML = "";
    }
  }

  function updateCountryTabButtons(availableCountries) {
    countryButtonMap.forEach((button, country) => {
      const hasData = availableCountries.has(country);
      const isActive = hasData && state.selectedCountry === country;
      button.disabled = !hasData;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-selected", String(isActive));
      button.setAttribute("tabindex", isActive ? "0" : "-1");
    });
  }

  function renderCountryDetails(countryName) {
    if (!countryElements.content || !countryElements.empty) return;

    const normalizedCountry = countryName || "Unknown";
    const countryTracks = currentFilteredState.tracks.filter((track) => (track.artistCountry || "Unknown") === normalizedCountry);

    if (!countryTracks.length) {
      showCountryPrompt("This country has no placements under the current filters.");
      return;
    }

    const artistSummaries = new Map();
    const playlistSummaries = new Map();
    const uniquePlaylistFollowers = new Map();
    const regionCounts = new Map();

    let diasporaCount = 0;

    countryTracks.forEach((track) => {
      if (track.diaspora) {
        diasporaCount += 1;
      }

      const region = track.regionGroup || "Unknown";
      regionCounts.set(region, (regionCounts.get(region) || 0) + 1);

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

    const trackCount = countryTracks.length;
    const uniqueArtists = artistSummaries.size;
    const uniquePlaylists = playlistSummaries.size;
    const popularityValues = countryTracks
      .map((track) => track.trackPopularity)
      .filter((value) => typeof value === "number");
    const avgPopularity = popularityValues.length ? average(popularityValues) : null;
    const followerReach = Array.from(uniquePlaylistFollowers.values()).reduce((total, value) => total + (value || 0), 0);
    const diasporaShare = formatPercent(diasporaCount, trackCount);

    const sortedRegions = Array.from(regionCounts.entries()).sort((a, b) => b[1] - a[1]);

    countryElements.empty.hidden = true;
    countryElements.content.hidden = false;

    if (countryElements.name) {
      countryElements.name.textContent = normalizedCountry;
    }
    if (countryElements.summary) {
      countryElements.summary.textContent = `${trackCount} tracks across ${uniquePlaylists} playlists within the active filters.`;
    }
    if (countryElements.flags) {
      const tags = [];
      if (sortedRegions.length) {
        tags.push(`<span class="tag">${sortedRegions[0][0]}</span>`);
      }
      tags.push(`<span class="tag">${diasporaShare} diaspora</span>`);
      countryElements.flags.innerHTML = tags.join(" ");
    }

    if (countryElements.metricTracks) {
      countryElements.metricTracks.textContent = String(trackCount);
    }
    if (countryElements.metricArtists) {
      countryElements.metricArtists.textContent = String(uniqueArtists);
    }
    if (countryElements.metricPlaylists) {
      countryElements.metricPlaylists.textContent = String(uniquePlaylists);
    }
    if (countryElements.metricPopularity) {
      countryElements.metricPopularity.textContent = avgPopularity !== null ? avgPopularity.toFixed(1) : "--";
    }
    if (countryElements.metricDiaspora) {
      countryElements.metricDiaspora.textContent = diasporaShare;
    }
    if (countryElements.metricFollowers) {
      countryElements.metricFollowers.textContent = formatNumber(followerReach);
    }

    if (countryElements.artistRows) {
      const artistRows = Array.from(artistSummaries.values())
        .sort((a, b) => b.trackCount - a.trackCount || a.name.localeCompare(b.name))
        .map((artist) => {
          const avgArtistPopularity = artist.popularity.length ? average(artist.popularity) : null;
          const medianArtistPosition = artist.positions.length ? median(artist.positions) : null;
          const diasporaArtistShare = formatPercent(artist.diasporaPlacements, artist.trackCount);
          return `
            <tr>
              <td data-label="Artist">${artist.name}</td>
              <td data-label="Placements">${artist.trackCount}</td>
              <td data-label="Playlists">${artist.playlists.size}</td>
              <td data-label="Avg popularity">${avgArtistPopularity !== null ? avgArtistPopularity.toFixed(1) : "--"}</td>
              <td data-label="Median position">${medianArtistPosition !== null ? medianArtistPosition.toFixed(0) : "--"}</td>
              <td data-label="Diaspora share">${diasporaArtistShare}</td>
            </tr>
          `;
        });

      countryElements.artistRows.innerHTML = artistRows.length
        ? artistRows.join("")
        : '<tr><td colspan="6">No artist placements for this country within the filters.</td></tr>';
    }

    if (countryElements.playlistRows) {
      const playlistRows = Array.from(playlistSummaries.values())
        .sort((a, b) => b.trackCount - a.trackCount || a.name.localeCompare(b.name))
        .slice(0, 20)
        .map((playlist) => {
          const medianPlaylistPosition = playlist.positions.length ? median(playlist.positions) : null;
          const launchTag = playlist.launchYear ? `<span class="tag">Launched ${playlist.launchYear}</span>` : "";
          return `
            <tr>
              <td data-label="Playlist">
                <div class="table-stack">
                  <strong>${playlist.name}</strong>
                  ${launchTag}
                </div>
              </td>
              <td data-label="Curator">
                <div class="table-stack">
                  <span>${playlist.curator}</span>
                  <span class="tag">${playlist.curatorType}</span>
                </div>
              </td>
              <td data-label="Track placements">${playlist.trackCount}</td>
              <td data-label="Unique artists">${playlist.artists.size}</td>
              <td data-label="Median position">${medianPlaylistPosition !== null ? medianPlaylistPosition.toFixed(0) : "--"}</td>
              <td data-label="Followers">${formatNumber(playlist.followers || 0)}</td>
            </tr>
          `;
        });

      countryElements.playlistRows.innerHTML = playlistRows.length
        ? playlistRows.join("")
        : '<tr><td colspan="6">No playlists surface this country within the filters.</td></tr>';
    }
  }

  function updateCountrySpotlight() {
    if (!countryElements.tabs) return;

    const countryCounts = sumCounts(currentFilteredState.tracks, (track) => track.artistCountry || "Unknown");
    const availableCountries = new Set(
      Object.entries(countryCounts)
        .filter(([, count]) => count >= MIN_COUNTRY_TRACK_COUNT)
        .map(([country]) => country)
    );
    updateCountryTabButtons(availableCountries);

    if (!currentFilteredState.tracks.length) {
      showCountryPrompt("No countries within the current filters.");
      return;
    }

    if (state.countryQuery.trim() && (!state.selectedCountry || !availableCountries.has(state.selectedCountry))) {
      showCountryPrompt("No country matches that search within the current filters.");
      return;
    }

    if (!state.selectedCountry || !availableCountries.has(state.selectedCountry)) {
      const sortedAvailable = Array.from(availableCountries).sort((a, b) => a.localeCompare(b));
      state.selectedCountry = sortedAvailable[0] || null;
    }

    if (!state.selectedCountry) {
      showCountryPrompt("No countries available within the current filters.");
      return;
    }

    renderCountryDetails(state.selectedCountry);
  }

  function initCountrySpotlight() {
    if (!countryElements.tabs || !countryIndex.list.length) {
      if (countryElements.empty) {
        countryElements.empty.textContent = "No countries available in the dataset.";
      }
      return;
    }

    if (!state.selectedCountry) {
      state.selectedCountry = countryIndex.defaultCountry || countryIndex.list[0] || null;
    }

    countryElements.tabs.innerHTML = countryIndex.list
      .map((country) => {
        const isActive = state.selectedCountry === country;
        return `<button type="button" data-country-tab="${country}" role="tab" aria-selected="${isActive}" tabindex="${isActive ? "0" : "-1"}">${country}</button>`;
      })
      .join("");

    countryButtonMap.clear();
    countryElements.tabs.querySelectorAll("button[data-country-tab]").forEach((button) => {
      countryButtonMap.set(button.dataset.countryTab, button);
    });

    countryElements.tabs.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-country-tab]");
      if (!button || button.disabled) return;
      const { countryTab } = button.dataset;
      if (!countryTab) return;
      state.selectedCountry = countryTab;
      state.countryQuery = "";
      if (countryElements.search) {
        countryElements.search.value = "";
      }
      updateCountrySpotlight();
    });

    updateCountrySpotlight();
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

    const regionCounts = sumCounts(currentFilteredState.tracks, (track) => track.regionGroup || "Unknown");
    const availableRegions = new Set(
      Object.entries(regionCounts)
        .filter(([, count]) => count >= MIN_REGION_TRACK_COUNT)
        .map(([region]) => region)
    );
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

      renderDashboardPlaylistSection([]);
      updateCards(filteredPlaylists, filteredTracks);
      updateArtistInspectorView();
      updateRegionSpotlight();
      updateCountrySpotlight();
      return;
    }

    updateCards(filteredPlaylists, filteredTracks);
    updateCharts(filteredTracks, filteredPlaylists);
    renderDashboardPlaylistSection(filteredPlaylists);
    updateArtistInspectorView();
    updateRegionSpotlight();
    updateCountrySpotlight();

    if (!hasRenderedInitialView) {
      hasRenderedInitialView = true;
      if (loadingOverlay) {
        requestAnimationFrame(() => loadingOverlay.classList.add("is-hidden"));
      }
    }
  }

  initFilters();
  initArtistLookup();
  initRegionSpotlight();
  initCountrySpotlight();
  attachListeners();
  initMetadata();
  initQuickViewPresets();
  updateDashboard();
  initChartTabs();

  // Theme management
  function applyTheme(theme) {
    const root = document.documentElement;
    const normalized = theme === "neo" ? "neo" : "classic";
    if (normalized === "neo") {
      root.setAttribute("data-theme", "neo");
    } else {
      root.removeAttribute("data-theme");
    }
    localStorage.setItem("uiTheme", normalized);
    updateThemeToggleLabel(normalized);
  }

  function updateThemeToggleLabel(theme) {
    const btn = document.getElementById("theme-toggle");
    if (!btn) return;
    if (theme === "neo") {
      btn.textContent = "✨ Classic";
      btn.setAttribute("aria-label", "Switch to Classic theme");
      btn.title = "Switch to Classic";
    } else {
      btn.textContent = "🌙 Neo";
      btn.setAttribute("aria-label", "Switch to Neo theme");
      btn.title = "Switch to Neo";
    }
  }

  // Initialize theme from localStorage
  (function initTheme() {
    const saved = localStorage.getItem("uiTheme") || "classic";
    applyTheme(saved);
    const btn = document.getElementById("theme-toggle");
    if (btn) {
      btn.addEventListener("click", () => {
        const current = localStorage.getItem("uiTheme") || "classic";
        applyTheme(current === "neo" ? "classic" : "neo");
      });
    }
  })();

  async function fetchArtistMetadata() {
    const csvPath = "../data/data/artist_metadata.csv";
    try {
      const response = await fetch(csvPath, { cache: "no-store" });
      if (!response.ok) {
        return new Map();
      }
      const text = await response.text();
      return parseArtistCsv(text);
    } catch (error) {
      console.warn("Unable to fetch artist metadata CSV", error);
      return new Map();
    }
  }

  function parseArtistCsv(text) {
    if (!text) {
      return new Map();
    }
    const lines = text.split(/\r?\n/).filter((line) => line.trim().length > 0);
    if (!lines.length) {
      return new Map();
    }
    const header = splitCsvLine(lines[0]).map((item) => item.trim().toLowerCase());
    const colIndex = {
      artist: header.indexOf("artist"),
      artistCountry: header.indexOf("artistcountry"),
      regionGroup: header.indexOf("regiongroup"),
      diaspora: header.indexOf("diaspora"),
    };
    const metadataMap = new Map();
    for (let i = 1; i < lines.length; i += 1) {
      const values = splitCsvLine(lines[i]);
      if (!values.length) continue;
      const artistRaw = values[colIndex.artist] || "";
      const normalized = normalizeArtistName(artistRaw);
      if (!normalized) continue;
      metadataMap.set(normalized, {
        artistCountry: values[colIndex.artistCountry]?.trim() || "Unknown",
        regionGroup: values[colIndex.regionGroup]?.trim() || "Unknown",
        diaspora: normalizeBoolean(values[colIndex.diaspora]),
      });
    }
    return metadataMap;
  }

  function splitCsvLine(line) {
    const result = [];
    let current = "";
    let inQuotes = false;
    for (let i = 0; i < line.length; i += 1) {
      const char = line[i];
      if (char === '"') {
        if (inQuotes && line[i + 1] === '"') {
          current += '"';
          i += 1;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (char === ',' && !inQuotes) {
        result.push(current);
        current = "";
      } else {
        current += char;
      }
    }
    result.push(current);
    return result;
  }

  function normalizeBoolean(value) {
    if (value === undefined || value === null) return false;
    const normalized = String(value).trim().toLowerCase();
    return normalized === "true" || normalized === "1" || normalized === "yes" || normalized === "y";
  }

  function normalizeArtistName(name) {
    if (!name) return "";
    return String(name).split(",")[0].trim().toLowerCase();
  }

  function applyArtistMetadataInPlace(currentDataset, metadataMap) {
    if (!(metadataMap instanceof Map) || !metadataMap.size) {
      return;
    }
    currentDataset.playlists.forEach((playlist) => {
      (playlist.tracks || []).forEach((track) => {
        const normalized = normalizeArtistName(track?.artist);
        if (!normalized) {
          return;
        }
        const meta = metadataMap.get(normalized);
        if (!meta) {
          return;
        }
        track.artistCountry = meta.artistCountry ?? track.artistCountry ?? "Unknown";
        track.regionGroup = meta.regionGroup ?? track.regionGroup ?? "Unknown";
        track.diaspora = Boolean(meta.diaspora);
      });
    });
  }
})();
