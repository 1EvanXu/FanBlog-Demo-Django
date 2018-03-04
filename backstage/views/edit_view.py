import threading
import threadpool
from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError, DatabaseError
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from datetime import datetime
from backstage.models import Category, Article, PublishedArticle, load_content, save_content, publish_in_redis

ARTICLES_BASE_DIR = '/home/evan/articles/'
ARTICLES_HTML_DIR = ARTICLES_BASE_DIR + 'html/'
ARTICLES_MARKDOWN_DIR = ARTICLES_BASE_DIR + 'markdown/'


def edit_article(request, new='edited', is_full=False):
    context = {}
    article_id = request.session.get("article_id")

    print("从SESSION中取出 article id ->", article_id)
    if new == 'edited':
        if article_id:
            try:
                article = Article.objects.get(article_id=article_id)
                print("数据库中对应 article id ->", article_id)
                context['title'] = article.title
                # context['content_path'] = str(article_id) + ".md"
            except (OperationalError, ObjectDoesNotExist, DatabaseError):
                article_id = generate_article_id()
                request.session['article_id'] = article_id
                print("edited条件中 article_id 更新->", article_id)
        else:
            article_id = generate_article_id()
            request.session['article_id'] = article_id
    elif new == "new":
        article_id = generate_article_id()
        request.session['article_id'] = article_id
        print("new条件中 article_id 更新->", article_id)

    print("处理之后 article_id ->", article_id)
    context["article_id"] = article_id
    categories = Category.objects.order_by("-created_time")
    context['categories'] = categories

    template = 'backstage/edit.html'
    if is_full:
        template = 'backstage/full-editor-md.html'

    return render(request, template, context)


h_lock = threading.Lock()
m_lock = threading.Lock()
pool = threadpool.ThreadPool(8)


def save_article(request):

    if request.is_ajax() and request.method == 'POST':
        article_id = request.POST.get("article_id")
        if article_id == "":
            return redirect("backstage:edit")

        title = request.POST.get("title")
        if title == "":
            title = article_id

        html_text = request.POST.get('htmlText')
        markdown_text = request.POST.get('markdownText')
        save_method = request.POST.get("saveMethod")
        print("POST请求中的数据: ", request.POST)

        if html_text or markdown_text:

            html_text_path = ARTICLES_HTML_DIR + article_id + ".html"
            markdown_text_path = ARTICLES_MARKDOWN_DIR + article_id + ".md"

            reqs1 = []
            if save_method == 'manual':
                print("手动保存时将，内容保存至硬盘文件")
                arg_list1 = [html_text_path, html_text, h_lock]
                arg_list2 = [markdown_text_path, markdown_text, m_lock]
                fun_args1 = [(arg_list1, None), (arg_list2, None)]
                reqs1 = threadpool.makeRequests(save_to_file, fun_args1)

            arg_list_3 = [article_id, html_text, 'html']
            arg_list_4 = [article_id, markdown_text, 'md']
            fun_args2 = [(arg_list_3, None), (arg_list_4, None)]
            reqs2 = threadpool.makeRequests(save_content, fun_args2)

            reqs = reqs2 + reqs1
            [pool.putRequest(req) for req in reqs]
            pool.wait()

            try:
                defaults = {
                    'title': title,
                    'html_file_path': html_text_path,
                    'md_file_path': markdown_text_path,
                    'latest_modify_time': datetime.now()
                }
                Article.objects.get_or_create(pk=article_id, defaults=defaults)
            except OperationalError:
                pass

        return HttpResponse("OK")

    return render(request, 'errorpages/403.html')


def pub_article(request):

    if request.method == 'POST':

        article_id = request.POST.get("article_id")
        title = request.POST.get("article_title")
        article_type = request.POST.get("article_type")
        category_id = request.POST.get("categories")
        abstract = request.POST.get("abstract", "")
        category = "其他"
        pub_id = generate_pub_id()
        url = "/blog/a/details/" + pub_id
        print("即将存入数据表中的数据：", article_id, title, article_type, category_id, url)
        try:
            article = Article.objects.get(article_id=article_id)
            article.title = title
            article.type = article_type
            status = article.status
            article.status = 2
            article.save()
            if status != 2:
                published_article = PublishedArticle(pub_id=pub_id, url=url, article=article, category_id=category_id)
                published_article.save()
                category = Category.objects.get(pk=category_id).category_name
        except (DatabaseError, ObjectDoesNotExist):
            return HttpResponse("发布失败", status=403)
        else:
            publish_in_redis(pub_id, title, article_type, category, url, abstract=abstract)

        return HttpResponse("OK!发布成功！", content_type="text")

    return Http404()


def load_markdown(request):

    if request.is_ajax():

        article_id = request.GET.get('article_id', default=1)
        try:
            article = Article.objects.get(pk=article_id)
            md = load_content(article_id, article.md_file_path)
        except ObjectDoesNotExist:
            md = '请开始你的新文章...'
        return HttpResponse(md, content_type='text')

    return Http404()


def save_to_file(path, content, lock):

    lock.acquire()
    print("开启保存文件至 ", path, " 的线程...")
    with open(path, 'w') as f:
        f.write(content)
        f.flush()
    lock.release()
    print("保存文件至 ", path, " 的线程完成执行并释放锁！")


def generate_article_id():
    try:
        article_id = Article.objects.last().article_id + 1
    except (ObjectDoesNotExist, OperationalError, DatabaseError, AttributeError):
        article_id = generate_pub_id()
    print("generate_article_id()函数产生的 article id -> ", article_id)
    return article_id


def generate_pub_id():

    # 或者用UUID取代
    now = datetime.now()
    pub_id = now.strftime("%y%m%d%S")
    try:
        PublishedArticle.objects.get(pub_id)
        # (ObjectDoesNotExist, DatabaseError)
    except:
        pass
    else:
        pub_id = PublishedArticle.objects.last().pub_id + 1

    return pub_id




