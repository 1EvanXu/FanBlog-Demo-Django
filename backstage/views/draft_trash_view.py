from django.db import OperationalError, DatabaseError
import os
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render

from backstage.models import Article


def draft_and_trash(request, dt='draft', p=1):
    context = {}
    try:

        status = 1
        template = 'backstage/draft.html'
        if dt == "trash":
            status = 0
            template = 'backstage/trash.html'

        articles = Article.objects.filter(status=status).order_by("-created_time")
        paginator = Paginator(articles, 10)
        try:
            articles_in_page = paginator.page(p)
        except PageNotAnInteger:
            articles_in_page = paginator.page(1)
        except EmptyPage:
            articles_in_page = paginator.page(paginator.num_pages)

        context['articles'] = articles_in_page
        context['pages'] = range(1, paginator.num_pages + 1)
        return render(request, template, context)

    except OperationalError:
        return render(request, 'errorpages/404.html')


def delete_permanently(request):

    if request.is_ajax() and request.method == 'POST':
        delete_articles = request.POST.getlist('delete_articles', default=[])
        try:
            articles = Article.objects.in_bulk(delete_articles)
            for delete_id in articles:
                os.remove(articles[delete_id].html_file_path)
                os.remove(articles[delete_id].md_file_path)
                articles[delete_id].delete()
        except:
            return HttpResponse("删除失败！", status=403)
        return HttpResponse('删除成功')

    return HttpResponse(status=404)


def revert_from_trash(request):

    if request.is_ajax() and request.method == 'POST':
        revert_articles = request.POST.getlist('revert_articles', default=[])
        try:
            articles = Article.objects.in_bulk(revert_articles)
            for key in articles:
                if articles[key].status == 0:
                    articles[key].status = 1
                    articles[key].save()
        except DatabaseError:
            return HttpResponse("还原失败！", status=403)
        return HttpResponse('还原成功！')

    return HttpResponse(status=404)
