from django.db import models

# Create your models here.

import redis

CONNECTION_POOL_BLOG = redis.ConnectionPool(host='localhost', port=6379)
CONNECTION_BLOG = redis.Redis(connection_pool=CONNECTION_POOL_BLOG)


def get_redis_connection():

    return CONNECTION_BLOG
