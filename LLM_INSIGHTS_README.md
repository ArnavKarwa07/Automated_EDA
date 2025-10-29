# LLM Insights Engine - Real-Time Dashboard Analysis

## Overview

The **LLM Insights Engine** is an advanced AI-powered analysis system that generates real-time, actionable insights for your dashboards and data. It goes beyond basic statistics to provide strategic recommendations, pattern discovery, and business intelligence.

## Features

### 🤖 **AI-Powered Analysis**

- Uses GPT-4 (or GPT-3.5-turbo) for intelligent data interpretation
- Context-aware insights based on dashboard type and user goals
- Natural language explanations of complex patterns

### 📊 **Dashboard-Specific Insights**

#### **Executive Dashboards**

- **Executive Summary**: High-level overview for C-suite decision making
- **Key Performance Insights**: Critical trends and metrics analysis
- **Strategic Opportunities**: Data-driven growth opportunities
- **Risk Factors**: Potential concerns requiring attention
- **Recommended Actions**: Prioritized, actionable next steps
- **Business Impact**: Translation of insights to business outcomes

#### **Data Quality Dashboards**

- **Quality Score**: 0-100 assessment with detailed justification
- **Critical Issues**: Most serious data quality problems
- **Completeness Analysis**: Missing data impact assessment
- **Consistency Findings**: Type, format, and range issues
- **Anomalies Detection**: Outliers and unusual patterns
- **Remediation Priorities**: Ordered fix list with impact estimates
- **Readiness Assessment**: Production-readiness evaluation

#### **Exploratory Dashboards**

- **Pattern Discovery**: Hidden relationships and trends
- **Correlation Insights**: Significant relationships and implications
- **Distribution Analysis**: Data distribution characteristics
- **Segmentation Opportunities**: Natural groupings in data
- **Statistical Highlights**: Interesting statistical findings
- **Hypothesis Generation**: Testable hypotheses for further research
- **Deep Dive Recommendations**: Areas warranting detailed analysis

### 🎯 **Intelligent Features**

- **Context-Aware**: Adapts analysis based on user-provided context
- **Fallback Mode**: Works without LLM using statistical analysis
- **Structured Output**: JSON format for programmatic access
- **Human-Readable Summaries**: Formatted for dashboard display

## Installation & Setup

### Prerequisites

```bash
# Install required packages (server)
pip install -r server/requirements.txt
```

### Environment Configuration

```bash
# Preferred: Groq (fast, cost-effective)
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.1-70b-versatile

# Optional: OpenAI fallback
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini
```

### Backend Integration

The LLM Insights Engine is automatically integrated into the LangGraph dashboard workflow:

```python
# In langgraph_dashboard_builder.py
from services.llm_insights_engine import LLMInsightsEngine

# Initialized automatically in LangGraphDashboardBuilder
self.insights_engine = LLMInsightsEngine()  # auto-selects Groq if GROQ_API_KEY is set
```

## Usage

### Backend API

Insights are automatically generated when creating dashboards:

```python
# API endpoint: /api/langgraph/dashboard/generate
POST /api/langgraph/dashboard/generate
{
  "file_id": "your_file_id",
  "dashboard_type": "executive",  # or "data_quality", "exploratory"
  "user_context": "Q4 Performance Review",
  "target_audience": "executive"
}

# Response includes llm_insights
{
  "success": true,
  "llm_insights": {
    "analysis_type": "executive",
    "executive_summary": "...",
    "key_insights": [...],
    "opportunities": [...],
    "risks": [...],
    "recommendations": [...],
    "business_impact": "...",
    "generated_at": "2024-01-01T12:00:00"
  }
}
```

### Frontend Integration

Use the `LLMInsightsPanel` component:

```jsx
import LLMInsightsPanel from "../components/LLMInsightsPanel";

// In your dashboard page/component
<LLMInsightsPanel
  llmInsights={dashboardData.llm_insights}
  dashboardType="executive"
/>;
```

### Direct Usage

Generate insights independently:

