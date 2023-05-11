from django.shortcuts import render
from app.models import RunRequest
import os
import kfp


def get_client():
    credentials = kfp.auth.ServiceAccountTokenVolumeCredentials()

    return kfp.Client(host=os.environ.get("PIPELINE_URL"), credentials=credentials)


def admin_view(request):
    kfp_client = get_client()
    namespace = kfp_client.get_user_namespace()
    if os.environ.get("DEV_MODE") == 'True':
        namespace = 'researcher-nedeliakova'
    run_requests = RunRequest.objects.all()

    return render(request, 'admin.html', {'namespace': str(namespace), 'run_requests': run_requests})


def request_detail(request, id):
    return render(request, 'admin_request_detail.html')


def approve_run_request(request_id):
    run_request = request_id