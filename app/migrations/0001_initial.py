# Generated by Django 3.2 on 2023-05-09 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RunRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('state', models.IntegerField()),
                ('pipeline_id', models.UUIDField()),
                ('dataset_id', models.UUIDField()),
                ('user_id', models.UUIDField()),
            ],
        ),
    ]
