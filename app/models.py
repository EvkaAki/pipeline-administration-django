from django.db import models


class RunRequest(models.Model):
    description = models.TextField()
    state = models.IntegerField()
    pipeline_id = models.UUIDField()
    dataset_id = models.UUIDField()
    user_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pipeline_id


class Notifications(models.Model):
    message = models.TextField()
    # description = models.TextField()
    # state = models.IntegerField()
    # pipeline_id = models.UUIDField()
    # dataset_id = models.UUIDField()
    # user_id = models.UUIDField()

    # def __str__(self):
    #     return self.pipeline_id