```python
from services.llm_insights_engine import LLMInsightsEngine
import pandas as pd

# Initialize engine
engine = LLMInsightsEngine(
    model_name="gpt-4o-mini",  # or "gpt-3.5-turbo"
    temperature=0.3
)

# Generate insights
insights = engine.analyze_dashboard(
    df=your_dataframe,
    dashboard_type="executive",
    chart_specs=chart_specifications,
    data_analysis=statistical_analysis,
    user_context="Q4 Business Review"
)

# Access insights
print(insights['executive_summary'])
print(insights['recommendations'])
```

## Architecture

### Workflow Integration

```
Dashboard Generation Workflow:
1. Initialize Session
2. Convert Data to JSON
3. Analyze Requirements
4. Generate Layout
5. Create Charts
6. Generate Basic Insights
7. 🆕 Generate LLM Insights  ← NEW NODE
8. Generate Code
9. Verify Code
10. Finalize Dashboard
```

### State Management

```python
class DashboardGenerationState(TypedDict):
    # ... other fields ...
    insights: List[str]  # Basic insights
    llm_insights: Dict[str, Any]  # 🆕 Structured LLM insights
```

### Prompting Strategy

The engine uses specialized prompts for each dashboard type:

```python
# Executive Dashboard Prompt
SystemMessage: "You are an expert business intelligence analyst..."
HumanMessage: "Analyze this executive dashboard and provide strategic insights..."

# Data Quality Prompt
SystemMessage: "You are a data quality expert..."
HumanMessage: "Assess the data quality of this dataset..."

# Exploratory Prompt
SystemMessage: "You are a data scientist and statistical analyst..."
HumanMessage: "Perform exploratory analysis on this dataset..."
```

## Examples

### Executive Dashboard Analysis

```python
# Input
df = pd.DataFrame({
    'revenue': [100000, 120000, 115000, 130000],
    'profit': [20000, 25000, 22000, 28000],
    'customers': [1000, 1100, 1050, 1200]
})

# Output
{
    "executive_summary": "Revenue shows 30% growth trend with strong customer acquisition. Profit margins stable at 20%. Slight dip in month 3 suggests seasonal effect.",

    "key_insights": [
        "Revenue grew 30% over the period with consistent upward trend",
        "Customer base increased 20% indicating successful acquisition",
        "Profit margins maintained at healthy 20% level"
    ],

    "opportunities": [
        "Capitalize on growth momentum with targeted marketing",
        "Investigate and replicate success factors from high-performing periods"
    ],

    "recommendations": [
        "Set up automated alerts for revenue dips >5%",
        "Analyze customer cohorts to identify high-value segments",
        "Forecast next quarter revenue using current growth trajectory"
    ]
}
```

### Data Quality Assessment

```python
# Input: Dataset with missing values and outliers

# Output
{
    "quality_score": 72,
    "score_justification": "Good completeness (85%) offset by outlier concerns",

    "critical_issues": [
        "15% missing values in 'income' column",
        "Outliers detected in 'age' field (value: 1000)",
        "Inconsistent date formats in 'signup_date'"
    ],

    "remediation_priorities": [
        "Priority 1: Remove/fix outlier in 'age' (data entry error likely)",
        "Priority 2: Impute missing 'income' using median by segment",
        "Priority 3: Standardize date formats to ISO 8601"
    ],

    "readiness_assessment": "Data requires cleaning before production use. Estimated 2-4 hours for remediation."
}
```

### Exploratory Analysis

```python
# Input: Employee dataset with multiple variables

# Output
{
    "patterns": [
        "Strong positive correlation (r=0.89) between experience and income",
        "Age distribution shows bimodal pattern suggesting two employee cohorts",
        "Job satisfaction peaks at 10-15 years experience then declines"
    ],

    "hypotheses": [
        "Education level moderates the experience-income relationship",
        "Satisfaction decline after 15 years may indicate burnout",
        "Department differences account for 40% of salary variance"
    ],

    "deep_dive_recommendations": [
        "Segment analysis by department to identify retention issues",
        "Investigate satisfaction drivers in 10-15 year cohort",
        "Build predictive model for high-potential employees"
    ]
}
```

## Configuration

### Model Selection

```python
# High quality (recommended)
engine = LLMInsightsEngine(model_name="gpt-4o-mini", temperature=0.3)

# Faster/cheaper
engine = LLMInsightsEngine(model_name="gpt-3.5-turbo", temperature=0.3)

# More creative (higher temperature)
engine = LLMInsightsEngine(model_name="gpt-4o-mini", temperature=0.7)
```

