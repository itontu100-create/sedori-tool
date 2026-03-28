import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

RAKUTEN_APP_ID = os.environ.get("RAKUTEN_APP_ID", "")


def search_rakuten(keyword, hits=10):
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"
    params = {
        "applicationId": RAKUTEN_APP_ID,
        "keyword": keyword,
        "hits": hits,
        "sort": "+itemPrice",
        "availability": 1,
        "formatVersion": 2,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("Items", [])


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    if not RAKUTEN_APP_ID:
        return jsonify({"error": "楽天APIキー（RAKUTEN_APP_ID）が設定されていません。"}), 500

    keyword = request.json.get("keyword", "").strip()
    hits = int(request.json.get("hits", 10))

    if not keyword:
        return jsonify({"error": "商品名を入力してください。"}), 400

    try:
        items = search_rakuten(keyword, hits=hits)
        results = []
        for item in items:
            image_urls = item.get("mediumImageUrls", [])
            results.append({
                "name": item.get("itemName", ""),
                "price": item.get("itemPrice", 0),
                "shop": item.get("shopName", ""),
                "url": item.get("itemUrl", "#"),
                "image": image_urls[0] if image_urls else None,
            })
        return jsonify({"items": results})
    except requests.exceptions.Timeout:
        return jsonify({"error": "楽天APIへの接続がタイムアウトしました。しばらくしてから再試行してください。"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"楽天APIへの接続に失敗しました：{e}"}), 502
    except Exception as e:
        return jsonify({"error": f"エラーが発生しました：{e}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
