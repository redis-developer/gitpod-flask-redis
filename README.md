# A Python Flask / Redis template on Gitpod

This is a [Python](https://www.python.org/) [Flask](https://flask.palletsprojects.com/) template configured for ephemeral development environments on [Gitpod](https://www.gitpod.io/) with [Redis Stack](https://redis.io/docs/stack/) using the [redis-py](https://pypi.org/project/redis/) client and [RedisInsight](https://github.com/RedisInsight/RedisInsight) visualization tool.  You can also run this application locally if you prefer.

The application is a basic counter that stores a value in Redis in the `mycounter` key.  It's intended as a start point for building your own Flask applications that use Redis.

If you prefer to work with Node.js, we've also built this same application using Node.js and the Express framework.  [Check it out here](https://github.com/redis-developer/gitpod-flask-redis).

## Quick Start

There are two ways of running this application - entirely in the cloud with Gitpod, or locally on your own machine either with your own install of Redis Stack or using Docker.

### Using Gitpod

When using Gitpod, the only things you need are:

* A modern browser (we have tested with [Google Chrome](https://www.google.com/chrome/)).
* A [GitHub](https://github.com) account.

Click the button below to start a new cloud development environment using Gitpod:

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/redis-developer/gitpod-flask-redis)

If you're using Gitpod for the first time, you'll need to authorize it to work with your GitHub account.

Gitpod will then open a workspace in the browser for you.  This contains:

* VS Code for editing the code.
* An embedded browser window with the application running in it.
* Two terminal sessions: the left hand terminal can be used for entering commands, the right hand one starts the application for you.  Flask monitors for changes in the application code and will restarts the application for you whenever you save code changes in VS Code.

Take a note of your workspace URL which looks something like this:

```
https://yourgithubusername-gitpodexpr-eamwc2bab7h.ws-eu38.gitpod.io/
```

If you want to open the application in a separate browser tab outside of the Gitpod workspace tab, append `5000-` to the workspace URL, for example:

```
https://5000-yourgithubusername-gitpodexpr-eamwc2bab7h.ws-eu38.gitpod.io/
```

To start RedisInsight, append `8001-` to the workspace URL and open that in another new tab.  For example:

```
https://8001-yourgithubusername-gitpodexpr-eamwc2bab7h.ws-eu38.gitpod.io/
```

You'll need to agree to the terms and conditions the first time that you start RedisInsight.

The application should show that the current value of the counter is 0, and RedisInsight should show you an empty database with no keys yet.

### Running Locally

To run the application locally you'll need to install the following:

* The [git command line tools](https://git-scm.com/downloads).
* A recent version of [Python 3](https://www.python.org/downloads/) (the application has been tested using Python 3.9.5).
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (to run a Redis Stack container) or a local install of Redis Stack ([installation options here](https://redis.io/docs/stack/get-started/install/)).
* Your favorite IDE if you want to edit / read the code (we like [VS Code](https://code.visualstudio.com/)).

First, clone the repo, create a Python virtual environment and install dependencies:

```bash
$ git clone https://github.com/redis-developer/gitpod-flask-redis.git
$ cd gitpod-flask-redis
$ python3 -m venv venv
$ . ./venv/bin/activate
$ pip install -r requirements.txt
```

Also, set Flask to development mode so that it will restart the server automatically for you when you make code changes:

```bash
$ export FLASK_ENV=development
```

If you're using Docker to run Redis Stack, start the container:

```bash
$ docker-compose up -d
```

This starts a Redis Stack container with Redis listening on port 6379 and RedisInsight listening on port 8001.

If you're not using Docker, install a copy of Redis Stack using your platform's package manager ([see options here](https://redis.io/docs/stack/get-started/install/)).  Make sure it's up and running with Redis on port 6379 and RedisInsight on port 8001 (these are the default port values).

Once Redis Stack is up and running, you can go ahead and start the application like this:

```bash
$ flask run
```

Now, open tabs in your browser for each of the following URLs:

* Application: `http://127.0.0.1:5000`
* RedisInsight: `http://127.0.0.1:8001` (agree to the terms and conditions the first time you visit this URL)

The application should show that the current value of the counter is 0, and RedisInsight should show you an empty database with no keys yet.

Don't stop the application now, but when you're ready to, press Ctrl-C in the terminal window that Flask is running in.

If you're using Docker, you can stop the Redis Stack container like this when you're finished with it:

```bash
$ cd gitpod-express-redis
$ docker-compose down
```

## How the Application Works

Before diving into code, let's first try out the application and see what data is stored in Redis.

* Initially, there's nothing in Redis and the application shows the counter's value to be 0.
* Pressing the "Increment" button adds one to the counter's current value, which is stored in a key named "mycounter" in Redis.
* Press "Increment" a few times, then refresh your RedisInsight tab's view of the database to see that a key named "mycounter" has been added, and that it's value matches that shown in the application front end.
* Press the "Reset" button, then refresh your RedisInsight tab's view of the database.  Note that the "mycounter" key has now been deleted.

### Front End

The application's front end isn't our focus here.  It's a simple web application built with Bulma and vanilla JavaScript.  The JavaScript that handles button presses is contained in `static/app.js` and the HTML can be found in `templates/homepage.html` - it's a simple [Flask template](https://flask.palletsprojects.com/en/2.1.x/tutorial/templates/).  There are no CSS files in this repo, the CSS and Font Awesome JS files that Bulma uses are served from a CDN.

### Back End

Now let's look at the code in `app.py` to see how to use Node Redis to connect to Redis Stack.

#### Initializing Flask and Redis

This is a regular Flask application - so we initialize Flask and annotate the Python functions for each route using `@app.route`.  We also create a Redis client using redis-py and connect it to Redis Stack running on port 6379 of our local machine:

```python
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
```

#### Home Page

The home page is also the application's only page, and it's rendered like this:

```python
@app.route("/")
def home():
    # Get the current counter value.
    count = r.get(COUNTER_KEY_NAME)
    if count is None:
        count = 0

    # Render the home page with the current counter value.
    return render_template('homepage.html', count = count)
```

Here, we use the Redis `GET` command to get the value stored at our counter's key, if any.  If the key doesn't exist yet (Redis returns `None`), we set `count` to an initial value of `0`.  Note that we don't write this to Redis as there's no need (our increment button code will deal with that).

Finally, we render out the `homepage.html` template (in `templates/homepage.ejs`), passing it the value of `count` - this makes sure that when the homepage is rendered, the current value of the counter is there.

#### Pressing the Increment Button

When the Increment button is pressed in the front end, a request is sent to `/incr`, which is handled by the following code:

```python
@app.route("/incr")
def incr():
    # Atomically add one to the counter in Redis.
    # If the key doesn't exist, Redis will create it with
    # an initial value of 1.
    count = r.incrby(COUNTER_KEY_NAME, 1)
    return { "count": count }
```

The [Redis `INCRBY`](https://redis.io/commands/incrby/) command atomically increments the numeric value stored at a given key by a specified amount.  If the key doesn't exist, Redis creates it for us (this is why we don't need to store an initial value of 0 in Redis in the home page route).  `INCRBY` returns the new value stored at the key, and that's what we send back to the front end.

#### Pressing the Reset Button

When the Reset button is pressed in the front end, a request is sent to `/reset`, which is handled by the following code:

```python
@app.route("/reset")
def reset():
    # Reset by just deleting the key from Redis.
    r.delete(COUNTER_KEY_NAME)
    return { "count": 0 }
```

To reset the counter, we delete its key from Redis, then return 0 to the front end.  The front end JavaScript then updates the displayed value for the counter.

## Making Changes to the Application

If you change the application code, Flask will restart the server and pick up your changes immediately.  For example, let's make the Increment button add 10 to the value of the counter rather than 1...

The redis-py `incrby` function takes two parameters:

* The key name holding the value to increment.
* A number to increment the current value by.

In `app.py`, find the line:

```python
count = r.incrby(COUNTER_KEY_NAME, 1)
```

and change it to read:

```python
count = r.incrby(COUNTER_KEY_NAME, 10)
```

Save your changes and try hitting the Increment button again... what happens to the value of the counter now?

## What Capabilities does Redis Stack have?

[Redis Stack](https://redis.io/docs/stack/) includes the following:

* An open source [Redis 6.2](https://redis.io/docs/getting-started/) server instance.
* The [RediSearch](https://redis.io/docs/stack/search/) module, adding full text search and secondary indexing capabilities.
* The [RedisJSON](https://redis.io/docs/stack/json/) module, which enables JSON as a native data type in Redis.
* The [Redis Graph](https://redis.io/docs/stack/graph/) module, allowing you to store data in Redis as a graph and retrieve it with Cthe Cypher query language.
* The [RedisBloom](https://redis.io/docs/stack/bloom/) module which implements additional probabilistic data structures such as Bloom and Cuckoo filters.
* The [RedisTimeSeries](https://redis.io/docs/stack/timeseries/) module, which adds a time series data type and aggregations to Redis.
* [RedisInsight](https://redis.io/docs/stack/insight/), a data visualization and management tool for Redis.

## Additional Resources

Looking to learn more about Redis? Here's some useful resources:

* Chat with us and get your questions answered on the [Redis Discord server](https://discord.gg/redis).
* Subscribe to our [YouTube channel](https://www.youtube.com/c/Redisinc).
* [redis.io](https://redis.io/) - Docmentation and reference materials.
* [developer.redis.com](https://developer.redis.com) - the official Redis Developer site.
* [Redis University](https://university.redis.com) - free online Redis courses.
