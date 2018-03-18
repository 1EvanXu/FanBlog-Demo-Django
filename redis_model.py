import time
from datetime import datetime
import redis
from redis.exceptions import RedisError

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
__CONNECTION_POOL = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)
__CONNECTION = redis.Redis(connection_pool=__CONNECTION_POOL)
__CONTENT_EXPIRE_TIME = 43200


def get_redis_connection():
    return __CONNECTION


def publish_record(pub_id, title, pub_type, category, link, abstract='', conn=__CONNECTION):

    '''
    This function will save some information as a hash type in redis, 
    each published article record corresponds to a hash, the prefix of
    the key name of each hash is 'pub_article:', the suffix is a unique
    id of each published article. the article will also record in a zset
    named 'articles_rank:' and a list named 'all_pub_articles:'.
    '''

    pub_id = str(pub_id)
    pub_article = 'pub_article:' + pub_id
    pipe = conn.pipeline()
    pipe.hmset(pub_article, {
        'title': title,
        'type': pub_type,
        'category': category,
        'abstract': abstract,
        'pub_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'link': link,
        'votes_count': 0,
        'visitors_count': 0,
        'comments_count': 0,
    })

    pipe.zadd('articles_rank:', pub_article, 0)
    pipe.lpush('all_pub_articles:', pub_article)
    pip.execute()
    print(pub_id, ":", title, '-> 已经在Redis中发布并计入文章排名')


def delete_publish_record(pub_id, conn=__CONNECTION):
    
    '''
    Delete a publish article record and other records related in redis.
    '''
    pub_id = str(pub_id)
    try:
        pipe = conn.pipeline()
        pipe.delete('pub_article:' + pub_id)
        pipe.delete('voted:' + pub_id)
        pipe.delete('article_visitors_records:' + pub_id)
        pipe.zrem('articles_rank:', 'pub_article:' + pub_id)
        pipe.lrem('all_pub_articles:', 'pub_article:' + pub_id)
        pipe.execute()
        print(pub_id, '-> 已经在Redis中删除')
    except RedisError:
        pass


def article_vote_record(voter, pub_id, conn=__CONNECTION):
    
    '''
    Record each vote by different voter for each published article.
    The parameter 'voter' contains information about voter type (user or passager)
    and ip of voter.
    '''
    pub_id = str(pub_id)
    pub_article = 'pub_article:' + pub_id
    try:
        if conn.zadd('voted:' + pub_id, voter, time.time()):
            conn.hincrby(pub_article, 'votes_count', 1)
            conn.zincrby('articles_rank:', pub_article, 1)
            print('对 ', pub_id, ' 的投票成功！')
            return True
    except RedisError:
        pass
    return False


def has_voted(visit_record, pub_id, conn=__CONNECTION):

    pub_id = str(pub_id)

    try:
        r = conn.zrank("voted:" + pub_id, visit_record)
        if r is not None:
            return True
    except RedisError:
        pass
    return False


def article_visit_record(visitor, pub_id, conn=__CONNECTION):
    pub_id = str(pub_id)
    pub_article = 'pub_article:' + pub_id
    try:
        if conn.zadd('article_visitors_records:' + pub_id, visitor, time.time()):
            conn.hincrby(pub_article, 'visitors_count', 1)
            conn.zincrby('articles_rank:', pub_article, 1)
            return True
    except RedisError:
        pass
    return False


def blog_visit_record(visit_record, conn=__CONNECTION):

    try:
        if conn.zadd('visitors_records:', visit_record, time.time()):
            location = visit_record.split(':')[-2]
            conn.zincrby('region_distributions:', location, 1)
            return True
    except RedisError:
        pass
    return False


def load_aricle_content(article_id, file_path, file_type='md', conn=__CONNECTION):

    article = "article_content:" + file_type + ":" + article_id
    content = conn.get(article)
    if not content:
        try:
            print("文件路径: ", file_path)
            with open(file_path, 'r') as f:
                content = f.read(1024)
            conn.set(article, content)
            conn.expire(article, __CONTENT_EXPIRE_TIME)
            print("在redis中创建该键，并为 ", article, "设置过期时间：", __CONTENT_EXPIRE_TIME)
        except RedisError:
            content = "非常抱歉！内容无法加载，请重新编辑！"

    return content


def save_article_content(article_id, content, file_type="md", conn=__CONNECTION):
    article = "article_content:" + file_type + ":" + article_id

    try:
        if not conn.get(article):
            conn.set(article, content)
            conn.expire(article, __CONTENT_EXPIRE_TIME)
            print("在redis中保存该键，并为 ", article, "设置过期时间：", __CONTENT_EXPIRE_TIME)
        else:
            conn.set(article, content)
    except RedisError:
        return False
    return True


def update_comments_count(pub_id, conn=__CONNECTION):
    pub_id = str(pub_id)
    pub_article = 'pub_article:' + pub_id
    try:
        conn.hincrby(pub_article, 'comments_count', 1)
        conn.zincrby('articles_rank:', pub_article, 1)
    except RedisError:
        pass

# TODO
def user(user_name, user_ip, conn=__CONNECTION):
    conn.hset("users:", user_name, user_ip)

# TODO
def hgetall_pub_article(pub_article, conn=__CONNECTION):

    result = conn.hgetall(pub_article)
    return {
        'title': result[b'title'].decode('utf-8'),
        'type': result[b'type'].decode('utf-8'),
        'category': result[b'category'].decode('utf-8'),
        'abstract': result[b'abstract'].decode('utf-8'),
        'pub_time': result[b'pub_time'].decode('utf-8'),
        'link': result[b'link'].decode('utf-8'),
        'votes': int(result[b'votes_count']),
        'visitor': int(result[b'visitors_count']),
        'comments': int(result[b'comments_count'])
    }


PRECISION = [300, 7200, 86400]  # ５minutes, 2hours, 1 day


def update_PV_counter(count=1, conn=__CONNECTION):
    now = time.time()

    pipe = conn.pipeline()

    for prec in PRECISION:
        pnow = int(now / prec) * prec
        pipe.zadd('PV_counters:', 'PV_counter:' + str(prec), 0)
        pipe.hincrby('PV_counter:' + str(prec), pnow, count)
        print("点击已计入", 'PV_counter:' + h)
    pipe.execute()


def get_PV_counter(precision, conn=__CONNECTION):
   
    data = conn.hgetall('PV_counter:' + precision)
    result_to_return = []
    for k, v in data.iteritems():
        result_to_return.append((int(k), int(v)))
    result_to_return.sort()
    return result_to_return
