import os
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CVScore, CandidateCV, JobPost
from .serializers import CVScoreSerializer, CandidateCVSerializer, JobPostSerializer
from .utlils import extract_text_from_file, extract_job_info_with_deepseek, score_cv_against_job

class JobPostUploadView(APIView):
    permission_classes = []  

    def post(self, request):
        serializer = JobPostSerializer(data=request.data)
        if serializer.is_valid():
            job_post = serializer.save() 
            return Response(JobPostSerializer(job_post).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
class CandidateCVUploadView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = CandidateCVSerializer(data=request.data)
        
        if serializer.is_valid():
            cv = serializer.save()
            text = extract_text_from_file(cv.file.path)
            cv.extracted_text = text
            extracted = extract_job_info_with_deepseek(text)
            if isinstance(extracted, list):
                extracted = {item["field"]: item["value"] for item in extracted}

            cv.skills = extracted.get("skills", [])
            cv.education_levels = extracted.get("education_levels", [])
            cv.experience = extracted.get("experience", "")
            cv.tools = extracted.get("tools", [])
            cv.save()  
            score, matched, missing = score_cv_against_job(cv, cv.job_post)
            CVScore.objects.create(
                cv=cv,
                score=score,
                matched_keywords=matched,
                missing_keywords=missing,
            )

            return Response(CandidateCVSerializer(cv).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class CVScoreListView(APIView):
    permission_classes = []

    def get(self, request):
        job_id = request.query_params.get('job_id', None)

        if not job_id:
            return Response({"detail": "job_id parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        cv_scores = CVScore.objects.filter(
            cv__job_post_id=job_id, 
            score__gte=70
        ).select_related('cv').order_by('-score')

        if not cv_scores.exists():
            return Response({"detail": "No CV scores found for this job."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CVScoreSerializer(cv_scores, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
