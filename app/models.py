from django.db import models


class RunRequest(models.Model):
    message = models.TextField()
    state = models.IntegerField()
    pipeline_id = models.UUIDField()
    pipeline_version_id = models.UUIDField()
    pipeline_version_name = models.TextField()
    pipeline_name = models.TextField()
    dataset_id = models.UUIDField()
    user_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    pipeline_params = models.JSONField(null=True, blank=True)
    run_id = models.UUIDField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)

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


class DatasetRequest(models.Model):
    message = models.TextField()
    response_comment = models.TextField(null=True, blank=True)
    state = models.IntegerField()
    dataset_id = models.UUIDField()
    user_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)