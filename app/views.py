from django.shortcuts import render, redirect
import kfp
import os


def researcher_view(request):
    credentials = kfp.auth.ServiceAccountTokenVolumeCredentials(path=None)
    client = kfp.Client(host=os.environ.get("PIPELINE_URL"), credentials=credentials)
    namespace = client.get_user_namespace()
    if namespace == 'admin':
        return redirect("admin", foo="bar")
    pipelines = client.list_pipelines()
    dev_mode = os.environ.get("DEV_MODE")
    print('here')

    return render(request, 'researcher.html', {'pipelines': pipelines.pipelines, 'bla': dev_mode})


def admin_view(request):
    return render(request, 'hello.html', {})
