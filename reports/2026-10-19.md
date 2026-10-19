# KshKnights weekly report — 2026-10-19

- Data: box scores through 2026-10-16 (60 games this season, 402 prior season)
- Fantasy export: matchdays [1, 2] · file 866a041da2076957
- Window: 2026-10-20 → 2026-10-26 · 10 games
- Model: `heuristic` · validation MAE per game: heuristic 5.81, naive_last_game 7.12
- News check: news check failed: 401 Client Error: Unauthorized for url: https://api.anthropic.com/v1/messages

## Transfers
No squad in `config/my_team.yaml`: optimal squad built from scratch.

Budget 100.0 · cost 99.8 · left 0.2 · expected lineup score **162.7** (captain x2, bench 50%)

Formation (G-F-C): **3-1-1** · main 6 = starting five + 6th man · bench G-F-F-C

## Recommended roster
| Role | Pos | Player | Club | Price | Proj | G | Opponents | Last | L4 avg | Season | Min L4 | Δ price | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Captain | G | Elijah Bryant | HTA | 15.3 | 22.3 | 1 | vs VIR | 24.2 | 23.6 | 25.8 | 29.0 | 0.5 |  |
| Starter | G | Theo Maledon | RMB | 10.0 | 19.2 | 1 | @ TEL | 28.6 | 25.7 | 22.5 | 23.7 | 0.2 |  |
| Starter | G | Jean Montero | OLY | 13.1 | 18.9 | 1 | vs ULK | 19.8 | 24.9 | 22.2 | 24.2 | 0.7 |  |
| Starter | F | Mbaye Ndiaye | OLY | 7.3 | 13.8 | 1 | vs ULK | 30.8 | 21.6 | 16.8 | 21.6 | 0.0 |  |
| Starter | C | Aleksander Balcerowski | BAR | 8.3 | 15.2 | 1 | – | – | – | – | – | 0.5 | unmatched |
| 6th man | C | Moses Wright | MIL | 13.7 | 18.4 | 1 | vs BAR | 19.0 | 20.1 | 18.3 | 20.9 | -0.2 |  |
| Bench | G | Andres Feliz | RMB | 6.3 | 14.0 | 1 | @ TEL | 33.0 | 23.1 | 15.1 | 18.9 | 0.4 |  |
| Bench | F | Edwin Jackson | ASV | 4.5 | 5.7 | 1 | @ ZAL | 14.0 | 14.0 | 14.0 | 25.9 | -0.1 |  |
| Bench | F | Nikos Rogkavopoulos | PAO | 4.4 | 5.4 | 1 | vs BAS | 0.0 | 6.3 | 6.8 | 9.5 | -0.1 |  |
| Bench | C | Aliou Diarra | VIR | 6.6 | 13.1 | 1 | @ HTA | 16.5 | 19.8 | 20.2 | 18.7 | 0.7 |  |
| Coach | HC | Zeljko Obradovic | PAO | 10.3 | 13.3 | 1 | vs BAS | – | – | – | – | 0.3 |  |

## Top 8 core
Elijah Bryant (HTA, 22.3), Theo Maledon (RMB, 19.2), Jean Montero (OLY, 18.9), Moses Wright (MIL, 18.4), Aleksander Balcerowski (BAR, 15.2), Andres Feliz (RMB, 14.0), Mbaye Ndiaye (OLY, 13.8), Aliou Diarra (VIR, 13.1)

## Best alternatives by position

**G**

| Player | Club | Price | Proj | Proj/credit | L4 avg | Flags |
|---|---|---|---|---|---|---|
| Sylvain Francisco | PAO | 14.9 | 20.3 | 1.37 | 18.2 |  |
| Kendrick Nunn | PAO | 14.5 | 18.4 | 1.27 | – |  |
| Dzanan Musa | DUB | 13.2 | 17.2 | 1.31 | – |  |
| Nadir Hifi | PBB | 14.4 | 16.7 | 1.16 | 17.2 |  |
| Mike James | EFS | 16.3 | 16.6 | 1.02 | 11.7 |  |

**F**

| Player | Club | Price | Proj | Proj/credit | L4 avg | Flags |
|---|---|---|---|---|---|---|
| Sasha Vezenkov | OLY | 17.6 | 21.5 | 1.22 | 25.8 |  |
| Dwayne Bacon | DUB | 13.5 | 18.4 | 1.36 | 21.1 |  |
| Chima Moneke | CZV | 15.2 | 18.1 | 1.19 | 21.8 |  |
| Dario Saric | EFS | 14.9 | 17.3 | 1.16 | 18.2 |  |
| Zach Leday | HTA | 13.2 | 16.1 | 1.22 | 18.7 |  |

