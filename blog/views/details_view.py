import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from django.http import HttpResponse
from django.shortcuts import render
from redis import RedisError
import time
from backstage.models import PublishedArticle, hgetall_pub_article, article_vote, article_visit_record, has_voted, \
    Comment, comment_record_in_redis
import os


def get_detail(request, pub_id):

    try:
        published_article = PublishedArticle.objects.get(pub_id=pub_id)
        title = published_article.article.title
        article_type = published_article.article.get_type_display()
        category = published_article.category.category_name
        pub_time = published_article.pub_time
        html_file_path = published_article.article.html_file_path
        total_comments_number = Comment.objects.filter(belonged_pub_article_id=pub_id).count()

        if os.path.exists(html_file_path):
            html_file_path = html_file_path.split("/")[-1]
        else:
            return render(request, 'errorpages/404.html')
    except DatabaseError:
        return render(request, 'errorpages/404.html')

    username = request.session.get('username', "")

    ip = request.get_host()
    if ip.find(":"):
        ip = ip.partition(":")[0]

    if username:
        visit_record = "user:" + username
    else:
        visit_record = "visitor:" + ip

    voted = has_voted(visit_record, pub_id)

    try:
        article_visit_record(visit_record, pub_id)
        puba_in_redis = hgetall_pub_article('pub_article:' + str(pub_id))
        votes = puba_in_redis['votes']
        visitors = puba_in_redis['visitor']
    except RedisError:
        votes = 0
        visitors = 0

    context = {
        'pub_id': pub_id,
        'title': title,
        'type': article_type,
        'category': category,
        'pub_time': pub_time,
        'votes': votes,
        'visitors': visitors,
        'html_file_path': html_file_path,
        'is_voted': voted,
        'username': username,
        'total_comments_number': total_comments_number
    }

    try:
        previous_article = published_article.get_previous_by_pub_time()
        context['previous'] = previous_article
    except ObjectDoesNotExist:
        pass
    try:
        next_article = published_article.get_next_by_pub_time()
        context['next'] = next_article
    except ObjectDoesNotExist:
        pass

    return render(request, 'blog/details.html', context)


def praise(request):

    if request.is_ajax():
        pub_id = request.GET.get('pub_id')
        username = request.session.get('username', "")

        ip = request.get_host()
        if ip.find(":"):
            ip = ip.partition(":")[0]

        if username:
            voter = "user:" + username
        else:
            voter = "visitor:" + ip

        praise_result = article_vote(voter, pub_id)

        return HttpResponse(praise_result)

    return render(request, "errorpages/403.html")


def to_comment(request):

    if request.is_ajax() and request.method == "POST":
        username = request.session.get("username", "")
        commentator = "evan"
        pub_id = request.POST.get('pub_id')
        comment_content = request.POST.get('comment')
        comment_content = comment_content.strip()
        comment_id_reply = request.POST.get('commentIdReply')
        child_comment_id_reply = request.POST.get('childCommentIdReply')

        print(comment_id_reply, child_comment_id_reply)

        try:
            comment = Comment(belonged_pub_article_id=pub_id, commentator=commentator, comment_content=comment_content,
                              parent_comment_id=comment_id_reply, reply_id=child_comment_id_reply)
            comment.save()
            comment_record_in_redis(pub_id)
            result = "评论成功！"
        except DatabaseError:
            result = "评论失败，无法连接数据库！"

        return HttpResponse(result)


def load_comments(request):

    if request.is_ajax():
        pub_id = request.GET.get('pub_id')
        comments = Comment.objects.filter(belonged_pub_article_id=pub_id, parent_comment=None).order_by('-comment_time')
        comments_json = comments_to_json(comments)
        print(comments_json)
        return HttpResponse(json.dumps(comments_json), content_type='json')


def comments_to_json(comments):
    comments_json = []

    for comment in comments:
        comment_json = comment_to_json(comment)
        child_comments = comment.child_comment.all().order_by('comment_time')
        if child_comments.count() > 0:
            child_comments_json = comments_to_json(child_comments)
            comment_json['childComments'] = child_comments_json
        comments_json.append(comment_json)

    return comments_json


def comment_to_json(comment):

    comment_json = dict()
    comment_json['commentId'] = str(comment.id)
    comment_json['commentator'] = comment.commentator
    comment_json['commentTime'] = comment.comment_time.strftime("%Y-%m-%d %H:%M:%S")
    comment_json['commentContent'] = comment.comment_content
    if comment.reply:
        comment_json['replyTo'] = comment.reply.commentator
    return comment_json


def to_reply(request):
    pass

