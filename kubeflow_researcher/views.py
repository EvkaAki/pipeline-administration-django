from django.shortcuts import render
import requests
import app.views
from django.shortcuts import render, redirect
from app.forms import AddRunRequestForm


def researcher_view(request):
    errors = ''
    r = requests.get(url='http://dp.host.haus/api/workgroup/env-info')

    client = app.views.get_client()

    namespace = client.get_user_namespace()
    if namespace == 'admin':
        return redirect("/run-requests/admin/administrator/requests")
    pipelines = client.list_pipelines()

    if request.method == 'POST':
        run_request_form = AddRunRequestForm(request.POST)
        if run_request_form.is_valid():
            user_data = app.views.get_kubeflow_user(request)
            run_request = run_request_form.save(commit=False)
            run_request.user_id = 'eed9e625-1d4c-483a-dd8f-2d6b58e0a3ed'
            run_request.user_email = user_data.get('user', 'anonymous@gmail.com')
            run_request.pipeline_name = 'tmp'
            run_request.pipeline_version_name = 'tmp'
            run_request.state = 0
            run_request.save()
        else:
            errors = run_request_form.errors

    return render(request, 'researcher.html',
                  {'pipelines': pipelines.pipelines, 'errors': errors, 'namespace': namespace})