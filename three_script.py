import numpy as np
from scipy import stats
import pandas as pd
import sqlite3 as sql
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import dtale as dt
from pathlib import Path
import os

# connect al SQL database
db_path = 'nba.sqlite'
connection = sql.connect(db_path)
print("SQL database connected")
table = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", connection)
print(table)

# Impostiamo lo stile generale dei plot
plt.style.use('bmh')
plt.rc('font', family='serif', serif='Times New Roman')
# Diciamo a Matplotlib di usare un font compatibile con la matematica
plt.rcParams['mathtext.fontset'] = 'cm'
# impostiamo la grandezza dei font degli oggetti principali
plt.rcParams.update({'font.size': 12})        # Font base
plt.rcParams.update({'axes.titlesize': 11})   # Titoli dei grafici
plt.rcParams.update({'axes.labelsize': 12})   # Label dei grafici
plt.rcParams.update({'legend.fontsize': 11})   # Legenda
plt.rcParams.update({'lines.linewidth': 1.5})   # Larghezza linee
plt.rcParams.update({'lines.linestyle': 'solid'})   # Larghezza linee
plt.rcParams.update({'lines.markersize': 5})  # Grandezza marker

# Creiamo una figura
width  = 6
height = width / 1.618

query = """
  WITH stacked_games AS (
    -- Dati squadra in CASA
    SELECT 
      SUBSTR(season_id, 2, 4) AS season,
      team_id_home AS team_id,
      team_name_home AS team_name,
      CASE WHEN wl_home = 'W' THEN 1 ELSE 0 END AS win,
      fgm_home AS fgm,
      fga_home AS fga,
      fg3m_home AS fg3m,
      fg3a_home AS fg3a,
      fta_home AS fta,
      oreb_home AS orb,
      tov_home AS tov,
      dreb_away AS opp_drb -- Rimbalzi difensivi avversari (necessari per ORB%)
    FROM game
    WHERE season_id LIKE '2%'

    UNION ALL

    -- Dati squadra in TRASFERTA
    SELECT 
      SUBSTR(season_id, 2, 4) AS season,
      team_id_away AS team_id,
      team_name_away AS team_name,
      CASE WHEN wl_away = 'W' THEN 1 ELSE 0 END AS win,
      fgm_away AS fgm,
      fga_away AS fga,
      fg3m_away AS fg3m,
      fg3a_away AS fg3a,
      fta_away AS fta,
      oreb_away AS orb,
      tov_away AS tov,
      dreb_home AS opp_drb
    FROM game
    WHERE season_id LIKE '2%'
  )
  -- Ora aggreghiamo tutto per stagione e squadra
  SELECT 
    season,
    team_name,
    AVG(win) AS win_rate,
    SUM(fgm + 0.5 * fg3m) / CAST(SUM(fga) AS FLOAT) AS efg_pct,        -- eFG%
    SUM(fgm) / CAST(SUM(fga) AS FLOAT) AS fg_pct,
    SUM(fg3a) / CAST(SUM(fga) AS FLOAT) AS three_pt_rate,
    SUM(tov) / (SUM(fga) + 0.44 * SUM(fta) + SUM(tov)) AS tov_pct,     -- TOV% (Percentuale possessi persi)
    SUM(orb) / CAST(SUM(orb) + SUM(opp_drb) AS FLOAT) AS orb_pct,      -- ORB% (Percentuale rimbalzi offensivi presi su quelli disponibili)
    COUNT(*) AS total_games
  FROM stacked_games
  GROUP BY season, team_id
  ORDER BY season ASC, win_rate DESC
"""
# creating the pandas object from the query
df_game = pd.read_sql(query, connection).astype({"season": int})
                 
# Pulizia, Filtriamo i dati post-1980
# Visto che prima del 1980 il tiro da 3 non esisteva
df_game_clear = df_game[df_game['season'] > 1984].copy()

d = dt.show(df_game_clear, host='localhost')
#d.open_browser()

#Recuperiamo il valore minimo e massimo della season
start_year = int(df_game_clear['season'].min()) # 1985
end_year = int(df_game_clear['season'].max()) # 2022

#--------- Prima figura ----------

# ------------------------------
# Plot win_rate - three_pt_rate: Tirare tante triple garantisce più vittorie?
# ------------------------------

X_volume = df_game_clear['three_pt_rate'].values
Y_win = df_game_clear['win_rate'].values
Y_season = df_game_clear['season'].values