**C**

| Player | Club | Price | Proj | Proj/credit | L4 avg | Flags |
|---|---|---|---|---|---|---|
| Jonas Valanciunas | ZAL | 15.9 | 19.5 | 1.23 | 16.2 |  |
| Mfiondu Kabengele | DUB | 14.5 | 18.3 | 1.26 | 18.6 |  |
| Mathias Lessort | PAO | 15.0 | 17.2 | 1.15 | 17.2 |  |
| Ante Zizic | BJK | 12.0 | 16.6 | 1.38 | 21.0 |  |
| Walter Tavares | RMB | 14.3 | 16.3 | 1.14 | 16.4 |  |

**HC**

| Player | Club | Price | Proj | Proj/credit | L4 avg | Flags |
|---|---|---|---|---|---|---|
| Tomas Masiulis | ZAL | 7.6 | 8.9 | 1.17 | – |  |
| Dimitris Itoudis | HTA | 8.2 | 7.7 | 0.94 | – |  |
| Georgios Bartzokas | OLY | 10.3 | 7.0 | 0.68 | – |  |
| Xavier Albert | VBC | 7.1 | 5.6 | 0.79 | – |  |
| Pedro Martinez | RMB | 8.7 | 4.9 | 0.57 | – |  |

## Value picks (projection per credit, ≤ 7.0 credits)
| Pos | Player | Club | Price | Proj | Proj/credit |
|---|---|---|---|---|---|
| G | Josep Puerto | VBC | 5.3 | 7.4 | 1.41 |
| C | Mouhamed Faye | PBB | 6.6 | 8.9 | 1.35 |
| F | Mikael Jantunen | RMB | 6.1 | 7.1 | 1.17 |
| C | Usman Garuba | RMB | 6.0 | 7.0 | 1.17 |
| F | Oscar Da Silva | BAY | 7.0 | 8.1 | 1.16 |
| F | Dejan Davidovac | CZV | 4.3 | 5.0 | 1.15 |
| F | Konstantinos Mitoglou | PAO | 5.9 | 6.7 | 1.14 |
| G | Kamar Baldwin | BAY | 7.0 | 7.4 | 1.06 |

## Availability / data flags (most expensive first)
| Player | Club | Price | Flag | Source |
|---|---|---|---|---|
| Nikola Milutinov | OLY | 14.8 | DNP last 1 |  |
| Daron Russell | EFS | 10.3 | DNP last 1 |  |
| David Dejulius | BJK | 9.7 | DNP last 1 |  |
| Mathis Dossou-yovo | ASV | 9.3 | unmatched |  |
| Marek Blazevic | ZAL | 9.1 | DNP last 1 |  |
| Mo Gueye | VBC | 8.6 | unmatched |  |
| Santi Yusta | EFS | 8.4 | DNP last 1 |  |
| Aleksander Balcerowski | BAR | 8.3 | unmatched |  |
| Max Shulga | RMB | 7.9 | unmatched |  |
| Mam Jaiteh | DUB | 6.7 | unmatched |  |
| Kaodirichi Akobundu-Ehiogu | ZAL | 6.6 | unmatched |  |
| Antonis Karagiannidis | OLY | 6.4 | unmatched |  |
| Ignas Sargiunas | FBT | 6.2 | DNP last 1 |  |
| Shane Hunter | MTA | 5.8 | unmatched |  |
| Max Heidegger | HTA | 5.7 | unmatched |  |

## Unmatched fantasy players (projection = fantasy season average)
Abdu Kone (BAR), Aleksander Balcerowski (BAR), Andrej Bjelic (CZV), Andrija Susic (BAY), Antonis Karagiannidis (OLY), Caspar Vossenberg (BAY), Darius Karutasu (EFS), Frederic Bourdillon (HTA), George Papas (OLY), Georgios Bourneles (OLY), Iason Varvaritis (PAO), Kaodirichi Akobundu-Ehiogu (ZAL), Lucas Mari (VBC), Mam Jaiteh (DUB), Mathis Dossou-yovo (ASV), Max Heidegger (HTA), Max Shulga (RMB), Mo Gueye (VBC), Niko Jerkic (BAY), Nobel Boungou-colo (PBB), Pedro Souza (KBA), Shane Hunter (MTA), Thierry Henry Alves de Souza (KBA), Uros Danilovic (PAR), Vojin Medarevic (CZV), Yagiz Aksu (BJK)

Fix persistent mismatches in `config/overrides.yaml`.

---
Proj = projected fantasy points over the window (sum over games), after volatility penalty and availability discount. Last/L4/Season are fantasy points computed from box scores (PIR, +10% on wins).