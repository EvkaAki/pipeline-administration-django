# Generated by Django 3.2 on 2025-05-10 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_datasetrequest_response_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='runrequest',
            name='result',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='runrequest',
            name='run_id',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
