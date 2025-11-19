# 🎵 Afrobeats Observatory Dashboards

Two interactive dashboard implementations for analyzing gatekeeping patterns in Spotify's Afrobeats ecosystem:

## 📊 Dashboard Options

### 1. **Enhanced Streamlit Dashboard** (Recommended for Analysis)
**File**: `scripts/dashboard.py`

**Features**:
- ✅ Custom academic theme matching web design
- ✅ 5 tabbed sections: Overview, Regional Analysis, Temporal Trends, Label Distribution, Methodology
- ✅ Real-time filtering with visual feedback
- ✅ Dataset metadata explorer
- ✅ CSV export functionality
- ✅ Responsive metrics cards with icons

**Run Command**:
```powershell
streamlit run scripts/dashboard.py
```

**Access**: Opens automatically at `http://localhost:8501`

---

### 2. **Plotly Dash Dashboard** (Production-Ready Alternative)
**File**: `scripts/dashboard_dash.py`

**Features**:
- ✅ Bootstrap CYBORG theme for polished UI
- ✅ Reactive callbacks for instant updates
- ✅ Production-grade architecture
- ✅ Custom CSS styling
- ✅ Tabbed interface with methodology section
- ✅ Interactive data tables with sorting

**Run Command**:
```powershell
python scripts/dashboard_dash.py
```

**Access**: Navigate to `http://localhost:8050`

---

## 🚀 Quick Start

### Install Dependencies

```powershell
pip install -r requirements-dashboards.txt
```

### Run Streamlit (Enhanced Version)

```powershell
cd "c:\Users\Rilwan\OneDrive\DATA SCIENCE COURSE\Newtest"
streamlit run scripts/dashboard.py
```

### Run Plotly Dash (Alternative)

```powershell
cd "c:\Users\Rilwan\OneDrive\DATA SCIENCE COURSE\Newtest"
python scripts/dashboard_dash.py
```

---

## 🎨 Design Features

### Streamlit Enhancements
- **Custom Theme**: `.streamlit/config.toml` with academic color palette (#FFB400 accent on dark gradient)
- **CSS Injection**: Professional metric cards, tab styling, section dividers
- **Academic Branding**: MSc dissertation badge, citations, methodology
- **UX Improvements**: Icons, better labels, collapsible sections

### Dash Implementation
- **Bootstrap Components**: Professional card layouts, responsive grid
- **Custom Styling**: Inline CSS for metric cards, tabs, and tables
- **Reactive Updates**: All charts/tables update simultaneously on filter change
- **Modern UI**: Rounded corners, shadows, accent gradients

---

## 📐 Comparison

| Feature | Streamlit | Plotly Dash |
|---------|-----------|-------------|
| **Setup Complexity** | ⭐⭐ Very Easy | ⭐⭐⭐ Moderate |
| **Customization** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| **Performance** | ⭐⭐⭐⭐ Fast | ⭐⭐⭐⭐⭐ Very Fast |
| **Deployment** | ⭐⭐⭐⭐ Simple | ⭐⭐⭐⭐⭐ Production-ready |
| **Learning Curve** | ⭐⭐ Gentle | ⭐⭐⭐⭐ Steeper |
| **Best For** | Academic demos | Portfolio/Production |

---

## 🎓 MSc Project Integration

Both dashboards include:

### Academic Elements
- ✅ Project title with "MSc Dissertation" badge
- ✅ Research abstract and keywords
- ✅ Methodology section with data collection details
- ✅ BibTeX citation format
- ✅ Dataset metadata display
- ✅ Data quality indicators

### Analytical Features
- ✅ Multi-dimensional filtering (curator, region, label, year, diaspora)
- ✅ Key metrics: Nigeria share, diaspora representation, regional diversity
- ✅ Regional analysis: Choropleth map, country spotlight
- ✅ Temporal trends: Release year distribution, exposure concentration
- ✅ Label distribution: Major vs independent analysis
- ✅ Curator concentration patterns

---

## 📊 Data Requirements

Both dashboards expect:
- **Primary dataset**: `data/processed/afrobeats_playlists.json`
- **Artist metadata**: `data/data/artist_metadata.csv`

Ensure data is current by running:
```powershell
python scripts/fetch_spotify_data.py
```

---

## 🔧 Troubleshooting

### Streamlit Issues

**Theme not applying?**
```powershell
# Clear cache and restart
streamlit cache clear
streamlit run scripts/dashboard.py
```

**Port already in use?**
```powershell
# Run on different port
streamlit run scripts/dashboard.py --server.port 8502
```

### Dash Issues

**Import errors?**
```powershell
pip install --upgrade dash dash-bootstrap-components
```

**Callbacks not firing?**
- Ensure all filters have default values
- Check browser console for JavaScript errors

---

## 🎯 Recommended Workflow

1. **Development/Analysis**: Use **Streamlit** for quick exploration
2. **Presentation/Demo**: Use **Streamlit** for live walkthrough
3. **Portfolio/Production**: Use **Plotly Dash** for hosted deployment
4. **Web Access**: Use static `web/index.html` for GitHub Pages

---

## 📈 Next Steps

### Optional Enhancements
- [ ] Add PDF export (ReportLab integration)
- [ ] Implement URL state sharing (filter persistence)
- [ ] Add statistical significance tests (chi-square, t-tests)
- [ ] Create animated temporal evolution
- [ ] Build comparative playlist mode
- [ ] Add authentication for Dash deployment

### Deployment Options
- **Streamlit Cloud**: Free hosting for Streamlit apps
- **Heroku**: Works for both (Dash recommended)
- **Render**: Modern hosting platform
- **Azure/AWS**: Production-grade infrastructure

---

## 📝 Citation

When using these dashboards, cite as:

```bibtex
@misc{afrobeats_observatory_2025,
  author = {MSc Candidate},
  title = {Afrobeats Playlist Gatekeeping Observatory: Interactive Analysis Platforms},
  year = {2025},
  howpublished = {MSc Computing & Data Science Dissertation},
  note = {Dual implementation: Streamlit (analytical) and Plotly Dash (production)}
}
```

---

## 💡 Tips

**For best experience**:
- Use Chrome/Edge for full feature support
- Enable dark mode for optimal theme rendering
- Adjust zoom to 90-100% for dashboard layout
- Use filters incrementally to understand data distribution

**For presentations**:
- Pre-filter to interesting scenarios
- Use full-screen mode (F11)
- Prepare narrative around key metrics
- Export CSV for backup/validation
