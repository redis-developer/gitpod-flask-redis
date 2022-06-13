import pip
from flask import Flask, render_template
import redis, time

app = Flask(__name__)

# Connect to Redis
r = redis.Redis(
    host='localhost', 
    port=6379, 
    db=0, 
    decode_responses=True
)

r.delete('words_bloom')
r.bf().create('words_bloom', 0.01, 1000)

@app.route("/addbloom/<thing>")
def add_bloom(thing):
    start = time.perf_counter()
    ans = r.bf().add('words_bloom', thing)
    diff = time.perf_counter() - start
    if ans == 1:
        return { "check": 'Added', "time":  diff}
    else:
        return { "check": 'Probably already in filter - cannot add', "time":  diff }

@app.route("/addset/<thing>")
def add_set(thing):
    start = time.perf_counter()
    ans = r.sadd('words_set', thing)
    diff = time.perf_counter() - start
    if ans == 1:
        return { "check": 'Added', "time":  diff }
    else:
        return { "check": 'Already in set - cannot add', "time":  diff }

@app.route("/checkbloom/<thing>")
def check_bloom(thing):
    print(type(thing))
    start = time.perf_counter()
    ans = r.bf().exists('words_bloom', thing)
    diff = time.perf_counter() - start
    if ans == 1:
        return { "check": 'Probably in filter', "time":  diff }
    else:
        return { "check": 'Definitely not in filter', "time":  diff }

@app.route("/checkset/<thing>")
def check_set(thing):
    start = time.perf_counter()
    ans = r.sismember('words_set', thing)
    diff = time.perf_counter() - start
    if ans == 1:
        return { "check": 'Definitely in set', "time":  diff }
    else:
        return { "check": 'Definitely not in set', "time":  diff }

@app.route("/pop")
def populate():
    # pipe = r.pipeline(transaction=False)
    with open('words.txt', 'r') as f:
        for line in f:
            print(line)
            ans1 = r.bf().add('words_bloom', str(line))
            print(ans1)
            ans2 = r.sadd('words_set', str(line))
            print(ans2)
    # pipe.execute()
    return { "check": 'Populated' }

@app.route("/reset")
def reset():
    # Reset by just deleting the key from Redis.
    r.delete('bloom')
    return { "check": 'Deleted bloom filter- now empty' }

@app.route("/")
def home():
    # Get the current counter value
    # Render the home page with the current counter value.
    return render_template('homepage.html')
