# KshKnights weekly report — 2026-10-05

- Data: box scores through 2026-10-02 (30 games this season, 402 prior season)
- Fantasy export: matchdays [1, 2] · file 866a041da2076957
- Window: 2026-10-06 → 2026-10-12 · 10 games
- Model: `heuristic` · validation MAE per game: heuristic 5.83, naive_last_game 7.11
- News check: news check failed: 400 Client Error: Bad Request for url: https://api.anthropic.com/v1/messages

## Transfers
No squad in `config/my_team.yaml`: optimal squad built from scratch.

Budget 100.0 · cost 100.0 · left 0.0 · expected lineup score **164.0** (captain x2, bench 50%)

Formation (G-F-C): **1-2-2** · main 6 = starting five + 6th man · bench G-F-F-C

## Recommended roster
| Role | Pos | Player | Club | Price | Proj | G | Opponents | Last | L4 avg | Season | Min L4 | Δ price | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Captain | F | Sasha Vezenkov | OLY | 17.6 | 25.5 | 1 | vs IST | 23.0 | 27.1 | 28.2 | 23.4 | 1.0 |  |
| Starter | G | Theo Maledon | RMB | 10.0 | 16.1 | 1 | vs PAR | 40.0 | 25.3 | 22.7 | 22.8 | 0.2 |  |
| Starter | F | Azuolas Tubelis | ZAL | 11.6 | 17.5 | 1 | @ BAR | 25.0 | 24.1 | 24.1 | 26.1 | 0.9 |  |
| Starter | C | Aleksander Balcerowski | BAR | 8.3 | 15.2 | 1 | – | – | – | – | – | 0.5 | unmatched |
| Starter | C | Tonye Jekiri | PAR | 8.6 | 14.2 | 1 | @ MAD | 23.1 | 21.8 | 20.9 | 19.6 | 0.9 |  |
| 6th man | G | Elijah Bryant | HTA | 15.3 | 23.7 | 1 | @ PAM | 44.0 | 33.8 | 30.4 | 32.5 | 0.5 |  |
| Bench | G | Luca Vildoza | PAR | 7.8 | 12.3 | 1 | @ MAD | 17.6 | 17.7 | 16.9 | 19.6 | 0.7 |  |
| Bench | F | Leopold Cavaliere | PBB | 4.8 | 6.3 | 1 | vs ASV | 11.0 | 8.0 | 7.3 | 14.9 | 0.0 |  |
| Bench | F | Eleftherios Mantzoukas | PAO | 4.8 | 6.1 | 1 | vs ULK | 7.7 | 13.3 | 13.9 | 22.8 | 0.3 |  |
| Bench | C | Aliou Diarra | VIR | 6.6 | 12.8 | 1 | @ MUN | 33.0 | 24.2 | 21.7 | 23.4 | 0.7 |  |
| Coach | HC | Maxime Lefevre | PBB | 4.6 | 7.5 | 1 | vs ASV | – | – | – | – | -0.8 |  |

## Top 8 core
Sasha Vezenkov (OLY, 25.5), Elijah Bryant (HTA, 23.7), Azuolas Tubelis (ZAL, 17.5), Theo Maledon (RMB, 16.1), Aleksander Balcerowski (BAR, 15.2), Tonye Jekiri (PAR, 14.2), Aliou Diarra (VIR, 12.8), Luca Vildoza (PAR, 12.3)

## Best alternatives by position

**G**

| Player | Club | Price | Proj | Proj/credit | L4 avg | Flags |
|---|---|---|---|---|---|---|
| Carlik Jones | PAR | 14.5 | 19.4 | 1.34 | 24.0 |  |
| Jean Montero | OLY | 13.1 | 17.7 | 1.35 | 15.9 |  |
| Kevin Punter | BAR | 14.0 | 17.7 | 1.26 | 24.0 |  |
| Nadir Hifi | PBB | 14.4 | 17.2 | 1.20 | 14.0 |  |
| Sylvain Francisco | PAO | 14.9 | 17.0 | 1.14 | 18.0 |  |

**F**

| Player | Club | Price | Proj | Proj/credit | L4 avg | Flags |
|---|---|---|---|---|---|---|
| Nikola Mirotic | VBC | 11.8 | 16.7 | 1.41 | 22.1 |  |
| Dario Saric | EFS | 14.9 | 16.3 | 1.10 | 17.4 |  |
| Chima Moneke | CZV | 15.2 | 16.1 | 1.06 | 14.5 |  |
| Dwayne Bacon | DUB | 13.5 | 15.8 | 1.17 | 18.5 |  |
| Kameron Taylor | VBC | 12.6 | 15.1 | 1.20 | 16.3 |  |

**C**

