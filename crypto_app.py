# crypto_app.py
import random
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS  # <-- 1. ADD THIS LINE

# --- Core Logic Functions (Copied from before) ---
def fetch_simulated_trending_tokens():
    """Simulates fetching trending tokens."""
    tokens = [
        {'name': 'BNB', 'volatility': 0.3, 'category': 'L1'},
        {'name': 'CAKE', 'volatility': 0.7, 'category': 'DeFi'},
        {'name': 'USDT', 'volatility': 0.05, 'category': 'Stablecoin'},
        {'name': 'FLOKI', 'volatility': 0.9, 'category': 'Meme'},
        {'name': 'XVS', 'volatility': 0.6, 'category': 'Lending'},
        {'name': 'TUSD', 'volatility': 0.06, 'category': 'Stablecoin'}
    ]
    return random.sample(tokens, k=random.randint(3, 5))

def get_allocation_strategy(risk_profile, tokens_df):
    """Generates a crypto allocation strategy based on user risk profile."""
    allocations = {
        "conservative": [0.50, 0.40, 0.10],
        "balanced": [0.30, 0.40, 0.30],
        "aggressive": [0.10, 0.30, 0.60]
    }
    target = allocations.get(risk_profile)
    if not target: return None
    
    stablecoins = tokens_df[tokens_df['volatility'] < 0.1]
    blue_chips = tokens_df[(tokens_df['volatility'] >= 0.1) & (tokens_df['volatility'] < 0.5)]
    high_risk = tokens_df[tokens_df['volatility'] >= 0.5]

    portfolio = {}
    if not stablecoins.empty: portfolio[stablecoins['name'].iloc[0]] = target[0]
    if not blue_chips.empty: portfolio[blue_chips['name'].iloc[0]] = target[1]
    if not high_risk.empty: portfolio[high_risk['name'].iloc[0]] = target[2]

    total_allocation = sum(portfolio.values())
    if total_allocation > 0:
        for token in portfolio:
            portfolio[token] = portfolio[token] / total_allocation
    return portfolio

def generate_explanation(portfolio, budget, risk_profile):
    """Creates a user-friendly, structured explanation of the allocation."""
    if not portfolio:
        return {"error": "Could not generate a portfolio."}
    
    output = {
        "profile": risk_profile,
        "budget": budget,
        "recommendations": [],
        "summary": ""
    }
    
    for token, percentage in portfolio.items():
        output["recommendations"].append({
            "token": token,
            "percentage": round(percentage, 2),
            "amount": round(budget * percentage, 2)
        })

    if risk_profile == "conservative":
        output["summary"] = "This strategy prioritizes capital preservation with minimal risk."
    elif risk_profile == "balanced":
        output["summary"] = "A balanced approach mixing stable and high-growth assets."
    elif risk_profile == "aggressive":
        output["summary"] = "This strategy aims for maximum growth by taking on more risk."
        
    return output

# --- Flask Application Setup ---
app = Flask(__name__)
CORS(app)  # <-- 2. ADD THIS LINE to enable Cross-Origin Resource Sharing

# --- API Endpoint Definition ---
@app.route('/get-advice', methods=['POST'])
def get_advice():
    """API endpoint to get crypto allocation advice."""
    data = request.get_json()
    
    if not data or 'budget' not in data or 'risk_profile' not in data:
        return jsonify({"error": "Missing budget or risk_profile"}), 400

    budget = data['budget']
    risk_profile = data['risk_profile'].lower()

    # Run the core logic
    tokens = fetch_simulated_trending_tokens()
    tokens_df = pd.DataFrame(tokens)
    portfolio = get_allocation_strategy(risk_profile, tokens_df)
    
    # Generate a structured response
    explanation_data = generate_explanation(portfolio, budget, risk_profile)
    
    # Return the data as a JSON response
    return jsonify(explanation_data)

# --- Run the application ---
if __name__ == '__main__':
    app.run(debug=True)