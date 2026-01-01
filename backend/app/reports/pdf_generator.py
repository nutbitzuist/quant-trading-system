"""
PDF Report Generator
Generates comprehensive stock analysis reports
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import io


@dataclass
class ReportData:
    """Data for report generation."""
    regime: str
    volatility: str
    timestamp: str
    top_buy: List[Dict[str, Any]]
    top_avoid: List[Dict[str, Any]]
    sector_recommendations: Dict[str, str]
    model_weights: Dict[str, float]
    active_models: int
    total_screened: int


class PDFReportGenerator:
    """
    Generates PDF reports for stock analysis.
    
    Uses reportlab for PDF generation.
    Falls back to HTML if reportlab not available.
    """
    
    def __init__(self):
        """Initialize generator."""
        self.title = "Quant Trading System"
        self.subtitle = "Thai SET100 Analysis Report"
    
    def generate_html(self, data: ReportData) -> str:
        """
        Generate HTML report (can be converted to PDF).
        
        Args:
            data: Report data
            
        Returns:
            HTML string
        """
        top_buy_rows = "\n".join([
            f"""
            <tr>
                <td>{i+1}</td>
                <td><strong>{stock['ticker']}</strong></td>
                <td>{stock['score']:.1f}</td>
                <td><span class="signal-{stock['signal'].lower().replace('_', '-')}">{stock['signal']}</span></td>
                <td>{stock['agreement']*100:.0f}%</td>
                <td>{stock.get('position', 0):.1f}%</td>
            </tr>
            """
            for i, stock in enumerate(data.top_buy[:10])
        ])
        
        top_avoid_rows = "\n".join([
            f"""
            <tr>
                <td>{i+1}</td>
                <td><strong>{stock['ticker']}</strong></td>
                <td>{stock['score']:.1f}</td>
                <td><span class="signal-{stock['signal'].lower().replace('_', '-')}">{stock['signal']}</span></td>
                <td>{stock['agreement']*100:.0f}%</td>
            </tr>
            """
            for i, stock in enumerate(data.top_avoid[:10])
        ])
        
        sector_rows = "\n".join([
            f"<tr><td>{sector}</td><td class='{rec.lower()}'>{rec}</td></tr>"
            for sector, rec in data.sector_recommendations.items()
        ])
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{self.title} - Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            color: #1a1a1a;
            line-height: 1.5;
            padding: 40px;
            max-width: 1000px;
            margin: 0 auto;
        }}
        .header {{ 
            text-align: center; 
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #D4AF37;
        }}
        h1 {{ font-size: 28px; color: #1E3A5F; }}
        h2 {{ font-size: 18px; color: #666; margin-top: 8px; }}
        h3 {{ font-size: 16px; margin: 20px 0 10px; color: #1E3A5F; }}
        
        .meta {{ 
            display: flex; 
            justify-content: space-between; 
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .meta-item {{ text-align: center; }}
        .meta-label {{ font-size: 12px; color: #666; }}
        .meta-value {{ font-size: 18px; font-weight: bold; }}
        
        .regime-bull {{ color: #22C55E; }}
        .regime-bear {{ color: #EF4444; }}
        .regime-sideways {{ color: #F59E0B; }}
        
        .section {{ margin-bottom: 30px; }}
        
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; color: #1E3A5F; }}
        tr:hover {{ background: #f8f9fa; }}
        
        .signal-strong-buy {{ background: #16A34A; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
        .signal-buy {{ background: #4ADE80; color: black; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
        .signal-hold {{ background: #A3A3A3; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
        .signal-avoid {{ background: #FB923C; color: black; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
        .signal-strong-avoid {{ background: #DC2626; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
        
        .overweight {{ color: #22C55E; font-weight: 600; }}
        .neutral {{ color: #666; }}
        .underweight {{ color: #EF4444; font-weight: 600; }}
        
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        
        .footer {{ 
            margin-top: 40px; 
            padding-top: 20px; 
            border-top: 1px solid #eee; 
            text-align: center; 
            color: #666;
            font-size: 12px;
        }}
        
        @media print {{
            body {{ padding: 20px; }}
            .meta {{ break-inside: avoid; }}
            table {{ break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 {self.title}</h1>
        <h2>{self.subtitle}</h2>
    </div>
    
    <div class="meta">
        <div class="meta-item">
            <div class="meta-label">Market Regime</div>
            <div class="meta-value regime-{data.regime.lower()}">{data.regime}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Volatility</div>
            <div class="meta-value">{data.volatility}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Active Models</div>
            <div class="meta-value">{data.active_models}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Stocks Screened</div>
            <div class="meta-value">{data.total_screened}</div>
        </div>
    </div>
    
    <div class="section">
        <h3>🟢 Top Buy Recommendations</h3>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Ticker</th>
                    <th>Score</th>
                    <th>Signal</th>
                    <th>Agreement</th>
                    <th>Position %</th>
                </tr>
            </thead>
            <tbody>
                {top_buy_rows}
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h3>🔴 Top Avoid List</h3>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Ticker</th>
                    <th>Score</th>
                    <th>Signal</th>
                    <th>Agreement</th>
                </tr>
            </thead>
            <tbody>
                {top_avoid_rows}
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h3>📈 Sector Recommendations</h3>
        <div class="grid">
            <table>
                <thead><tr><th>Sector</th><th>Recommendation</th></tr></thead>
                <tbody>{sector_rows}</tbody>
            </table>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated from Quant Stock Analysis, quant.myalgostack.com</p>
        <p>Report generated: {data.timestamp} (GMT+7)</p>
        <p>This report is for informational purposes only. Not financial advice.</p>
    </div>
</body>
</html>
        """
        
        return html
    
    def generate_report(self, data: ReportData) -> bytes:
        """
        Generate PDF report.
        
        Args:
            data: Report data
            
        Returns:
            PDF bytes
        """
        try:
            from weasyprint import HTML
            html = self.generate_html(data)
            pdf = HTML(string=html).write_pdf()
            return pdf
        except ImportError:
            # Fall back to HTML if weasyprint not available
            return self.generate_html(data).encode('utf-8')


