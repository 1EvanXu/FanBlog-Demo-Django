from django.db import models


class PublishedArticle(models.Model):

    pub_id = models.IntegerField(unique=True)
    article = models.OneToOneField('Article', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.SET_DEFAULT, default=1,
                                 related_name='published_article', related_query_name='published_article')
    pub_time = models.DateTimeField(auto_now=True, editable=False)
    url = models.URLField()

    class Meta:
        app_label = 'backstage'
        db_table = 'published_articles'
        verbose_name = '已发布的文章'


class Article(models.Model):
    ARTICLE_TYPES = {
        ('original', '原创'),
        ('reprint', '转载'),
        ('translation', '翻译')
    }

    STATUS_TYPE = {
        (0, 'DELETED'),
        (1, 'IN DRAFTS'),
        (2, 'PUBLISHED')
    }

    article_id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=ARTICLE_TYPES, default='original')
    created_time = models.DateTimeField(auto_now=True, editable=False)
    latest_modify_time = models.DateTimeField(auto_now=True)
    status = models.SmallIntegerField(choices=STATUS_TYPE, default=1)
    html_file_path = models.URLField(default="/")
    md_file_path = models.URLField(default="/")

    def __str__(self):

        return "[" + \
               str(self.article_id) + ", " + \
               self.title + ", " + \
               self.type + ", " + \
               str(self.status) + "]"

    class Meta:
        app_label = 'backstage'
        db_table = 'articles'
        verbose_name = '所有文章'


class Category(models.Model):

    category_name = models.CharField(max_length=50)
    category_describe = models.TextField(null=True)
    created_time = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        app_label = 'backstage'
        db_table = 'categories'
        verbose_name = '文章的类别'


class Comment(models.Model):

    belonged_pub_article = models.ForeignKey('PublishedArticle', to_field='pub_id', on_delete=models.SET_DEFAULT,
                                             default=None, related_name="comments", related_query_name="comments")
    commentator = models.CharField(max_length=50)
    comment_content = models.TextField()
    comment_time = models.DateTimeField(auto_now=True, editable=False)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name="child_comment")
    reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name="reply_to")

    class Meta:
        app_label = 'backstage'
        db_table = 'comments'
        verbose_name = '文章中的评论'


class Message(models.Model):

    subject = models.CharField(max_length=50)
    writer = models.CharField(max_length=20)
    concat_info = models.CharField(max_length=50)
    message = models.TextField()
    readed = models.BooleanField(default=False)
    compose_time = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        app_label = 'backstage'
        db_table = 'messages'
        verbose_name = '博客留言'
