from django.db import OperationalError
from django.http import Http404
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from backstage.models import Category

CONTEXT_FOR_CATEGORY = {}


def category(request, page=1):
    try:
        categories = Category.objects.order_by("-created_time")
        paginator = Paginator(categories, 10)
        try:
            categories_in_page = paginator.page(page)
        except PageNotAnInteger:
            categories_in_page = paginator.page(1)
        except EmptyPage:
            categories_in_page = paginator.page(paginator.num_pages)

        CONTEXT_FOR_CATEGORY['categories'] = categories_in_page
        CONTEXT_FOR_CATEGORY['pages'] = range(1, paginator.num_pages + 1)
        return render(request, 'backstage/category.html', CONTEXT_FOR_CATEGORY)
    except OperationalError:
        raise Http404
    finally:
        CONTEXT_FOR_CATEGORY.clear()


def create_category(request):

    if request.method == "POST":
        category_name = request.POST['name']
        category_describe = request.POST['details']
        new_category = Category(category_name=category_name, category_describe=category_describe)

        try:
            new_category.save()
            CONTEXT_FOR_CATEGORY['result'] = 'OK!创建成功！'
        except OperationalError:
            CONTEXT_FOR_CATEGORY['result'] = '创建成功！'
        return redirect('backstage:category')
    else:
        raise Http404('Page Not Found!')


def delete_category(request, category_id):

    try:
        c = Category.objects.get(id=category_id)
        c.delete()
        CONTEXT_FOR_CATEGORY['result'] = "OK!删除成功！"
    except:
        CONTEXT_FOR_CATEGORY['result'] = "删除失败！"
    return redirect('backstage:category')
