from flask import Flask, request
import requests
import sys

app = Flask(__name__)

# 🟢 IMPORTANT: use the SAME token + chat id that worked before
BOT_TOKEN = "8260999319:AAGiEu3HVEqy7dvp8F2tnKAj1OGc0w1FLQc"   # <- your token
CHAT_ID   = "-5015909020"                                     # <- keep minus!

@app.route("/telegram", methods=["GET", "POST"])
def telegram_bridge():
    # Get msg from query (?msg=...) or POST body
    msg = request.args.get("msg") or request.form.get("msg")
    print("Bridge received msg:", msg)
    sys.stdout.flush()

    if not msg:
        return "No message provided", 400

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}

    try:
        r = requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Error calling Telegram:", e)
        sys.stdout.flush()
        return "Telegram error", 500

    print("Telegram status:", r.status_code)
    print("Telegram response:", r.text)
    sys.stdout.flush()

    if r.ok:
        return "OK", 200
    else:
        return "Telegram error", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
