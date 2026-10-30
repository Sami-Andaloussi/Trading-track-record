# Corrections à reporter dans `data/*.py`

Les fichiers `track_record/*.md` et les notebooks ont été corrigés à la main, parce que `data/*.py` n'est pas dans le dépôt. **Avant tout nouveau `python3 src/build_notebooks.py`, reporte chaque correction ci-dessous dans le `data/YYYY-MM.py` du mois**, sinon le build les écrase.

Pour chaque correction : l'ancien texte, puis le nouveau. Seules les phrases modifiées sont citées ; le reste du paragraphe ne change pas. Une fois tout reporté, `python3 src/build_notebooks.py --execute` doit redonner exactement les fichiers du dépôt (vérifie avec `git diff`).

## Ce qui ne demande rien dans `data/`

- **Notebooks** (`global_track_record.ipynb`, `years/2023.ipynb`, `years/2024.ipynb`) : l'avertissement sous le titre vient de `SAMPLE_NOTE` dans `src/build_notebooks.py`, et la vue « account-level » (+14,8 %, 0,45 % par R) a été retirée de `src/`. Le build les régénère tels quels.
- **README.md** : il n'est pas généré, rien à reporter.
- **Nouveau champ `r_note`** : `meta_line()` dans `src/build_notebooks.py` l'affiche après « closed » quand un trade fermé n'a pas de `r`. Ces trades restent hors des totaux (comme avant, `closed_entries()` exige un `r`).

## Mars 2023 — `data/2023-03.py`

Avant :

> I sized this down to 35% of my normal risk going in — US CPI was coming up and the Fed was in a genuinely uncertain spot because of the banking crisis, and I was already carrying dollar exposure through an AUD/USD short.

Après :

> I sized this down to 35% of my normal risk going in — US CPI was coming up and the Fed was in a genuinely uncertain spot because of the banking crisis.

**En-tête de trade** — Champs : `status` `"open"` → `"closed"`, supprimer `floating_r`, ajouter `r_note: "exit not logged"` (laisser `r` vide).

Avant :

> ***USDJPY** · long · still open · +1.05R floating · 2023-03*

Après :

> ***USDJPY** · long · closed · exit not logged · 2023-03*

Avant :

> This is the position still open as the month closes out, sitting on a floating profit of roughly +1.05R, carrying over into April.

Après :

> It was still open as the month closed out, sitting on a floating profit of roughly +1.05R. I closed it later but never wrote up the exit, so it isn't counted in this month's numbers or in the journal's totals.

## Octobre 2023 — `data/2023-10.py`

Avant :

> That's exactly the mistake I'd tell anyone else never to make, and it's a reminder that even with a decade in the market, the obvious mistakes are still there to make.

Après :

> That's exactly the mistake I'd tell anyone else never to make.

Avant :

> If I'd caught this one, October wouldn't have closed negative, which says something about how much execution discipline — actually being there to take the trade — matters as much as being right.

Après :

> If I'd caught this one, October would have been a much better month, which says something about how much execution discipline — actually being there to take the trade — matters as much as being right.

## Décembre 2023 — `data/2023-12.py`

Avant :

> I didn't really want to re-trade EUR/AUD at this point — I already had AUD exposure through NZD/CAD (long) and AUD/CAD (long, entered the day before), and I think I still had AUD/CHF open too.

Après :

> I didn't really want to re-trade EUR/AUD at this point — I already had AUD exposure through NZD/CAD (long) and AUD/CAD (long, entered the day before).

## Janvier 2024 — `data/2024-01.py`

Avant :

> This one continued the same idea behind a position I still had open at month-end (+0.12R floating, an extremely similar setup).

Après :

> This one continued the same idea behind a second AUD/USD long, described at the end of this entry.

Ajouter, juste après la phrase :

> AUD/USD did break higher shortly after, and I re-entered at close to the same price.

la phrase :

> That re-entry was still open at month-end (+0.12R floating); I closed it later but never wrote up the exit, so it isn't counted in the journal's numbers.

