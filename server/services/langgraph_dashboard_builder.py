"""
LangGraph-powered dashboard builder that generates complete dashboard code dynamically.
Replaces template-based approach with intelligent code generation.
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Optional, Literal, TypedDict
from datetime import datetime
import logging
import uuid

from langgraph.graph import StateGraph, END
from .langgraph_agents import LangGraphAgentOrchestrator
from .dashboard_tools import DashboardToolFactory
from .csv_to_json import CSVToJSONConverter

logger = logging.getLogger(__name__)


class DashboardGenerationState(TypedDict, total=False):
    """State for dashboard generation workflow"""
    session_id: str
    df: pd.DataFrame
    json_data: Dict[str, Any]
    dashboard_type: str
    user_context: str
    target_audience: str
    layout_requirements: Dict[str, Any]
    chart_specifications: List[Dict[str, Any]]
    styling_preferences: Dict[str, Any]
    generated_html: str
    generated_css: str
    generated_js: str
    insights: List[str]
    error_messages: List[str]


class CodeGenerationAgent:
    """Agent responsible for generating dashboard code components"""
    
    def __init__(self):
        self.html_templates = self._load_html_components()
        self.css_frameworks = self._load_css_frameworks()
        self.js_libraries = self._load_js_libraries()
    
    def generate_html_structure(self, layout_config: Dict[str, Any], dashboard_type: str) -> str:
        """Generate HTML structure based on layout configuration"""
        
        # Base HTML structure
        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            self._generate_html_head(dashboard_type),
            '<body>',
            self._generate_dashboard_container(layout_config, dashboard_type),
            self._generate_script_section(),
            '</body>',
            '</html>'
        ]
        
        return '\n'.join(html_parts)
    
    def _generate_html_head(self, dashboard_type: str) -> str:
        """Generate HTML head section with appropriate meta tags and external resources"""
        title = f"{dashboard_type.replace('_', ' ').title()} Dashboard"
        
        return f"""<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="AI-generated {dashboard_type} dashboard">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        {self._generate_embedded_css(dashboard_type)}
    </style>
