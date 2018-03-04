from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import *

from backstage.models import blog_visit_record, update_counter
from ip.ip import find_city_by_ip


class BackstageInterceptor(MiddlewareMixin):

    exact_url_list = [
        '/back/login/',
        '/back/login_validate/',
        '/back/logout/',
        '/back/statistics/sys/',
        '/back/statistics/nav/',
        '/back/statistics/location/',
        '/back/statistics/pv/1/',
        '/back/statistics/pv/7/',
        '/back/edit/save/',
    ]

    def process_request(self, request):
        path = request.path

        # 可增加功能：管理员账户权限的限制功能
        if path.startswith("/back/") and path not in self.exact_url_list:
            administrator = request.session.get('admin', None)
            print("来自后台拦截器：admin:", administrator)
            if not administrator:
                return redirect('backstage:login', permanent=True)


class BlogInterceptor(MiddlewareMixin):

    exact_url_list = [
        '/blog/side/latest/',
        '/blog/side/categories/',
        '/blog/side/popular/',
        '/blog/a/comment/',
        '/blog/a/load_comment',
        '/blog/a/praise/'
    ]

    def process_request(self, request):

        path = request.path
        if path.startswith("/blog/") and path not in self.exact_url_list:

            update_counter()

            user = request.session.get('user', None)
            host_ip = request.get_host().partition(':')[0]
            if host_ip != '127.0.0.1' or not host_ip.startswith('192.168'):
                query_result = find_city_by_ip(host_ip)
                if not query_result[0]:
                    query_result[0] = "其他"

                if user:
                    visitor_type = 'users:' + user + ":"
                else:
                    visitor_type = 'visitors:visitors:'

                visitor_record = visitor_type + host_ip + ":" + query_result[0] + ":" + query_result[1]
                blog_visit_record(visitor_record)


class MultipleProxyMiddleware(MiddlewareMixin):

    FORWARDED_FOR_FIELDS = [
        'HTTP_X_FORWARDED_FOR',
        'HTTP_X_FORWARDED_HOST',
        'HTTP_X_FORWARDED_SERVER',
    ]

    def process_request(self, request):
        """
        Rewrites the proxy headers so that only the most
        recent proxy is used.
        """
        for field in self.FORWARDED_FOR_FIELDS:
            if field in request.META:
                if ',' in request.META[field]:
                    parts = request.META[field].split(',')
                    request.META[field] = parts[-1].strip()