### Fallback Behavior

If OpenAI API is unavailable:

```python
# Automatic fallback to statistical insights
try:
    insights_engine = LLMInsightsEngine()
    use_llm_insights = True
except Exception:
    use_llm_insights = False
    # Falls back to rule-based insights
```

## Performance

### Latency

- **LLM Mode**: 3-8 seconds (API call to OpenAI)
- **Fallback Mode**: <1 second (local computation)

### Cost

- **Executive Dashboard**: ~1,500 tokens = $0.002 per analysis
- **Data Quality**: ~2,000 tokens = $0.003 per analysis
- **Exploratory**: ~2,500 tokens = $0.004 per analysis

### Caching

Results are included in dashboard state and can be cached:

```python
# Cache insights in result
result["llm_insights"] = insights
```

## Testing

Run comprehensive tests:

```bash
cd server
python test_llm_insights.py
```

Expected output:

```
🤖 LLM INSIGHTS ENGINE TEST SUITE 🤖

Testing Executive Dashboard LLM Insights
✅ Insights generated successfully!
📊 Executive Summary: ...
🎯 Key Insights: ...

Testing Data Quality Dashboard LLM Insights
✅ Quality insights generated!
📊 Overall Quality Score: 87/100

Testing Exploratory Dashboard LLM Insights
✅ Exploratory insights generated!
🔍 Key Patterns Discovered: ...

✅ All LLM insights tests PASSED!
```

## Troubleshooting

### Common Issues

**Issue**: `ValueError: OPENAI_API_KEY environment variable not set`

```bash
# Solution
export OPENAI_API_KEY=your_key_here
# or add to .env file
```

**Issue**: LLM returns malformed JSON

```python
# The engine has built-in JSON extraction
# Falls back to structured defaults if parsing fails
```

**Issue**: Slow response times

```python
# Use faster model
engine = LLMInsightsEngine(model_name="gpt-3.5-turbo")

# Or reduce context size (implemented automatically)
```

## Best Practices

1. **Provide Context**: Include user_context for better insights

   ```python
   user_context="Q4 2024 Executive Review - Focus on growth metrics"
   ```

2. **Choose Right Dashboard Type**: Insights are optimized per type

   - Use "executive" for KPI/business analysis
   - Use "data_quality" for data preparation
   - Use "exploratory" for pattern discovery

3. **Review Fallback Insights**: Test without LLM to ensure graceful degradation

4. **Monitor Costs**: Track API usage in production

   ```python
   # Log insights generation
   logger.info(f"LLM insights cost: ~{token_count * 0.000002} USD")
   ```

5. **Cache Results**: Store insights to avoid regeneration
   ```python
   # Include in dashboard metadata
   dashboard["metadata"]["llm_insights"] = insights
   ```

## Future Enhancements

- [ ] Multi-language support
- [ ] Custom insight templates
- [ ] Insight confidence scores
- [ ] Historical trend analysis
- [ ] Comparative dashboard insights
- [ ] Interactive insight refinement
- [ ] Export insights as PDF reports

## API Reference

### `LLMInsightsEngine`

#### Constructor

```python
LLMInsightsEngine(
    model_name: str = "gpt-4o-mini",
    temperature: float = 0.3
)
```

#### Methods

**`analyze_dashboard(df, dashboard_type, chart_specs, data_analysis, user_context=None)`**

- Returns: `Dict[str, Any]` - Structured insights

**`_analyze_executive_dashboard(...)`** - Executive-specific insights

**`_analyze_data_quality(...)`** - Data quality assessment

**`_analyze_exploratory_dashboard(...)`** - Pattern discovery

### `generate_insights_summary(insights)`

Converts structured insights to readable summary list.

```python
summary = generate_insights_summary(insights)
# Returns: List[str] - Formatted summary points
```

## Contributing

To add new insight types:

1. Create new analysis method in `LLMInsightsEngine`
2. Add corresponding prompt template
3. Update `analyze_dashboard()` router
4. Add frontend rendering in `LLMInsightsPanel`
5. Add tests in `test_llm_insights.py`

## License

Part of the Automated EDA project.
