from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import OperationalError, DatabaseError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from backstage.models import Article, PublishedArticle, cancel_publish_in_redis, RedisError


def all_articles(request, page=1):
    context = {}
    try:
        articles = Article.objects.order_by("-created_time")
        paginator = Paginator(articles, 10)
        try:
            articles_in_page = paginator.page(page)
        except PageNotAnInteger:
            articles_in_page = paginator.page(1)
        except EmptyPage:
            articles_in_page = paginator.page(paginator.num_pages)

        context['articles'] = articles_in_page
        context['pages'] = range(1, paginator.num_pages + 1)

    except OperationalError:
        pass
    return render(request, 'backstage/all_articles.html', context)


def published_articles(request, page=1):
    context = {}
    try:
        pub_articles = PublishedArticle.objects.order_by('-pub_time')
        paginator = Paginator(pub_articles, 10)
        try:
            pub_articles_in_page = paginator.page(page)
        except PageNotAnInteger:
            pub_articles_in_page = paginator.page(1)
        except EmptyPage:
            pub_articles_in_page = paginator.page(paginator.num_pages)

        context['pub_articles'] = pub_articles_in_page
        context['pages'] = range(1, paginator.num_pages + 1)

    except OperationalError:
        pass

    return render(request, 'backstage/pub_articles.html', context)


def to_edit(request, article_id):
    request.session['article_id'] = article_id
    return redirect('backstage:edit_article', new='edited')


def to_delete(request):
    if request.is_ajax() and request.method == 'POST':
        delete_articles = request.POST.getlist('delete_articles', default=[])
        try:
            articles = Article.objects.in_bulk(delete_articles)
            for delete_id in articles:
                if articles[delete_id].status != 2:
                    articles[delete_id].status = 0
                    articles[delete_id].save()
        except:
            return HttpResponse("删除失败！", status=403)
        return HttpResponse('删除成功')

    return HttpResponse(status=404)


def cancel_publish(request):

    if request.is_ajax() and request.method == 'POST':
        cancel_publish_articles = request.POST.getlist('delete_articles', default=[])
        print("从网页接收的要取消发布的文章的 primary key 列表 ->", cancel_publish_articles)
        try:
            pub_articles = PublishedArticle.objects.in_bulk(cancel_publish_articles)
            print("要取消发布的文章列表 -> ", pub_articles)
            for key in pub_articles:
                print("要取消发布的文章 -> ", pub_articles[key])
                cancel_publish_in_redis(pub_articles[key].pub_id)
                pub_articles[key].article.status = 1
                pub_articles[key].article.save()
                pub_articles[key].delete()

        except (DatabaseError, RedisError):
            return HttpResponse("取消发布失败！", status=403)
        return HttpResponse('取消发布成功')

    return HttpResponse(status=404)

