from flask import Flask, redirect
import redis

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def render_page():
    count = r.get("mycounter")
    if count is None:
        count = 0

    return f'<h1>Flask Redis Starter Application</h1><p>Count:{count}</p><ul><li><a href="/incr">Increment counter</a></li><li><a href="/reset">Reset counter</a></li></ul>'

@app.route("/incr")
def incr():
    count = r.incr("mycounter", 1)
    return render_page()

@app.route("/reset")
def reset():
    r.delete("mycounter")
    return render_page()

@app.route("/")
def home():
    return render_page()