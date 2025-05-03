from django.urls import path
from .views import CVScoreListView, CandidateCVUploadView, JobPostDetailView, JobPostListView, JobPostUploadView

urlpatterns = [
    path('job-posts/', JobPostUploadView.as_view(), name='jobpost-upload'),
    path('cv-submit/', CandidateCVUploadView.as_view(), name='cv-upload'),
    path('cv-scores/', CVScoreListView.as_view(), name='cv-scores'),
    path('jobs/', JobPostListView.as_view(), name='job-list'),
    path('jobs/<int:id>/', JobPostDetailView.as_view(), name='job-detail'),
]
