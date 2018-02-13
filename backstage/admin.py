from django.contrib import admin

# Register your models here.
# from (your models files or packages) import (model class)
# add the follow code
# admin.site.register(model class)
from .models import Manager
admin.site.register(Manager)
