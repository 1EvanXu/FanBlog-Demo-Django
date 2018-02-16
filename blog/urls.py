from django.urls import path, include
from blog import views

app_name = 'blog'

details_patterns = [
    path('<int:p>/', views.get_all_puba, name="get_all_published_articles"),
    path('details/<int:pub_id>', views.get_detail, name="published_article_detail"),
    path('praise/', views.praise, name="praise"),
    path('comment/', views.to_comment, name="comment"),
    path('load_comments/', views.load_comments, name="load_comments")
]

side_info_patterns = [
    path('latest/', views.get_latest_articles, name="get_latest_articles"),
    path('popular/', views.get_popular_articles, name="get_popular_articles"),
    path('categories/', views.get_categories, name="get_categories")
]

categories_patterns = [
    path('<int:c>/', views.category_view, name="category_view"),
    path('<int:c>/p/<int:p>/', views.category_view, name="category_view_pages")
]

message_patterns = [
    path('', views.message, name="leaving message"),
    path('compose/', views.compose, name="compose message")
]

urlpatterns = [
    path('', views.get_all_puba, name="blog_index", kwargs={'p': 1}),
    path('a/', include(details_patterns)),
    path('side/', include(side_info_patterns)),
    path('categories/', include(categories_patterns)),
    path('message/', include(message_patterns))
]
