from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import OperationalError
from django.shortcuts import render

from backstage.models import Category


def category_view(request, c, p=1):

    context = {}
    try:
        category = Category.objects.get(pk=c)
        category_name = category.category_name
        context['category_id'] = c
        context['category_name'] = category_name

        articles = category.published_article.all().order_by('-pub_time')
        paginator = Paginator(articles, 10)
        try:
            pub_articles_in_page = paginator.page(p)
        except PageNotAnInteger:
            pub_articles_in_page = paginator.page(1)
        except EmptyPage:
            pub_articles_in_page = paginator.page(paginator.num_pages)

        context['pub_articles'] = pub_articles_in_page
        context['pages'] = range(1, paginator.num_pages + 1)
    except OperationalError:
        pass

    return render(request, 'blog/categories.html', context)
