from django.contrib import admin
from django.urls import path, include # Make sure 'include' is here!

urlpatterns = [
    path('admin/', admin.site.urls),
    # This line tells Django: "When someone visits the home page, 
    # go look at the URLs inside jobee_app"
    path('', include('jobee_app.urls')), 
]
