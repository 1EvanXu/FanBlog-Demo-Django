from django.db import models


class Manager(models.Model):

    name = models.CharField(max_length=10, unique=True, null=False, blank=False)
    password = models.CharField(max_length=16, unique=True, null=False, blank=False)
    email = models.EmailField()
    level = models.CharField(max_length=9, default='common')

    def __str__(self):
        return "[" + self.name + ", " + self.email + "]"

    class Meta:
        app_label = 'backstage'
        db_table = 'managers'
        default_related_name = 'manager'
        verbose_name = '后台管理员'

