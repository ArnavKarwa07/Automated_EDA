# Automated EDA Dashboard Builder 🚀

An advanced automated exploratory data analysis system with AI-powered dashboard generation using Model Context Protocol (MCP).

## 🌟 New Dashboard Features

### ✨ Automated Dashboard Builder

- **AI-Powered Analysis**: Automatically determines the best dashboard type for your data
- **Multiple Dashboard Types**: Executive Summary, Data Quality Report, Exploratory Analysis
- **Smart Recommendations**: Context-aware suggestions based on data characteristics
- **MCP Integration**: Uses Model Context Protocol for intelligent dashboard automation
- **Export Capabilities**: HTML and JSON export formats
- **Interactive Visualizations**: Plotly-powered charts with full interactivity

### 🎯 Dashboard Types

#### 1. Executive Summary Dashboard

- **Best for**: Business reporting, high-level overview
- **Features**: Key metrics cards, priority charts, executive insights
- **Use cases**: Management presentations, business reviews

#### 2. Data Quality Report

- **Best for**: Data validation, quality assessment
- **Features**: Quality score, missing data analysis, outlier detection
- **Use cases**: Data cleaning planning, quality audits

#### 3. Exploratory Analysis Dashboard

- **Best for**: Research, detailed analysis, pattern discovery
- **Features**: Comprehensive visualizations, distribution analysis, correlation maps
- **Use cases**: Research projects, in-depth data exploration

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Quick Setup

```bash
# Clone the repository
git clone <repository-url>
cd Automated_EDA

# Run the setup script
cd server
python setup.py

# Update environment variables
# Edit server/.env with your API keys
```

### Manual Setup

```bash
# Backend setup
cd server
pip install -r requirements.txt
python main.py

# Frontend setup (in a new terminal)
cd client
npm install
npm run dev
```

## 🚀 Quick Start

### 1. Upload Data

- Navigate to the upload page
- Upload your CSV file
- Get instant data preview and statistics

### 2. Generate Dashboard

- Click "Auto Dashboard" for AI-powered generation
- Or choose "Configure Analysis" for custom options
- Select dashboard type and customizations

### 3. View & Export

- View dashboard in full-screen mode
- Export as HTML for sharing
- Export as JSON for programmatic use

## 📊 API Endpoints

### Dashboard Endpoints

```
POST /api/dashboard/auto-generate
POST /api/dashboard/generate
POST /api/dashboard/analyze-requirements
GET  /api/dashboard/templates
POST /api/dashboard/recommendations
GET  /api/dashboard/{dashboard_id}
GET  /api/dashboard/{dashboard_id}/export
GET  /api/dashboards
POST /api/dashboard/generate-all-types
```

### MCP Interface

```python
from services.mcp_dashboard_server import DashboardMCPInterface

interface = DashboardMCPInterface()

# Auto-generate optimal dashboard
result = await interface.auto_generate_dashboard(
    file_path="data.csv",
    business_context="Sales analysis"
)

# Get AI recommendations
recommendations = await interface.get_dashboard_recommendations(
    file_path="data.csv",
    context="Quality assessment"
)
```

## 🔧 Configuration

### Environment Variables

```env
# Required for AI features
GROQ_API_KEY=your_groq_api_key_here

# Optional database (defaults to SQLite)
DATABASE_URL=sqlite:///./automated_eda.db

# Security
SECRET_KEY=your_secret_key_here
```

### Dashboard Customization

```python
customizations = {
    "color_scheme": "blue",  # blue, green, purple, orange, red
    "chart_size": "medium",  # small, medium, large
    "layout_density": "comfortable"  # compact, comfortable, spacious
}
```

## 🧠 AI Integration

### Smart Dashboard Selection

The system automatically analyzes your data to suggest the optimal dashboard type:

- **Data Quality Issues** → Data Quality Report
- **Rich Multi-variate Data** → Exploratory Analysis
- **General Purpose** → Executive Summary

### Business Context Awareness

Provide business context for better recommendations:

- "Sales analysis" → Executive Summary with revenue focus
- "Data validation" → Data Quality Report
- "Research study" → Exploratory Analysis

## 📈 Features Overview

### Automated Analysis

- ✅ Missing value detection
- ✅ Outlier identification
- ✅ Data type optimization
- ✅ Correlation analysis
- ✅ Distribution analysis

### Visualization Types

- ✅ Interactive histograms
- ✅ Correlation heatmaps
- ✅ Scatter plots
- ✅ Box plots
- ✅ Bar charts
- ✅ Missing value patterns

### Dashboard Features

- ✅ Responsive design
- ✅ Interactive charts
- ✅ Export capabilities
- ✅ Real-time generation
- ✅ AI-powered insights

## 🔄 Workflow Example

```python
# 1. Upload data via UI or API
file_id = upload_csv("sales_data.csv")

# 2. Get AI recommendations
recommendations = get_recommendations(file_id, "sales analysis")

# 3. Generate dashboard
dashboard = auto_generate_dashboard(file_id, "executive_summary")

# 4. Export and share
export_dashboard(dashboard.id, format="html")
```

## 🎨 Dashboard Templates

### Executive Summary Template

- Metric cards with KPIs
- Priority visualizations
- Key insights panel
- Clean, professional layout

### Data Quality Template

- Quality score indicator
- Missing data analysis
- Outlier detection charts
- Recommendation panel

### Exploratory Template

- Comprehensive chart grid
- Distribution analysis
- Correlation matrices
- Pattern insights

## 🔍 Technical Architecture

### MCP Integration

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Layer     │    │ MCP Dashboard   │
│   Dashboard UI  │◄──►│   FastAPI       │◄──►│ Server          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
                                                      ▼
                                               ┌─────────────────┐
                                               │ Dashboard       │
                                               │ Builder         │
                                               └─────────────────┘
                                                      │
                                                      ▼
                                               ┌─────────────────┐
                                               │ AI Agent        │
                                               │ (Groq)          │
                                               └─────────────────┘
```

### Component Structure

- **Dashboard Builder**: Core dashboard generation logic
- **MCP Server**: Model Context Protocol interface
- **AI Agent**: Groq-powered analysis and insights
- **Chart Generator**: Plotly-based visualization engine
- **Template Engine**: Jinja2-based HTML generation

## 🚦 Status & Health

### API Health Check

```bash
curl http://localhost:8000/health
```

### Dashboard Status

```bash
curl http://localhost:8000/api/dashboards
```

## 📚 Examples

### Quick Dashboard Generation

```javascript
// Frontend example
const response = await fetch("/api/dashboard/auto-generate", {
  method: "POST",
  body: formData,
});

const { dashboard } = await response.json();
console.log("Dashboard generated:", dashboard.id);
```

### Custom Dashboard

```javascript
const customization = {
  dashboard_type: "exploratory",
  customizations: {
    color_scheme: "purple",
    chart_size: "large",
  },
};
```

## 🛡️ Security

- CORS enabled for frontend integration
- File upload validation
- Secure file handling
- Environment variable protection

## 🔮 Future Enhancements

- [ ] Real-time dashboard updates
- [ ] Collaborative dashboards
- [ ] Custom template builder
- [ ] Advanced export formats (PDF, PowerPoint)
- [ ] Dashboard versioning
- [ ] User authentication
- [ ] Cloud storage integration

## 📖 Documentation

- [API Documentation](docs/api.md)
- [MCP Protocol](docs/mcp.md)
- [Dashboard Templates](docs/templates.md)
- [Customization Guide](docs/customization.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your enhancements
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:

- Create an issue on GitHub
- Check the documentation
- Review example code

---

**Built with ❤️ using FastAPI, React, and AI**
