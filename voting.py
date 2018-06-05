import redis
import time

ONE_WEEK_IN_SECONDS = 7 * 86400
VOTE_SCORE = 432
ARTICLES_PER_PAGE = 25

r = redis.StrictRedis(host='localhost', port=6379, db=0)
r.flushall()

def post_article(user, title, link):
    # fetch new article id
    article_id = r.incr("article:")

    # Save that user already voted for this article
    voted = "voted:" + str(article_id)
    r.sadd(voted, user)

    # Insert article hash
    article_key = "article:" + str(article_id)
    now = time.time()

    r.hmset(article_key, {
        'title': title,
        'link': link,
        'poster': user,
        'time': now,
        'votes': 1
        })

    # Add time and voting scores
    r.zadd("score:", now + VOTE_SCORE, article_key)
    r.zadd("time:", now, article_key)

    return article_id

def article_vote(user, article_id):
    cutoff = time.time() - ONE_WEEK_IN_SECONDS
    article_key = f'article:{article_id}'
    
    # Check whether article is not old and can be voted on
    if r.zscore('time:', article_key) < cutoff:
        return
    
    # If there no vote from the same user
    if r.sadd(f'voted:{article_id}', user):
        r.zincrby('score:', article_key, VOTE_SCORE)
        r.hincrby(article_key, 'votes', 1) # increment votes property in article hash

def get_articles(page, order='score:'):
    start = (page-1) * ARTICLES_PER_PAGE
    end = ARTICLES_PER_PAGE - 1

    # Select subset of keys in sorted set (sorted from highest to lowest)
    ids = r.zrevrange(order, start, end)
    articles = []
    
    for id in ids:
        article_data = r.hgetall(id)
        article_data['id'] = id
        articles.append(article_data)
        print(article_data)

id = post_article("1", "Test", "TestLink")
article_vote("2", id)

post_article("2", "Test2", "TestLink")

print()
print('By Score')
get_articles(1)
print()

print('By Time')
get_articles(1, order="time:")

print("Done")