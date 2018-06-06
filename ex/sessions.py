import redis
import time

ONE_WEEK_IN_SECONDS = 7 * 86400
VOTE_SCORE = 432
ARTICLES_PER_PAGE = 25

r = redis.StrictRedis(host='localhost', port=6379, db=0)
r.flushall()

def register_token(token, user_id):
    r.hset('login:', token, user_id)

def check_token(token):
    return r.hget('login:', token)

def record_visit(user_id, page=None):
    timestamp = time.time()

    # Records recent actvity of each users
    r.zadd('recent:', timestamp, user_id)
    
    if page:
        r.zadd(f'viewed:{user_id}', timestamp, page)
        r.zremrangebyrank(f'viewed:{user_id}', 0, -6) # Keep to 5 most recent visits

def print_activity(user_id):
    recent_views = r.zrange(f'viewed:{user_id}', 0, -1)

    print(recent_views)

jack = 1
bob = 2

register_token("bob-token", bob)
register_token("token-token", jack)


record_visit(jack, page="/order/123")
record_visit(jack, page="/order/23")
record_visit(jack, page="/order/23111")
record_visit(jack, page="/")
record_visit(jack, page="/home")
record_visit(jack, page="/dashboard")

print_activity(jack)