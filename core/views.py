import random
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.http.response import JsonResponse
from django.conf import settings
from openai import OpenAI
import core.prompt as Prompt
import json

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


def request_ai_api(request):
    prompt = Prompt.word

    client = OpenAI(api_key=settings.AI_API_KEY)

    #APIを使ってリクエストを投げる
    response = client.responses.create(
        model="gpt-5-nano",
        input=prompt,
        store=True
    )

    data = json.loads(response.output_text)
    return JsonResponse(data)



    # client = OpenAI(api_key=settings.AI_API_KEY)

    # #APIを使ってリクエストを投げる
    # response = client.responses.create(
    #     model="gpt-5-nano",
    #     input="おはよう！元気？",
    #     store=True
    # )

    # print(response.output_text)

    # json = {"data1": "hoge", "data2": "fuga", "response": response.output_text}
    # return JsonResponse(json)
