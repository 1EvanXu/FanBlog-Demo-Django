
from django.urls import path, include, re_path

from backstage import views

app_name = 'backstage'

category_patterns = [
    path('', views.category, name="category"),
    path('page/<int:page>/', views.category, name="category_pages"),
    path('create/', views.create_category, name="create_new_category"),
    path('delete/<int:category_id>/', views.delete_category, name="delete_category"),
]

edit_patterns = [
    path('', views.edit_article, name="edit"),
    re_path("(?P<new>(new|edited))/", views.edit_article, name="edit_article"),
    path('save/', views.save_article, name="save_article"),
    path('publish/', views.pub_article, name="publish_article"),
    path('load/', views.load_markdown, name="load_markdown"),
    path('full-editor/', views.edit_article, kwargs={'is_full': True}, name="full_editor")
]

articles_patterns = [
    path('all/', views.all_articles, name="all_articles"),
    path('all/page/<int:page>/', views.all_articles, name="all_articles_pages"),
    path('all/e/<int:article_id>/', views.to_edit, name="to_edit_from_all"),
    path('all/d/', views.to_delete, name="to_delete_from_all"),
    path('published/', views.published_articles, name="published_articles"),
    path('published/page/<int:page>/', views.published_articles, name="pub_articles_pages"),
    path('published/e/<int:article_id>/', views.to_edit, name="to_edit_from_pub"),
    path('published/d/', views.cancel_publish, name="to_delete_from_pub"),
    path('revert/', views.revert_from_trash, name="revert_from_trash"),
    path('delPermanently/', views.delete_permanently, name="delete_permanently"),
]

statistics_patterns = [
    path('', views.statistics, name="statistics"),
    path('sys/', views.sys, name="get_system_info"),
    path('nav/', views.nav_info, name="get_nav_info"),
    path('location/', views.get_visitors_location_info, name='get_location_info'),
    path('pv/<int:option>/', views.get_pv_info, name="get_pv_info")
]

upload_patterns = [
    path('image/', views.image_upload, name="image_upload"),
]

message_box_patterns = [
    path('', views.message_box, name="message_box"),
    path('p/<int:p>/', views.message_box, name="message_pages"),
    path('read/<int:message_id>/', views.read_message, name="read_message"),
    path('delete/', views.delete_message, name="delete_message"),
    path('stat/', views.change_stat, name="change_state"),
]

urlpatterns = [
    path('', views.statistics, name="index"),
    path('login/', views.login, name='login'),
    path('login_validate/', views.login_validate, name='validate'),
    path('logout/', views.logout, name='logout'),
    path('statistics/', include(statistics_patterns)),
    path('category/', include(category_patterns)),
    path('edit/', include(edit_patterns)),
    path('articles/', include(articles_patterns)),
    re_path("(?P<dt>(draft|trash))/(?P<p>\d*)/", views.draft_and_trash, name="draft_and_trash"),
    path('upload/', include(upload_patterns)),
    path('message/', include(message_box_patterns))
]

