# KshKnights weekly report — 2026-10-12

- Data: box scores through 2026-10-09 (40 games this season, 402 prior season)
- Fantasy export: matchdays [1, 2] · file 866a041da2076957
- Window: 2026-10-13 → 2026-10-19 · 20 games
- Model: `heuristic` · validation MAE per game: heuristic 5.86, naive_last_game 7.19
- News check: news check failed: 401 Client Error: Unauthorized for url: https://api.anthropic.com/v1/messages

## Transfers
No squad in `config/my_team.yaml`: optimal squad built from scratch.

Budget 100.0 · cost 100.0 · left 0.0 · expected lineup score **311.4** (captain x2, bench 50%)

Formation (G-F-C): **3-1-1** · main 6 = starting five + 6th man · bench G-F-F-C

## Recommended roster
| Role | Pos | Player | Club | Price | Proj | G | Opponents | Last | L4 avg | Season | Min L4 | Δ price | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Captain | G | Elijah Bryant | HTA | 15.3 | 46.7 | 2 | vs BES, @ PAN | 23.0 | 30.5 | 28.5 | 32.2 | 0.5 |  |
| Starter | G | Carlik Jones | PAR | 14.5 | 38.1 | 2 | vs PAN, @ ULK | 27.0 | 24.4 | 26.6 | 26.1 | 1.4 |  |
| Starter | G | Theo Maledon | RMB | 10.0 | 32.8 | 2 | vs ASV, @ MIL | 13.2 | 21.3 | 20.3 | 22.5 | 0.2 |  |
| Starter | F | Mbaye Ndiaye | OLY | 7.3 | 24.7 | 2 | @ PAM, @ BAR | 15.4 | 17.5 | 14.7 | 16.1 | 0.0 |  |
| Starter | C | Moses Wright | MIL | 13.7 | 36.9 | 2 | vs MAD, vs DUB | 32.0 | 22.8 | 19.1 | 26.0 | -0.2 |  |
| 6th man | C | Aleksander Balcerowski | BAR | 8.3 | 30.4 | 2 | – | – | – | – | – | 0.5 | unmatched |
| Bench | G | Josep Puerto | VBC | 5.3 | 12.0 | 2 | vs OLY, vs TEL | 7.7 | 7.4 | 6.9 | 14.3 | 0.1 |  |
| Bench | F | Semi Ojeleye | CZV | 7.5 | 23.6 | 2 | vs PRS, @ ASV | 18.7 | 14.7 | 13.2 | 24.3 | 0.2 |  |
| Bench | F | Nikos Rogkavopoulos | PAO | 4.4 | 12.3 | 2 | vs HTA, @ PAR | 14.3 | 9.7 | 8.5 | 7.2 | -0.1 |  |
| Bench | C | Aliou Diarra | VIR | 6.6 | 29.0 | 2 | vs BAS, @ PRS | 19.8 | 23.2 | 21.2 | 21.8 | 0.7 |  |
| Coach | HC | Xavier Albert | VBC | 7.1 | 16.7 | 2 | vs OLY, vs TEL | – | – | – | – | 0.6 |  |

## Top 8 core
Elijah Bryant (HTA, 46.7), Carlik Jones (PAR, 38.1), Moses Wright (MIL, 36.9), Theo Maledon (RMB, 32.8), Aleksander Balcerowski (BAR, 30.4), Aliou Diarra (VIR, 29.0), Mbaye Ndiaye (OLY, 24.7), Semi Ojeleye (CZV, 23.6)

## Best alternatives by position

**G**

| Player | Club | Price | Proj | Proj/credit | L4 avg | Flags |
|---|---|---|---|---|---|---|
| Sylvain Francisco | PAO | 14.9 | 39.1 | 2.62 | 19.3 |  |
| Jean Montero | OLY | 13.1 | 35.9 | 2.74 | 18.4 |  |
| Dzanan Musa | DUB | 13.2 | 35.3 | 2.68 | – |  |
| Kendrick Nunn | PAO | 14.5 | 33.8 | 2.33 | – |  |
| Nadir Hifi | PBB | 14.4 | 33.2 | 2.30 | 17.2 |  |

**F**

| Player | Club | Price | Proj | Proj/credit | L4 avg | Flags |
|---|---|---|---|---|---|---|
| Sasha Vezenkov | OLY | 17.6 | 41.9 | 2.38 | 19.0 |  |
| Jordan Nwora | CZV | 12.8 | 32.6 | 2.55 | 15.3 |  |
| Dwayne Bacon | DUB | 13.5 | 32.5 | 2.41 | 16.3 |  |
| Kameron Taylor | VBC | 12.6 | 32.3 | 2.57 | 18.0 |  |
| Azuolas Tubelis | ZAL | 11.6 | 31.2 | 2.69 | 18.8 |  |

