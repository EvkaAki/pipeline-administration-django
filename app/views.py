from django.shortcuts import redirect
from kubernetes import client, config
from urllib.parse import urlencode
import kfp
import requests
import os
import json
import boto3
from botocore.client import Config
from django.http import StreamingHttpResponse, Http404
from app.models import RunRequest, DatasetRequest
from pipeline_administration_django.settings import DATAPROVIDER_API_ENDPOINT



from django.http import Http404, StreamingHttpResponse

def download_artefact_view(request):
    run_request_id = request.GET.get('run_request_id')
    if not run_request_id:
        raise Http404("Run ID not provided")

    run_request = RunRequest.objects.filter(pk=run_request_id).first()
    if not run_request or not run_request.result:
        raise Http404("Run request not found")

    user_email_json = get_kubeflow_user(request)
    user_email = user_email_json.get('user', 'anonymous@gmail.com')

    if run_request.user_email != user_email and user_email != 'admin':
        raise Http404("You do not have permission to access this artefact")

#     body = f"{run_request.result} \n {run_request.run_id}"
#     response = StreamingHttpResponse(body, content_type='text/plain')
#     response['Content-Disposition'] = f'attachment; filename="result.txt"'
#     return response
#
    body = stream_output_artefact(run_request)
    response = StreamingHttpResponse(body, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="output_artefact_{run_request_id}.signed.zip"'
    return response


def get_client():
#     credentials = kfp.auth.ServiceAccountTokenVolumeCredentials()
    return kfp.Client(host=os.environ.get("PIPELINE_URL"))

def get_admin_client():
    with open(os.environ['KF_PIPELINES_SA_TOKEN_PATH'], "r") as f:
        token = f.read()

    return kfp.Client(host=os.environ.get("PIPELINE_URL"), client_id="admin", existing_token=token)


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

def get_pipeline_version(pipeline_id, version_id):
    client = get_client()
    version = client.get_pipeline_version(pipeline_id, version_id)
    return version

def get_first_pipeline_version(pipeline_id):
    pipeline_id = str(pipeline_id)
    client = get_admin_client()
    versions = client.list_pipeline_versions(pipeline_id)
    if not versions.pipeline_versions:
        raise ValueError("No versions found for pipeline")
    return versions.pipeline_versions[0]


def get_token_from_request(request):
    return request.COOKIES.get('authservice_session')

def get_kubeflow_user(request):
    auth_service_session = get_token_from_request(request)
    cookies = {'authservice_session': auth_service_session}
    response = requests.get(url='https://kubeflowthesis.com/api/workgroup/env-info', cookies=cookies)

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            print('Decoding JSON has failed')
    else:
        print(f'Request failed with status code {response.status_code}')

    return {}


def fetch_dataset_by_id(token, dataset_id):
    url = DATAPROVIDER_API_ENDPOINT + "/user/dataset/get"
    headers = {'Content-Type': 'application/json'}
    data = {'token': token, 'dataset_id': str(dataset_id)}
    response = requests.get(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        dataset = response.json()
        return dataset
    else:
        return None

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


def stream_full_dataset(token, dataset_id):
    url = f"{DATAPROVIDER_API_ENDPOINT}/stream/full"
    params = {
        "dataset_id": dataset_id,
        "token": token
    }
    response = requests.get(url, params=params, stream=True)
    if response.status_code != 200:
        raise Exception(f"Failed to stream dataset: {response.status_code} {response.text}")
    return response.iter_lines(decode_unicode=True)

def get_stream_full_dataset_url(token, dataset_id):
    base_url = f"{DATAPROVIDER_API_ENDPOINT}/stream/full"
    query = urlencode({
        "dataset_id": dataset_id,
        "token": token
    })
    return f"{base_url}?{query}"

def stream_output_artefact(run_request):
    if not run_request.result or run_request.result == 'None':
        raise ValueError("Run request does not have a result")

    s3 = boto3.client(
        's3',
        endpoint_url='http://minio-service.kubeflow.svc.cluster.local:9000',
        aws_access_key_id=os.getenv('MINIO_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('MINIO_SECRET_KEY'),
        config=Config(signature_version='s3v4', s3={'addressing_style': 'path'}),
        region_name='us-east-1'
    )

    bucket = 'artifacts'
    response = s3.get_object(Bucket=bucket, Key=run_request.result)
    return response['Body']


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