| Player | Club | Price | Proj | Proj/credit | L4 avg | Flags |
|---|---|---|---|---|---|---|
| Jonas Valanciunas | ZAL | 15.9 | 19.1 | 1.20 | 20.0 |  |
| Nikola Milutinov | OLY | 14.8 | 17.8 | 1.20 | 3.3 |  |
| Moses Wright | MIL | 13.7 | 17.5 | 1.28 | 16.1 |  |
| Mfiondu Kabengele | DUB | 14.5 | 17.3 | 1.20 | 17.5 |  |
| Walter Tavares | RMB | 14.3 | 15.7 | 1.10 | 17.8 |  |

**HC**

| Player | Club | Price | Proj | Proj/credit | L4 avg | Flags |
|---|---|---|---|---|---|---|
| Georgios Bartzokas | OLY | 10.3 | 10.5 | 1.02 | – |  |
| Xavier Albert | VBC | 7.1 | 8.5 | 1.19 | – |  |
| Zeljko Obradovic | PAO | 10.3 | 7.1 | 0.69 | – |  |
| Pedro Martinez | RMB | 8.7 | 6.0 | 0.69 | – |  |
| Aleksander Sekulic | BAR | 8.1 | 5.6 | 0.69 | – |  |

## Value picks (projection per credit, ≤ 7.0 credits)
| Pos | Player | Club | Price | Proj | Proj/credit |
|---|---|---|---|---|---|
| G | Sebastian Herrera | PBB | 5.1 | 5.9 | 1.17 |
| C | Usman Garuba | RMB | 6.0 | 6.8 | 1.13 |
| F | Amath M'baye | PBB | 6.3 | 7.0 | 1.11 |
| F | David Lighty | ASV | 5.1 | 5.6 | 1.11 |
| F | Edgaras Ulanovas | ZAL | 6.4 | 7.0 | 1.10 |
| F | Konstantinos Mitoglou | PAO | 5.9 | 6.4 | 1.08 |
| G | Josep Puerto | VBC | 5.3 | 5.6 | 1.05 |
| F | Mikael Jantunen | RMB | 6.1 | 6.4 | 1.04 |

## Availability / data flags (most expensive first)
| Player | Club | Price | Flag | Source |
|---|---|---|---|---|
| Amir Coffey | HTA | 12.4 | unmatched |  |
| Patrick Baldwin Jr | CZV | 10.5 | unmatched |  |
| Johnny Juzang | FBT | 9.9 | DNP last 1 |  |
| Tosan Evbuomwan | BAR | 9.3 | unmatched |  |
| Mathis Dossou-yovo | ASV | 9.3 | unmatched |  |
| Tyty Washington | ASV | 9.2 | unmatched |  |
| Maozinha Pereira | PBB | 9.2 | unmatched |  |
| Kevin Kokila | VIR | 8.8 | unmatched |  |
| Mo Gueye | VBC | 8.6 | unmatched |  |
| Aleksander Balcerowski | BAR | 8.3 | unmatched |  |
| Max Shulga | RMB | 7.9 | unmatched |  |
| Eugene German | HTA | 7.7 | DNP last 1 |  |
| Chris Silva | FBT | 7.6 | DNP last 1 |  |
| Mam Jaiteh | DUB | 6.7 | unmatched |  |
| Kaodirichi Akobundu-Ehiogu | ZAL | 6.6 | unmatched |  |

## Unmatched fantasy players (projection = fantasy season average)
Abdu Kone (BAR), Aleksander Balcerowski (BAR), Amir Coffey (HTA), Andrej Bjelic (CZV), Andrija Susic (BAY), Antonis Karagiannidis (OLY), Caspar Vossenberg (BAY), Darius Karutasu (EFS), Davide Casarin (VIR), Frederic Bourdillon (HTA), George Papas (OLY), Georgios Bourneles (OLY), Iason Varvaritis (PAO), Kaodirichi Akobundu-Ehiogu (ZAL), Kevin Kokila (VIR), Lucas Mari (VBC), Mam Jaiteh (DUB), Maozinha Pereira (PBB), Mathis Dossou-yovo (ASV), Max Heidegger (HTA), Max Shulga (RMB), Mo Gueye (VBC), Niko Jerkic (BAY), Nikola Djurisic (CZV), Nobel Boungou-colo (PBB), Patrick Baldwin Jr (CZV), Pedro Souza (KBA), Shane Hunter (MTA), Thierry Henry Alves de Souza (KBA), Tosan Evbuomwan (BAR), Tyty Washington (ASV), Uros Danilovic (PAR), Vojin Medarevic (CZV), Yagiz Aksu (BJK)

Fix persistent mismatches in `config/overrides.yaml`.

---
Proj = projected fantasy points over the window (sum over games), after volatility penalty and availability discount. Last/L4/Season are fantasy points computed from box scores (PIR, +10% on wins).