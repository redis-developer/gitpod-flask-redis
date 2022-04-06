from flask import Flask, render_template
import redis

app = Flask(__name__)

# Connect to Redis
r = redis.Redis(
    host='localhost', 
    port=6379, 
    db=0, 
    decode_responses=True
)

# Redis key name that we will store our counter in.
COUNTER_KEY_NAME = "mycounter"

@app.route("/incr")
def incr():
    # Atomically add one to the counter in Redis.
    # If the key doesn't exist, Redis will create it with
    # an initial value of 1.
    count = r.incrby(COUNTER_KEY_NAME, 1)
    return { "count": count }

@app.route("/reset")
def reset():
    # Reset by just deleting the key from Redis.
    r.delete(COUNTER_KEY_NAME)
    return { "count": 0 }

@app.route("/")
def home():
    # Get the current counter value.
    count = r.get(COUNTER_KEY_NAME)
    if count is None:
        count = 0

    # Render the home page with the current counter value.
    return render_template('homepage.html', count = count)
