# QuickSight Column Mapping — Manaos ESG Nature / Biodiversity

Ce document définit le mapping entre les colonnes du dataset ESG et
les types / rôles QuickSight (DIMENSION vs MEASURE).

Les types QuickSight possibles sont :

- **STRING**
- **INTEGER**
- **DECIMAL**
- **DATETIME**
- **BOOLEAN**

## 1. Colonnes d’identification / structure

| Colonne               | Type pandas | Type QuickSight | Rôle       | Commentaire |
|-----------------------|------------|-----------------|-----------|-------------|
| INSTRUMENT_ID         | object     | STRING          | Dimension | Identifiant d’instrument. |
| PORTFOLIO_ID          | object     | STRING          | Dimension | Identifiant de portefeuille. |
| PORTFOLIO_NAME        | object     | STRING          | Dimension | Nom du portefeuille (label). |
| ISSUER_CNTRY_DOMICILE | object     | STRING          | Dimension | Code pays ; à déclarer en rôle géographique "Country". |
| NACE_GROUP_CODE       | float64    | DECIMAL / INT   | Dimension | Code NACE groupe (peut être casté en INTEGER ou converti en STRING). |
| NACE_SECTION_CODE     | object     | STRING          | Dimension | Section NACE (A, B, C…). |
| GICS_SECTOR           | object     | STRING          | Dimension | Secteur GICS — dimension sectorielle principale. |

## 2. Scores biodiversité / nature

| Colonne               | Type pandas | Type QuickSight | Rôle    |
|-----------------------|------------|-----------------|--------|
| BIO_SCORE_FLOAT       | float64    | DECIMAL         | Mesure |
| BIO_SCORE_INT         | float64    | DECIMAL / INT   | Mesure |
| BIO_SCORE_GRADE       | object     | STRING          | Dimension |
| BIO_SCORE_GRADE_NUM   | float64    | DECIMAL / INT   | Mesure |
| BIO_POLICY_TEXT       | object     | STRING          | Dimension (tooltip / détail) |
| BIO_POLICY_TEXT_NUM   | float64    | DECIMAL         | Mesure |
| BIODIV_EXPOSURE_INDEX | float64    | DECIMAL         | Mesure |
| BIO_SCORE_DECILE      | float64    | DECIMAL / INT   | Mesure |

## 3. Indicateurs nature / risque / dépendance

| Colonne                        | Type pandas | Type QS | Rôle    |
|--------------------------------|------------|---------|--------|
| NORMALIZED_EXPOSURE_0_1        | float64    | DECIMAL | Mesure (poids) |
| PROTECTED_AREAS_OVERLAP_PCT    | float64    | DECIMAL | Mesure |
| PROXIMITY_TO_PA_KM             | float64    | DECIMAL | Mesure |
| LAND_CONVERSION_HA_SINCE_2020  | float64    | DECIMAL | Mesure |
| PCT_SUPPLY_TRACEABLE           | float64    | DECIMAL | Mesure |
| HCV_ASSESSMENTS_COUNT          | float64    | DECIMAL | Mesure |
| IUCN_CR_SPECIES_IMPACTED       | float64    | DECIMAL | Mesure |
| WATER_BOD_PROXIMITY_RISK       | object     | STRING  | Dimension (catégorie de risque) |
| WATER_BOD_PROXIMITY_RISK_NUM   | float64    | DECIMAL | Mesure |
| TNFD_READY                     | object     | STRING  | Dimension (Yes/No) |
| TNFD_READY_NUM                 | float64    | DECIMAL | Mesure |
| DISCLOSURE_QUALITY             | object     | STRING  | Dimension |
| DATA_QUALITY_SCORE             | float64    | DECIMAL | Mesure |
| DATA_GAPS_FLAG                 | object     | STRING  | Dimension (Yes/No) |
| OPERATES_IN_KEY_BIOME          | object     | STRING  | Dimension (Yes/No) |
| PRESSURE_SCORE                 | float64    | DECIMAL | Mesure |
| RESPONSE_SCORE                 | float64    | DECIMAL | Mesure |
| STATE_SCORE                    | float64    | DECIMAL | Mesure |
| WEIGHT_PRESSURE                | float64    | DECIMAL | Mesure |
| WEIGHT_RESPONSE                | float64    | DECIMAL | Mesure |
| WEIGHT_STATE                   | float64    | DECIMAL | Mesure |
| COMPOSITE_INDEX                | float64    | DECIMAL | Mesure |

## 4. Indicateurs financiers / exposure nature

| Colonne                      | Type pandas | Type QS | Rôle    |
|------------------------------|------------|---------|--------|
| HABITAT_DEPENDENCY_PCT       | float64    | DECIMAL | Mesure |
| SUPPLY_FOREST_RISK_PCT       | float64    | DECIMAL | Mesure |
| RESTORATION_AREA_HA          | float64    | DECIMAL | Mesure |
| NATURE_RELATED_SPEND_USD_M   | float64    | DECIMAL | Mesure |

## 5. Recommandations QuickSight

- **Dimension géographique** :  
  - `ISSUER_CNTRY_DOMICILE` → rôle géographique = *Country*.

- **Dimension sectorielle** :  
  - `GICS_SECTOR` comme dimension principale pour les analyses par secteur.  
  - `NACE_GROUP_CODE` et `NACE_SECTION_CODE` pour des vues plus granulaires.

- **Mesure principale ESG (proxy “émissions / intensité”)** :  
  - `COMPOSITE_INDEX` ou `BIO_SCORE_FLOAT` selon le récit du dashboard.

- **Poids de portefeuille / allocation** :  
  - `NORMALIZED_EXPOSURE_0_1` comme *Weight* générique.  
  - `NATURE_RELATED_SPEND_USD_M` pour des vues monétaires (dépenses nature).