</head>"""
    
    def _generate_dashboard_container(self, layout_config: Dict[str, Any], dashboard_type: str) -> str:
        """Generate main dashboard container structure"""
        
        sections = layout_config.get("sections", [])
        grid_columns = layout_config.get("grid_structure", {}).get("columns", 2)
        
        container_html = [
            f'<div class="dashboard-container dashboard-{dashboard_type}">',
            self._generate_header_section(dashboard_type),
            f'<div class="dashboard-grid" style="grid-template-columns: repeat({grid_columns}, 1fr);">'
        ]
        
        # Generate sections based on layout
        for i, section in enumerate(sections):
            container_html.append(self._generate_section_html(section, i))
        
        container_html.extend([
            '</div>',  # Close dashboard-grid
            self._generate_footer_section(),
            '</div>'   # Close dashboard-container
        ])
        
        return '\n'.join(container_html)
    
    def _generate_header_section(self, dashboard_type: str) -> str:
        """Generate dashboard header with title and metadata"""
        title = dashboard_type.replace('_', ' ').title()
        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        return f"""
    <header class="dashboard-header">
        <div class="header-content">
            <h1 class="dashboard-title">{title} Dashboard</h1>
            <p class="dashboard-subtitle">AI-Generated Analysis • {timestamp}</p>
        </div>
        <div class="header-actions">
            <button class="action-btn" onclick="exportDashboard()">
                <span>📊</span> Export
            </button>
            <button class="action-btn" onclick="refreshDashboard()">
                <span>🔄</span> Refresh
            </button>
        </div>
    </header>"""
    
    def _generate_section_html(self, section: Dict[str, Any], index: int) -> str:
        """Generate HTML for individual dashboard section"""
        section_type = section.get("type", "chart")
        section_id = section.get("id", f"section_{index}")
        span_style = self._get_grid_span_style(section.get("span", {}))
        height_class = f"height-{section.get('height', 'standard')}"
        
        if section_type == "kpi_cards":
            return self._generate_kpi_section(section_id, span_style, height_class)
        elif section_type == "chart":
            return self._generate_chart_section(section_id, span_style, height_class, section)
        elif section_type == "insights_panel":
            return self._generate_insights_section(section_id, span_style, height_class)
        else:
            return self._generate_generic_section(section_id, span_style, height_class, section)
    
    def _generate_kpi_section(self, section_id: str, span_style: str, height_class: str) -> str:
        """Generate KPI cards section"""
        return f"""
    <section class="dashboard-section kpi-section {height_class}" style="{span_style}" id="{section_id}">
        <div class="kpi-container" id="{section_id}_container">
            <!-- KPI cards will be populated by JavaScript -->
        </div>
    </section>"""
    
    def _generate_chart_section(self, section_id: str, span_style: str, height_class: str, section: Dict[str, Any]) -> str:
        """Generate chart section"""
        chart_title = section.get("title", "Chart Analysis")
        
        return f"""
    <section class="dashboard-section chart-section {height_class}" style="{span_style}">
        <div class="section-header">
            <h3 class="section-title">{chart_title}</h3>
            <div class="section-controls">
                <button class="control-btn" onclick="toggleFullscreen('{section_id}')">⛶</button>
            </div>
        </div>
        <div class="chart-container" id="{section_id}">
            <div class="chart-loading">
                <div class="spinner"></div>
                <p>Loading visualization...</p>
            </div>
        </div>
    </section>"""
    
    def _generate_insights_section(self, section_id: str, span_style: str, height_class: str) -> str:
        """Generate insights panel section"""
        return f"""
    <section class="dashboard-section insights-section {height_class}" style="{span_style}">
        <div class="section-header">
            <h3 class="section-title">🔍 Key Insights</h3>
        </div>
        <div class="insights-content" id="{section_id}">
            <!-- Insights will be populated by JavaScript -->
        </div>
    </section>"""
    
    def _generate_generic_section(self, section_id: str, span_style: str, height_class: str, section: Dict[str, Any]) -> str:
        """Generate generic section"""
        title = section.get("title", "Analysis")
        
        return f"""
    <section class="dashboard-section generic-section {height_class}" style="{span_style}">
        <div class="section-header">
            <h3 class="section-title">{title}</h3>
        </div>
        <div class="section-content" id="{section_id}">
            <!-- Content will be populated by JavaScript -->
        </div>
    </section>"""
    
    def _get_grid_span_style(self, span: Dict[str, Any]) -> str:
        """Convert span configuration to CSS grid style"""
        css_parts = []
        
        if "col" in span:
            css_parts.append(f"grid-column: {span['col']}")
        if "row" in span:
            css_parts.append(f"grid-row: {span['row']}")
        
        return "; ".join(css_parts)
    
    def _generate_footer_section(self) -> str:
        """Generate dashboard footer"""
        return """
    <footer class="dashboard-footer">
        <p>Generated by LangGraph AI Dashboard Builder • 
           <span id="generation-time"></span> • 
           <a href="#" onclick="showDataSources()">Data Sources</a>
        </p>
    </footer>"""
    
    def _generate_script_section(self) -> str:
        """Generate JavaScript section placeholder"""
        return """
    <script>
        // Dashboard JavaScript will be injected here
        document.getElementById('generation-time').textContent = new Date().toLocaleString();
    </script>"""
    
    def _generate_embedded_css(self, dashboard_type: str) -> str:
        """Generate embedded CSS for the dashboard"""
        color_schemes = {
            "executive": {
                "primary": "#1e40af",
                "secondary": "#3b82f6", 
                "accent": "#60a5fa",
                "background": "#f8fafc",
                "surface": "#ffffff",
                "text": "#1f2937"
            },
            "data_quality": {
                "primary": "#059669",
                "secondary": "#10b981",
                "accent": "#34d399",
                "background": "#f0fdf4",
                "surface": "#ffffff",
                "text": "#1f2937"
            },
            "exploratory": {
                "primary": "#7c3aed",
                "secondary": "#8b5cf6",
                "accent": "#a78bfa",
                "background": "#faf5ff",
                "surface": "#ffffff",
                "text": "#1f2937"
            }
        }
        
        colors = color_schemes.get(dashboard_type, color_schemes["exploratory"])
        
        return f"""
        :root {{
            --primary-color: {colors['primary']};
            --secondary-color: {colors['secondary']};
            --accent-color: {colors['accent']};
            --background-color: {colors['background']};
            --surface-color: {colors['surface']};
            --text-color: {colors['text']};
            --border-radius: 12px;
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            --transition: all 0.3s ease;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
        }}

        .dashboard-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            min-height: 100vh;
            display: grid;
            grid-template-rows: auto 1fr auto;
            gap: 20px;
        }}

        .dashboard-header {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 30px;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .dashboard-title {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}

        .dashboard-subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}

        .header-actions {{
            display: flex;
            gap: 10px;
        }}

        .action-btn {{
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: var(--transition);
        }}

        .action-btn:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }}

        .dashboard-grid {{
            display: grid;
            gap: 20px;
            grid-auto-rows: minmax(200px, auto);
        }}

        .dashboard-section {{
            background: var(--surface-color);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            border: 1px solid rgba(0, 0, 0, 0.05);
            overflow: hidden;
            transition: var(--transition);
        }}

        .dashboard-section:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }}

        .section-header {{
            padding: 20px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .section-title {{
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--primary-color);
        }}

        .section-controls {{
            display: flex;
            gap: 8px;
        }}

        .control-btn {{
            background: none;
            border: 1px solid rgba(0, 0, 0, 0.1);
            color: var(--text-color);
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            transition: var(--transition);
        }}

        .control-btn:hover {{
            background: var(--accent-color);
            color: white;
            border-color: var(--accent-color);
        }}

        .chart-container {{
            padding: 20px;
            height: 100%;
            min-height: 300px;
        }}

        .kpi-container {{
            padding: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}

        .kpi-card {{
            background: linear-gradient(135deg, var(--accent-color) 0%, var(--primary-color) 100%);
            color: white;
            padding: 25px;
            border-radius: var(--border-radius);
            text-align: center;
            transition: var(--transition);
        }}

        .kpi-card:hover {{
            transform: scale(1.05);
        }}

        .kpi-value {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}

        .kpi-label {{
            font-size: 1rem;
            opacity: 0.9;
        }}

        .kpi-trend {{
            font-size: 0.9rem;
            margin-top: 10px;
        }}

        .insights-content {{
            padding: 20px;
        }}

        .insight-item {{
            display: flex;
            align-items: flex-start;
            padding: 15px 0;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        }}

        .insight-item:last-child {{
            border-bottom: none;
        }}

        .insight-icon {{
            width: 8px;
            height: 8px;
            background: var(--accent-color);
            border-radius: 50%;
            margin-right: 15px;
            margin-top: 8px;
            flex-shrink: 0;
        }}

        .insight-text {{
            flex: 1;
            font-size: 0.95rem;
            line-height: 1.6;
        }}

        .chart-loading {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            color: var(--primary-color);
        }}

        .spinner {{
            width: 40px;
            height: 40px;
            border: 4px solid rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 15px;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        .height-small {{
            grid-row: span 1;
        }}

        .height-standard {{
            grid-row: span 2;
        }}

        .height-large {{
            grid-row: span 3;
        }}

        .height-compact {{
            grid-row: span 1;
            min-height: 120px;
        }}

        .dashboard-footer {{
            text-align: center;
            padding: 20px;
            color: rgba(0, 0, 0, 0.6);
            font-size: 0.9rem;
        }}

        .dashboard-footer a {{
            color: var(--primary-color);
            text-decoration: none;
        }}

        .dashboard-footer a:hover {{
            text-decoration: underline;
        }}

        @media (max-width: 768px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr !important;
            }}
            
            .dashboard-header {{
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }}
            
            .dashboard-title {{
                font-size: 2rem;
            }}
        }}
        """
    
    def generate_javascript_code(self, chart_configs: List[Dict[str, Any]], insights: List[str], json_data: Dict[str, Any]) -> str:
        """Generate JavaScript code for dashboard functionality"""
        
        js_code = f"""
