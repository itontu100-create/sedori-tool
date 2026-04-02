import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

RAKUTEN_APP_ID = os.environ.get("RAKUTEN_APP_ID")

def search_rakuten(keyword, hits=10):
    url = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20220601"
    params = {
        "applicationId": RAKUTEN_APP_ID,
        "keyword": keyword,
        "hits": hits,
        "sort": "+itemPrice",
        "formatVersion": 2
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    keyword = request.json.get("keyword")
    hits = request.json.get("hits", 10)
    try:
        data = search_rakuten(keyword, hits)
        items = data.get("Items", [])
        results = []
        for item in items:
            buy_price = item["itemPrice"]
            sell_price = int(buy_price * 1.3)
            profit = int(sell_price * 0.85) - buy_price
            profit_rate = round(profit / sell_price * 100, 1)
            results.append({
                "name": item["itemName"],
                "buy_price": buy_price,
                "sell_price": sell_price,
                "profit": profit,
                "profit_rate": profit_rate,
                "url": item["itemUrl"]
            })
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
