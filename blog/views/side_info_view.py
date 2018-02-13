import json

from django.db import DatabaseError
from django.http import HttpResponse
from redis import RedisError

from backstage.models import hgetall_pub_article, Category
from blog.models import get_redis_connection


def get_latest_articles(request):

    if request.is_ajax():
        try:
            conn = get_redis_connection()
            puba_list = conn.lrange('all_pub_articles:', start=0, end=5)
        except RedisError:
            return HttpResponse(status=500)

        results = []
        for item in puba_list:
            puba_name = item.decode("utf-8")
            puba = hgetall_pub_article(puba_name)
            results.append(puba)

        return HttpResponse(json.dumps(results))


def get_categories(request):

    if request.is_ajax():
        try:
            categories = Category.objects.all()
        except DatabaseError:
            return HttpResponse(status=500)

        category_list = []
        for c in categories:
            category_list.append({
                "categoryId": c.id,
                "categoryName": c.category_name,
                "ownArticles": c.published_article.all().count()
            })
        print(category_list)
        return HttpResponse(json.dumps(category_list))


def get_popular_articles(request):
    if request.is_ajax():
        popular_articles = []
        try:
            conn = get_redis_connection()
            tuple_list = conn.zrevrange('articles_rank:', 0, 7, withscores=True)
            for t in tuple_list:
                puba = hgetall_pub_article(t[0], conn)
                puba['popularity'] = t[1]
                popular_articles.append(puba)
        except RedisError:
            return HttpResponse(status=500)
        print(popular_articles)
        return HttpResponse(json.dumps(popular_articles))