**C**

| Player | Club | Price | Proj | Proj/credit | L4 avg | Flags |
|---|---|---|---|---|---|---|
| Jonas Valanciunas | ZAL | 15.9 | 38.8 | 2.44 | 20.4 |  |
| Mathias Lessort | PAO | 15.0 | 36.5 | 2.43 | 24.6 |  |
| Walter Tavares | RMB | 14.3 | 33.8 | 2.36 | 17.6 |  |
| Mfiondu Kabengele | DUB | 14.5 | 33.6 | 2.32 | 14.1 |  |
| Nikola Milutinov | OLY | 14.8 | 33.1 | 2.23 | 10.8 |  |

**HC**

| Player | Club | Price | Proj | Proj/credit | L4 avg | Flags |
|---|---|---|---|---|---|---|
| Zeljko Obradovic | PAO | 10.3 | 16.4 | 1.60 | – |  |
| Pedro Martinez | RMB | 8.7 | 14.5 | 1.67 | – |  |
| Ibon Navarro | CZV | 6.7 | 14.1 | 2.10 | – |  |
| Saras Jasikevicius | FBT | 9.0 | 13.8 | 1.53 | – |  |
| Aleksander Sekulic | BAR | 8.1 | 10.5 | 1.30 | – |  |

## Value picks (projection per credit, ≤ 7.0 credits)
| Pos | Player | Club | Price | Proj | Proj/credit |
|---|---|---|---|---|---|
| F | Konstantinos Mitoglou | PAO | 5.9 | 15.6 | 2.65 |
| F | Leopold Cavaliere | PBB | 4.8 | 11.7 | 2.44 |
| C | Usman Garuba | RMB | 6.0 | 14.4 | 2.40 |
| G | Andres Feliz | RMB | 6.3 | 14.3 | 2.27 |
| F | Oscar Da Silva | BAY | 7.0 | 15.7 | 2.25 |
| F | Justin Anderson | DUB | 6.4 | 13.7 | 2.14 |
| F | Eleftherios Mantzoukas | PAO | 4.8 | 10.2 | 2.12 |
| F | Edgaras Ulanovas | ZAL | 6.4 | 13.4 | 2.10 |

## Availability / data flags (most expensive first)
| Player | Club | Price | Flag | Source |
|---|---|---|---|---|
| Filip Petrusev | DUB | 12.5 | DNP last 1 |  |
| Amir Coffey | HTA | 12.4 | unmatched |  |
| Mathis Dossou-yovo | ASV | 9.3 | unmatched |  |
| Tyty Washington | ASV | 9.2 | unmatched |  |
| Maozinha Pereira | PBB | 9.2 | unmatched |  |
| Mo Gueye | VBC | 8.6 | unmatched |  |
| Aleksander Balcerowski | BAR | 8.3 | unmatched |  |
| Max Shulga | RMB | 7.9 | unmatched |  |
| Mam Jaiteh | DUB | 6.7 | unmatched |  |
| Myles Cale | ASV | 6.7 | DNP last 1 |  |
| Kaodirichi Akobundu-Ehiogu | ZAL | 6.6 | unmatched |  |
| Antonis Karagiannidis | OLY | 6.4 | unmatched |  |
| Agustin Ubal | BAR | 6.0 | DNP last 3 |  |
| Shane Hunter | MTA | 5.8 | unmatched |  |
| Max Heidegger | HTA | 5.7 | unmatched |  |

## Unmatched fantasy players (projection = fantasy season average)
Abdu Kone (BAR), Aleksander Balcerowski (BAR), Amir Coffey (HTA), Andrej Bjelic (CZV), Andrija Susic (BAY), Antonis Karagiannidis (OLY), Caspar Vossenberg (BAY), Darius Karutasu (EFS), Davide Casarin (VIR), Frederic Bourdillon (HTA), George Papas (OLY), Georgios Bourneles (OLY), Iason Varvaritis (PAO), Kaodirichi Akobundu-Ehiogu (ZAL), Lucas Mari (VBC), Mam Jaiteh (DUB), Maozinha Pereira (PBB), Mathis Dossou-yovo (ASV), Max Heidegger (HTA), Max Shulga (RMB), Mo Gueye (VBC), Niko Jerkic (BAY), Nikola Djurisic (CZV), Nobel Boungou-colo (PBB), Pedro Souza (KBA), Shane Hunter (MTA), Thierry Henry Alves de Souza (KBA), Tyty Washington (ASV), Uros Danilovic (PAR), Vojin Medarevic (CZV), Yagiz Aksu (BJK)

Fix persistent mismatches in `config/overrides.yaml`.

---
Proj = projected fantasy points over the window (sum over games), after volatility penalty and availability discount. Last/L4/Season are fantasy points computed from box scores (PIR, +10% on wins).