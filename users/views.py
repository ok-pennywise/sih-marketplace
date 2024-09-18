from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from users.forms import UserRegistrationForm
from users.models import User


def register_user(request):
    form = UserRegistrationForm()
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserRegistrationForm()

    return render(request, "users/registration.html", {"form": form})


@login_required
def dashboard(request):
    if request.user.user_type == User.FARMER:
        return render(request, "users/farmer_dashboard.html", {"user": request.user})
    elif request.user.user_type == User.BUYER:
        return render(request, "users/buyer_dashboard.html", {"user": request.user})
    else:
        return render(request, template_name="users/login.html")