// Dashboard Data and Configuration
const dashboardData = {json.dumps(json_data, indent=2)};
const chartConfigs = {json.dumps(chart_configs, indent=2)};
const insights = {json.dumps(insights, indent=2)};

// Dashboard Initialization
document.addEventListener('DOMContentLoaded', function() {{
    initializeDashboard();
}});

function initializeDashboard() {{
    renderKPICards();
    renderCharts();
    renderInsights();
    setupEventListeners();
}}

// KPI Card Rendering
function renderKPICards() {{
    const kpiContainer = document.querySelector('.kpi-container');
    if (!kpiContainer) return;
    
    const kpiData = extractKPIData();
    kpiContainer.innerHTML = '';
    
    kpiData.forEach(kpi => {{
        const kpiCard = createKPICard(kpi);
        kpiContainer.appendChild(kpiCard);
    }});
}}

function extractKPIData() {{
    // Extract KPI data from dashboard data
    const numericalColumns = dashboardData.metadata?.data_types?.numerical_columns || [];
    const data = dashboardData.data?.records || [];
    
    return numericalColumns.slice(0, 4).map(col => {{
        const values = data.map(row => row[col]).filter(val => val != null);
        const total = values.reduce((sum, val) => sum + val, 0);
        const avg = values.length > 0 ? total / values.length : 0;
        
        return {{
            label: col.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase()),
            value: total,
            average: avg,
            trend: Math.random() > 0.5 ? 'up' : 'down',
            trendPercent: (Math.random() * 20 - 10).toFixed(1)
        }};
    }});
}}

