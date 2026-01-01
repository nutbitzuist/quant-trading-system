"""
Reports API Routes
Endpoints for generating PDF and other reports
"""

from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse
from datetime import datetime

from app.reports.pdf_generator import PDFReportGenerator, ReportData, create_mock_report_data

router = APIRouter()


@router.get("/pdf")
async def generate_pdf_report():
    """
    Generate PDF report of current analysis.
    
    Returns HTML report (can be printed to PDF).
    """
    generator = PDFReportGenerator()
    data = create_mock_report_data()
    
    html = generator.generate_html(data)
    
    return HTMLResponse(content=html)


@router.get("/pdf/download")
async def download_pdf_report():
    """
    Download PDF report.
    
    Attempts to generate actual PDF if weasyprint is available.
    """
    generator = PDFReportGenerator()
    data = create_mock_report_data()
    
    try:
        from weasyprint import HTML
        html = generator.generate_html(data)
        pdf = HTML(string=html).write_pdf()
        
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=quant-report-{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )
    except ImportError:
        # Return HTML if weasyprint not available
        html = generator.generate_html(data)
        return HTMLResponse(
            content=html,
            headers={
                "Content-Disposition": f"attachment; filename=quant-report-{datetime.now().strftime('%Y%m%d')}.html"
            }
        )


@router.get("/summary")
async def get_report_summary():
    """
    Get report summary data (for API consumption).
    """
    data = create_mock_report_data()
    
    return {
        "regime": data.regime,
        "volatility": data.volatility,
        "timestamp": data.timestamp,
        "top_buy": [
            {"ticker": s["ticker"], "score": s["score"], "signal": s["signal"]}
            for s in data.top_buy[:5]
        ],
        "top_avoid": [
            {"ticker": s["ticker"], "score": s["score"], "signal": s["signal"]}
            for s in data.top_avoid[:5]
        ],
        "active_models": data.active_models,
        "total_screened": data.total_screened,
    }
