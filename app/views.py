from django.shortcuts import render, redirect
from .models import RunRequest
from .forms import AddRunRequestForm
from kubernetes import client, config
import kfp
import requests
import os


def get_client():
    credentials = kfp.auth.ServiceAccountTokenVolumeCredentials()

    return kfp.Client(host=os.environ.get("PIPELINE_URL"), credentials=credentials)


def researcher_view(request):
    errors = ''
    r = requests.get(url='http://dp.host.haus/api/workgroup/env-info')

    client = get_client()

    namespace = client.get_user_namespace()
    if namespace == 'admin':
        return redirect("/run-requests/admin/administrator")
    pipelines = client.list_pipelines()

    if request.method == 'POST':
        run_request_form = AddRunRequestForm(request.POST)
        # print('parsing form', run_request_form.is_valid())
        # print(run_request_form.errors)
        if run_request_form.is_valid():
            run_request = run_request_form.save(commit=False)
            run_request.user_id = 'eed9e625-1d4c-483a-dd8f-2d6b58e0a3ed'
            run_request.state = 0
            run_request.save()
        else:
            errors = run_request_form.errors

    return render(request, 'researcher.html', {'pipelines': pipelines.pipelines, 'r': r, 'errors': errors})


def admin_view(request):
    bombom = get_client()
    haha = bombom.get_user_namespace()

    run_requests = RunRequest.objects.all()
    return render(request, 'admin.html', {'haha': haha, 'run_requests': run_requests})


def approve_run_request(request_id):
    run_request = request_id
