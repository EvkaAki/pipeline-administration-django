from django.http import JsonResponse
from app.models import RunRequest
import app.views
from django.shortcuts import render, redirect
from app.forms import AddRunRequestForm
from django.core.paginator import Paginator
from app.forms import AddRunRequestForm, AddDatasetRequestForm


def researcher_view(request):
    errors = ''
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
        if request.POST.get('form_id') == 'add_run_request':
            errors = add_run_request(request)
        elif request.POST.get('form_id') == 'add_dataset_request':
            errors = add_dataset_request(request)

    return render(request, 'researcher.html',
                  {'pipelines': pipelines.pipelines, 'errors': errors, 'namespace': namespace,
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
        run_request.save()
    else:
        errors = run_request_form.errors
    return errors

    return render(request, 'researcher.html',
                  {'pipelines': pipelines.pipelines,
                   'errors': errors,
                   'namespace': namespace,
                   'my_requests': my_requests,
                   'pagination_range': range(1, my_requests.paginator.num_pages + 1)})

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
    for version in pipeline_versions.versions:
        versions[version.id] = version.name

    return JsonResponse(versions)
