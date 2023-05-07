from django.shortcuts import render
import kfp
import os


def homePageView(request):
    pipeline_url = os.getenv("PIPELINE_URL")
    credentials = kfp.auth.ServiceAccountTokenVolumeCredentials(path=None)
    client = kfp.Client(host=pipeline_url, credentials=credentials)
    # namespace = client.get_user_namespace()
    pipelines = client.list_pipelines()

    return render(request, 'hello.html', {'pipelines': pipelines.pipelines})
