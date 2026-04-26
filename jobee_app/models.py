from django.db import models
from django.contrib.auth.models import User
import random

def generate_id():
    return str(random.randint(100000, 999999))

class GraduateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    grad_id = models.CharField(max_length=6, unique=True, default=generate_id)
    fullname = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    password = models.CharField(max_length=128, blank=True)  # Store hashed password
    dob = models.DateField(null=True, blank=True)
    address = models.TextField()

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    admin_id = models.CharField(max_length=6, unique=True, default=generate_id)
    name = models.CharField(max_length=100)
    fullname = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    password = models.CharField(max_length=128, blank=True)  # Store hashed password
    username = models.CharField(max_length=150, blank=True)

class JobPosting(models.Model):
    job_id = models.CharField(max_length=6, unique=True, default=generate_id)
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    setup = models.CharField(max_length=50, choices=[('Online (WFH)','Online (WFH)'),('On field (Face-to-face)','On field (Face-to-face)'),('Hybrid','Hybrid')])
    url = models.URLField()
    date_posted = models.DateTimeField(auto_now_add=True)

class AdminInvitationToken(models.Model):
    token = models.CharField(max_length=10, unique=True)
    created_by = models.ForeignKey(AdminProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)

    def generate_token(self):
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        self.token = ''.join(secrets.choice(alphabet) for _ in range(10))
        return self.token