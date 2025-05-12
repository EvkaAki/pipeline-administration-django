from django.shortcuts import render
from django.core import serializers
from django.http import StreamingHttpResponse

import app.views
import hashlib
from app.models import RunRequest, DatasetRequest
import os
from django.core.paginator import Paginator
from django.utils import timezone
import time
import json
from kfp import Client

def admin_view(request):
    kfp_client = app.views.get_client()
    namespace = kfp_client.get_user_namespace()
    if os.environ.get("DEV_MODE") == 'True':
        namespace = 'researcher-nedeliakova'

    run_requests = RunRequest.objects.all().order_by('-id')
    dataset_requests = DatasetRequest.objects.all().order_by('-id')

    # Fetch datasets from the API based on dataset_id
    token = app.views.get_token_from_request(request)
    if token:
        dataset_cache = {}

        for dr in dataset_requests:
            if dr.dataset_id not in dataset_cache:
                dataset_cache[dr.dataset_id] = app.views.fetch_dataset_by_id(token, dr.dataset_id)
            dataset = dataset_cache[dr.dataset_id]
            if dataset and 'name' in dataset:
                dr.dataset_name = dataset['name']

        for rr in run_requests:
            if rr.dataset_id not in dataset_cache:
                dataset_cache[rr.dataset_id] = app.views.fetch_dataset_by_id(token, rr.dataset_id)
            dataset = dataset_cache[rr.dataset_id]
            if dataset and 'name' in dataset:
                rr.dataset_name = dataset['name']


#         for dr in dataset_requests:
#             dataset = app.views.fetch_dataset_by_id(token, dr.dataset_id)
#             dataset_name_map[dr.dataset_id] = dataset['name']

    paginator = Paginator(run_requests, 10)
    page_number = request.GET.get("page")
    run_requests = paginator.get_page(page_number)

    return render(request, 'admin.html', {
        'namespace': str(namespace),
        'run_requests': run_requests,
        'dataset_requests': dataset_requests,
        'request_pagination_range': range(1, run_requests.paginator.num_pages + 1)
    })


def dataset_request_detail(request, request_id):
    messages = {'message': ''}
    dataset_request = DatasetRequest.objects.get(pk=request_id)
    kfp_client = app.views.get_admin_client()
    namespace = kfp_client.get_user_namespace()

    if request.method == 'POST':
        decision = request.POST.get('decision')
        if decision == "2":
            token = app.views.get_token_from_request(request)
            messages = app.views.dataset_grant_access(token, dataset_request.dataset_id, dataset_request.user_email)
            # print(messages)
        dataset_request.state = int(decision)
        dataset_request.response_comment = request.POST.get('response_comment')
        dataset_request.save()

    return render(request, 'admin_dataset_request_detail.html',
                  {'dataset_request': dataset_request, 'messages': messages, 'namespace': namespace})


def request_detail(request, request_id):
    token = app.views.get_token_from_request(request)
#     def line_generator():
#         for line in app.views.stream_full_dataset(token, 'fcfda582-9ed5-44db-aec1-cb37e99ce368'):
#             yield line + '\n'
#
#     return StreamingHttpResponse(line_generator(), content_type='text/csv')

    kfp_client = app.views.get_admin_client()
    run_request = RunRequest.objects.get(pk=request_id)
    run_request_serialized = serializers.serialize('json', [run_request])
    namespace = kfp_client.get_user_namespace()
    pipeline = kfp_client.get_pipeline(str(run_request.pipeline_id))
    alert = {'status': 'success', 'message': ''}
    debug = ''
    parameters_dict = {}

    experiment_name = namespace + '_' + str(hashlib.md5(run_request.user_email.encode('utf-8')).hexdigest())
