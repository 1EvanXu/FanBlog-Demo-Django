# Generated by Django 2.0 on 2018-02-01 02:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backstage', '0011_auto_20180201_1042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'DELETED'), (2, 'PUBLISHED'), (1, 'IN DRAFTS')], default=1),
        ),
        migrations.AlterField(
            model_name='comment',
            name='parent_comment',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent', to='backstage.Comment'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='reply',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reply_to', to='backstage.Comment'),
        ),
    ]