from django.db import models

class RunRequest(models.Model):
    pipeline_id = models.Int
