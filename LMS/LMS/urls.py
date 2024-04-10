"""
URL configuration for LMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from . import views, user_login

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("404", views.page_not_found, name="404"),
    path("base", views.base, name="base"),
    path("", views.home, name="home"),
    path("Courses", views.single_course, name="singleCourse"),
    path("Courses/filter-data", views.filter_data, name="filter-data"),
    path("Course/<slug:slug>", views.course_details, name="course_detail"),
    path("search", views.search_course, name="search_course"),
    path("contect_us", views.contect_us, name="contect_us"),
    path("about_us", views.about_us, name="about_us"),
    # This path is for login module
    path("accounts/", include("django.contrib.auth.urls")),
    # This path is for register module
    path("accounts/register", user_login.register, name="register"),
    # This path is for login
    path("doLogin", user_login.do_login, name="doLogin"),
    # this path is for profile edit page
    path("accounts/profile", user_login.profile, name="profile"),
    # this path is for profile UPDATE page
    path("accounts/profile/update", user_login.profile_update, name="profile_update"),
    path("checkout/<slug:slug>", views.checkOut, name="checkout"),
    path("my-course", views.my_course, name="my_course"),
    path("verify_payment", views.verify_payment, name="verify_payment"),
    path("course/watch_course/<slug:slug>", views.watch_course, name="watch_course"),
    path("subscribe", views.subscribe, name="subscribe"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