fig1, (ax1, bx1) = plt.subplots(2, 1, figsize=(width, height + 2))
plt.subplots_adjust(hspace=0.4)

#---- scatter win-tiri da tre
scatter = ax1.scatter(
  X_volume,
  Y_win,
  c=df_game_clear['season'],
  cmap='viridis',
  alpha=0.7,
  edgecolor='none'
)

# Calcolo della regressione lineare
slope1, intercept1, r_value1, p_value1, std_err1 = stats.linregress(X_volume, Y_win)

# Calcoliamo i valori di Y basandoci sulla retta di regressione
line1 = slope1 * X_volume + intercept1
ax1.plot(X_volume, line1, 
         color='red', 
         label=f'r_pearson = {r_value1:.2f}'
)
print("win_rate - three_pt_rate: ",r_value1, p_value1)

ax1.set_xlabel('Tiri da 3')
ax1.set_ylabel('Win')
ax1.grid(True, linestyle=':', alpha=0.5)
ax1.legend(loc='upper left')

#---- scatter season-tiri da tre
scatterb1 = bx1.scatter(
  X_volume,
  Y_season,
  c=df_game_clear['season'],
  cmap='viridis',
  alpha=0.7,
  edgecolor='none'
)

# Calcolo della regressione lineare
slope1b, intercept1b, r_value1b, p_value1b, std_err1b = stats.linregress(X_volume, Y_season)

line1b = slope1b * X_volume + intercept1b
bx1.plot(X_volume, line1b,
         color='red', 
         label=f'r_pearson = {r_value1b:.2f}'
)
print("three_pt_rate - stagione: ",r_value1b, p_value1b)

bx1.set_yticks(np.arange(1985, 2025, 10)) # Imposta i segni ogni 5 anni dal 1985 al 2023
bx1.set_xlabel('Tiri da 3')
bx1.set_ylabel('Stagione')
bx1.grid(True, linestyle=':', alpha=0.5)
bx1.legend(loc='upper left')

# Aggiungiamo una Colorbar unica per spiegare il colore dei punti (la season)
cbar1 = fig1.colorbar(scatter, ax=[ax1], orientation='vertical', pad=0.04)
cbar1.set_label('Stagione', rotation=270, labelpad=15)

# salvo il plot in PDF
# plt.tight_layout()  # Evita che i titoli o le etichette vengano tagliati
cartella_salvataggio = Path(r"C:\Users\calci\OneDrive\Desktop\Lab\Computazionale\DC1\latex\plot")
percorso_finale = cartella_salvataggio / f'win_three_season.pdf'
plt.savefig(percorso_finale, format='pdf', bbox_inches='tight')
print(f"Salvato con successo in: {percorso_finale}")



#--------- Seconda figura ----------

# --------------------
# win_rate - efg_rate: L'efficienza è ciò che correla maggiormente con le vittorie?
# --------------------

#aggiungere ax4 se serve
fig2, (ax3, bx3) = plt.subplots(2, 1, figsize=(width, height + 2))
# Distanzia i grafici orizzontalmente per evitare sovrapposizioni
plt.subplots_adjust(hspace=0.5)

# X: Efficienza, Y: Vittorie
X_eff = df_game_clear['efg_pct'].values

#---- scatter efg - win
scatter3 = ax3.scatter(
  X_eff, 
  Y_win, 
  c=df_game_clear['season'], 
  cmap='viridis',
  alpha=0.7, 
  edgecolor='none'
)

# Calcolo della regressione lineare
# slope (m) è la pendenza, intercept (q) è l'intercetta, r_value3 è coeff di pearson
slope3, intercept3, r_value3, p_value3, std_err3 = stats.linregress(X_eff, Y_win)

# Calcoliamo i valori di Y basandoci sulla retta di regressione
line3 = slope3 * X_eff + intercept3
ax3.plot(X_eff, line3, 
         color='red', 
         label=f'r_pearson = {r_value3:.2f}'
)
print("win_rate - efg_rate: ",r_value3, p_value3)

ax3.set_xlabel('eFG%')
ax3.set_ylabel('Win')
ax3.grid(True, linestyle=':', alpha=0.5)
ax3.legend(loc='upper left')

