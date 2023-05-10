from django.shortcuts import render, redirect
from .models import RunRequest
from .forms import AddRunRequestForm
import kfp
import os


def researcher_view(request):
    credentials = kfp.auth.ServiceAccountTokenVolumeCredentials()
    client = kfp.Client(host=os.environ.get("PIPELINE_URL"), credentials=credentials)
    namespace = client.get_user_namespace()
    if namespace == 'admin':
        return redirect("/run-requests/admin/administrator")
    pipelines = client.list_pipelines()

    return render(request, 'researcher.html', {'pipelines': pipelines.pipelines})


def admin_view(request):
    credentials = kfp.auth.ServiceAccountTokenVolumeCredentials(path=None)
    client = kfp.Client(host=os.environ.get("PIPELINE_URL"), credentials=credentials)
    namespace = client.get_user_namespace()
    run_requests = RunRequest.objects.all()

    return render(request, 'admin.html', {'run_requests': run_requests})


def add_run_request(request):
    if request.method == 'POST':
        form = AddRunRequestForm(request.POST)
        if form.is_valid():
            run_request = form.save(commit=False)
            run_request.user_id = 'a'
            run_request.state = 'b'

            return redirect('/run-requests/admin/administrator')
    else:
        form = AddRunRequestForm()

    return render(request, 'add_run_request.html', {'form': form})
