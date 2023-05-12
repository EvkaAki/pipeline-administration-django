from django.shortcuts import redirect
from kubernetes import client, config
import kfp
import requests
import os
import json

from pipeline_administration_django.settings import DATAPROVIDER_API_ENDPOINT


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


def get_token_from_request(request):
    return request.COOKIES.get('authservice_session')


def get_kubeflow_user(request):
    auth_service_session = get_token_from_request(request)
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


def fetch_available_datasets(token):
    # print(DATAPROVIDER_API_ENDPOINT)
    url = DATAPROVIDER_API_ENDPOINT + "/user/dataset/available"
    headers = {'Content-Type': 'application/json'}
    data = {'token': token}
    response = requests.get(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        datasets = response.json()
        return datasets
    else:
        return None


def fetch_requestable_datasets(token):
    url = DATAPROVIDER_API_ENDPOINT + "/user/dataset/requestable"
    headers = {'Content-Type': 'application/json'}
    data = {'token': token}
    response = requests.get(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        datasets = response.json()
        return datasets
    else:
        return None


def dataset_grant_access(token, dataset_id, user_id):
    url = DATAPROVIDER_API_ENDPOINT + "/access/grant"
    headers = {'Content-Type': 'application/json'}
    data = {'token': token, 'dataset_id': str(dataset_id), 'user_id': user_id}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    # print(response.status_code)
    # print(response)
    if response.status_code in [201, 400, 401]:
        return response.json()
    return {"message": "Something went wrong: " + str(response.status_code)}
