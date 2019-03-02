from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/info")
def get_user_info():
    return {"" : ""}

# Get price range from user
@app.route("/range")
def set_price_range():
    return (10, 20)

# Search for items within a set price range
@app.route("/items")
def select_items(price_range):



    return None

# Build cart from selected items
@app.route("/order")
def build_order(items):
    return None

# Finalize purchase with user information
@app.route("/finalize")
def commit_purchase():
    return None

if __name__ == "__main__":
    app.run()
