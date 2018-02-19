import json
from datetime import datetime, timedelta
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.db import OperationalError, DatabaseError
from redis import RedisError
from backstage.models import PublishedArticle, Article, get_redis_connection, hgetall_pub_article, Comment, Manager, \
    Message
from backstage.views.system_info import get_system_info


def statistics(request):

    published_article_num = get_published_article_num()
    article_total_num = get_article_total_num()
    popular_articles = get_popular_articles()
    total_votes = get_total_votes()
    latest_comments = get_latest_comments()
    context = {

        'published_article_num': published_article_num,
        'article_total_num': article_total_num,
        'popular_articles': popular_articles,
        'total_votes': total_votes,
        'latest_comments': latest_comments,
        'total_visit': get_total_visit()
    }
    print(context)
    return render(request, 'backstage/statistics.html', context)


def sys(request):

    if request.is_ajax():
        system_info = get_system_info()
        return HttpResponse(json.dumps(system_info), content_type="application/json")


def nav_info(request):

    if request.is_ajax():
        task_info = {
            'uncompleted': 0,
            'percentage': 100,
            'admin': '',
            'adminImg': '',
            'unreadMsgNum': ''
        }

        try:
            draft_articles_num = Article.objects.filter(status=1).count()
            total_articles_num = Article.objects.all().count()
            percentage = round((1 - (draft_articles_num / total_articles_num)) * 100)

            task_info['uncompleted'] = draft_articles_num
            task_info['percentage'] = percentage
            task_info['unreadMsgNum'] = Message.objects.filter(readed=False).count()
            task_info['admin'] = request.session.get('admin').get('name')

            if task_info['admin']:
                manager = Manager.objects.get(name=task_info['admin'])
                task_info['adminImg'] = manager.image
        except DatabaseError:
            pass
        
        return HttpResponse(json.dumps(task_info), content_type='json')

    return render(request, 'errorpages/500.html')


def get_published_article_num():

    try:
        return PublishedArticle.objects.count()
    except OperationalError:
        return 0


def get_article_total_num():
    try:
        return Article.objects.count()
    except OperationalError:
        return 0


def get_popular_articles():

    popular_articles = []
    try:
        conn = get_redis_connection()
        tuple_list = conn.zrevrange('articles_rank:', 0, 11, withscores=True)
        for t in tuple_list:
            puba = hgetall_pub_article(t[0], conn)
            puba['popularity'] = t[1]
            popular_articles.append(puba)
    except RedisError:
        pass

    return popular_articles


def get_total_visit():
    total_visit = 0
    try:
        conn = get_redis_connection()
        total_visit = conn.zcard('visitors_records:')
    except RedisError:
        pass
    return total_visit


def get_total_votes():

    total_votes = 0
    try:
        conn = get_redis_connection()
        tuple_list = conn.zrevrange('articles_rank:', 0, 11, withscores=True)
        for t in tuple_list:
            total_votes += int(conn.hget(t[0], 'votes'))
    except RedisError:
        pass
    return total_votes


def get_latest_comments():

    latest_comments = Comment.objects.order_by('-comment_time')[0:5]
    latest_comments_list = []
    for c in latest_comments:

        latest_comments_list.append({
            "header": c.commentator + "评论了" + c.belonged_pub_article.article.title,
            "link": c.belonged_pub_article.url,
            'time': c.comment_time.strftime("%Y-%m-%d %H:%M:%S"),
            'content': c.comment_content
        })

    return latest_comments_list


COLOR_CHOICE = ['#f56954', '#00a65a', '#f39c12', '#00c0ef', '#d2d6de']


def get_visitors_location_info(request):

    if request.is_ajax():
        conn = get_redis_connection()
        location_list = conn.zrevrange('region_distributions:', 0, 4, withscores=True)
        pie_data = []
        for i in range(len(location_list)):
            pie_data.append({
                'value': location_list[i][1],
                'color': COLOR_CHOICE[i],
                'highlight': COLOR_CHOICE[i],
                'label': location_list[i][0].decode('utf-8')
            })
        return HttpResponse(json.dumps(pie_data), content_type='json')

    return Http404


def get_pv_info(request, option):

    if request.is_ajax():
        conn = get_redis_connection()
        now = datetime.now()
        pv_info = {'x': [0], 'y': [0]}

        if option == 1:
            count_hits = conn.hgetall('count:7200:hit')
            timestamp = datetime(year=now.year, month=now.month, day=now.day, hour=0, minute=0, second=0).timestamp()

            keys = list(count_hits.keys())
            keys.sort()

            for k in keys:
                if float(k) >= timestamp:
                    pv_info['x'].append(datetime.fromtimestamp(float(k)).strftime("%H:%M"))
                    pv_info['y'].append(int(count_hits[k]))

        print("1:", pv_info)

        if option == 7:
            count_hits = conn.hgetall('count:86400:hit')
            today = datetime(year=now.year, month=now.month, day=now.day, hour=0, minute=0, second=0)
            week_ago = today + timedelta(days=-7)

            week_ago_stamp = week_ago.timestamp()
            keys = list(count_hits.keys())
            keys.sort()

            for k in keys:

                if float(k) >= week_ago_stamp:
                    pv_info['x'].append(datetime.fromtimestamp(float(k)).strftime("%m-%d"))
                    pv_info['y'].append(int(count_hits[k]))

        print("7:", pv_info)

        if len(pv_info['x']) == 0:
            pv_info['x'] = [i for i in range(7)]

        if len(pv_info['y']) == 0:
            pv_info['y'] = [1] * 7

        return HttpResponse(json.dumps(pv_info), content_type='json')
