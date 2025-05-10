from django.http import JsonResponse
from app.models import RunRequest
import app.views
from django.shortcuts import render, redirect
from app.forms import AddRunRequestForm
from django.core.paginator import Paginator
from app.forms import AddRunRequestForm, AddDatasetRequestForm
import json


def researcher_view(request):
    debugdata = ''
    errors = {'run': '', 'dataset': ''}
    client = app.views.get_client()

    namespace = client.get_user_namespace()
    if namespace == 'admin':
        return redirect("/run-requests/admin/administrator/requests")

    pipelines = client.list_pipelines()
    datasets_available = app.views.fetch_available_datasets(app.views.get_token_from_request(request))
    datasets_requestable = app.views.fetch_requestable_datasets(app.views.get_token_from_request(request))
    user_email_json = app.views.get_kubeflow_user(request)
    user_email = user_email_json.get('user', 'anonymous@gmail.com')
    my_requests = RunRequest.objects.filter(user_email=user_email).order_by('-updated_at')
    paginator = Paginator(my_requests, 5)
    page_number = request.GET.get("page")
    my_requests = paginator.get_page(page_number)

    if request.method == 'POST':
        form_id = request.POST.get('form_id')
        if form_id == 'add_run_request':
            errors['run'] = add_run_request(request)
        elif form_id == 'add_dataset_request':
            errors['dataset'] = add_dataset_request(request)

    return render(request, 'researcher.html',
                  {'debugdata': debugdata, 'pipelines': pipelines.pipelines, 'errors': errors, 'namespace': namespace,
                   'datasets_available': datasets_available, 'datasets_requestable': datasets_requestable,
                   'my_requests': my_requests, 'pagination_range': range(1, my_requests.paginator.num_pages + 1)})


def add_run_request(request):
    errors = ''
    run_request_form = AddRunRequestForm(request.POST)
    if run_request_form.is_valid():
        user_data = app.views.get_kubeflow_user(request)
        run_request = run_request_form.save(commit=False)
        run_request.user_email = user_data.get('user', 'anonymous@gmail.com')
        run_request.state = 0

        pipeline_params = {}
        for key in request.POST:
            if key.startswith('pipeline_papams['):
                param_name = key[len('pipeline_papams['):-1]
                pipeline_params[param_name] = request.POST[key]
        run_request.pipeline_params = pipeline_params

        run_request.save()
    else:
        errors = run_request_form.errors

    return errors

def add_dataset_request(request):
    errors = ''
    dataset_request_form = AddDatasetRequestForm(request.POST)
    if dataset_request_form.is_valid():
        user_data = app.views.get_kubeflow_user(request)
        dataset_request = dataset_request_form.save(commit=False)
        dataset_request.user_email = user_data.get('user', 'anonymous@gmail.com')
        dataset_request.state = 0
        dataset_request.save()
    else:
        errors = dataset_request_form.errors
    return errors


def get_pipeline_versions_to_ajax(request):
    pipeline_versions = app.views.get_pipeline_versions_by_id(request)

    versions = {}
    for version in pipeline_versions.pipeline_versions:
        versions[version.pipeline_version_id] = version.display_name

    return JsonResponse(versions)

def get_pipeline_version_params_ajax(request):
    pipeline_id = request.GET.get('pipeline_id')
    pipeline_version_id = request.GET.get('version_id')

    if not pipeline_id or not pipeline_version_id:
        return JsonResponse({'error': 'Pipeline ID and Version ID are required.'}, status=400)

    pipeline_version = app.views.get_pipeline_version(pipeline_id, pipeline_version_id)

    try:
        param_defs = pipeline_version.pipeline_spec['root']['inputDefinitions']['parameters']

    except KeyError:
        return JsonResponse({'error': 'Missing input parameters in pipeline spec.'}, status=500)

    parameters = [
        {
            "name": name,
            "type": details.get("parameterType", "UNKNOWN")
        }
        for name, details in param_defs.items()
    ]

    return JsonResponse(parameters, safe=False)


#     return JsonResponse({
#         'pipeline_id': pipeline_id,
#         'version_id': pipeline_version_id
#     })
