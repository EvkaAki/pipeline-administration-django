from django.shortcuts import redirect
from django.http import JsonResponse
from kubernetes import client, config
import kfp
import requests
import os


def get_client():
    credentials = kfp.auth.ServiceAccountTokenVolumeCredentials()

    return kfp.Client(host=os.environ.get("PIPELINE_URL"), credentials=credentials)


def get_view(request):
    kfp_client = get_client()
    namespace = kfp_client.get_user_namespace()
    if namespace == 'admin':
        return redirect('administrator/requests')
    else:
        return redirect('researcher/requests')


def get_pipeline_versions_by_id(request):
    kfp_client = get_client()

    return kfp_client.list_pipeline_versions(pipeline_id=request.GET.get('pipeline_id'))


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

