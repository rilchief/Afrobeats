# Afrobeats Playlist Bias Analysis

## Regional representation

Chi-square = 225.47, df = 36, p-value = 0.0000

## Label representation

Chi-square = 0.00, df = 0, p-value = 1.0000

## Track popularity across curator types

ANOVA F = 21.76, p = 0.0000

Kruskal-Wallis H = 38.89, p = 0.0000

## Artist popularity across curator types

ANOVA F = 22.43, p = 0.0000

Kruskal-Wallis H = 27.24, p = 0.0000

## Artist follower counts across curator types

ANOVA F = 1.78, p = 0.1493, eta^2 = 0.004

Kruskal-Wallis H = 16.72, p = 0.0008

|Group A|Group B|t|p_adj|Cohen d|
|---|---|---|---|---|
|Independent Curator|Media Publisher|1.91|0.3432|0.13|
|Independent Curator|Festival Curator|1.69|0.5686|0.15|
|Independent Curator|User-Generated|1.17|1.0000|0.10|
|User-Generated|Media Publisher|0.07|1.0000|0.01|
|User-Generated|Festival Curator|0.48|1.0000|0.09|

## Release year across curator types

ANOVA F = 8.11, p = 0.0000

Kruskal-Wallis H = 121.65, p = 0.0000

## Top recurring artists

                 artist  playlist_count
                   Rema              13
       Davido, Omah Lay              11
              Burna Boy              11
  Shallipopi, Burna Boy              10
                  Asake               9
Burna Boy, Travis Scott               8
             Ayra Starr               8
 DJ Tunez, Wizkid, FOLA               7
        Olamide, Wizkid               7
     Ayra Starr, Wizkid               7

## Statistical Analysis

### Rich-Get-Richer Dynamics: Popularity vs. Playlist Coverage

Using the processed playlist data in `data/processed/afrobeats_playlists.json`, a track-level dataset was constructed where each row corresponds to a unique track and includes its Spotify popularity score and the number of curated Afrobeats playlists in which it appears.

For each track (n ≈ 886), a popularity score was computed (mean Spotify popularity across all appearances) and a playlist coverage measure was derived (the number of distinct curated playlists that include the track). The relationship between these two variables was quantified using Pearson and Spearman correlations.

The results show a moderately positive and highly statistically significant association between popularity and playlist coverage:

- Pearson correlation: r ≈ 0.31 (p < 1e-20)
- Spearman correlation: ρ ≈ 0.37 (p < 1e-29)

These values indicate that more popular tracks tend to appear on a larger number of curated Afrobeats playlists. In other words, once a track becomes popular, it is more likely to be repeatedly surfaced across multiple curated lists, reinforcing its visibility. This pattern is consistent with a "rich-get-richer" feedback loop in Afrobeats playlist curation.

### Multivariate Drivers of Popularity (Regression Analysis)

To understand which artist and catalog characteristics are associated with higher Spotify popularity, a multiple linear regression model was estimated with track popularity as the dependent variable and release year, diaspora status, artist region group and label type as predictors. The model explains around 9–10% of the variance in popularity (R² ≈ 0.10, adjusted R² ≈ 0.09) and is statistically significant overall, indicating that these factors together capture some of the structural drivers of success.

Using the baseline region as a reference category, several regions show substantially higher popularity scores even after controlling for other variables. In particular, tracks from Central Africa, North America, Northern Europe and especially Southern Africa are between roughly +29 and +38 popularity points higher than the baseline region (all p < 0.05). Other regions have positive but non-significant coefficients, suggesting weaker or more uncertain effects.

Overall, the regression results suggest that geography and catalog infrastructure continue to matter for Afrobeats success on Spotify. Some regions and label contexts are systematically associated with higher track popularity, even after accounting for release timing, which supports the idea that structural factors beyond listener preference influence which Afrobeats tracks become "successful" on the platform.

