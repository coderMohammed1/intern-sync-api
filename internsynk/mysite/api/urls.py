from django.urls import path
from .views import apply, is_authed, post_get_jobs, regster_login, edit_jobs, get_applications, pdf_extract, update_application_status,search_sort,counts
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

@csrf_exempt
def test_connection(request):
    return JsonResponse({'status': 'ok', 'message': 'Backend is working'})

urlpatterns = [
    path("test", test_connection, name="test-connection"),

    # User endpoints
    path("users", regster_login.Regester.as_view(), name="create-user"),  # POST
    path("users/login", regster_login.Login.as_view(), name="login-user"),  # POST
    path("users/is-authed", is_authed.is_authed.as_view(), name="is-authed"),  # GET

    # Job endpoints
    path("jobs", post_get_jobs.Get_jobs.as_view(), name="list-jobs"),  # GET
    path("jobs/post", post_get_jobs.Post_job.as_view(), name="create-job"),  # POST
    path("jobs/<int:jid>", edit_jobs.Edit.as_view(), name="edit-job"),  # PUT
    path("jobs/<int:jid>/apply", apply.Applly.as_view(), name="apply-to-job"),  # POST
    path("jobs/count", counts.Counts.as_view(), name="count-jobs"),  # GET
    path("jobs/applicants/count", counts.Applicants_number.as_view(), name="count-applicants"),  # GET
    path("jobs/<int:apid>/applications", get_applications.Aplicants.as_view(), name="list-job-applicants"),  # GET
    path("jobs/search", search_sort.SearchAndSort.as_view(), name="search-sort-jobs"),  # GET with query params
    path("students/applications", get_applications.StudentApplications.as_view(), name="list-student-applications"),  # GET
    path("applications/<int:application_id>/status", update_application_status.UpdateApplicationStatus.as_view(), name="update-application-status"),  # PUT
    path("applications/<int:apId>/cv", get_applications.CV.as_view(), name="get-cv"),  # GET
    path("students/applications/count/<str:stat>", counts.StudentApplications.as_view(), name="count-student-applications"),  # GET
    
    # PDF extract endpoints
    path("applications/<int:application_id>/extract-pdf", pdf_extract.PDFTextExtract.as_view(), name="extract-pdf-text-get"),  # GET
    path("applications/extract-pdf", pdf_extract.PDFTextExtract.as_view(), name="extract-pdf-text-post"),  # POST
]




schema_view = get_schema_view(
    openapi.Info(
        title="internsynk",
        default_version='v1',
        description="API documentation for internsynk",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]