from django.shortcuts import render, redirect
from .models import RunRequest
from .forms import AddRunRequestForm
from django.http import JsonResponse
from kubernetes import client, config
import kfp
import requests
import json
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
            run_request.user_email = 'evanedeliakova@gmail.com'
            run_request.state = 0
            run_request.save()
        else:
            errors = run_request_form.errors

    return render(request, 'researcher.html', {'pipelines': pipelines.pipelines, 'errors': errors})


def admin_view(request):
    kfp_client = get_client()
    namespace = kfp_client.get_user_namespace()
    if os.environ.get("DEV_MODE") == 'True':
        namespace = 'researcher-nedeliakova'
    run_requests = RunRequest.objects.all()

    return render(request, 'admin.html', {'namespace': str(namespace), 'run_requests': run_requests})


def get_pipeline_versions(request):
    kfp_client = get_client()
    pipeline_versions = kfp_client.list_pipeline_versions(pipeline_id=request.GET.get('pipeline_id'))

    versions = {}
    for version in pipeline_versions.versions:
        versions[version.id] = version.name

    return JsonResponse(versions)


def approve_run_request(request_id):
    run_request = request_id
