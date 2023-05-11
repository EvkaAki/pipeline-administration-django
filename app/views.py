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


def get_pipeline_versions(request):
    kfp_client = get_client()
    pipeline_versions = kfp_client.list_pipeline_versions(pipeline_id=request.GET.get('pipeline_id'))

    versions = {}
    for version in pipeline_versions.versions:
        versions[version.id] = version.name

    return JsonResponse(versions)


def get_kubeflow_user(request):
    auth_service_session = request.COOKIES.get('authservice_session')
    cookies = {'authservice_session': auth_service_session}
    response = requests.get(url='http://dp.host.haus/api/workgroup/env-info', cookies=cookies)

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            print('Decoding JSON has failed')
    else:
        print(f'Request failed with status code {response.status_code}')

    return {}

