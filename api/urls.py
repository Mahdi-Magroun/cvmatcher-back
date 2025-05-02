from django.urls import path
from .views import CVScoreListView, CandidateCVUploadView, JobPostUploadView

urlpatterns = [
    path('job-posts/', JobPostUploadView.as_view(), name='jobpost-upload'),
    path('cv-submit/', CandidateCVUploadView.as_view(), name='cv-upload'),
    path('cv-scores/', CVScoreListView.as_view(), name='cv-scores'),

]