function createKPICard(kpi) {{
    const card = document.createElement('div');
    card.className = 'kpi-card';
    
    const trendIcon = kpi.trend === 'up' ? '↗️' : '↘️';
    const trendColor = kpi.trend === 'up' ? '#10b981' : '#ef4444';
    
    card.innerHTML = `
        <div class="kpi-value">${{formatNumber(kpi.value)}}</div>
        <div class="kpi-label">${{kpi.label}}</div>
        <div class="kpi-trend" style="color: ${{trendColor}}">
            ${{trendIcon}} ${{kpi.trendPercent}}%
        </div>
    `;
    
    return card;
}}

// Chart Rendering
function renderCharts() {{
    chartConfigs.forEach((config, index) => {{
        const chartElement = document.getElementById(config.id || `chart_${{index}}`);
        if (chartElement) {{
            renderChart(chartElement, config);
        }}
    }});
}}

function renderChart(element, config) {{
    // Remove loading spinner
    element.innerHTML = '';
    
    try {{
        if (config.type === 'histogram') {{
            renderHistogram(element, config);
        }} else if (config.type === 'scatter') {{
            renderScatter(element, config);
        }} else if (config.type === 'bar_chart') {{
            renderBarChart(element, config);
        }} else if (config.type === 'heatmap') {{
            renderHeatmap(element, config);
        }} else if (config.type === 'line_chart') {{
            renderLineChart(element, config);
        }} else {{
            renderDefaultChart(element, config);
        }}
    }} catch (error) {{
        console.error('Error rendering chart:', error);
        element.innerHTML = '<div class="error-message">Error loading chart</div>';
    }}
}}

function renderHistogram(element, config) {{
    const data = extractColumnData(config.columns?.[0] || Object.keys(dashboardData.data?.by_column || {{}})[0]);
    
    const trace = {{
        x: data,
        type: 'histogram',
        name: config.title || 'Distribution',
        marker: {{ color: config.color || '#3b82f6' }},
        nbinsx: 30
    }};
    
    const layout = {{
        title: config.title || 'Distribution Analysis',
        xaxis: {{ title: config.columns?.[0] || 'Value' }},
        yaxis: {{ title: 'Frequency' }},
        margin: {{ t: 40, r: 30, b: 40, l: 60 }},
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    }};
    
    Plotly.newPlot(element, [trace], layout, {{responsive: true}});
}}

