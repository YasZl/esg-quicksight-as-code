# Validation Matrix — Librairie ESG vs Dataset Manaos Nature / Biodiversity

Ce document vérifie la cohérence entre :

1. Les champs “logiques” attendus par la librairie ESG (CO₂-style).
2. Les colonnes effectivement disponibles dans le dataset Manaos Nature / Biodiversity.
3. Les adaptations nécessaires pour utiliser ce dataset dans les visuels / filtres.

---

## 1. Champs logiques de la librairie

Champs “logiques” utilisés typiquement dans `visuals_basic`, `visuals_advanced`,
`filters`, `parameters_esg`, etc. :

- `sector`
- `subsector`
- `country`
- `year`
- `company`
- `isin`
- `emissions_total`
- `scope1`, `scope2`, `scope3`
- `revenue`
- `portfolio_weight`

Ces champs sont mappés dans `esg_lib/column_mapping.py`.

---

## 2. Mapping vers le dataset Manaos Nature / Biodiversity

| Champ logique    | Colonne dataset               | OK ? | Commentaire |
|------------------|-------------------------------|------|-------------|
| sector           | `GICS_SECTOR`                 | Oui   | Secteur principal. |
| subsector        | `NACE_GROUP_CODE`             | Oui  | Approximé par le code NACE (ou `NACE_SECTION_CODE`). |
| country          | `ISSUER_CNTRY_DOMICILE`       | Oui   | Code pays, utilisable en dimension géographique. |
| year             | *(aucune)*                    | Non   | Pas de dimension temporelle dans ce fichier. |
| company          | `PORTFOLIO_NAME`              | Oui   | Approximé par le nom de portefeuille. |
| isin             | `INSTRUMENT_ID`               | Oui  | Identifiant instrument. |
| emissions_total  | `COMPOSITE_INDEX`             | Oui*  | Interprété comme “score composite de biodiversité”. |
| scope1           | *(aucune)*                    | Non  | Pas d’émissions CO₂ Scope1. |
| scope2           | *(aucune)*                    | Non   | Pas d’émissions CO₂ Scope2. |
| scope3           | *(aucune)*                    | Non   | Pas d’émissions CO₂ Scope3. |
| revenue          | `NATURE_RELATED_SPEND_USD_M`  | Oui*  | Proxy “montants nature-related”. |
| portfolio_weight | `NORMALIZED_EXPOSURE_0_1`     | Oui  | Poids de portefeuille normalisé dans [0,1]. |

Oui* = champ disponible mais interprété comme proxy (pas une émission CO₂ réelle).

---

## 3. Impacts sur les visuels et filtres

### 3.1. Visuels type CO₂

Exemples :

- Emissions par secteur (bar chart).
- Emissions par pays (map).
- WACI, intensité carbone, etc.

Avec ce dataset :

- `emissions_total` sera en réalité `COMPOSITE_INDEX` (ou `BIO_SCORE_FLOAT`).
- `portfolio_weight` = `NORMALIZED_EXPOSURE_0_1`.

Les visuels sont donc des **analyses de risque / intensité biodiversité par secteur/pays**,
et non des émissions de CO₂.

### 3.2. Paramètres / filtres

Les paramètres décrits dans le sujet (Year, Country, Sector, SubSector, etc.)
peuvent être mappés comme suit :

- `Year` : **non applicable** (pas de colonne temporelle).
- `Country` : `ISSUER_CNTRY_DOMICILE`.
- `Sector` : `GICS_SECTOR`.
- `SubSector` : `NACE_GROUP_CODE` ou `NACE_SECTION_CODE`.

Les filtres QuickSight peuvent donc être mis en place correctement, avec une restriction :
pas de filtrage par année sur ce dataset.

---

## 4. Conclusion

- La structure logique de la librairie ESG (sector, country, emissions_total, weight)
  est **compatible** avec le dataset Manaos, à condition :
  - d’assumer que “émissions” = indices / scores biodiversité,
  - de documenter clairement cette interprétation.

- Les fonctions de visualisation et de filtres pourront être réutilisées en grande partie,
  mais le wording métier (“CO₂”, “émissions”, “intensité carbone”) devra être adapté à
  la biodiversité (ex. “Biodiversity composite score”, “Nature risk intensity”, etc.).
