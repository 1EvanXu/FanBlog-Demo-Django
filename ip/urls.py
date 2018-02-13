from django.urls import path
from ip import views


app_name = 'ip'

urlpatterns = [
    path('', views.ip_query, name='ip_query'),
    path('query/', views.do_ip_query, name='do_ip_query'),
]