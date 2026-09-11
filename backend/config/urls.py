from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def home(request):
    return JsonResponse({
        "status": "success",
        "message": "Reconciliation API is running successfully",
        "endpoints": {
            "organizations": "/api/organizations/",
            "disagreements": "/api/disagreements/?org_id=ORG-A",
        }
    })


urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("api/", include("reconciliation.urls")),
]