#     debug = 'experiment_name: ' + experiment_name
#     experiment_name = 'admin_7542896038893142685'

    if request.method == 'POST':
        decision = request.POST.get('decision')
        if decision == "deny":
            run_request.state = 1
            run_request.save()
            alert['message'] = 'Run request rejected'
            alert['status'] = 'success'
            return render(request, 'admin_request_detail.html',
                          {'namespace': namespace,
                           'run_request': run_request,
                           'request_pagination_range': range(1, ),
                           'pipeline': pipeline,
                           'debug': debug,
                           'parameters': [],
                           'alert': alert})

        try:
            experiment = kfp_client.get_experiment(experiment_name=experiment_name)
        except ValueError:
            experiment = kfp_client.create_experiment(
                name=experiment_name,
                namespace=namespace,
                description=f"Experiment for user {run_request.user_email}"
            )

        new_pipeline = clone_pipeline_to_admin(run_request.pipeline_id, run_request.pipeline_version_id, run_request.id)
        pipeline_version = app.views.get_first_pipeline_version(pipeline.pipeline_id)

        parameters = dict(run_request.pipeline_params)
        parameters['url'] = app.views.get_stream_full_dataset_url(token, run_request.dataset_id)
        param_defs = pipeline_version.pipeline_spec['root']['inputDefinitions']['parameters']
        parameters = prepare_pipeline_params(parameters, param_defs)

        run = kfp_client.run_pipeline(
            job_name="Run_for_user_" + run_request.user_email + "_" + str(timezone.now()),
            experiment_id=experiment.experiment_id,
            pipeline_id=pipeline.pipeline_id,
            version_id=pipeline_version.pipeline_version_id,
            params=parameters
        )
        if run is not None:
            run_request.state = 2
            run_request.run_id = run.run_id
            run_request.save()
            alert['message'] = 'Run request approved and pipeline started successfully'
            alert['status'] = 'success'
        else:
            alert['status'] = 'error'
            alert.message = 'Failed to start pipeline run'

    return render(request, 'admin_request_detail.html',
                  {'namespace': namespace,
                   'run_request': run_request,
                   'request_pagination_range': range(1, ),
                   'pipeline': pipeline,
                   'debug': debug,
                   'parameters': [],
                   'alert': alert})


def prepare_pipeline_params(parameters, param_defs):
    converted = {}
    for name, value in parameters.items():
        param_type = param_defs.get(name, {}).get('parameterType', 'STRING')

        try:
            if param_type == 'NUMBER_INTEGER':
                converted[name] = int(value)
            elif param_type == 'NUMBER_DOUBLE':
                converted[name] = float(value)
            elif param_type == 'BOOLEAN':
                if isinstance(value, bool):
                    converted[name] = value
                elif str(value).lower() in ['true', '1', 'yes']:
                    converted[name] = True
                elif str(value).lower() in ['false', '0', 'no']:
                    converted[name] = False
                else:
                    raise ValueError(f"Invalid boolean: {value}")
            else:
                converted[name] = str(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid value for parameter '{name}' of type '{param_type}': {value}") from e

    return converted


def clone_pipeline_to_admin(pipeline_id, version_id, run_request_id):
    pipeline_id = str(pipeline_id)
    version_id = str(version_id)
    target_namespace = "admin"
    timestamp = time.strftime("%Y%m%d%H%M%S")
    package_file = f"copied_pipeline_{timestamp}.json"

    client = app.views.get_client()
    version = client.get_pipeline_version(pipeline_id, version_id)
    spec = version.pipeline_spec
    new_name = f"{version.display_name} - Run Request {run_request_id} - {timestamp}"

    with open(package_file, "w") as f:
        json.dump(spec, f)

    admin_client = app.views.get_admin_client()
    new_pipeline = admin_client.upload_pipeline(
        pipeline_package_path=package_file,
        pipeline_name=new_name,
        description=f"Copied from version {version_id}",
        namespace=target_namespace
    )

    os.remove(package_file)
    return new_pipeline

def approve_run_request(request_id):
    run_request = request_id