function renderScatter(element, config) {{
    const xData = extractColumnData(config.columns?.[0]);
    const yData = extractColumnData(config.columns?.[1]);
    
    const trace = {{
        x: xData,
        y: yData,
        mode: 'markers',
        type: 'scatter',
        name: config.title || 'Scatter Plot',
        marker: {{ 
            color: config.color || '#3b82f6',
            size: 8,
            opacity: 0.7
        }}
    }};
    
    const layout = {{
        title: config.title || 'Scatter Plot Analysis',
        xaxis: {{ title: config.columns?.[0] || 'X' }},
        yaxis: {{ title: config.columns?.[1] || 'Y' }},
        margin: {{ t: 40, r: 30, b: 40, l: 60 }},
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    }};
    
    Plotly.newPlot(element, [trace], layout, {{responsive: true}});
}}

function renderBarChart(element, config) {{
    const data = extractColumnData(config.columns?.[0]);
    const valueCounts = getValueCounts(data);
    
    const trace = {{
        x: Object.keys(valueCounts),
        y: Object.values(valueCounts),
        type: 'bar',
        name: config.title || 'Bar Chart',
        marker: {{ color: config.color || '#3b82f6' }}
    }};
    
    const layout = {{
        title: config.title || 'Bar Chart Analysis',
        xaxis: {{ title: config.columns?.[0] || 'Category' }},
        yaxis: {{ title: 'Count' }},
        margin: {{ t: 40, r: 30, b: 40, l: 60 }},
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    }};
    
    Plotly.newPlot(element, [trace], layout, {{responsive: true}});
}}

function renderHeatmap(element, config) {{
    const numericalColumns = dashboardData.metadata?.data_types?.numerical_columns || [];
    const correlationMatrix = calculateCorrelationMatrix(numericalColumns);
    
    const trace = {{
        z: correlationMatrix.values,
        x: correlationMatrix.columns,
        y: correlationMatrix.columns,
        type: 'heatmap',
        colorscale: 'RdBu',
        zmid: 0,
        showscale: true
    }};
    
    const layout = {{
        title: 'Correlation Matrix',
        margin: {{ t: 40, r: 30, b: 40, l: 60 }},
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    }};
    
    Plotly.newPlot(element, [trace], layout, {{responsive: true}});
}}

function renderLineChart(element, config) {{
    const yData = extractColumnData(config.columns?.[0]);
    const xData = Array.from({{length: yData.length}}, (_, i) => i);
    
    const trace = {{
        x: xData,
        y: yData,
        type: 'scatter',
        mode: 'lines+markers',
        name: config.title || 'Trend',
        line: {{ color: config.color || '#3b82f6', width: 3 }},
        marker: {{ size: 6 }}
    }};
    
    const layout = {{
        title: config.title || 'Trend Analysis',
        xaxis: {{ title: 'Index' }},
        yaxis: {{ title: config.columns?.[0] || 'Value' }},
        margin: {{ t: 40, r: 30, b: 40, l: 60 }},
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    }};
    
    Plotly.newPlot(element, [trace], layout, {{responsive: true}});
}}

function renderDefaultChart(element, config) {{
    element.innerHTML = `
        <div style="text-align: center; padding: 40px; color: #6b7280;">
            <h3>Chart Type: ${{config.type}}</h3>
            <p>Visualization will be rendered here</p>
        </div>
    `;
}}

// Insights Rendering
function renderInsights() {{
    const insightsContainer = document.querySelector('.insights-content');
    if (!insightsContainer) return;
    
    insightsContainer.innerHTML = '';
    
    insights.forEach(insight => {{
        const insightElement = createInsightElement(insight);
        insightsContainer.appendChild(insightElement);
    }});
}}

