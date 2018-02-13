# Generated by Django 2.0 on 2018-01-26 08:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backstage', '0008_auto_20180125_1504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='status',
            field=models.SmallIntegerField(choices=[(2, 'PUBLISHED'), (0, 'DELETED'), (1, 'IN DRAFTS')], default=1),
        ),
        migrations.AlterField(
            model_name='article',
            name='type',
            field=models.CharField(choices=[('original', '原创'), ('translation', '翻译'), ('reprint', '转载')], default='original', max_length=20),
        ),
        migrations.AlterField(
            model_name='publishedarticle',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='published_article', related_query_name='published_article', to='backstage.Category'),
        ),
    ]
