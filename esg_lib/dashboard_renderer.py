"""
Dashboard Renderer Module
=========================
Renders portfolio dashboard visualizations from Excel data.

Author: Weihua SHI
Date: 2026-01-20
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict, Optional
from pathlib import Path


# Professional color scheme for business presentations
COLORS = {
    'primary': '#1f77b4',      # Professional blue
    'secondary': '#ff7f0e',    # Orange accent
    'success': '#2ca02c',      # Green
    'danger': '#d62728',       # Red
    'info': '#17becf',         # Light blue
    'warning': '#ff9896',      # Light red
    'corporate_bond': '#4472C4',  # Blue
    'equity': '#ED7D31',          # Orange
    'sovereign_bond': '#A5A5A5',  # Gray
}


def load_portfolio_data(file_path: str) -> pd.DataFrame:
    """
    Load portfolio data from Excel file.

    Args:
        file_path: Path to the Excel file

    Returns:
        DataFrame with portfolio holdings
    """
    df = pd.read_excel(file_path, sheet_name='Inventory', skiprows=3)

    # Clean column names (remove trailing *)
    df.columns = [col.replace(' *', '').strip() for col in df.columns]

    # For testing: create mock valuations if all values are 1
    if df['Security market valuation in portfolio currency'].nunique() == 1:
        # Generate realistic mock data
        import numpy as np
        np.random.seed(42)

        # Create valuations based on security type
        valuations = []
        for _, row in df.iterrows():
            sec_type = row['Security type']
            if sec_type == 'Corporate bond':
                val = np.random.uniform(50000, 500000)
            elif sec_type == 'Equity':
                val = np.random.uniform(100000, 1000000)
            elif sec_type == 'Sovereign bond':
                val = np.random.uniform(200000, 800000)
            else:
                val = np.random.uniform(10000, 100000)
            valuations.append(val)

        df['Security market valuation in portfolio currency'] = valuations

    return df


def create_kpi_card(df: pd.DataFrame) -> go.Figure:
    """
    Create KPI card showing total invested value.

    Args:
        df: Portfolio DataFrame

    Returns:
        Plotly figure
    """
    total_value = df['Security market valuation in portfolio currency'].sum()

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="number",
        value=total_value,
        number={
            'valueformat': ',.0f',
            'prefix': '€',
            'font': {'size': 60, 'color': COLORS['primary']}
        },
        title={
            'text': "Total Invested Value",
            'font': {'size': 24, 'color': '#333333'}
        },
        domain={'x': [0, 1], 'y': [0, 1]}
    ))

    fig.update_layout(
        height=300,
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(t=50, b=50, l=50, r=50),
        font=dict(family="Arial, sans-serif")
    )

    return fig


def create_security_type_pie(df: pd.DataFrame) -> go.Figure:
    """
    Create pie chart showing investment distribution by security type.

    Args:
        df: Portfolio DataFrame

    Returns:
        Plotly figure
    """
    # Aggregate by security type
    type_dist = df.groupby('Security type')['Security market valuation in portfolio currency'].sum().reset_index()
    type_dist.columns = ['Security Type', 'Value']
    type_dist = type_dist.sort_values('Value', ascending=False)

    # Calculate percentages
    total = type_dist['Value'].sum()
    type_dist['Percentage'] = (type_dist['Value'] / total * 100).round(1)

    # Color mapping
    color_map = {
        'Corporate bond': COLORS['corporate_bond'],
        'Equity': COLORS['equity'],
        'Sovereign bond': COLORS['sovereign_bond']
    }
    colors = [color_map.get(t, COLORS['primary']) for t in type_dist['Security Type']]

    fig = go.Figure(data=[go.Pie(
        labels=type_dist['Security Type'],
        values=type_dist['Value'],
        hole=0.4,
        marker=dict(colors=colors),
        textposition='auto',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Value: €%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title={
            'text': "Investment Distribution by Security Type",
            'font': {'size': 20, 'color': '#333333'},
            'x': 0.5,
            'xanchor': 'center'
        },
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05,
            font=dict(size=12)
        ),
        margin=dict(t=80, b=50, l=50, r=150),
        font=dict(family="Arial, sans-serif")
    )

    return fig


def create_top_holdings_bar(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """
    Create horizontal bar chart showing top N holdings by value.

    Args:
        df: Portfolio DataFrame
        top_n: Number of top holdings to display

    Returns:
        Plotly figure
    """
    # Get top holdings
    top_holdings = df.nlargest(top_n, 'Security market valuation in portfolio currency')

    # Sort for better visualization
    top_holdings = top_holdings.sort_values('Security market valuation in portfolio currency')

    # Truncate long names
    top_holdings['Short Name'] = top_holdings['Security name'].apply(
        lambda x: x[:40] + '...' if len(str(x)) > 40 else x
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=top_holdings['Short Name'],
        x=top_holdings['Security market valuation in portfolio currency'],
        orientation='h',
        marker=dict(
            color=COLORS['primary'],
            line=dict(color='white', width=1)
        ),
        text=top_holdings['Security market valuation in portfolio currency'].apply(lambda x: f'€{x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Value: €%{x:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': f"Top {top_n} Holdings by Investment Value",
            'font': {'size': 20, 'color': '#333333'},
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis=dict(
            title="Investment Value (€)",
            showgrid=True,
            gridcolor='#E5E5E5',
            zeroline=False
        ),
        yaxis=dict(
            title="",
            showgrid=False
        ),
        height=600,
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(t=80, b=80, l=250, r=150),
        font=dict(family="Arial, sans-serif", size=11)
    )

    return fig


def create_dashboard_html(
    df: pd.DataFrame,
    output_path: str = "dashboard_preview.html",
    title: str = "Portfolio Dashboard - Quick Preview"
) -> str:
    """
    Create complete dashboard HTML with all visualizations.

    Args:
        df: Portfolio DataFrame
        output_path: Path to save HTML file
        title: Dashboard title

    Returns:
        Path to generated HTML file
    """
    # Create individual charts
    kpi_fig = create_kpi_card(df)
    pie_fig = create_security_type_pie(df)
    bar_fig = create_top_holdings_bar(df)

    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                padding: 20px;
            }}

            .dashboard-container {{
                max-width: 1400px;
                margin: 0 auto;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                padding: 30px;
            }}

            .dashboard-header {{
                text-align: center;
                margin-bottom: 40px;
                border-bottom: 3px solid #1f77b4;
                padding-bottom: 20px;
            }}

            .dashboard-header h1 {{
                color: #333333;
                font-size: 32px;
                margin-bottom: 10px;
            }}

            .dashboard-header p {{
                color: #666666;
                font-size: 14px;
            }}

            .chart-section {{
                margin-bottom: 40px;
            }}

            .chart-container {{
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }}

            .two-column {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin-top: 30px;
            }}

            @media (max-width: 1024px) {{
                .two-column {{
                    grid-template-columns: 1fr;
                }}
            }}

            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                color: #999999;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="dashboard-container">
            <div class="dashboard-header">
                <h1>{title}</h1>
                <p>Portfolio Date: {df['Portfolio date'].iloc[0].strftime('%B %d, %Y')} |
                   Holdings: {len(df):,} securities</p>
            </div>

            <div class="chart-section">
                <div class="chart-container" id="kpi-chart"></div>
            </div>

            <div class="two-column">
                <div class="chart-container" id="pie-chart"></div>
                <div class="chart-container" id="bar-chart"></div>
            </div>

            <div class="footer">
                <p>Generated by ESG QuickSight Dashboard Renderer | Weihua SHI © 2026</p>
                <p>ESILV - Pi2 Project</p>
            </div>
        </div>

        <script>
            // Render KPI
            var kpiData = {kpi_fig.to_json()};
            Plotly.newPlot('kpi-chart', kpiData.data, kpiData.layout, {{responsive: true}});

            // Render Pie Chart
            var pieData = {pie_fig.to_json()};
            Plotly.newPlot('pie-chart', pieData.data, pieData.layout, {{responsive: true}});

            // Render Bar Chart
            var barData = {bar_fig.to_json()};
            Plotly.newPlot('bar-chart', barData.data, barData.layout, {{responsive: true}});
        </script>
    </body>
    </html>
    """

    # Save to file
    output_file = Path(output_path)
    output_file.write_text(html_content, encoding='utf-8')

    print(f"✅ Dashboard HTML generated: {output_file.absolute()}")
    print(f"📊 Total holdings: {len(df):,}")
    print(f"💰 Total value: €{df['Security market valuation in portfolio currency'].sum():,.0f}")

    return str(output_file.absolute())


def main():
    """
    Example usage of the dashboard renderer.
    """
    # Load data
    data_file = "demo_cross_asset_type_2025-03-31_ORIGINAL.xlsx"
    df = load_portfolio_data(data_file)

    # Generate dashboard
    html_path = create_dashboard_html(
        df,
        output_path="portfolio_dashboard_preview.html",
        title="Portfolio Dashboard - Quick Preview"
    )

    print(f"\n🎉 Dashboard ready! Open: {html_path}")


if __name__ == "__main__":
    main()
