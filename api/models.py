from django.db import models


class JobPost(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='job_descriptions/')
    skills = models.JSONField(default=list, blank=True)        
    education_levels = models.JSONField(default=list, blank=True)  
    experience = models.CharField(max_length=100, blank=True)   
    tools = models.JSONField(default=list, blank=True)   
    def __str__(self):
        return self.title


class CandidateCV(models.Model):
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='cvs')
    candidate_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='candidate_cvs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_text = models.TextField(blank=True) 
    # New extracted fields
    skills = models.JSONField(default=list, blank=True)        
    education_levels = models.JSONField(default=list, blank=True)  
    experience = models.CharField(max_length=100, blank=True)   
    tools = models.JSONField(default=list, blank=True)   
    def __str__(self):
        return f"{self.candidate_name} - {self.job_post.title}"


class CVScore(models.Model):
    cv = models.OneToOneField(CandidateCV, on_delete=models.CASCADE, related_name='score')
    score = models.FloatField()
    matched_keywords = models.TextField(blank=True)  
    missing_keywords = models.TextField(blank=True)  
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Score: {self.score:.2f} for {self.cv}"
