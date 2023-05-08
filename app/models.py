from django.db import models


class Request(models.Model):
    description = models.TextField()
    state = models.IntegerField()
    pipeline_id = models.UUIDField()
    dataset_id = models.UUIDField()
    user_id = models.UUIDField()

    def __str__(self):
        return self.pipeline_id