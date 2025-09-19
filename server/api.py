from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import json
import os
import aiofiles
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import asyncio

from services.data_processor import DataProcessor
from services.ai_agent import AIAgent
from services.chart_generator import ChartGenerator
from services.dashboard_builder import DashboardBuilder
from services.mcp_dashboard_server import DashboardMCPInterface


def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj


router = APIRouter(prefix="/api", tags=["EDA"])

# In-memory storage for uploaded files (use database in production)
uploaded_files = {}


def initialize_uploaded_files():
    """Initialize uploaded_files from existing files in uploads directory"""
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        for filename in os.listdir(uploads_dir):
            if filename.endswith(".csv"):
                # Extract file_id from filename (format: {file_id}_{original_name}.csv)
                if "_" in filename:
                    file_id = filename.split("_")[0]
                    file_path = os.path.join(uploads_dir, filename)
                    original_name = (
                        "_".join(filename.split("_")[1:]).replace(".csv", "") + ".csv"
                    )

                    # Get file modification time as upload time
                    upload_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                    # Try reading basic metadata
                    shape = None
                    columns = None
                    dtypes = None
                    try:
                        df_meta = pd.read_csv(file_path, nrows=5)
                        columns = df_meta.columns.tolist()
                        # Get dtypes by reading a sample
                        dtypes = df_meta.dtypes.astype(str).to_dict()
                        # Get full shape efficiently by counting lines
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            row_count = sum(1 for _ in f) - 1  # minus header
                        shape = (max(row_count, 0), len(columns or []))
                    except Exception:
                        pass

                    uploaded_files[file_id] = {
                        "file_path": file_path,
                        "filename": original_name,
                        "original_filename": original_name,
                        "upload_time": upload_time,
                        "shape": shape,
                        "columns": columns,
                        "dtypes": dtypes,
                    }


# Initialize from existing files
initialize_uploaded_files()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload CSV file for EDA processing"""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    file_id = str(uuid.uuid4())
    file_path = f"uploads/{file_id}_{file.filename}"

    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)

    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # Load and validate CSV
    try:
        df = pd.read_csv(file_path)

        # Store file metadata
        uploaded_files[file_id] = {
            "filename": file.filename,
            "file_path": file_path,
            "upload_time": datetime.now(),
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
        }

        return {
            "file_id": file_id,
            "filename": file.filename,
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "preview": df.head().to_dict("records"),
        }

    except Exception as e:
        # Clean up file if CSV parsing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Error reading CSV file: {str(e)}")


@router.get("/file/{file_id}/info")
async def get_file_info(file_id: str):
    """Get basic information about uploaded file"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    processor = DataProcessor()
    basic_info = processor.get_basic_info(df)

    return basic_info


@router.get("/files/list")
async def list_uploaded_files():
    """Debug endpoint to list all available files"""
    return {
        "uploaded_files_count": len(uploaded_files),
        "uploaded_files": {
            file_id: info["original_filename"]
            for file_id, info in uploaded_files.items()
        },
        "uploads_directory": os.listdir("uploads") if os.path.exists("uploads") else [],
    }


@router.post("/process")
async def process_data(
    file_id: str = Form(...),
    operation: str = Form(...),  # 'clean', 'transform', 'classify', 'visualize'
    mode: str = Form(...),  # 'manual', 'ai'
    options: Optional[str] = Form(None),  # JSON string of options
):
    """Process data based on operation and mode"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    # Parse options if provided
    processed_options = json.loads(options) if options else {}

    processor = DataProcessor()
    chart_generator = ChartGenerator()

    try:
        if mode == "ai":
            ai_agent = AIAgent()
            result = await ai_agent.process_data(df, operation, processed_options)
        else:
            # Manual mode processing
            if operation == "clean":
                result = processor.clean_data(df, processed_options)
            elif operation == "transform":
                result = processor.transform_data(df, processed_options)
            elif operation == "classify":
                result = processor.classify_data(df, processed_options)
            elif operation == "visualize":
                result = chart_generator.generate_charts(df, processed_options)
            else:
                raise HTTPException(status_code=400, detail="Invalid operation")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.get("/charts/{file_id}")
async def get_charts(file_id: str, chart_types: Optional[str] = None):
    """Generate charts for visualization"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    chart_generator = ChartGenerator()
    charts = chart_generator.generate_all_charts(df, chart_types)

    return {"charts": charts}


@router.get("/insights/{file_id}")
async def get_ai_insights(file_id: str):
    """Get AI-generated insights about the dataset"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    ai_agent = AIAgent()
    insights = await ai_agent.generate_insights(df)

    return {"insights": insights}


@router.delete("/file/{file_id}")
async def delete_file(file_id: str):
    """Delete uploaded file"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]

    # Remove file from disk
    if os.path.exists(file_info["file_path"]):
        os.remove(file_info["file_path"])

    # Remove from memory
    del uploaded_files[file_id]

    return {"message": "File deleted successfully"}


