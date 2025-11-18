# esg_lib/visuals_basic.py

class GenericVisual:
    """Generic visual object with basic expected methods."""
    
    def __init__(self, visual_type, dataset_id):
        self.visual_type = visual_type
        self.dataset_id = dataset_id
        self.dimensions = []
        self.measures = []
        self.title = ""

    def add_dimension(self, dim):
        self.dimensions.append(dim)

    def add_measure(self, measure):
        self.measures.append(measure)

    def add_title(self, title):
        self.title = title

    def compile(self):
        """Returns a generic dict representation"""
        return {
            "Type": self.visual_type,
            "DatasetId": self.dataset_id,
            "Dimensions": self.dimensions,
            "Measures": self.measures,
            "Title": self.title
        }


# ---------------------------------------------------------
# 1. Emissions by Sector (Bar Chart)
# ---------------------------------------------------------

def make_emissions_by_sector_bar(dataset_id, mappings):
    """
    mappings = { "sector": "...", "emissions": "..." }
    """
    vis = GenericVisual("bar_chart", dataset_id)

    vis.add_dimension(mappings["sector"])
    vis.add_measure(mappings["emissions"])
    vis.add_title("Emissions by Sector")

    return vis.compile()


# ---------------------------------------------------------
# 2. Emissions Over Time (Line Chart)
# ---------------------------------------------------------

def make_emissions_over_time_line(dataset_id, mappings):
    """
    mappings = { "date": "...", "emissions": "..." }
    """
    vis = GenericVisual("line_chart", dataset_id)

    vis.add_dimension(mappings["date"])
    vis.add_measure(mappings["emissions"])
    vis.add_title("Emissions Over Time")

    return vis.compile()


# ---------------------------------------------------------
# 3. Sector Share (Pie Chart)
# ---------------------------------------------------------

def make_sector_share_pie(dataset_id, mappings):
    """
    mappings = { "sector": "...", "emissions": "..." }
    """
    vis = GenericVisual("pie_chart", dataset_id)

    vis.add_dimension(mappings["sector"])
    vis.add_measure(mappings["emissions"])
    vis.add_title("Emission Share by Sector")

    return vis.compile()


# ---------------------------------------------------------
# 4. Total Emissions (KPI)
# ---------------------------------------------------------

def make_total_emissions_kpi(dataset_id, mappings):
    """
    mappings = { "emissions": "..." }
    """
    vis = GenericVisual("kpi", dataset_id)

    vis.add_measure(mappings["emissions"])
    vis.add_title("Total Emissions")

    return vis.compile()


# ---------------------------------------------------------
# 5. Emissions Table
# ---------------------------------------------------------

def make_emissions_table(dataset_id, mappings):
    """
    mappings = {
        "sector": "...",
        "emissions": "...",
        "date": "..."   (optional)
    }
    """
    vis = GenericVisual("table", dataset_id)

    if "sector" in mappings:
        vis.add_dimension(mappings["sector"])
    if "date" in mappings:
        vis.add_dimension(mappings["date"])

    vis.add_measure(mappings["emissions"])
    vis.add_title("Emissions Table")

    return vis.compile()

"""

dataset_id = "ESG_DATASET_001"
mappings = {
    "sector": "Sector",
    "emissions": "CO2_Emissions"
}

output = make_emissions_by_sector_bar(dataset_id, mappings)
print(output)


dataset_id = "ESG_DATASET_001"
mappings = {
    "date": "Year",
    "emissions": "CO2_Emissions"
}

output = make_emissions_over_time_line(dataset_id, mappings)
print(output)
"""