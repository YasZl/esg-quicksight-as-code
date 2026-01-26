# Data Quality Report — Manaos ESG Nature / Biodiversity

Ce rapport décrit la qualité du dataset ESG fourni pour le projet Manaos
(biodiversité / nature), après un nettoyage léger appliqué dans le notebook.

## 1. Description générale du dataset

- Fichier source : `ESG_BIG.csv`
- Nombre de lignes initial : **252 517**
- Nombre de colonnes : **44**
- Nombre de lignes après nettoyage (`df_clean`) : **165 938**

Le nettoyage appliqué :

1. Suppression des lignes sans `PORTFOLIO_ID` **ou** `PORTFOLIO_NAME`.
2. Suppression des lignes ayant plus de 50 % de valeurs manquantes.
3. Nettoyage des chaînes de caractères (`strip()`).
4. Normalisation des drapeaux (Yes/No) pour certaines colonnes (sans forcer en booléen).

Le dataset contient des informations sur :

- les instruments (`INSTRUMENT_ID`) et portefeuilles (`PORTFOLIO_ID`, `PORTFOLIO_NAME`),
- des caractéristiques pays / secteur (`ISSUER_CNTRY_DOMICILE`, `GICS_SECTOR`, NACE),
- des scores de biodiversité (BIO_SCORE\*, COMPOSITE_INDEX, PRESSURE/RESPONSE/STATE),
- des indicateurs de risque, traçabilité, restauration, dépenses nature, etc.

Il s’agit d’un dataset **Nature / Biodiversity**, pas d’un dataset CO₂ classique
(Scope1/2/3, émissions, revenue). Les KPIs “émissions” devront donc utiliser
des colonnes proxy adaptées à la biodiversité.

---

## 2. Profils de colonnes

### 2.1. Colonnes d’identification / structure

| Colonne               | Type    | Rôle principal                | Commentaire |
|-----------------------|---------|-------------------------------|-------------|
| `INSTRUMENT_ID`       | object  | Identifiant instrument        | Id unique ou quasi-unique de la ligne instrument/portefeuille. |
| `PORTFOLIO_ID`        | object  | Identifiant portefeuille      | Identifie le portefeuille. Utilisé pour des filtres et agrégations. |
| `PORTFOLIO_NAME`      | object  | Nom du portefeuille           | Libellé lisible par humain. |
| `ISSUER_CNTRY_DOMICILE` | object | Pays de domiciliation        | Code pays (ex : `FR`, `US`, `CA`). À utiliser comme dimension géographique. |
| `NACE_GROUP_CODE`     | float64 | Code NACE (groupe)           | Code de secteur économique, sert de sous-secteur. |
| `NACE_SECTION_CODE`   | object  | Section NACE                  | Catégorie NACE de haut niveau (A, B, C, …). |
| `GICS_SECTOR`         | object  | Secteur GICS                  | Dimension sectorielle principale pour les analyses. |

### 2.2. Scores biodiversité / nature

| Colonne                    | Type    | Description |
|----------------------------|---------|-------------|
| `BIO_SCORE_FLOAT`          | float64 | Score de biodiversité (version décimale). |
| `BIO_SCORE_INT`            | float64 | Score de biodiversité (version entière). |
| `BIO_SCORE_GRADE`          | object  | Grade (A, B, C, …) associé au score. |
| `BIO_SCORE_GRADE_NUM`      | float64 | Version numérique du grade. |
| `BIO_POLICY_TEXT`          | object  | Description textuelle de la politique biodiversité. |
| `BIO_POLICY_TEXT_NUM`      | float64 | Encodage numérique de cette politique. |
| `BIODIV_EXPOSURE_INDEX`    | float64 | Indice d’exposition biodiversité. |
| `BIO_SCORE_DECILE`         | float64 | Décile du score biodiversité (1 à 10). |

### 2.3. Indicateurs nature / risque / dépendance

