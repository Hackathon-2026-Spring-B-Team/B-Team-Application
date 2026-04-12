import random
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # ユーザー作成
            return redirect("login")  # 登録後はログイン画面へ
    else:
        form = UserCreationForm()
    return render(request, "signup.html", {"form": form})