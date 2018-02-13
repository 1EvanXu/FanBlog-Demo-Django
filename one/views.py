from django.shortcuts import render


def page_not_found(request):
    return render(request, 'errorpages/404.html')


def page_error(request):
    return render(request, 'errorpages/500.html')


def permission_denied(request):
    return render(request, 'errorpages/403.html')


def bad_request(request):
    return render(request, 'errorpages/400.html')