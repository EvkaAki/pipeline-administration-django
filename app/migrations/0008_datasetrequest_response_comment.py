# Generated by Django 3.2 on 2023-05-12 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_datasetrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasetrequest',
            name='response_comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]
