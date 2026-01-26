# esg_lib/portfolio_inventory_mapping.py

"""
Mapping logique → colonnes réelles du dataset Inventory
"""

PORTFOLIO_INVENTORY_MAPPING = {
    # -------------------
    # Portfolio info
    # -------------------
    "portfolio_id": "Portfolio ID",
    "portfolio_name": "Portfolio name",
    "portfolio_currency": "Portfolio currency",
    "portfolio_date": "Portfolio date",

    # -------------------
    # Security info
    # -------------------
    "security_id": "Security ID",
    "security_name": "Security name",
    "security_type": "Security type",
    "security_currency": "Security quotation currency",

    # -------------------
    # Measures
    # -------------------
    "portfolio_nav": "Portfolio validated nav",
    "security_value": "Security clean market valuation in portfolio currency",
    "security_exposure": "Security market exposure in portfolio currency",
}
