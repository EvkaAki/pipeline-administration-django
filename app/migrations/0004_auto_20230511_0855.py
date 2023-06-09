# Generated by Django 3.2 on 2023-05-11 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20230510_0856'),
    ]

    operations = [
        migrations.AddField(
            model_name='runrequest',
            name='pipeline_name',
            field=models.TextField(default='Pipeline Name'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='runrequest',
            name='user_email',
            field=models.EmailField(default='Pipeline Name', max_length=254),
            preserve_default=False,
        ),
    ]
