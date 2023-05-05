from django.shortcuts import render
import kfp


def homePageView(request):
    credentials = kfp.auth.ServiceAccountTokenVolumeCredentials(path=None)
    # client = kfp.Client(host="http://localhost:1234", credentials=credentials)
    client = kfp.Client(host="http://ml-pipeline.kubeflow.svc.cluster.local:8888", credentials=credentials)
    # namespace = client.get_user_namespace()
    pipelines = client.list_pipelines()

    return render(request, 'hello.html', {'pipelines': pipelines.pipelines})
