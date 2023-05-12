from django.shortcuts import render

import app.views
from app.models import RunRequest, DatasetRequest
import os
import json
from django.utils import timezone


def admin_view(request):
    kfp_client = app.views.get_client()
    namespace = kfp_client.get_user_namespace()
    if os.environ.get("DEV_MODE") == 'True':
        namespace = 'researcher-nedeliakova'
    run_requests = RunRequest.objects.all()
    dataset_requests = DatasetRequest.objects.all()

    return render(request, 'admin.html',
                  {'namespace': str(namespace), 'run_requests': run_requests, 'dataset_requests': dataset_requests})


def dataset_request_detail(request, request_id):
    messages = {'message': ''}
    dataset_request = DatasetRequest.objects.get(pk=request_id)
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
                  {'dataset_request': dataset_request, 'messages': messages})


def request_detail(request, request_id):
    kfp_client = app.views.get_client()

    run_request = RunRequest.objects.get(pk=request_id)
    namespace = kfp_client.get_user_namespace()
    pipeline = kfp_client.get_pipeline(str(run_request.pipeline_id))
    alert = ''
    parameters_dict = {}

    experiment_name = namespace + '_' + str(hash(run_request.user_email))

    if request.method == 'POST':
        try:
            experiment = kfp_client.get_experiment(experiment_name=experiment_name)
        except ValueError:
            experiment = kfp_client.create_experiment(
                name=experiment_name,
                namespace=namespace,
                description="Experiment for user run_request.user_email"
            )
        parameters = request.POST.getlist('parameters[]')

        for parameter, key in parameters:
            parameters_dict[key] = parameter
            # TODO get the custom parameters from the request and put it int he params

        run = kfp_client.run_pipeline(
            job_name="Run_for_user_" + run_request.user_email + "_" + str(timezone.now()),
            experiment_id=experiment.id,
            pipeline_id=pipeline.id,
            version_id=run_request.pipeline_version_id,
            params=parameters_dict
        )
        if run is not None:
            run_request.state = 2
            run_request.save()
            alert = 'real happines'
        else:
            alert = 'saddness'

    return render(request, 'admin_request_detail.html',
                  {'namespace': namespace,
                   'run_request': run_request,
                   'pipeline': pipeline,
                   'parameters': pipeline.parameters,
                   'alert': alert})


def approve_run_request(request_id):
    run_request = request_id
