from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db import DatabaseError
from django.http import HttpResponse
from django.shortcuts import render

from backstage.models import Message


def message_box(request, p=1):
    context = {}
    try:
        messages = Message.objects.order_by('-compose_time')
        paginator = Paginator(messages, 10)
        try:
            messages_in_page = paginator.page(p)
        except PageNotAnInteger:
            messages_in_page = paginator.page(1)
        except EmptyPage:
            messages_in_page = paginator.page(paginator.num_pages)

        context['messages'] = messages_in_page
        context['total_pages'] = paginator.num_pages

    except DatabaseError:
        pass

    return render(request, 'backstage/message-box.html', context)


def read_message(request, message_id):
    pass


def delete_message(request):
    if request.is_ajax() and request.method == 'POST':
        delete_messages = request.POST.getlist('delete_messages', default=[])
        try:
            messages = Message.objects.in_bulk(delete_messages)
            for delete_id in messages:

                messages[delete_id].delete()
        except DatabaseError:
            return HttpResponse("删除失败！", status=403)
        return HttpResponse('删除成功')

    return HttpResponse(status=404)


def change_stat(request):
    if request.is_ajax() and request.method == 'POST':
        marked_messages = request.POST.getlist('marked_messages', default=[])
        try:
            messages = Message.objects.in_bulk(marked_messages)
            for msg_id in messages:
                messages[msg_id].readed = True
                messages[msg_id].save()
        except DatabaseError:
            return HttpResponse("标记失败！", status=403)
        return HttpResponse('标记成功')

    return HttpResponse(status=404)