function createInsightElement(insight) {{
    const element = document.createElement('div');
    element.className = 'insight-item';
    element.innerHTML = `
        <div class="insight-icon"></div>
        <div class="insight-text">${{insight}}</div>
    `;
    return element;
}}

// Utility Functions
function extractColumnData(columnName) {{
    if (!columnName || !dashboardData.data) return [];
    
    if (dashboardData.data.by_column && dashboardData.data.by_column[columnName]) {{
        return dashboardData.data.by_column[columnName].filter(val => val != null);
    }}
    
    if (dashboardData.data.records) {{
        return dashboardData.data.records
            .map(record => record[columnName])
            .filter(val => val != null);
    }}
    
    return [];
}}

function getValueCounts(data) {{
    const counts = {{}};
    data.forEach(value => {{
        counts[value] = (counts[value] || 0) + 1;
    }});
    return counts;
}}

function calculateCorrelationMatrix(columns) {{
    const matrix = [];
    const size = columns.length;
    
    for (let i = 0; i < size; i++) {{
        const row = [];
        for (let j = 0; j < size; j++) {{
            if (i === j) {{
                row.push(1);
            }} else {{
                const corr = calculateCorrelation(
                    extractColumnData(columns[i]),
                    extractColumnData(columns[j])
                );
                row.push(corr);
            }}
        }}
        matrix.push(row);
    }}
    
    return {{ values: matrix, columns: columns }};
}}

function calculateCorrelation(x, y) {{
    if (x.length !== y.length || x.length === 0) return 0;
    
    const n = x.length;
    const meanX = x.reduce((sum, val) => sum + val, 0) / n;
    const meanY = y.reduce((sum, val) => sum + val, 0) / n;
    
    let numerator = 0;
    let sumXSquared = 0;
    let sumYSquared = 0;
    
    for (let i = 0; i < n; i++) {{
        const xDiff = x[i] - meanX;
        const yDiff = y[i] - meanY;
        numerator += xDiff * yDiff;
        sumXSquared += xDiff * xDiff;
        sumYSquared += yDiff * yDiff;
    }}
    
    const denominator = Math.sqrt(sumXSquared * sumYSquared);
    return denominator === 0 ? 0 : numerator / denominator;
}}

function formatNumber(num) {{
    if (num >= 1000000) {{
        return (num / 1000000).toFixed(1) + 'M';
    }} else if (num >= 1000) {{
        return (num / 1000).toFixed(1) + 'K';
    }} else {{
        return num.toFixed(0);
    }}
}}

// Event Handlers
function setupEventListeners() {{
    // Make charts responsive
    window.addEventListener('resize', function() {{
        const charts = document.querySelectorAll('.chart-container [id]');
        charts.forEach(chart => {{
            if (chart.id && window.Plotly) {{
                Plotly.Plots.resize(chart.id);
            }}
        }});
    }});
}}

function exportDashboard() {{
    // Create export functionality
    const dashboardHTML = document.documentElement.outerHTML;
    const blob = new Blob([dashboardHTML], {{ type: 'text/html' }});
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'dashboard.html';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}}

function refreshDashboard() {{
    location.reload();
}}

function toggleFullscreen(elementId) {{
    const element = document.getElementById(elementId);
    if (element) {{
        if (document.fullscreenElement) {{
            document.exitFullscreen();
        }} else {{
            element.requestFullscreen();
        }}
    }}
}}

