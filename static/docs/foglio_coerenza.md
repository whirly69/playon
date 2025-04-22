
# 🧩 Foglio di Coerenza - Gestione Formazioni

Questo documento raccoglie le convenzioni usate nel progetto per evitare inconsistenze tra modifiche successive.

---

## ✅ ID HTML fissi

| ID                   | Descrizione                                 |
|----------------------|---------------------------------------------|
| convocati-list       | Lista dei giocatori convocati               |
| team1-list           | Lista dei giocatori squadra "Rossi"         |
| team2-list           | Lista dei giocatori squadra "Blu"           |
| progress-team1       | Barra di avanzamento squadra Rossi          |
| progress-team2       | Barra di avanzamento squadra Blu            |
| summary-team1        | Resoconto squadra Rossi                     |
| summary-team2        | Resoconto squadra Blu                       |
| vote-inputs-container| Contenitore input voti per generazione auto |

---

## 🎯 Classi CSS

| Classe               | Descrizione                                 |
|----------------------|---------------------------------------------|
| list-group-item      | Elementi delle liste di giocatori           |
| vote-stars           | Container stelle votazione                  |
| btn-outline-primary  | Pulsante assegnazione a squadra Blu         |
| btn-outline-danger   | Pulsante assegnazione a squadra Rossi       |
| btn-outline-secondary| Pulsante rimozione da squadra               |

---

## 🔧 Funzioni JavaScript Globali

| Funzione                       | Scopo                                 |
|--------------------------------|---------------------------------------|
| assign(playerId, team)         | Sposta un giocatore in una squadra    |
| removeFromTeam(playerId)       | Rimuove un giocatore dalla squadra    |
| createPlayerItem(player)       | Crea un elemento per lista convocati  |
| createTeamItem(player, team)   | Crea un elemento per lista squadra    |
| createStars(playerId, initial) | Crea le stelle per la votazione       |
| updateCounters()               | Aggiorna contatori e resoconti        |
| getSummary(players, teamId)    | Genera sommario per una squadra       |
| renderSummary(summary, id)     | Inserisce HTML del resoconto          |

---

## 🧠 Variabili JavaScript Globali

| Variabile            | Descrizione                                 |
|----------------------|---------------------------------------------|
| parsedPlayers        | Lista dei giocatori convocati               |
| parsedAssignments    | Dizionario {playerId: team}                 |
| mode                 | Modalità attiva (manual, auto_simple, ...)  |

---

## ✨ Modalità speciali

- `mode === "auto_simple"` attiva:
  - Stelle per voti (createStars)
  - Pulsante "Genera formazioni"
  - Voti inizializzati a 3 stelle

---

## 📌 Note

- I giocatori già assegnati **non devono** essere spostati durante la generazione automatica.
- L'ordinamento dei ruoli è definito nella costante `ROLE_ORDER`.
- Le squadre non devono mai superare il numero massimo (`match.players_per_team`).
- I resoconti devono aggiornarsi **in tempo reale**.