## Mars 2024 — `data/2024-03.py`

**En-tête de trade** — Champs : `status` `"open"` → `"closed"`, supprimer `floating_r`, ajouter `r_note: "exit not logged"` (laisser `r` vide).

Avant :

> ***SPX500** · long · still open · +0.65R floating · 2024-03*

Après :

> ***SPX500** · long · closed · exit not logged · 2024-03*

Avant :

> The day before writing this, I closed 50% of the position at a fresh all-time high; the other half is still open, and I'm expecting new highs into early April.

Après :

> The day before writing this, I closed 50% of the position at a fresh all-time high; the other half was still open at month-end (+0.65R floating), and I was expecting new highs into early April. I closed it later but never wrote up the exit, so it isn't counted in the journal's numbers.

## Mai 2024 — `data/2024-05.py`

**En-tête de trade** — Champs : garder `status: "closed"` sans `r`, ajouter `r_note: "R not recorded"`.

Avant :

> ***NZDCAD** · short · closed · May 01, 2024*

Après :

> ***NZDCAD** · short · closed · R not recorded · May 01, 2024*

Ajouter, juste après la phrase :

> It ended up being my biggest loss of the month, but I don't have any real complaint about how I got into it or managed it — some trades just don't work, even when everything lines up on paper.

la phrase :

> I didn't keep the exact R on this one, so it isn't counted in this month's numbers or in the journal's totals.

## Juillet 2024 — `data/2024-07.py`

Avant :

> Between that signal and the same bounce pattern repeating, I cut another 25% on Wednesday, right ahead of the ECB rate decision.

Après :

> Between that signal and the same bounce pattern repeating, I tightened my stop on the remaining 25% on Wednesday, right ahead of the ECB rate decision.

**Paragraphe ajouté** (dans le `body`, juste après le premier paragraphe du NZD/CAD long du 09.07) :

> That was a break from my own rule. When two positions carry the same exposure I cut the size of each, as I did on the USD/CHF long in February 2023 or the USD/CAD long in June. Here I opened two positions on the same CAD thesis on the same day and didn't size either one down, so I had roughly double the risk on a single idea. The result doesn't change that: the rule was broken.

Avant :

> Same bearish-CAD thesis as the NZD/CAD long I put on earlier the same day, but this time there was no adverse surprise waiting on the other side — no RBNZ-style shock — so the thesis actually got to play out in full.

Après :

> Same bearish-CAD thesis as the NZD/CAD long I put on earlier the same day. This was the second half of the doubled CAD bet I flag in that entry. This time there was no adverse surprise waiting on the other side, no RBNZ-style shock, so the thesis actually got to play out in full.

## Août 2024 — `data/2024-08.py`

Avant :

> The thesis here was a monetary policy divergence trade: the RBA was still holding a hawkish line, with core inflation running at 3.9% in Q2 2024, while the RBNZ had just delivered its first rate cut with core inflation down at 2.8%.

Après :

> The thesis here was a monetary policy divergence trade: the RBA was still holding a hawkish line, with core inflation running at 3.9% in Q2 2024, while the RBNZ had just delivered its first rate cut on August 14th, taking the OCR from 5.50% to 5.25%, with headline inflation down to 3.3% in Q2 and the bank saying it was heading back inside its 1-3% target band.

## Septembre 2024 — `data/2024-09.py`

**En-tête de trade** — Champs : `status` `"open"` → `"closed"`, supprimer `floating_r`, ajouter `r_note: "exit not logged"` (laisser `r` vide).

Avant :

> ***AUDNZD** · long · still open · +0.40R floating · 2024-09*

Après :

> ***AUDNZD** · long · closed · exit not logged · 2024-09*

Avant :

> No fireworks yet — it's sitting on a small floating profit (~+0.4R) as of writing this.

Après :

> No fireworks — it was sitting on a small floating profit (~+0.4R) when I wrote this. I closed it before stopping trading at the end of September 2024, but never wrote up the exit, so it isn't counted in the journal's numbers.