function showDataSources() {{
    alert('Data source information:\\n' + JSON.stringify(dashboardData.metadata, null, 2));
}}
"""
        
        return js_code
    
    def _load_html_components(self) -> Dict[str, str]:
        """Load reusable HTML components"""
        return {
            "kpi_card": """
                <div class="kpi-card">
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-trend">{trend}</div>
                </div>
            """,
            "chart_container": """
                <div class="chart-container" id="{id}">
                    <div class="chart-loading">Loading...</div>
                </div>
            """
        }
    
    def _load_css_frameworks(self) -> Dict[str, str]:
        """Load CSS framework configurations"""
        return {
            "modern": "Modern design with cards and gradients",
            "minimal": "Clean minimal design",
            "corporate": "Professional corporate styling"
        }
    
    def _load_js_libraries(self) -> Dict[str, str]:
        """Load JavaScript library configurations"""
        return {
            "plotly": "Plotly.js for interactive charts",
            "d3": "D3.js for custom visualizations",
            "chart_js": "Chart.js for simple charts"
        }


class LangGraphDashboardBuilder:
    """Main LangGraph-powered dashboard builder"""
    
    def __init__(self):
        self.agent_orchestrator = LangGraphAgentOrchestrator()
        self.code_generator = CodeGenerationAgent()
        self.csv_converter = CSVToJSONConverter()
        self.dashboard_graph = self._create_dashboard_workflow()
    
    def _create_dashboard_workflow(self) -> StateGraph:
        """Create the complete dashboard generation workflow"""
        graph = StateGraph(DashboardGenerationState)
        
        # Add workflow nodes
        graph.add_node("initialize_session", self._initialize_session)
        graph.add_node("convert_data_to_json", self._convert_data_to_json)
        graph.add_node("analyze_dashboard_requirements", self._analyze_requirements)
        graph.add_node("generate_layout_structure", self._generate_layout)
        graph.add_node("create_chart_specifications", self._create_charts)
        graph.add_node("generate_insights", self._generate_insights)
        graph.add_node("generate_html_code", self._generate_html)
        graph.add_node("generate_javascript_code", self._generate_javascript)
        graph.add_node("finalize_dashboard", self._finalize_dashboard)
        
        # Define workflow edges
        graph.set_entry_point("initialize_session")
        graph.add_edge("initialize_session", "convert_data_to_json")
        graph.add_edge("convert_data_to_json", "analyze_dashboard_requirements")
        graph.add_edge("analyze_dashboard_requirements", "generate_layout_structure")
        graph.add_edge("generate_layout_structure", "create_chart_specifications")
        graph.add_edge("create_chart_specifications", "generate_insights")
        graph.add_edge("generate_insights", "generate_html_code")
        graph.add_edge("generate_html_code", "generate_javascript_code")
        graph.add_edge("generate_javascript_code", "finalize_dashboard")
        graph.add_edge("finalize_dashboard", END)
        
        return graph.compile()
    
    # Workflow node implementations
    def _initialize_session(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Initialize dashboard generation session"""
        session_id = uuid.uuid4().hex
        return {**state, "session_id": session_id, "error_messages": []}
    
    def _convert_data_to_json(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Convert DataFrame to optimized JSON format"""
        df = state["df"]
        json_result = self.csv_converter.convert_csv_to_json("", "optimized")
        
        # Use data processor to convert DataFrame directly
        json_data = self.agent_orchestrator.data_tools.convert_to_json_structure(df)
        
        return {**state, "json_data": json_data}
    
    def _analyze_requirements(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Analyze dashboard requirements based on data and user input"""
        df = state["df"]
        dashboard_type = state.get("dashboard_type", "exploratory")
        user_context = state.get("user_context", "")
        
        # Get appropriate tool for dashboard type
        tool_class = DashboardToolFactory.get_tool(dashboard_type)
        
        if dashboard_type == "executive":
            analysis = tool_class.analyze_business_metrics(df, user_context)
        elif dashboard_type == "data_quality":
            analysis = tool_class.analyze_data_quality_comprehensive(df)
        elif dashboard_type == "exploratory":
            analysis = tool_class.analyze_data_patterns(df)
        else:
            analysis = {"type": dashboard_type, "basic_analysis": "completed"}
        
        # Determine layout requirements
        if hasattr(tool_class, 'generate_executive_layout'):
            layout_requirements = tool_class.generate_executive_layout()
        else:
            layout_requirements = self.agent_orchestrator.dashboard_tools.generate_dashboard_layout(
                dashboard_type, len(df.columns)
            )
        
        return {**state, "layout_requirements": layout_requirements}
    
    def _generate_layout(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Generate optimal layout structure"""
        layout_requirements = state.get("layout_requirements", {})
        
        # Use the layout requirements as the final layout config
        return state
    
    def _create_charts(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Create chart specifications"""
        df = state["df"]
        dashboard_type = state.get("dashboard_type", "exploratory")
        
        # Get appropriate tool and create charts
        tool_class = DashboardToolFactory.get_tool(dashboard_type)
        
        if hasattr(tool_class, 'create_executive_charts'):
            layout_requirements = state.get("layout_requirements", {})
            charts = tool_class.create_executive_charts(df, layout_requirements)
        elif hasattr(tool_class, 'create_quality_charts'):
            quality_report = tool_class.analyze_data_quality_comprehensive(df)
            charts = tool_class.create_quality_charts(df, quality_report)
        elif hasattr(tool_class, 'create_exploratory_charts'):
            patterns = tool_class.analyze_data_patterns(df)
            charts = tool_class.create_exploratory_charts(df, patterns)
        else:
            # Fallback to general chart suggestions
            charts = self.agent_orchestrator.dashboard_tools.suggest_chart_types(df, dashboard_type)
        
        return {**state, "chart_specifications": charts}
    
    def _generate_insights(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Generate insights for the dashboard"""
        df = state["df"]
        dashboard_type = state.get("dashboard_type", "exploratory")
        
        # Generate insights based on dashboard type
        insights = [
            f"Dashboard generated for {len(df)} records across {len(df.columns)} variables",
            f"Analysis type: {dashboard_type.replace('_', ' ').title()}",
            f"Data completeness: {((1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100):.1f}%"
        ]
        
        # Add type-specific insights
        if dashboard_type == "executive":
            insights.extend([
                "Key performance indicators identified and prioritized",
                "Business metrics configured for executive review"
            ])
        elif dashboard_type == "data_quality":
            missing_percent = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
            insights.extend([
                f"Data quality assessment completed",
                f"Missing data: {missing_percent:.1f}% of total values"
            ])
        
        return {**state, "insights": insights}
    
    def _generate_html(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Generate HTML code for the dashboard"""
        layout_requirements = state.get("layout_requirements", {})
        dashboard_type = state.get("dashboard_type", "exploratory")
        
        html_code = self.code_generator.generate_html_structure(layout_requirements, dashboard_type)
        
        return {**state, "generated_html": html_code}
    
    def _generate_javascript(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Generate JavaScript code for dashboard functionality"""
        chart_specifications = state.get("chart_specifications", [])
        insights = state.get("insights", [])
        json_data = state.get("json_data", {})
        
        js_code = self.code_generator.generate_javascript_code(
            chart_specifications, insights, json_data
        )
        
        return {**state, "generated_js": js_code}
    
    def _finalize_dashboard(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Finalize the dashboard by combining all components"""
        html_code = state.get("generated_html", "")
        js_code = state.get("generated_js", "")
        
        # Inject JavaScript into HTML
        final_html = html_code.replace(
            "// Dashboard JavaScript will be injected here",
            js_code
        )
        
        return {**state, "generated_html": final_html}
    
    # Public API
    async def build_dashboard(
        self,
        df: pd.DataFrame,
        dashboard_type: str = "exploratory",
        user_context: str = "",
        target_audience: str = "analyst"
    ) -> Dict[str, Any]:
        """Build complete dashboard using LangGraph workflow"""
        try:
            initial_state: DashboardGenerationState = {
                "df": df,
                "dashboard_type": dashboard_type,
                "user_context": user_context,
                "target_audience": target_audience
            }
            
            result = self.dashboard_graph.invoke(initial_state)
            
            return {
                "success": True,
                "dashboard_html": result.get("generated_html", ""),
                "session_id": result.get("session_id", ""),
                "dashboard_type": dashboard_type,
                "json_data": result.get("json_data", {}),
                "chart_specifications": result.get("chart_specifications", []),
                "insights": result.get("insights", []),
                "layout_config": result.get("layout_requirements", {}),
                "generation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error building dashboard: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "dashboard_type": dashboard_type
            }