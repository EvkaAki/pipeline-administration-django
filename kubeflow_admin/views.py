from django.shortcuts import render

import app.views
from app.models import RunRequest
import os


def admin_view(request):
    kfp_client = app.views.get_client()
    namespace = kfp_client.get_user_namespace()
    if os.environ.get("DEV_MODE") == 'True':
        namespace = 'researcher-nedeliakova'
    run_requests = RunRequest.objects.all()

    return render(request, 'admin.html', {'namespace': str(namespace), 'run_requests': run_requests})


def request_detail(request, request_id):
    kfp_client = app.views.get_client()

    run_request = RunRequest.objects.get(pk=request_id)
    namespace = kfp_client.get_user_namespace()

    pipeline = kfp_client.get_pipeline(str(run_request.pipeline_id))

    return render(request, 'admin_request_detail.html',
                  {'namespace': namespace,
                   'run_request': run_request,
                   'pipeline': pipeline})


def approve_run_request(request_id):
    run_request = request_id