import random
import os
from datetime import timedelta, datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.http.response import JsonResponse
from django.conf import settings
from openai import OpenAI
import core.prompt as Prompt
import json
from core.models import Task, Plan
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

# Create your views here.
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

    # # 例: まずは plan を作る(本来であればユーザ画面のフォームからの入力情報を受け取る想定)
    # user = User.objects.get(id=1) # 仮ユーザーとしてID=1のユーザーを使用（本来はログインユーザー）
    # plan = Plan.objects.create(
    #     user=user,
    #     plan_name="基礎情報技術者試験",
    #     plan_start_date=data["tasks"][0]["task_start_date"],
    #     plan_end_date=data["tasks"][-1]["task_end_date"],
    # )

    # tasks = []

    # # tasks をDBに保存
    # for task_item in data["tasks"]:
    #     task = Task(
    #         plan=plan,
    #         genre=task_item.get("genre", ""),
    #         title=task_item.get("title", ""),
    #         is_active=False,
    #         task_start_date=task_item.get("task_start_date"),
    #         task_end_date=task_item.get("task_end_date"),
    #     )
    #     tasks.append(task)
    # Task.objects.bulk_create(tasks)

    return JsonResponse(data)

    # Task.objects.create(
    #     plan=plan,
    #     genre=task_item.get("genre", ""),
    #     title=task_item.get("title", ""),
    #     is_active=False,
    #     task_start_date=task_item.get("start"),
    #     task_end_date=task_item.get("end"),
    # )



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


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        password_confirm = request.POST.get("password_confirm", "").strip()

        if not username or not email or not password:
            messages.error(request, "すべての項目を入力してください")
        elif password != password_confirm:
            messages.error(request, "パスワードと確認用パスワードが一致しません。")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "そのユーザー名はすでに使われています")
        else :
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            login(request, user)
            return redirect("hoge") 

    return render(request, "auth/signup.html")


def signin(request):
    # すでにログイン済みのユーザーはリダイレクト
    if request.user.is_authenticated:
        return redirect("hoge")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        print(email, password)

        # authenticateメソッドはemailで認証できないのでカスタムメソッド_authenticate_with_emailで対応
        # user = authenticate(request, email=email, password=password)  
        user = _authenticate_with_email(email, password)

        print(user)

        if user is not None:
            login(request, user)
            return redirect("hoge")
        else:
            messages.error(request, "ユーザー名またはパスワードが違います。")

    return render(request, "auth/login.html")


def signout(request):
    logout(request)
    return redirect("signin")


def _authenticate_with_email(email, password):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None
    
    if user.check_password(password):
        return user
    return None


def home(request):
    plans = Plan.objects.filter(user_id=1)
    
    return render(request, 'home.html', {
        'plans': plans,
    })


def select(request):
    # POSTで選択プランデータが送られたらセッションに保存してリダイレクト
    if request.method == 'POST':
        selected_json = request.POST.get('selected_plan_json')
        if selected_json:
            try:
                selected_plan = json.loads(selected_json)
                request.session['selected_plan'] = selected_plan
            except json.JSONDecodeError:
                request.session['selected_plan'] = None
        return redirect('createploan/home')

    sample_path = os.path.join(settings.BASE_DIR, 'response_sample.json')
    plans = []
    try:
        with open(sample_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tasks = data.get('tasks', [])

            # 3つのプランにタスクを分割（連続するチャンク）
            num_plans = 3
            total = len(tasks)
            if total == 0:
                plans = []
            else:
                chunk_size = (total + num_plans - 1) // num_plans
                for i in range(num_plans):
                    chunk = tasks[i * chunk_size:(i + 1) * chunk_size]
                    if not chunk:
                        continue
                    plan = {
                        'id': str(i + 1),
                        'planname': f'プラン {i+1}',
                        'tasks': [],
                    }
                    for t in chunk:
                        start = t.get('task_start_date') or t.get('start')
                        end = t.get('task_end_date') or t.get('end')
                        days = ''
                        try:
                            if start and end:
                                d1 = datetime.strptime(start, '%Y-%m-%d').date()
                                d2 = datetime.strptime(end, '%Y-%m-%d').date()
                                days = (d2 - d1).days + 1
                        except Exception:
                            days = ''

                        plan['tasks'].append({
                            'id': t.get('id'),
                            'name': t.get('title') or t.get('name'),
                            'start_date': start,
                            'end_date': end,
                            'days': days,
                        })

                    plan['json_data'] = json.dumps(plan, ensure_ascii=False)
                    plans.append(plan)
    except FileNotFoundError:
        plans = []

    return render(request, 'createplan/select.html', {
        'plans': plans,
    })