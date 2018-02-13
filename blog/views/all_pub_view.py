from django.shortcuts import render
from redis import RedisError

from backstage.models import get_redis_connection, hgetall_pub_article


def get_all_puba(request, p=1):

    if p <= 0:
        p = 1

    num_per_page = 10
    start = (p - 1) * num_per_page
    end = p * num_per_page - 1
    try:
        conn = get_redis_connection()
        total_pages = int(conn.llen('all_pub_articles:') / num_per_page) + 1
        puba_list = conn.lrange('all_pub_articles:', start=start, end=end)
        results = []
        for item in puba_list:
            puba_name = item.decode("utf-8")
            puba = hgetall_pub_article(puba_name)
            results.append(puba)

        context = {
            'all_pubas': results,
            'total_pages': range(1, total_pages + 1),
            'current_page': p
        }
    except RedisError:
        context = {}
    return render(request, 'blog/all.html', context)


# def get_all_puba_from_sql(p=1):
#     context = {}
#     try:
#         pub_articles = PublishedArticle.objects.order_by('-pub_time')
#         paginator = Paginator(pub_articles, 10)
#         try:
#             pub_articles_in_page = paginator.page(page)
#         except PageNotAnInteger:
#             pub_articles_in_page = paginator.page(1)
#         except EmptyPage:
#             pub_articles_in_page = paginator.page(paginator.num_pages)
#
#         context['pub_articles'] = pub_articles_in_page
#         context['pages'] = range(1, paginator.num_pages + 1)
#
#     except OperationalError:
#         pass

