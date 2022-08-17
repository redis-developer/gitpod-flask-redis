from flask import Flask, render_template
import redis, time, string
from unidecode import unidecode

app = Flask(__name__)

# Connect to Redis
r = redis.Redis(
    host='localhost', 
    port=6379, 
    db=0, 
    decode_responses=True
)

r.delete('bloom')
r.delete('cuckoo')
r.delete('cms')
r.delete('topk')

r.bf().create('bloom', 0.01, 10000, noScale=True)
r.cf().create('cuckoo', 10000)
r.cms().initbyprob('cms', 0.001, 0.01)
r.topk().reserve('topk', 50, 8, 7, 0.925)

itemSet = "things"
sortedSet = "sortedThings"
stop_list = []

## add and check for bloom, cuckoo and set
@app.route("/addbloom/<thing>")
def add_bloom(thing):
    print(thing)
    if r.bf().add('bloom', thing):
        return { "check": 'Added' }
    else:
        return { "check": 'Probably already in filter - cannot add' }

@app.route("/addcuckoo/<thing>")
def add_cuckoo(thing):
    r.cf().add('cuckoo', thing)
    return { "check": 'Added - but cuckoo filters can contain duplicates' }

@app.route("/addset/<thing>")
def add_set(thing):
    if r.sadd(itemSet, thing):
        return { "check": 'Added' }
    else:
        return { "check": 'Already in set - cannot add' }

@app.route("/checkcuckoo/<thing>")
def check_cuckoo(thing):
    if r.cf().exists('cuckoo', thing):
        return { "check": 'Probably in filter' }
    else:
        return { "check": 'Definitely not in filter' }

@app.route("/checkbloom/<thing>")
def check_bloom(thing):
    if r.bf().exists('bloom', thing):
        return { "check": 'Probably in filter' }
    else:
        return { "check": 'Definitely not in filter' }

@app.route("/checkset/<thing>")
def check_set(thing):
    if r.sismember(itemSet, thing):
        return { "check": 'Definitely in set' }
    else:
        return { "check": 'Definitely not in set' }


@app.route("/addsorted/<thing>")
def add_sorted(thing):
    r.zadd('sortedThings', {thing: 1})
    return str(r.zrank('sortedThings', thing))
    # return "did something"

@app.route("/checksorted/<thing>")
def check_sorted(thing):
    return r.zrank('sortedThings', thing)

### size for bloom, cuckoo, set
@app.route("/bloomsize")
def bloom_info():
    info = r.bf().info('bloom')
    return str(info.size)

@app.route("/cuckoosize")
def cuckoo_info():
    info = r.cf().info('cuckoo')
    return str(info.size)

@app.route("/setsize")
def set_info():
    info = r.memory_usage(itemSet)
    return str(info)

# Reset by just deleting the key from Redis.
@app.route("/reset")
def reset():
    r.delete('bloom')
    r.delete('cuckoo')
    r.delete('cms')
    r.delete('top_k')
    r.delete(itemSet)
    r.delete(sortedSet)
    return { "check": 'Deleted everything' }

### code blocks to populate different structures with different data options
@app.route("/pop/book")
def pop_book():
    with open("pride_and_prejudice.txt") as f:
        pipe = r.pipeline()
        for line in f:
            line = unidecode(line)
            words = line.split(' ')
            for word in words:
                word = word.strip()
                word = word.strip('"(),.;_:!?')
                if word == "" and word not in stop_list:
                    continue
                print(word)
                pipe.topk().add('topk', word)
                pipe.cms().incrby('cms', [word], [1])
                pipe.zadd('sortedThings', {word: 1})
        pipe.execute()
    return "added pride and prejudice to top-k and cms"

@app.route("/pop/words_1000")
def pop_thou():
    with open("words_1000.txt") as f:
        pipe = r.pipeline()
        for line in f:
            word = line.strip()
            pipe.bf().add('bloom', word)
            pipe.cf().add('cuckoo', word)
            pipe.sadd(itemSet, word)
        pipe.execute()
    return "added 1,000 words to bloom and cuckoo"

