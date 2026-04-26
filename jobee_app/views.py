from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .models import JobPosting, GraduateProfile, AdminProfile, AdminInvitationToken, generate_id

# --- 1. LANDING & SELECTION ---
def index(request):
    return render(request, 'index.html')

def selection(request):
    if request.method == "POST":
        user_type = request.POST.get('user_type')
        if user_type == 'admin':
            token = request.POST.get('admin_token')
            if not token:
                return render(request, 'selection.html', {'error': 'Admin token is required'})
            try:
                invitation = AdminInvitationToken.objects.get(token=token, used=False)
                # Check if token has expired (optional)
                if invitation.expires_at and invitation.expires_at < timezone.now():
                    return render(request, 'selection.html', {'error': 'Token has expired'})
                return redirect(f'/admin-signup/?token={token}')
            except AdminInvitationToken.DoesNotExist:
                return render(request, 'selection.html', {'error': 'Invalid or used token'})
        elif user_type == 'graduate':
            return redirect('grad_signup')
    return render(request, 'selection.html')

# --- 2. ADMIN SIDE ---
def admin_signup(request):
    token = request.GET.get('token') or request.POST.get('token')
    if not token:
        return redirect('selection')  # No token, redirect back
    
    try:
        invitation = AdminInvitationToken.objects.get(token=token, used=False)
        if invitation.expires_at and invitation.expires_at < timezone.now():
            return render(request, 'selection.html', {'error': 'Token has expired'})
    except AdminInvitationToken.DoesNotExist:
        return render(request, 'selection.html', {'error': 'Invalid token'})
    
    if request.method == "POST":
        data = request.POST
        if data['password'] != data['confirmPassword']:
            return render(request, 'admin_signup.html', {'error': 'Passwords do not match', 'data': data, 'token': token})
        
        # Check if email already exists
        if User.objects.filter(username=data['email']).exists():
            return render(request, 'admin_signup.html', {'error': 'An account with this email already exists. Please use a different email.', 'data': data, 'token': token})
        
        # Create the Admin User
        user = User.objects.create_user(
            username=data['email'],  # Use email as username for consistency
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        AdminProfile.objects.create(
            user=user, 
            admin_id=generate_id(), 
            name=data['username'],
            fullname=f"{data['first_name']} {data['last_name']}",
            email=data['email'],
            password=user.password,  # Store the hashed password
            username=data['username']
        )
        
        # Get the created admin profile
        admin_profile = AdminProfile.objects.get(user=user)
        
        # Mark token as used
        invitation.used = True
        invitation.save()
        
        # Don't auto-login, redirect to success page
        return redirect(f'/registration-success/?type=admin&id={admin_profile.admin_id}')
    return render(request, 'admin_signup.html', {'token': token})

def admin_login(request):
    if request.method == "POST":
        admin_id = request.POST.get('admin_id')
        pw = request.POST.get('password')
        if not admin_id or not pw:
            return render(request, 'admin_login.html', {'error': 'Please fill in all fields'})
        try:
            admin_profile = AdminProfile.objects.get(admin_id=admin_id)
            user = authenticate(request, username=admin_profile.user.username, password=pw)
            if user is not None:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                return render(request, 'admin_login.html', {'error': 'Invalid Credentials'})
        except AdminProfile.DoesNotExist:
            return render(request, 'admin_login.html', {'error': 'Invalid Admin ID'})
    return render(request, 'admin_login.html')

def admin_dashboard(request):
    jobs = JobPosting.objects.all().order_by('-date_posted')
    if request.method == "POST":
        JobPosting.objects.create(
            title=request.POST['title'],
            company=request.POST['company'],
            location=request.POST['location'],
            setup=request.POST['setup'],
            description=request.POST['desc'],
            url=request.POST['url']
        )
        return redirect('admin_dashboard')
    return render(request, 'admin_dashboard.html', {'jobs': jobs, 'user_id': request.user.adminprofile.admin_id})

def delete_job(request, job_id):
    job = get_object_or_404(JobPosting, job_id=job_id)
    job.delete()
    return redirect('admin_dashboard')

def registration_success(request):
    user_type = request.GET.get('type')
    user_id = request.GET.get('id')
    
    if user_type == 'admin':
        login_url = 'admin_login'
    elif user_type == 'graduate':
        login_url = 'grad_login'
    else:
        return redirect('index')
    
    return render(request, 'registration_success.html', {
        'user_type': user_type,
        'user_id': user_id,
        'login_url': login_url
    })

def generate_admin_token(request):
    if request.method == "POST":
        token = AdminInvitationToken(created_by=request.user.adminprofile)
        token.generate_token()
        token.save()
        return render(request, 'admin_dashboard.html', {
            'jobs': JobPosting.objects.all().order_by('-date_posted'),
            'user_id': request.user.adminprofile.admin_id,
            'generated_token': token.token,
            'success': 'Admin invitation token generated successfully!'
        })
    return redirect('admin_dashboard')

# --- 3. GRADUATE SIDE ---
def grad_signup(request):
    if request.method == "POST":
        data = request.POST
        # Check password length as per your original requirement
        if len(data['password']) < 12:
            return render(request, 'grad_signup.html', {'error': 'Password must be at least 12 characters.', 'data': data})
        
        # Check if email already exists
        if User.objects.filter(username=data['email']).exists():
            return render(request, 'grad_signup.html', {'error': 'An account with this email already exists. Please use a different email.', 'data': data})
        
        # Create User & Profile
        user = User.objects.create_user(
            username=data['email'], 
            email=data['email'], 
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        GraduateProfile.objects.create(
            user=user,
            fullname=f"{data['first_name']} {data['last_name']}",
            email=data['email'],
            password=user.password,  # Store the hashed password
            address=data['address'], 
            dob=data['dob']
        )
        
        # Get the created profile to access the grad_id
        grad_profile = GraduateProfile.objects.get(user=user)
        
        # Don't auto-login, redirect to success page
        return redirect(f'/registration-success/?type=graduate&id={grad_profile.grad_id}')
    return render(request, 'grad_signup.html')

def grad_login(request):
    if request.method == "POST":
        grad_id = request.POST.get('grad_id')
        pw = request.POST.get('password')
        if not grad_id or not pw:
            return render(request, 'grad_login.html', {'error': 'Please fill in all fields'})
        try:
            grad_profile = GraduateProfile.objects.get(grad_id=grad_id)
            user = authenticate(request, username=grad_profile.user.username, password=pw)
            if user is not None:
                login(request, user)
                return redirect('grad_dashboard')
            else:
                return render(request, 'grad_login.html', {'error': 'Invalid Credentials'})
        except GraduateProfile.DoesNotExist:
            return render(request, 'grad_login.html', {'error': 'Invalid Graduate ID'})
    return render(request, 'grad_login.html')

def grad_dashboard(request):
    # Graduates see all available jobs
    jobs = JobPosting.objects.all().order_by('-date_posted')
    return render(request, 'grad_dashboard.html', {'jobs': jobs, 'user_id': request.user.graduateprofile.grad_id})

# --- 4. SHARED ---
def handle_logout(request):
    logout(request)
    return redirect('index')