| Colonne                        | Type    | Description |
|--------------------------------|---------|-------------|
| `NORMALIZED_EXPOSURE_0_1`      | float64 | Exposition normalisée dans [0, 1]. Excellent candidat pour un poids de portefeuille. |
| `PROTECTED_AREAS_OVERLAP_PCT`  | float64 | % de recouvrement avec des zones protégées. |
| `PROXIMITY_TO_PA_KM`           | float64 | Proximité des zones protégées (km). |
| `LAND_CONVERSION_HA_SINCE_2020` | float64 | Surface convertie depuis 2020 (hectares). |
| `PCT_SUPPLY_TRACEABLE`         | float64 | % de la supply chain traçable. |
| `HCV_ASSESSMENTS_COUNT`        | float64 | Nombre d’évaluations HCV. |
| `IUCN_CR_SPECIES_IMPACTED`     | float64 | Nombre d’espèces en danger critique (IUCN CR) potentiellement impactées. |
| `WATER_BOD_PROXIMITY_RISK`     | object  | Catégorie de risque lié à la proximité de rejets (Biochemical Oxygen Demand). |
| `WATER_BOD_PROXIMITY_RISK_NUM` | float64 | Version numérique du risque de proximité BOD. |
| `TNFD_READY`                   | object  | Flag textuel indiquant la readiness TNFD. |
| `TNFD_READY_NUM`               | float64 | Score numeric TNFD ready. |
| `DISCLOSURE_QUALITY`           | object  | Qualité de la divulgation (catégorie). |
| `DATA_QUALITY_SCORE`           | float64 | Score de qualité des données. |
| `DATA_GAPS_FLAG`               | object  | Indique s’il existe des gaps de données. |
| `OPERATES_IN_KEY_BIOME`        | object  | Indique si l’entité opère dans un biome clé. |
| `PRESSURE_SCORE`               | float64 | Score de pression. |
| `RESPONSE_SCORE`               | float64 | Score de réponse (mesures / politiques). |
| `STATE_SCORE`                  | float64 | Score d’état. |
| `WEIGHT_PRESSURE`              | float64 | Poids associé à la dimension pression. |
| `WEIGHT_RESPONSE`              | float64 | Poids associé à la dimension réponse. |
| `WEIGHT_STATE`                 | float64 | Poids associé à la dimension état. |
| `COMPOSITE_INDEX`              | float64 | Indice composite global (pression / réponse / état combinés). |

### 2.4. Indicateurs financiers / exposure nature

| Colonne                      | Type    | Description |
|------------------------------|---------|-------------|
| `HABITAT_DEPENDENCY_PCT`     | float64 | % de dépendance à l’habitat. |
| `SUPPLY_FOREST_RISK_PCT`     | float64 | % de supply chain associée à un risque forêt. |
| `RESTORATION_AREA_HA`        | float64 | Surface de restauration (hectares). |
| `NATURE_RELATED_SPEND_USD_M` | float64 | Montants engagés liés à la nature (en millions USD). |

---

## 3. Valeurs manquantes et filtrage

- Après filtrage, il reste **165 938** lignes sur 252 517 (~66 %).
- Les lignes retirées sont principalement celles :
  - sans `PORTFOLIO_ID` ou `PORTFOLIO_NAME`,
  - ou avec plus de 50 % de valeurs manquantes.

En général :

- Les colonnes d’identification (`INSTRUMENT_ID`, `PORTFOLIO_ID`, `PORTFOLIO_NAME`) sont largement renseignées.
- Plusieurs indicateurs avancés (ex. `HCV_ASSESSMENTS_COUNT`, `IUCN_CR_SPECIES_IMPACTED`) peuvent contenir plus de valeurs nulles, ce qui est attendu (données disponibles seulement pour certaines entreprises).

---

## 4. Anomalies / points de vigilance

- **Types de données**  
  - Les colonnes quantitatives sont correctement typées en `float64`.
  - Les colonnes catégorielles sont en `object` (strings) : secteurs, pays, qualité de divulgation, flags.

- **Drapeaux (flags)**  
  - `NO_NET_DEFORESTATION`, `NDPE_POLICY`, `RSPO_MEMBER`, `TNFD_READY`, `DATA_GAPS_FLAG`, `OPERATES_IN_KEY_BIOME` contenaient des valeurs hétérogènes (`Yes`, `No`, `Y`, `N`, `TRUE`, `FALSE`, etc.).  
  - Elles ont été harmonisées en valeurs texte `Yes` / `No` (sans forcer en booléen).

- **Absence de colonnes CO₂ / intensité carbone**  
  - Il n’y a **pas** de colonnes `Scope1`, `Scope2`, `Scope3`, `Revenue`, `Weight` comme dans un dataset CO₂ classique.
  - Les KPIs type WACI / émissions devront utiliser :
    - `COMPOSITE_INDEX` ou `BIO_SCORE_FLOAT` comme mesure “principal risk/intensity proxy”.
    - `NORMALIZED_EXPOSURE_0_1` comme poids de portefeuille.

---

## 5. Conclusion

- Le dataset est de **bonne qualité structurelle** pour un usage BI dans QuickSight :
  - Colonnes bien typées.
  - Dimensions sectorielles / géographiques bien identifiées.
  - Métriques multiples pour construire des KPIs biodiversité et nature.
- Le nettoyage appliqué filtre les lignes les plus incomplètes, tout en conservant une volumétrie importante (~166k lignes).
- Le principal point d’attention est **conceptuel** : ce dataset est centré sur la nature / biodiversité, pas sur les émissions CO₂.  
  La documentation des dashboards devra clairement refléter que les “émissions” et “intensités” sont basées sur des **proxies biodiversité** (`COMPOSITE_INDEX`, `BIO_SCORE_FLOAT`, etc.) plutôt que sur des tonnes de CO₂.
