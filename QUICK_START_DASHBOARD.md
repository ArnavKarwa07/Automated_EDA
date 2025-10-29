# Quick Start: LLM Dashboard Generator

## What Changed?

Your project now has an **intelligent dashboard generator** that creates Power BI/Tableau-style dashboards using AI instead of templates.

### Before vs After

**BEFORE** (Template-based):

- ❌ Static templates with limited customization
- ❌ Same layout for every dataset
- ❌ Manual code editing required

**AFTER** (LLM-powered):

- ✅ AI generates custom code for each dataset
- ✅ Adaptive layouts based on data characteristics
- ✅ Production-ready HTML/JSX dashboards
- ✅ Automatic verification & quality checks

## Fixed Issues

### 1. NumPy/SciPy Compatibility ✅

**Problem**: `NumPy version >=1.22.4 and <2.3.0 is required`

**Fixed**: Updated `requirements.txt` to pin NumPy to compatible version:

```
numpy>=1.22.4,<2.3.0
```

### 2. LangGraph Import Error ✅

**Problem**: `cannot import name 'ToolNode' from 'langgraph.prebuilt'`

**Fixed**: Removed unused import from `langgraph_agents.py`

### 3. Dashboard Generation Quality ✅

**Problem**: Template-based dashboards not producing Power BI/Tableau quality

**Fixed**:

- New LLM-driven code generator with structured prompts
- Comprehensive verification system
- Fallback to deterministic generator if LLM unavailable

## Quick Test (5 Minutes)

### Step 1: Install Dependencies

```powershell
cd server
pip install -r requirements.txt
```

### Step 2: Run Test Script

```powershell
# Basic test (uses fallback generator)
python test_dashboard_generation.py
```

**Expected Output**:

```
================================================================================
DASHBOARD GENERATION TEST
================================================================================

📊 Loading dataset: diabetes.csv
   ✓ Loaded 768 rows × 9 columns

────────────────────────────────────────────────────────────────────────────────
Testing: EXPLORATORY Dashboard
────────────────────────────────────────────────────────────────────────────────
   LLM Mode: DISABLED (using fallback)
   Generating dashboard...
   ✓ Dashboard generation successful!
   Generated HTML: 15,234 characters
   Charts configured: 4
   Insights generated: 5

   Verification Status: PASS
   Passed Checks: 8
   Warnings: 2
   Critical Issues: 0

   💾 Dashboard saved to: server/generated_dashboards/exploratory_dashboard_diabetes.html
   📂 Open in browser to view!
```

### Step 3: View Dashboard

Open the generated HTML file in your browser:

```powershell
# Find generated dashboards
ls generated_dashboards/*.html

# Open in default browser (Windows)
start generated_dashboards/exploratory_dashboard_diabetes.html
```

## Enable LLM Mode (Optional)

For even better quality dashboards, enable LLM generation:

### Step 1: Set API Key

```powershell
# Set your OpenAI API key
$env:OPENAI_API_KEY = "sk-your-key-here"

# Optional: Use GPT-4 for best quality
$env:USE_GPT4 = "true"
```

### Step 2: Run Test Again

```powershell
python test_dashboard_generation.py
```

**Expected Output** (with LLM):

```
   LLM Mode: ENABLED ✓
   Generating dashboard...
   ✓ Dashboard generation successful!

   LLM Review Score: 88/100
   Summary: Well-structured dashboard with excellent chart integration
```

## Use in Your Application

### Simple Example

```python
import pandas as pd
from services.langgraph_dashboard_builder import LangGraphDashboardBuilder

# Load your data
df = pd.read_csv("your_data.csv")

# Generate dashboard
builder = LangGraphDashboardBuilder()
result = await builder.build_dashboard(
    df=df,
    dashboard_type="exploratory"
)

# Save result
if result["success"]:
    with open("output.html", "w") as f:
        f.write(result["dashboard_html"])
    print("Dashboard created!")
```

### FastAPI Integration

Your existing API should work with minimal changes:

```python
# In api.py - update existing endpoint
@router.post("/generate-dashboard")
async def generate_dashboard(file: UploadFile):
    df = pd.read_csv(file.file)

    builder = LangGraphDashboardBuilder()
    result = await builder.build_dashboard(df=df)

    return {
        "html": result["dashboard_html"],
        "insights": result["insights"],
        "verification": result["verification_report"]
    }
```

## Dashboard Types

Try different types based on your needs:

### 1. Executive Dashboard

```python
result = await builder.build_dashboard(
    df=df,
    dashboard_type="executive",
    user_context="Sales performance Q4 2025",
    target_audience="executive"
)
```

**Features**: KPIs, trends, business metrics, minimal design

### 2. Data Quality Dashboard

```python
result = await builder.build_dashboard(
    df=df,
    dashboard_type="data_quality",
    target_audience="data_scientist"
)
```

**Features**: Missing data analysis, outliers, consistency checks

### 3. Exploratory Dashboard

```python
result = await builder.build_dashboard(
    df=df,
    dashboard_type="exploratory",
    target_audience="analyst"
)
```

**Features**: Correlations, distributions, comprehensive analysis

## Verification System

Every generated dashboard is automatically verified:

```python
result = await builder.build_dashboard(df=df)

# Check verification
verification = result["verification_report"]

print(f"Status: {verification['overall_status']}")  # PASS or FAIL
print(f"Passed: {len(verification['passed_checks'])}")
print(f"Warnings: {len(verification['warnings'])}")
print(f"Critical: {len(verification['critical_issues'])}")

# LLM review (if enabled)
if verification.get("llm_review"):
    review = verification["llm_review"]
    print(f"Score: {review['score']}/100")
    print(f"Summary: {review['summary']}")
```

## Troubleshooting

### Dependencies Won't Install

```powershell
# Create fresh virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Import Errors

```powershell
# Ensure you're in the server directory
cd server

# Run test from server directory
python test_dashboard_generation.py
```

### No Dashboards Generated

Check that you have CSV files in `uploads/`:

```powershell
# List CSV files
ls ..\uploads\*.csv

# If none, copy a sample
cp path\to\your\data.csv ..\uploads\
```

### LLM Not Working

1. Check API key is set:

   ```powershell
   echo $env:OPENAI_API_KEY
   ```

2. Verify langchain installation:

   ```powershell
   pip show langchain langchain-openai
   ```

3. Check logs for specific errors

**Note**: System automatically falls back to deterministic generator if LLM fails

## Next Steps

1. ✅ **Test with your data**: Run `test_dashboard_generation.py` with your datasets
2. ✅ **View generated dashboards**: Open HTML files in browser
3. ✅ **Integrate into API**: Update your FastAPI endpoints
4. ✅ **Enable LLM** (optional): Set `OPENAI_API_KEY` for best quality
5. ✅ **Customize**: Modify prompts and dashboard types as needed

## Support

- 📖 **Full Documentation**: See `LLM_DASHBOARD_GENERATOR_README.md`
- 🐛 **Issues**: Check verification reports for debugging
- 💡 **Examples**: Run test script to see working examples

---

**Ready to generate dashboards!** 🚀

Run: `python test_dashboard_generation.py`
