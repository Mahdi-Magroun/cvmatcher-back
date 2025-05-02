from django.urls import reverse
from rest_framework import serializers
from .models import CVScore, CandidateCV, JobPost
from .utlils import extract_text_from_file, extract_job_info_with_deepseek

class JobPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPost
        fields = '__all__'
        read_only_fields = [
            'uploaded_at',
            'description',
            'skills',
            'education_levels',
            'experience',
            'tools'
        ]

    def create(self, validated_data):
        # Save initial data (file, title)
        job_post = super().create(validated_data)

        # Step 1: Extract plain text from uploaded file (.txt or .pdf)
        text = extract_text_from_file(job_post.file.path)
        job_post.description = text

        # Step 2: Send the text to DeepSeek API to extract structured job data
        extracted = extract_job_info_with_deepseek(text)
            # Convert list of {"field": ..., "value": ...} to dictionary
        if isinstance(extracted, list):
               extracted = {item["field"]: item["value"] for item in extracted}

        job_post.skills = extracted.get('skills', [])
        job_post.education_levels = extracted.get('education_levels', [])
        job_post.experience = extracted.get('experience', "")
        job_post.tools = extracted.get('tools', [])
        job_post.save()
        return job_post


class CandidateCVSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateCV
        fields = '__all__'
        read_only_fields = ['uploaded_at', 'extracted_text', 'skills', 'education_levels', 'experience', 'tools']



class CVScoreSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='cv.candidate_name', read_only=True)
    cv_download_url = serializers.SerializerMethodField()

    class Meta:
        model = CVScore
        fields = ['score', 'cv', 'candidate_name', 'cv_download_url']

    def get_cv_download_url(self, obj):
     request = self.context.get('request')
     if obj.cv and obj.cv.file and request:
         return request.build_absolute_uri(obj.cv.file.url)
     return None