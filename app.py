from flask import Flask, render_template, redirect, url_for
import requests

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/log")
def log():
    return render_template("log.html")

@app.route("/test")
def test():
    return render_template("test.html")

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
@app.route("/cart")
def build_cart(items):
    return None

# Finalize purchase with user information
@app.route("/finalize")
def commit_purchase():
    return None

if __name__ == "__main__":
    app.run()
