"""
URL configuration for djangopj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from core import views as core_views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    path("hoge/", TemplateView.as_view(template_name='hoge.html'), name="hoge"),
    path("form/", TemplateView.as_view(template_name='createplan/form.html'), name="form"),
    # path("select/", TemplateView.as_view(template_name='select.html'), name="select"),
    path("regenerate/", TemplateView.as_view(template_name='regenerate.html'), name="regenerate"),
    path("home/", core_views.home, name="home"),
    #path("login/", TemplateView.as_view(template_name='login.html'), name="login"),
    #path("signup/", TemplateView.as_view(template_name='signup.html'), name="signup"),
    path("login/", core_views.signin, name="signin"), # loginという命名だとdjangoの予約語loginと被る
    path("signup/", core_views.signup, name="signup"),
    path("logout/", core_views.signout, name="signout"),
    path("select/", core_views.select, name="select"),

    # OpenAI API
    path('request_ai_api/', core_views.request_ai_api, name="request_ai_api"),
]