@router.post("/cleanup-session")
async def cleanup_session():
    """Clean up all uploaded files and session data"""
    try:
        deleted_count = 0
        for file_id, file_info in list(uploaded_files.items()):
            try:
                # Remove file from disk
                if os.path.exists(file_info["file_path"]):
                    os.remove(file_info["file_path"])
                deleted_count += 1
            except OSError:
                pass  # File might already be deleted

        # Clear all from memory
        uploaded_files.clear()

        return {
            "success": True,
            "message": f"Session cleaned up successfully. {deleted_count} files removed.",
            "deleted_count": deleted_count,
        }
    except Exception as e:
        return {"success": False, "message": f"Error during cleanup: {str(e)}"}


# === AUTOMATED DASHBOARD ENDPOINTS ===


@router.post("/dashboard/auto-generate")
async def auto_generate_dashboard(
    file_id: str = Form(...), business_context: Optional[str] = Form(None)
):
    """Automatically generate the optimal dashboard for a dataset using MCP"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    file_path = file_info["file_path"]

    try:
        dashboard_interface = DashboardMCPInterface()
        result = await dashboard_interface.auto_generate_dashboard(
            file_path, business_context or ""
        )

        if result["success"]:
            return convert_numpy_types(
                {
                    "success": True,
                    "dashboard": result["dashboard"],
                    "recommendations": result.get("recommendations", []),
                    "data_profile": result.get("data_profile", {}),
                    "charts_generated": result.get("charts_generated", 0),
                    "insights_generated": result.get("insights_generated", 0),
                }
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Dashboard generation failed: {str(e)}"
        )


@router.post("/dashboard/generate-interactive")
async def generate_interactive_dashboard(
    file_id: str = Form(...),
    include_raw_data: bool = Form(False),
    business_context: str = Form(""),
):
    """Generate an AI-powered interactive dashboard using an agentic pipeline"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    try:
        # Generate charts using chart generator
        chart_generator = ChartGenerator()
        charts = chart_generator.generate_all_charts(df, "all")

        # Prepare summary statistics
        data_processor = DataProcessor()
        summary_stats = {
            "total_rows": len(df),
            "numeric_columns": df.select_dtypes(include=["number"]).columns.tolist(),
            "categorical_columns": df.select_dtypes(
                include=["object"]
            ).columns.tolist(),
            "column_stats": {},
            "missing_data": {
                "percentage": float((df.isnull().sum().sum() / df.size) * 100)
            },
        }

        # Add column statistics with proper type conversion
        for col in summary_stats["numeric_columns"]:
            if not df[col].isnull().all():  # Only if column has data
                summary_stats["column_stats"][col] = {
                    "mean": (
                        float(df[col].mean()) if not pd.isna(df[col].mean()) else 0.0
                    ),
                    "std": float(df[col].std()) if not pd.isna(df[col].std()) else 0.0,
                    "min": float(df[col].min()) if not pd.isna(df[col].min()) else 0.0,
                    "max": float(df[col].max()) if not pd.isna(df[col].max()) else 0.0,
                }

        # Prepare raw data for filtering (if requested)
        raw_data = None
        if include_raw_data:
            # Convert dataframe data to native Python types
            df_sample = df.head(1000)  # Limit to first 1000 rows
            raw_data = {
                "data": convert_numpy_types(df_sample.to_dict("records")),
                "columns": df.columns.tolist(),
                "numeric_columns": summary_stats["numeric_columns"],
                "categorical_columns": summary_stats["categorical_columns"],
                "unique_categories": {},
                "unique_dates": [],
            }

            # Add unique values for filtering
            for col in summary_stats["categorical_columns"][
                :5
            ]:  # Limit to 5 categorical columns
                unique_vals = (
                    df[col].dropna().unique()[:20].tolist()
                )  # Limit to 20 unique values
                raw_data["unique_categories"][col] = convert_numpy_types(unique_vals)

        # Build AI-powered interactive dashboard
        dashboard_builder = DashboardBuilder()
        dashboard_html = await dashboard_builder.build_ai_interactive_dashboard(
            dataset_name=file_info["filename"],
            df=df,
            charts=convert_numpy_types(charts),
            summary_stats=convert_numpy_types(summary_stats),
            raw_data=convert_numpy_types(raw_data) if raw_data else None,
            business_context=business_context,
        )

        return {
            "success": True,
            "dashboard": {
                "id": str(uuid.uuid4()),
                "html": dashboard_html,
                "type": "ai_interactive",
                "charts_count": len(charts),
                "features": {
                    "ai_powered": True,
                    "dynamic_filtering": True,
                    "kpi_cards": True,
                    "responsive_layout": True,
                    "real_time_updates": include_raw_data,
                    "agentic_ai": True,
                },
                "metadata": convert_numpy_types(
                    {
                        "dataset_name": file_info["filename"],
                        "total_rows": len(df),
                        "total_columns": len(df.columns),
                        "dataset_shape": [len(df), len(df.columns)],
                        "dashboard_sections": 6,
                        "interactive_features": [
                            "ai_insights",
                            "filters",
                            "kpis",
                            "drill_down",
                        ],
                        "generated_at": datetime.now().isoformat(),
                    }
                ),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Interactive dashboard generation failed: {str(e)}"
        )


@router.post("/dashboard/generate")
async def generate_dashboard(
    file_id: str = Form(...),
    dashboard_type: str = Form(
        "auto"
    ),  # auto, executive_summary, data_quality, exploratory
    customizations: Optional[str] = Form(None),  # JSON string
):
    """Generate specific type of dashboard"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    # Parse customizations
    custom_options = json.loads(customizations) if customizations else {}

    try:
        dashboard_builder = DashboardBuilder()

        # Analyze requirements
        requirements = await dashboard_builder.analyze_dashboard_requirements(
            df, dashboard_type
        )

        # Generate dashboard
        dashboard = await dashboard_builder.generate_dashboard(
            df, requirements, custom_options
        )

        return {
            "success": True,
            "dashboard": {
                "id": dashboard["id"],
                "type": dashboard["type"],
                "html": dashboard["html"],
                "metadata": dashboard["metadata"],
            },
            "charts_generated": len(dashboard["charts"]),
            "insights_generated": len(dashboard["insights"]),
            "requirements": requirements,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Dashboard generation failed: {str(e)}"
        )


@router.post("/dashboard/analyze-requirements")
async def analyze_dashboard_requirements(file_id: str = Form(...)):
    """Analyze dataset and get dashboard recommendations"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    try:
        dashboard_builder = DashboardBuilder()
        requirements = await dashboard_builder.analyze_dashboard_requirements(df)

        return convert_numpy_types(
            {
                "success": True,
                "requirements": requirements,
                "dataset_info": {
                    "shape": df.shape,
                    "columns": df.columns.tolist(),
                    "data_types": df.dtypes.astype(str).to_dict(),
                },
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Requirements analysis failed: {str(e)}"
        )


@router.get("/dashboard/templates")
async def get_dashboard_templates():
    """Get available dashboard templates and their descriptions"""
    dashboard_interface = DashboardMCPInterface()
    result = await dashboard_interface.mcp_server.handle_request("get_templates", {})

    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=result["error"])


@router.post("/dashboard/recommendations")
async def get_dashboard_recommendations(
    file_id: str = Form(...), business_context: Optional[str] = Form(None)
):
    """Get AI-powered dashboard recommendations"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    file_path = file_info["file_path"]

    try:
        dashboard_interface = DashboardMCPInterface()
        result = await dashboard_interface.get_dashboard_recommendations(
            file_path, business_context or ""
        )

        if result["success"]:
            return convert_numpy_types(result)
        else:
            raise HTTPException(status_code=500, detail=result["error"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")


@router.get("/dashboard/{dashboard_id}")
async def get_dashboard(dashboard_id: str):
    """Get specific dashboard by ID"""
    try:
        dashboard_builder = DashboardBuilder()
        dashboard = await dashboard_builder.get_dashboard(dashboard_id)

        if dashboard:
            return {"success": True, "dashboard": dashboard}
        else:
            raise HTTPException(status_code=404, detail="Dashboard not found")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve dashboard: {str(e)}"
        )


@router.get("/dashboard/{dashboard_id}/export")
async def export_dashboard(dashboard_id: str, format: str = "html"):
    """Export dashboard in specified format"""
    try:
        dashboard_builder = DashboardBuilder()
        export_result = await dashboard_builder.export_dashboard(dashboard_id, format)

        return {"success": True, "export": export_result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/dashboards")
async def list_dashboards():
    """List all created dashboards"""
    try:
        dashboard_builder = DashboardBuilder()
        dashboards = await dashboard_builder.list_dashboards()

        return {
            "success": True,
            "dashboards": dashboards,
            "total_count": len(dashboards),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list dashboards: {str(e)}"
        )


@router.post("/dashboard/generate-all-types")
async def generate_all_dashboard_types(file_id: str = Form(...)):
    """Generate all three dashboard types for comparison"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    file_path = file_info["file_path"]

    try:
        dashboard_interface = DashboardMCPInterface()
        result = await dashboard_interface.generate_all_dashboard_types(file_path)

        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail="Failed to generate dashboards")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Dashboard generation failed: {str(e)}"
        )
