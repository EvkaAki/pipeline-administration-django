from django.shortcuts import render

import app.views
from app.models import RunRequest
import os
import json
from django.utils import timezone


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