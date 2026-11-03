from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.animal import Animal
from models.feed import FeedInventory
from services.ai_engine import DairyAIEngine

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ai-insights')
@login_required
def ai_hub():
    """
    Main Executive Dashboard for Farm Intelligence & Machine Learning Models.
    Unifies all 6 AI modules into a single, cohesive, interactive interface.
    """
    selected_cow_id = request.args.get('animal_id', type=int)
    forecast_days = request.args.get('days', 14, type=int)
    forecast_days = max(7, min(forecast_days, 14))

    # 1. Milk Yield Forecasting (Herd + Selected cow if any)
    herd_forecast = DairyAIEngine.forecast_milk_yield(days=forecast_days, animal_id=None)
    cow_forecast = DairyAIEngine.forecast_milk_yield(days=forecast_days, animal_id=selected_cow_id) if selected_cow_id else None

    # 2. Early Illness Anomaly Detection
    anomalies = DairyAIEngine.detect_yield_anomalies(lookback_days=14)

    # 3. Mastitis Risk Radar
    mastitis_records = DairyAIEngine.predict_mastitis_risk()
    high_mastitis_count = sum(1 for m in mastitis_records if m['risk_level'] == 'HIGH RISK')
    mod_mastitis_count = sum(1 for m in mastitis_records if m['risk_level'] == 'MODERATE RISK')

    # 4. Cull and Keep Recommendation Matrix
    cull_keep_data = DairyAIEngine.recommend_cull_keep()

    # 5. Feed Optimization & Stockout Depletion
    feed_depletion = DairyAIEngine.forecast_feed_depletion()
    optimal_ration = DairyAIEngine.optimize_feed_ration(animal_id=selected_cow_id)

    # 6. Financial Expense & Profit Forecasting (Next Month)
    financial_forecast = DairyAIEngine.forecast_financials_next_month()

    # Milking cattle for selector dropdown
    milking_cows = Animal.query.filter_by(milking_status='Milking').order_by(Animal.tag_number).all()

    return render_template(
        'ai_insights.html',
        herd_forecast=herd_forecast,
        cow_forecast=cow_forecast,
        selected_cow_id=selected_cow_id,
        forecast_days=forecast_days,
        anomalies=anomalies,
        mastitis_records=mastitis_records,
        high_mastitis_count=high_mastitis_count,
        mod_mastitis_count=mod_mastitis_count,
        cull_keep_data=cull_keep_data,
        feed_depletion=feed_depletion,
        optimal_ration=optimal_ration,
        financial_forecast=financial_forecast,
        milking_cows=milking_cows
    )

# --------------------------------------------------------------------------
# REST API Endpoints for Asynchronous UI updates & Chart.js live toggles
# --------------------------------------------------------------------------

@ai_bp.route('/api/ai/forecast')
@login_required
def api_forecast():
    animal_id = request.args.get('animal_id', type=int)
    days = request.args.get('days', 14, type=int)
    data = DairyAIEngine.forecast_milk_yield(days=days, animal_id=animal_id)
    return jsonify(data)

@ai_bp.route('/api/ai/anomalies')
@login_required
def api_anomalies():
    data = DairyAIEngine.detect_yield_anomalies()
    return jsonify(data)

@ai_bp.route('/api/ai/mastitis-risk')
@login_required
def api_mastitis():
    animal_id = request.args.get('animal_id', type=int)
    data = DairyAIEngine.predict_mastitis_risk(animal_id=animal_id)
    return jsonify(data)

@ai_bp.route('/api/ai/cull-keep')
@login_required
def api_cull_keep():
    data = DairyAIEngine.recommend_cull_keep()
    # Serialize animal object to avoid jsonify errors
    clean_cows = []
    for c in data['cows']:
        c_copy = dict(c)
        c_copy.pop('animal', None)
        clean_cows.append(c_copy)
    data['cows'] = clean_cows
    return jsonify(data)

@ai_bp.route('/api/ai/feed/ration')
@login_required
def api_feed_ration():
    animal_id = request.args.get('animal_id', type=int)
    weight = request.args.get('weight', type=float)
    daily_yield = request.args.get('yield', type=float)
    data = DairyAIEngine.optimize_feed_ration(animal_id=animal_id, custom_weight=weight, custom_yield=daily_yield)
    return jsonify(data)

@ai_bp.route('/api/ai/feed/depletion')
@login_required
def api_feed_depletion():
    data = DairyAIEngine.forecast_feed_depletion()
    return jsonify(data)

@ai_bp.route('/api/ai/financial-forecast')
@login_required
def api_financial_forecast():
    data = DairyAIEngine.forecast_financials_next_month()
    return jsonify(data)
