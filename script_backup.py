# ==============================================================================
# Plot efg_rate - three_pt_rate: tirare tante triple garantisce un'efficienza più alta?
# ==============================================================================

# Y: Efficienza Realizzativa Effettiva
Y_efficiency = df_game_clear['efg_pct'].values

# # Regressione lineare: coefs_eff = [pendenza_eff (m), intercetta_eff (q)]
# coefs_2 = np.polyfit(X_volume, Y_efficiency, 1)
# trend_eff_function = np.poly1d(coefs_2)

r2, p_value2 = stats.spearmanr(X_volume, Y_efficiency)
print("efg_rate - three_pt_rate: ",r2, p_value2)

#--- Scatter Plot 2---
scatter = ax2.scatter(
  X_volume,                    # Asse X: Volume tiri da 3
  Y_efficiency,                # Asse Y: Efficienza Effettiva (eFG%)
  c=df_game_clear['season'],   # Colore basato sull'anno (per vedere la transizione)
  cmap='viridis',              # Palette: viola (vecchio) -> giallo (nuovo)
  alpha=0.6,                   # Trasparenza per gestire la sovrapposizione
  edgecolor='none'             # Rimuove il bordo dei punti per pulizia
)


# Usiamo i valori minimi e massimi osservati di X per definire gli estremi della linea
X_eff_range = np.array([X_volume.min(), X_volume.max()])
ax2.plot(
  X_eff_range,
  trend_eff_function(X_eff_range),
  color='red', linestyle='--',
  label=f'y={coefs_2[0]:.2f}x + {coefs_2[1]:.2f}'
)

ax2.set_xlabel('Tiri da 3 (%)')
ax2.set_ylabel('eFG%')

# Vincoliamo gli assi in modo realistico (le percentuali sono tra 0 e 1)
# Un eFG% < 30% o > 70% è quasi impossibile a livello stagionale per un team
#ax2.set_ylim(0, 1)
ax2.grid(True, linestyle=':', alpha=0.5)
#ax2.legend(loc='upper left')


# ==============================================================================
# win_rate - fg_rate: L'efficienza classica è ciò che correla maggiormente con le vittorie?
# ==============================================================================

# # X: Efficienza, Y: Vittorie
# X_fg = df_game_clear['fg_pct'].values

# r4, p_value4 = stats.spearmanr(X_fg, Y_win)
# print("win_rate - fg_rate: ",r4, p_value4)

# scatter4 = ax4.scatter(
#   X_fg, 
#   Y_win, 
#   c=df_game_clear['season'], 
#   cmap='viridis',
#   alpha=0.6, 
#   edgecolor='none'
# )

# ax4.set_xlabel('FG%')
# ax4.set_ylabel('Win (%)')
# #ax4.set_ylim(0, 1)
# ax4.grid(True, linestyle=':', alpha=0.5)






#--------- Prima figura ----------

# ------------------------------
# Plot win_rate - three_pt_rate: Tirare tante triple garantisce più vittorie?
# ------------------------------

X_volume = df_game_clear['three_pt_rate'].values
Y_win = df_game_clear['win_rate'].values

fig1, (ax1) = plt.subplots(1, 1, figsize=(width, height))
plt.subplots_adjust(wspace=0.5)

# Plottiamo i punti individuali
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

# Aggiungiamo una Colorbar unica per spiegare il colore dei punti (la season)
cbar1 = fig1.colorbar(scatter, ax=[ax1], orientation='vertical', pad=0.04)
cbar1.set_label('Stagione', rotation=270, labelpad=15)

# salvo il plot in PDF
# plt.tight_layout()  # Evita che i titoli o le etichette vengano tagliati
cartella_salvataggio = Path(r"C:\Users\calci\OneDrive\Desktop\Lab\Computazionale\DC1\latex\plot")
percorso_finale = cartella_salvataggio / f'win_three.pdf'
plt.savefig(percorso_finale, format='pdf', bbox_inches='tight')
print(f"Salvato con successo in: {percorso_finale}")



#--------- Seconda figura ----------

# --------------------
# win_rate - efg_rate: L'efficienza è ciò che correla maggiormente con le vittorie?
# --------------------

#aggiungere ax4 se serve
fig2, (ax3) = plt.subplots(1, 1, figsize=(width, height))
# Distanzia i grafici orizzontalmente per evitare sovrapposizioni
plt.subplots_adjust(wspace=0.5)

# X: Efficienza, Y: Vittorie
X_eff = df_game_clear['efg_pct'].values

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

# Aggiungiamo una Colorbar unica per spiegare il colore dei punti (la season)
cbar2 = fig2.colorbar(scatter3, ax=[ax3], orientation='vertical', pad=0.04)
cbar2.set_label('Stagione', rotation=270, labelpad=15)

# salvo il plot in PDF
# plt.tight_layout()  # Evita che i titoli o le etichette vengano tagliati
cartella_salvataggio = Path(r"C:\Users\calci\OneDrive\Desktop\Lab\Computazionale\DC1\latex\plot")
percorso_finale = cartella_salvataggio / f'win_efg.pdf'
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