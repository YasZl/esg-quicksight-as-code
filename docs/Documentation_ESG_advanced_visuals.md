# Documentation – ESG Advanced Visuals

This module contains all advanced ESG visualizations used later in the dashboard construction.
Each visual is implemented as a reusable Python function and configured through ESG dataset mappings.

# Why do we need advanced visuals?

Advanced visuals allow us to explore the ESG dataset more deeply.  
They make it possible to:

- identify emission hotspots by country, sector, or year,  
- visualize the portfolio composition (e.g., sector × country),  
- detect changes in emissions over time,  
- map geographic exposure of the portfolio,  
- compare current carbon intensity vs target values.

These visuals provide insights that basic charts cannot give.


# What our code does

All advanced visuals are implemented in the file:
`esg_lib/visuals_advanced.py`
Each function creates a visual object from the AWS `quicksight_assets_class.py` module and configures it using the ESG dataset columns through a `mappings` dictionary.
We implemented the following visuals:

1. Heatmap – Emissions by Sector × Year

- Rows = sector  
- Columns = year  
- Values = total emissions  
- Use case: detect which sectors emit the most across time  
- Title added for readability  
- JSON output can be inspected using `.compile()`

2. Treemap – Portfolio Composition

- Groups = country → sector (hierarchy)  
- Size = total emissions  
- Color = carbon intensity  
- Use case: understand which segments of the portfolio dominate in terms of emissions

3. Filled Map – Geographic Emissions

- Geospatial field = country  
- Measure = total emissions (SUM)  
- Use case: visualize the geographic exposure of the portfolio

4. Geospatial Map – Points colored by sector

- Geospatial = country  
- Color = sector  
- Value = emissions  
- Use case: explore ESG exposure geographically using point markers

5. Waterfall – Change in Emissions

- Breakdown = sector  
- Category = year  
- Value = emissions  
- Use case: understand how emissions increased/decreased across sectors between years

6. Gauge – Carbon Intensity vs Target

- Main value = current carbon intensity  
- Target value = intensity objective  
- Use case: KPI to measure portfolio alignment (e.g., Net Zero pathway)

- Filter and parameter logic (Person 2 and 3)  
- Dataset validation (Person 1)

