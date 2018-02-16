from django.db import DatabaseError
from django.http import HttpResponse, Http404
from django.shortcuts import render

from backstage.models import Message


def message(request):
    return render(request, 'blog/message.html')


def compose(request):

    if request.is_ajax() and request.method == 'POST':
        subject = request.POST.get('subject')
        writer = request.POST.get('writer')
        concat_info = request.POST.get('concat_info')
        message_content = request.POST.get('message')
        try:
            msg = Message(subject=subject, writer=writer, concat_info=concat_info, message=message_content)
            msg.save()
        except DatabaseError:
            return HttpResponse('数据库错误！留言失败！', content_type='text')

        return HttpResponse('提交成功！', content_type='text')

    return Http404