def create_mock_report_data() -> ReportData:
    """Create mock data for testing."""
    return ReportData(
        regime="BULL",
        volatility="NORMAL",
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        top_buy=[
            {"ticker": "DELTA", "score": 92.5, "signal": "STRONG_BUY", "agreement": 0.85, "position": 8.5},
            {"ticker": "GPSC", "score": 88.2, "signal": "STRONG_BUY", "agreement": 0.82, "position": 7.2},
            {"ticker": "BDMS", "score": 85.0, "signal": "BUY", "agreement": 0.78, "position": 6.8},
            {"ticker": "SCB", "score": 82.3, "signal": "BUY", "agreement": 0.75, "position": 6.5},
            {"ticker": "AOT", "score": 80.1, "signal": "BUY", "agreement": 0.72, "position": 6.0},
        ],
        top_avoid=[
            {"ticker": "THAI", "score": 15.2, "signal": "STRONG_AVOID", "agreement": 0.88},
            {"ticker": "BA", "score": 18.5, "signal": "STRONG_AVOID", "agreement": 0.85},
            {"ticker": "MINT", "score": 22.1, "signal": "AVOID", "agreement": 0.72},
        ],
        sector_recommendations={
            "FINCIAL": "OVERWEIGHT",
            "TECH": "OVERWEIGHT",
            "INDUS": "NEUTRAL",
            "RESOURC": "UNDERWEIGHT",
            "PROPCON": "UNDERWEIGHT",
        },
        model_weights={"hqm": 1.2, "adx": 1.0, "quality": 0.8},
        active_models=12,
        total_screened=100,
    )
