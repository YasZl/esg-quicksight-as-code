# Documentation – ESG Basic Visuals

Ce module implémente les visuels ESG "simples" en utilisant
les vraies classes QuickSight du fichier :

`external/quicksight_assets_class.py`

Les fonctions sont définies dans :

`esg_lib/visuals_basic.py`


## 1. `make_emissions_by_sector_bar`

**But ESG**  
Afficher les émissions totales par secteur pour identifier les secteurs
les plus émetteurs dans le portefeuille.

**Signature**

```python
make_emissions_by_sector_bar(visual_id, dataset_id, mappings)
````

**Mappings attendus**

* `mappings["sector"]` : colonne secteur (ex. `"Sector"`)
* `mappings["emissions_total"]` : colonne émissions totales (ex. `"CO2_Emissions"`)

**Description technique**

* Crée un `BarChartVisual`.
* Ajoute une dimension catégorielle = secteur.
* Ajoute une mesure numérique = émissions (SUM).
* Ajoute un titre : `"Emissions by Sector"`.
* Le `.compile()` renvoie un JSON compatible QuickSight
  (structure avec `"BarChartVisual": { ... }`).

## 2. `make_emissions_over_time_line`

**But ESG**
Analyser l’évolution des émissions dans le temps (tendance).

**Signature**

```python
make_emissions_over_time_line(visual_id, dataset_id, mappings)
```

**Mappings attendus**

* `mappings["date"]` : colonne date / année (ex. `"Year"`)
* `mappings["emissions_total"]` : émissions totales.

**Description technique**

* Crée un `LineChartVisual` de type `"LINE"`.
* Ajoute une dimension date avec granularité `"YEAR"`.
* Ajoute une mesure numérique (SUM des émissions).
* Ajoute un titre : `"Emissions Over Time"`.

## 3. `make_sector_share_pie`

**But ESG**
Voir la part de chaque secteur dans les émissions totales.

**Signature**

```python
make_sector_share_pie(visual_id, dataset_id, mappings)
```

**Mappings attendus**

* `mappings["sector"]`
* `mappings["emissions_total"]`

**Description technique**

* Crée un `PieChartVisual`.
* Dimension = secteur.
* Mesure = émissions (SUM).
* Titre : `"Emission Share by Sector"`.

## 4. `make_total_emissions_kpi`

**But ESG**
Afficher un KPI global : émissions totales du portefeuille.

**Signature**

```python
make_total_emissions_kpi(visual_id, dataset_id, mappings)
```

**Mappings attendus**

* `mappings["emissions_total"]`

**Description technique**

* Crée un `KPIVisual`.
* Ajoute une mesure numérique (SUM des émissions).
* Titre : `"Total Emissions"`.

## 5. `make_emissions_table`

**But ESG**
Lister les holdings / lignes du portefeuille avec les informations
ESG principales (secteur, pays, année, émissions).

**Signature**

```python
make_emissions_table(visual_id, dataset_id, mappings)
```

**Mappings possibles**

* `mappings["company"]` (optionnel si présent)
* `mappings["sector"]`
* `mappings["country"]`
* `mappings["date"]`
* `mappings["emissions_total"]`

**Description technique**

* Crée un `TableVisual`.
* Ajoute des dimensions catégorielles (company, sector, country) si disponibles.
* Ajoute une dimension date (granularité YEAR) si disponible.
* Ajoute une mesure = émissions (SUM).
* Titre : `"Emissions Table (Holdings)"`.

## 6. `build_basic_esg_visuals`

**But**
Construire tous les visuels basiques d’un coup (utile pour des tests
rapides ou un notebook de démonstration).

**Signature**

```python
build_basic_esg_visuals(dataset_id, mappings) -> dict
```

**Retour**

Un dictionnaire de visuels compilés :

```python
{
  "kpi_total_emissions": {...},
  "bar_emissions_by_sector": {...},
  "pie_sector_share": {...},
  "line_emissions_over_time": {...},
  "table_emissions": {...},
}
```

Chaque valeur est le JSON renvoyé par `.compile()` sur le visuel
QuickSight correspondant.

## 7. Lien avec les mappings ESG

Les fonctions de ce module ne connaissent pas les noms de colonnes réelles.
Elles utilisent uniquement les clés logiques du dictionnaire `mappings` :

* `sector`
* `country`
* `date` / `year`
* `emissions_total`
* `carbon_intensity`
* `intensity_target`
* éventuellement `company`

Ces clés sont reliées aux colonnes du dataset dans `esg_lib/column_mapping.py`
(par exemple via `MANAOS_NATURE_MAPPINGS` pour le dataset biodiversité).

```

Tu crées `docs/visuals_basic.md` sur GitHub, tu colles tout ça dedans, tu commit, et c’est bon pour la doc de la Personne 3 ✅.
::contentReference[oaicite:0]{index=0}
```
