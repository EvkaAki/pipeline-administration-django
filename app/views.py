from django.shortcuts import render, redirect
from .models import RunRequest
import kfp
import os


def researcher_view(request):
    credentials = kfp.auth.ServiceAccountTokenVolumeCredentials(path=os.environ.get("KF_PIPELINES_SA_TOKEN_PATH"))
    client = kfp.Client(host=os.environ.get("PIPELINE_URL"), credentials=credentials)
    namespace = client.get_user_namespace()
    if namespace == 'admin':
        return redirect("/run-requests/admin/administrator")
    pipelines = client.list_pipelines()

    return render(request, 'researcher.html', {'pipelines': pipelines.pipelines})


def admin_view(request):
    credentials = kfp.auth.ServiceAccountTokenVolumeCredentials(path=None)
    client = kfp.Client(host=os.environ.get("PIPELINE_URL"), credentials=credentials)
    namespace = client.get_user_namespace()
    run_requests = RunRequest.objects.all()

    return render(request, 'admin.html', {'run_requests': run_requests})