#---- scatter efg - season
scatterb3 = bx3.scatter(
  X_eff, 
  Y_season, 
  c=df_game_clear['season'], 
  cmap='viridis',
  alpha=0.7, 
  edgecolor='none'
)

# Calcolo della regressione lineare
# slope (m) è la pendenza, intercept (q) è l'intercetta, r_value3 è coeff di pearson
slopeb3, interceptb3, r_valueb3, p_valueb3, std_errb3 = stats.linregress(X_eff, Y_season)

# Calcoliamo i valori di Y basandoci sulla retta di regressione
lineb3 = slopeb3 * X_eff + interceptb3
bx3.plot(X_eff, lineb3, 
         color='red', 
         label=f'r_pearson = {r_valueb3:.2f}'
)
print("efg_rate - stagione: ",r_valueb3, p_valueb3)

bx3.set_yticks(np.arange(1985, 2025, 10))
bx3.set_xlabel('eFG%')
bx3.set_ylabel('Stagione')
bx3.grid(True, linestyle=':', alpha=0.5)
bx3.legend(loc='upper left')

# Aggiungiamo una Colorbar unica per spiegare il colore dei punti (la season)
cbar2 = fig2.colorbar(scatter3, ax=[ax3], orientation='vertical', pad=0.04)
cbar2.set_label('Stagione', rotation=270, labelpad=15)

# salvo il plot in PDF
# plt.tight_layout()  # Evita che i titoli o le etichette vengano tagliati
cartella_salvataggio = Path(r"C:\Users\calci\OneDrive\Desktop\Lab\Computazionale\DC1\latex\plot")
percorso_finale = cartella_salvataggio / f'win_efg_season.pdf'
plt.savefig(percorso_finale, format='pdf', bbox_inches='tight')
print(f"Salvato con successo in: {percorso_finale}")


# ---------- terza figura -----------

fig3, (ax4, ax5) = plt.subplots(2, 1, figsize=(width , height + 2))
# Distanzia i grafici orizzontalmente per evitare sovrapposizioni
plt.subplots_adjust(hspace=0.4)

X_orb = df_game_clear["orb_pct"].values
X_tov = df_game_clear["tov_pct"].values

scatter4 = ax4.scatter(
  X_orb, 
  Y_win, 
  c=df_game_clear['season'], 
  cmap='viridis',
  alpha=0.7, 
  edgecolor='none'
)

# Calcolo della regressione lineare
slope4, intercept4, r_value4, p_value4, std_err4 = stats.linregress(X_orb, Y_win)
line4 = slope4 * X_orb + intercept4

ax4.plot(X_orb, line4, 
         color='red', 
         label=f'r_pearson = {r_value4:.2f}'
)
print("win_rate - orb_pct: ",r_value4, p_value4)
r_value4b, p_value4b = stats.pearsonr(X_orb, Y_season)
print("orb_ptc - stagione: ",r_value4b, p_value4b)

ax4.set_xlabel("ORB%")
ax4.set_ylabel("Win")
ax4.legend()

scatter5 = ax5.scatter(
  X_tov, 
  Y_win, 
  c=df_game_clear['season'], 
  cmap='viridis',
  alpha=0.7, 
  edgecolor='none'
)

# Calcolo della regressione lineare
slope5, intercept5, r_value5, p_value5, std_err5 = stats.linregress(X_tov, Y_win)
line5 = slope5 * X_tov + intercept5

ax5.plot(X_tov, line5, 
         color='red', 
         label=f'r_pearson = {r_value5:.2f}'
)
print("win_rate - tov_pct: ",r_value5, p_value5)
r_value5b, p_value5b = stats.pearsonr(X_tov, Y_season)
print("tov_ptc - stagione: ",r_value5b, p_value5b)

ax5.set_xlabel("TOV%")
ax5.set_ylabel("Win")
ax5.legend()

cbar3 = fig3.colorbar(scatter4, ax=[ax4, ax5], orientation='vertical', pad=0.04)
cbar3.set_label('Stagione', rotation=270, labelpad=15)

cartella_salvataggio = Path(r"C:\Users\calci\OneDrive\Desktop\Lab\Computazionale\DC1\latex\plot")
percorso_finale = cartella_salvataggio / f'orb_tov_rate.pdf'
plt.savefig(percorso_finale, format='pdf', bbox_inches='tight')
print(f"Salvato con successo in: {percorso_finale}")

plt.show()
input("Premi INVIO per chiudere il server e terminare lo script...")