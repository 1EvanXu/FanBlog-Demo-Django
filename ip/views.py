from django.http import HttpResponse, Http404
from django.shortcuts import render
from redis import RedisError
from ip.ip import find_city_by_ip
import re
import socket
import json


def ip_query(request):
    return render(request, 'ip/ipinfo.html')


def do_ip_query(request):

    if request.is_ajax():
        ip_or_domain = request.GET.get('ipOrDomain')

        ip_pat = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        domain_pat = re.compile('www\..+\.[a-z]{2,3}')

        if ip_pat.match(ip_or_domain):
            ip = ip_or_domain
        elif domain_pat.match(ip_or_domain):
            ip = socket.gethostbyname(ip_or_domain)
        else:
            return HttpResponse(json.dumps({'msg': 'Incorrect input!'}))

        if ip == '127.0.0.1' or ip.startswith('192.168.'):
            return HttpResponse(json.dumps({'msg': 'Local ip address!'}))

        try:
            query_result = find_city_by_ip(ip)
            result = {
                'ip': ip,
                'city': query_result[0],
                'country': query_result[1],
                'continent': query_result[2],
                'success': 1
            }
        except RedisError:
            result = {'success': 0}

        return HttpResponse(json.dumps(result), content_type='json')

    return Http404
