"""
Report API Routes
Endpoints for generating and downloading PDF/Excel reports
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import io
import logging
from datetime import datetime

from services.report_service import get_report_service
from services.ai_chat_service import get_analytics_summary, get_analytics_trends
from app.deps import get_current_user, get_admin_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportRequest(BaseModel):
    """Report generation request"""
    report_type: str  # daily, forecast, analytics, kz_market
    product_id: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


@router.get("/daily")
async def get_daily_report(
    format: str = Query("excel", enum=["excel", "csv"]),
    current_user=Depends(get_current_user)
):
    """Generate daily summary report"""
    try:
        report_service = get_report_service()

        # Get analytics data
        summary = await get_analytics_summary()
        trends = await get_analytics_trends()

        # Prepare report data
        data = {
            'summary': {
                'Total Products': summary.get('total_products', 0),
                'Total Records': summary.get('total_records', 0),
                'Average Demand': round(summary.get('avg_demand', 0), 2),
                'Report Date': datetime.now().strftime('%Y-%m-%d'),
            },
            'top_products': trends.get('rising', [])[:10],
            'alerts': [],  # Could integrate with alert service
        }

        # Generate Excel report
        excel_bytes = await report_service.generate_daily_report_excel(data)

        # Return as downloadable file
        filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.xlsx"

        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.error(f"Daily report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/{product_id}")
async def get_forecast_report(
    product_id: str,
    horizon_days: int = Query(7, ge=1, le=30),
    current_user=Depends(get_current_user)
):
    """Generate forecast report for a specific product"""
    try:
        from services.model_service import get_or_train_model, predict
        from services.insight_service import InsightGenerator

        report_service = get_report_service()

        # Get model and predictions
        model_data = get_or_train_model(product_id=product_id)
        if not model_data:
            raise HTTPException(status_code=404, detail="Product not found")

        model = model_data['model']
        df = model_data['df']
        metrics = model_data['metrics']

        # Get predictions
        predictions = predict(model, df, horizon_days=horizon_days)

        # Prepare history data
        history = []
        if not df.empty:
            recent_df = df.tail(30)
            for _, row in recent_df.iterrows():
                history.append({
                    'date': str(row.get('Date', '')),
                    'demand': float(row.get('Units Sold', 0)),
                    'inventory': float(row.get('Inventory Level', 0)),
                    'price': float(row.get('Unit Price', 0)),
                })

        # Prepare forecast data
        forecast = []
        for pred in predictions:
            forecast.append({
                'date': pred.get('date', ''),
                'predicted_demand': pred.get('predicted_demand', 0),
                'lower_bound': pred.get('predicted_demand', 0) * 0.85,
                'upper_bound': pred.get('predicted_demand', 0) * 1.15,
            })

        # Generate insights
        insight_gen = InsightGenerator()
        insights = insight_gen.generate_full_insight(
            product_id=product_id,
            predictions=predictions,
            metrics=metrics,
            history_df=df
        )

        # Generate Excel report
        excel_bytes = await report_service.generate_forecast_report_excel(
            product_id=product_id,
            history=history,
            forecast=forecast,
            insights=insights
        )

        filename = f"forecast_{product_id}_{datetime.now().strftime('%Y%m%d')}.xlsx"

        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forecast report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_analytics_report(
    current_user=Depends(get_current_user)
):
    """Generate analytics report"""
    try:
        report_service = get_report_service()

        # Get analytics data
        summary = await get_analytics_summary()
        trends = await get_analytics_trends()

        # Prepare data
        analytics_data = {
            'summary': summary,
            'trending_up': [
                {'product_id': p.get('product_id', ''), 'growth': p.get('growth', 0)}
                for p in trends.get('rising', [])[:10]
            ],
            'trending_down': [
                {'product_id': p.get('product_id', ''), 'growth': p.get('growth', 0)}
                for p in trends.get('declining', [])[:10]
            ],
            'categories': summary.get('categories', []),
        }

        # Generate report
        excel_bytes = await report_service.generate_analytics_report_excel(analytics_data)

        filename = f"analytics_report_{datetime.now().strftime('%Y%m%d')}.xlsx"

        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.error(f"Analytics report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kz-market")
async def get_kz_market_report(
    product_name: str = Query(..., min_length=1),
    wholesale_price: float = Query(..., gt=0),
    markup_percent: float = Query(25, ge=0, le=100),
    current_user=Depends(get_current_user)
):
    """Generate Kazakhstan market analysis report"""
    try:
        from services.kz_market_service import KZ_CITIES, CATEGORY_MULTIPLIERS

        report_service = get_report_service()

        # Calculate profitability for each city
        cities_data = []
        for city_id, city_info in KZ_CITIES.items():
            demand_mult = city_info.get('demand_multiplier', 1.0)
            competition = city_info.get('competition', 'medium')

            # Adjust markup based on competition
            comp_adjust = {'low': 1.1, 'medium': 1.0, 'high': 0.9}.get(competition, 1.0)
            effective_markup = markup_percent * comp_adjust

            retail_price = wholesale_price * (1 + effective_markup / 100)
            profit = retail_price - wholesale_price
            margin = (profit / retail_price) * 100 if retail_price > 0 else 0

            # Generate recommendation
            if margin >= 25 and demand_mult >= 0.8:
                recommendation = "✅ Highly Recommended"
            elif margin >= 20 and demand_mult >= 0.6:
                recommendation = "👍 Recommended"
            elif margin >= 15:
                recommendation = "⚠️ Consider"
            else:
                recommendation = "❌ Not Recommended"

            cities_data.append({
                'city': city_info.get('name', city_id),
                'tier': city_info.get('tier', 3),
                'retail_price': retail_price,
                'profit': profit,
                'margin': margin,
                'recommendation': recommendation,
            })

        # Sort by margin
        cities_data.sort(key=lambda x: x['margin'], reverse=True)

        # Calculate summary
        avg_margin = sum(c['margin'] for c in cities_data) / len(cities_data) if cities_data else 0
        recommended_count = sum(1 for c in cities_data if '✅' in c['recommendation'] or '👍' in c['recommendation'])
        best_city = cities_data[0]['city'] if cities_data else 'N/A'

        kz_data = {
            'product': {
                'name': product_name,
                'wholesale_price': wholesale_price,
                'category': 'General',
            },
            'cities': cities_data,
            'summary': {
                'best_city': best_city,
                'avg_margin': avg_margin,
                'recommended_count': recommended_count,
            }
        }

        # Generate report
        excel_bytes = await report_service.generate_kz_market_report_excel(kz_data)

        filename = f"kz_market_{product_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx"

        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.error(f"KZ market report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available")
async def get_available_reports(current_user=Depends(get_current_user)):
    """Get list of available report types"""
    return {
        "reports": [
            {
                "id": "daily",
                "name": "Daily Summary Report",
                "description": "Overview of daily metrics, top products, and alerts",
                "endpoint": "/reports/daily",
                "format": "Excel",
            },
            {
                "id": "forecast",
                "name": "Forecast Report",
                "description": "Detailed forecast analysis for a specific product",
                "endpoint": "/reports/forecast/{product_id}",
                "format": "Excel",
                "params": ["product_id", "horizon_days"],
            },
            {
                "id": "analytics",
                "name": "Analytics Report",
                "description": "Comprehensive analytics including trends and categories",
                "endpoint": "/reports/analytics",
                "format": "Excel",
            },
            {
                "id": "kz_market",
                "name": "Kazakhstan Market Report",
                "description": "City-by-city profitability analysis for KZ market",
                "endpoint": "/reports/kz-market",
                "format": "Excel",
                "params": ["product_name", "wholesale_price", "markup_percent"],
            },
        ]
    }