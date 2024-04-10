from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import messages
from E_learn.EmailBackEnd import EmailBackEnd
from django.contrib.auth import authenticate, login, logout


# This function is responsible to register new user
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")

        # check email
        if User.objects.filter(email=email).exists():
            messages.warning(request, "Email are already exixt")
            return redirect("register")

        # check username
        if User.objects.filter(username=username).exists():
            messages.warning(request, "Username already exists!")
            return redirect("register")

        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        return redirect("login")

    return render(request, "registration/register.html")


# This function is responsible for login to existing user
def do_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = EmailBackEnd.authenticate(request, username=email, password=password)
        if user != None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Email and Password Are Invalid !")
            return redirect("login")


# This function will show the page which will contain the profile edit functionality
def profile(request):
    return render(request, "registration/profile.html")


def profile_update(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        user_id = request.user.id

        user = User.objects.get(id=user_id)
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email

        if password != None and password != "":
            user.set_password(password)
    user.save()
    messages.success(request, "Profile Are Successfully Updated. ")
    return redirect("profile")