@app.route("/pop/words_10000")
def pop_ten_thou():
    with open("words_10000.txt") as f:
        pipe = r.pipeline()
        for line in f:
            word = line.strip()
            pipe.bf().add('bloom', word)
            pipe.cf().add('cuckoo', word)
            pipe.sadd(itemSet, word)
        pipe.execute()
    # return { "bloomSize": str(r.bf().info('bloom').size) }
    
    return "added 10,000 words to bloom and cuckoo"

@app.route("/pop/words_alpha")
def pop_lots():
    with open("words_alpha.txt") as f:
        pipe = r.pipeline()
        for line in f:
            word = line.strip()
            pipe.bf().add('bloom', word)
            pipe.cf().add('cuckoo', word)
            pipe.sadd(itemSet, word)
        pipe.execute()
    return "added 300,000+ words to bloom and cuckoo"

@app.route("/pop/users")
def pop_users():
    with open("users.txt") as f:
        # pipe = r.pipeline()
        for line in f:
            word = line.strip()
            ans = r.bf().add('bloom', word)
            if ans == 0:
                print(f'bf collisions on {word}')
            # ans = r.cf().add('cuckoo', word)
            # if ans == 0:
            #     print(f'cf collisions on {word}')
            # r.sadd(itemSet, word)
            # pipe.bf().add('bloom', word)
            # pipe.cf().add('cuckoo', word)
            # pipe.sadd(itemSet, word)
        # pipe.execute()
    return "added ~1,000,000 users to bloom and cuckoo"


@app.route("/counttopk/<thing>")
def count_topk(thing):
    print(thing)
    c = r.topk().count('topk', thing)
    return { "check": c }

@app.route("/querytopk/<thing>")
def query_topk(thing):
    return { "check": r.topk().query('topk', thing) }


@app.route("/infotopk")
def info_topk():
    topk_info = {}
    topk_info['width'] = r.topk().info('topk').width
    topk_info['depth'] = r.topk().info('topk').depth
    topk_info['decay'] = r.topk().info('topk').decay
    return topk_info


@app.route("/incrby/<thing>/<num>")
def incr_topk(thing, num):
    r.topk().incrby('topk', [thing], [num])
    return count_topk(thing)

@app.route("/addtopk/<thing>")
def add_topk(thing):
    r.topk().incrby('topk', [thing], [1])
    print(thing)
    return count_topk(thing)

@app.route("/listtopk")
def topk_list():
    top_list = r.topk().list('topk')
    if len(top_list) == 0:
        return "empty topk, cannot get topk"
    else:
        return { "check": str(len(top_list)) }

@app.route("/cmsinitdim/<name>/<width>/<depth>")
def init_cms(name, width, depth):
    if r.cms().initbydim(name, width, depth):
        return { "check": f'made cms {name}'}

@app.route("/cmsmerge/<cms1>/<cms2>")
def merge_cms(cms1, cms2):
    if r.cms().merge(cms1, 2, [cms1, cms2], weights=[1,3]):
        return { "check": 'merged' }

@app.route("/cmsincrby/<name>/<thing>/<num>")
def cms_incrby(thing, num, name):
    r.cms().incrby(name, [thing], [num])
    return str(cms_query(thing, name))

@app.route("/cmsquery/<name>/<thing>")
def cms_query(thing, name):
    return str(r.cms().query(name, thing))

@app.route("/cmsinfo/<name>")
def cms_info(name):
    cms_dict = {}
    cms_dict['width'] = r.cms().info(name).width
    cms_dict['depth'] = r.cms().info(name).depth
    cms_dict['count'] = r.cms().info(name).count
    return cms_dict

@app.route("/addcms/<thing>")
def cms_add(thing):
    r.cms().incrby('cms', [thing], [1])
    return str(cms_query(thing, 'cms'))

@app.route("/")
def home():
    # Get the current counter value
    # Render the home page with the current counter value.
    return render_template('homepage.html', 
                    bloomSize=str(r.memory_usage('bloom')), 
                    cuckooSize=str(r.memory_usage('cuckoo')),
                    setSize=str(r.memory_usage(itemSet)),
                    sortedSize=str(r.memory_usage(sortedSet)),
                    cmsSize=str(r.memory_usage('cms')),
                    topkSize=str(r.memory_usage('topk'))
                ) 

