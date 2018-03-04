import time
from datetime import datetime
import redis
from redis.exceptions import RedisError
CONNECTION_POOL = redis.ConnectionPool(host='localhost', port=6379)
CONNECTION = redis.Redis(connection_pool=CONNECTION_POOL)
CONTENT_EXPIRE_TIME = 43200


def get_redis_connection():
    return CONNECTION


def publish_in_redis(pub_id, title, pub_type, category, link, abstract='', conn=CONNECTION):

    pub_id = str(pub_id)
    pub_article = 'pub_article:' + pub_id
    conn.hmset(pub_article, {
        'title': title,
        'type': pub_type,
        'category': category,
        'abstract': abstract,
        'pub_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'link': link,
        'votes': 0,
        'visitor': 0,
        'comments': 0,
    })

    conn.zadd('articles_rank:', pub_article, 0)
    conn.lpush('all_pub_articles:', pub_article)
    print(pub_id, ":", title, '-> 已经在Redis中发布并计入文章排名')


def cancel_publish_in_redis(pub_id, conn=CONNECTION):
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


def article_vote(voter, pub_id, conn=CONNECTION):
    pub_id = str(pub_id)
    pub_article = 'pub_article:' + pub_id
    try:
        if conn.zadd('voted:' + pub_id, voter, time.time()):
            conn.hincrby(pub_article, 'votes', 1)
            conn.zincrby('articles_rank:', pub_article, 1)
            print('对 ', pub_id, ' 的投票成功！')
            return True
    except RedisError:
        pass
    return False


def has_voted(visit_record, pub_id, conn=CONNECTION):

    pub_id = str(pub_id)

    try:
        r = conn.zrank("voted:" + pub_id, visit_record)
        if r is not None:
            return True
    except RedisError:
        pass
    return False


def article_visit_record(visitor, pub_id, conn=CONNECTION):
    pub_id = str(pub_id)
    pub_article = 'pub_article:' + pub_id
    try:
        if conn.zadd('article_visitors_records:' + pub_id, visitor, time.time()):
            conn.hincrby(pub_article, 'visitor', 1)
            conn.zincrby('articles_rank:', pub_article, 1)
            print(visitor, '对 ', pub_id, ' 的访问成功！')
            return True
    except RedisError:
        pass
    return False


def blog_visit_record(visit_record, conn=CONNECTION):

    try:
        if conn.zadd('visitors_records:', visit_record, time.time()):
            location = visit_record.split(':')[-2]
            conn.zincrby('region_distributions:', location, 1)
            return True
    except RedisError:
        pass
    return False


def load_content(article_id, file_path, file_type='md', conn=CONNECTION):

    content = "article_content:" + file_type + ":" + article_id
    content_value = conn.get(content)
    if not content_value:
        try:
            print("文件路径: ", file_path)
            with open(file_path, 'r') as f:
                content_value = f.read(1024)
            conn.set(content, content_value)
            conn.expire(content, CONTENT_EXPIRE_TIME)
            print("在redis中创建该键，并为 ", content, "设置过期时间：", CONTENT_EXPIRE_TIME)
        except RedisError:
            content_value = "非常抱歉！内容无法加载，请重新编辑！"

    return content_value


def comment_record_in_redis(pub_id, conn=CONNECTION):
    pub_id = str(pub_id)
    pub_article = 'pub_article:' + pub_id
    try:
        conn.hincrby(pub_article, 'comments', 1)
        conn.zincrby('articles_rank:', pub_article, 1)
    except RedisError:
        pass


def save_content(article_id, content_value, file_type="md", conn=CONNECTION):
    content = "article_content:" + file_type + ":" + article_id

    try:
        if not conn.get(content):
            conn.set(content, content_value)
            conn.expire(content, CONTENT_EXPIRE_TIME)
            print("在redis中保存该键，并为 ", content, "设置过期时间：", CONTENT_EXPIRE_TIME)
        else:
            conn.set(content, content_value)
    except RedisError:
        return False
    return True


def user(user_name, user_ip, conn=CONNECTION):
    conn.hset("users:", user_name, user_ip)


def hgetall_pub_article(pub_article, conn=CONNECTION):

    result = conn.hgetall(pub_article)
    return {
        'title': result[b'title'].decode('utf-8'),
        'type': result[b'type'].decode('utf-8'),
        'category': result[b'category'].decode('utf-8'),
        'abstract': result[b'abstract'].decode('utf-8'),
        'pub_time': result[b'pub_time'].decode('utf-8'),
        'link': result[b'link'].decode('utf-8'),
        'votes': int(result[b'votes']),
        'visitor': int(result[b'visitor']),
        'comments': int(result[b'comments'])
    }


PRECISION = [300, 7200, 86400]  # ５minutes, 2hours, 1 day


def update_counter(count=1, name='hit', conn=CONNECTION):
    now = time.time()

    pipe = conn.pipeline()

    for prec in PRECISION:
        pnow = int(now / prec) * prec
        h = '%s:%s' % (prec, name)
        pipe.zadd('counters:', 'count:' + h, 0)
        pipe.hincrby('count:' + h, pnow, count)
        print("点击已计入", 'count:' + h)
    pipe.execute()


def get_counter(precision, name='hit', conn=CONNECTION):
    h = '%s:%s' % (precision, name)
    data = conn.hgetall('count:' + h)
    to_return = []
    for k, v in data.iteritems():
        to_return.append((int(k), int(v)))
    to_return.sort()
    return to_return

