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
from django.core import serializers
from django.db.models import Prefetch, Count, Q

# Create your views here.
def request_ai_api(request):
    # prompt = Prompt.word
    prompt = ""
    plan_name = ""
    plan_date = ""
    daily_available_minutes = ""
    if request.method == "POST" and request.POST.get('regenerate') == None: # 再生成でない場合
        plan_name = request.POST.get("license_name", "").strip()
        request.session['plan_name'] = plan_name 
        plan_date = request.POST.get("test_date", "").strip()
        request.session['plan_date'] = plan_date 
        daily_available_minutes = request.POST.get("study_hours", "").strip()
        request.session['daily_available_minutes'] = daily_available_minutes 
        # prompt_option = request.session.get('prompt_option')
        # request.session['prompt_option'] = [] # セッション（prompt_option）の値を初期化
        prompt = Prompt.generate_prompt(plan_name, plan_date, daily_available_minutes)
    elif request.method == "POST" and request.POST.get('regenerate') == 'regenerate':
        plan_name = request.session.pop('plan_name', None)
        plan_date = request.session.pop('plan_date', None)
        daily_available_minutes = request.session.pop('daily_available_minutes', None)   
        feedback = request.POST.get("feedback", "").strip()
        print(plan_name, plan_date, daily_available_minutes)
        prompt = Prompt.generate_prompt(plan_name, plan_date, daily_available_minutes, feedback)

    client = OpenAI(api_key=settings.AI_API_KEY)

    #APIを使ってリクエストを投げる
    response = client.responses.create(
        model="gpt-5-nano",
        input=prompt,
        store=True
    )

    data = json.loads(response.output_text)

    print(data)
    
    # プランデータをセッションに保存して select へリダイレクト
    request.session['ai_generated_plans'] = data.get('plans', [])
    
    return redirect('select')

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


def regenerate(request):
    if request.method == "POST":
        original_data = request.session.pop('ai_generated_plans', None)
        feedback = request.POST.get("feedback", "").strip()

        prompt = Prompt.regenerate_prompt(original_data, feedback)

        client = OpenAI(api_key=settings.AI_API_KEY)

        #APIを使ってリクエストを投げる
        response = client.responses.create(
            model="gpt-5-nano",
            input=prompt,
            store=True
        )

        data = json.loads(response.output_text)

        print(data)
        
        # プランデータをセッションに保存して select へリダイレクト
        request.session['ai_generated_plans'] = data.get('plans', [])
        
        return redirect('select')

    return render(request, "createplan/regenerate.html")


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
            return redirect("home") 

    return render(request, "auth/signup.html")


def signin(request):
    # すでにログイン済みのユーザーはリダイレクト
    if request.user.is_authenticated:
        return redirect("form")

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
            return redirect("home")
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

def form(request):
    return redirect(
        
    )


def home(request): 
    today = timezone.now().date()

    plans = Plan.objects.prefetch_related(
        Prefetch(
            'tasks',
            queryset=Task.objects.filter(
                task_start_date__date__lte=today,
                task_end_date__date__gte=today,
            ).order_by('task_start_date'),
            to_attr='today_tasks'
        )
    ).filter(user=request.user)

    # print(plans.first().today_tasks)
    # plans = Plan.objects.prefetch_related('tasks').filter(user=request.user)

    # plan = Plan.objects.prefetch_related('tasks').filter(user=request.user).first() 
    # # FIXME 現在選択中のプラン,一時的に最初の要素を取得

    # today = timezone.now().date()
    # today_task = Task.objects.filter(
    #     plan=plan,
    #     plan__user=request.user,
    #     task_start_date__date__lte=today,
    #     task_end_date__date__gte=today,
    # ).order_by('task_start_date').first()


    # FIXME 一旦JSONを返す仕様としている
    # data = []

    # for plan in plans:
    #     data.append({
    #         "id": plan.id,
    #         "plan_name": plan.plan_name,
    #         "plan_start_date": plan.plan_start_date,
    #         "plan_end_date": plan.plan_end_date,
    #         "tasks": [
    #             {
    #                 "id": task.id,
    #                 "genre": task.genre,
    #                 "title": task.title,
    #                 "is_active": task.is_active,
    #                 "task_start_date": task.task_start_date,
    #                 "task_end_date": task.task_end_date,
    #             }
    #             for task in plan.tasks.all()
    #         ]
    #     })

    # return JsonResponse(data, safe=False)
    plan = plans.first()

    if plan:
        print(plan.today_tasks)
    else:
        print(None)

    return render(request, 'dashboard/home.html', {
        'plans': plans if plans.exists() else None
    })


def select(request):
    # POSTで選択プランデータが送られたらセッションに保存してリダイレクト
    if request.method == 'POST':
        selected_plan_index = request.POST.get('selected_plan_index')

        ai_plans = request.session.pop('ai_generated_plans', None)

        # FIXME 一旦コメントアウト
        #　if selected_plan_index and ai_plans:　
        if ai_plans:
            try:
                # インデックスに対応するプランを取得                
                #selected_index = int(selected_plan_index)
                #elected_plan = ai_plans[selected_index]

                # FIXME: 現状は暫定対応として先頭プラン(index=0)を使用
                # 本来はフロントから受け取った selected_plan_index を反映する
                selected_plan = ai_plans[0]

                request.session['selected_plan'] = selected_plan

                user = request.user

                plan = Plan.objects.create(
                    user=user,
                    #plan_name=selected_plan.get("planname", ""),
                    plan_name=request.session.pop('plan_name', None),
                    plan_start_date=selected_plan["tasks"][0]["task_start_date"],
                    plan_end_date=selected_plan["tasks"][-1]["task_end_date"],
                )

                tasks = []

                # tasks をDBに保存
                for task_item in selected_plan["tasks"]:
                    task = Task(
                        plan=plan,
                        genre=task_item.get("genre", ""),
                        title=task_item.get("title") or task_item.get("name", ""),
                        is_active=False,
                        task_start_date=task_item.get("task_start_date"),
                        task_end_date=task_item.get("task_end_date"),
                    )
                    tasks.append(task)
                Task.objects.bulk_create(tasks)                
            except (json.JSONDecodeError, ValueError, IndexError, KeyError):
                request.session['selected_plan'] = None
        return redirect('home')

    # セッションから AI 生成プランを取得
    ai_plans = request.session.get('ai_generated_plans', None)
    
    if ai_plans:
        # AI 生成データを使用
        plans = _process_plans(ai_plans)
    else:
        # サンプルファイルから読み込み
        sample_path = os.path.join(settings.BASE_DIR, 'response_sample.json')
        plans = []
        try:
            with open(sample_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tasks = data.get('tasks', [])
                plans = _process_tasks_to_plans(tasks)
        except FileNotFoundError:
            plans = []

    return render(request, 'createplan/select.html', {
        'plans': plans,
    })


def plan_table(request, plan_id):
    plan = Plan.objects.filter(id=plan_id).prefetch_related('tasks').filter(user=request.user).first() 
    # FIXME 現在選択中のプラン,一時的に最初の要素を取得

    today = timezone.now().date()
    today_task = Task.objects.filter(
        plan=plan,
        plan__user=request.user,
        task_start_date__date__lte=today,
        task_end_date__date__gte=today,
    ).order_by('task_start_date').first()

    # data = []

    # # for plan in plans:
    # data.append({
    #     "id": plan.id,
    #     "plan_name": plan.plan_name,
    #     "plan_start_date": plan.plan_start_date,
    #     "plan_end_date": plan.plan_end_date,
    #     "tasks": [
    #         {
    #             "id": task.id,
    #             "genre": task.genre,
    #             "title": task.title,
    #             "is_active": task.is_active,
    #             "task_start_date": task.task_start_date,
    #             "task_end_date": task.task_end_date,
    #         }
    #         for task in plan.tasks.all()
    #     ]
    # })

    return render(request, 'dashboard/plan_table.html', {
        'plan': plan,
        'today_task': today_task
    })


def task_detail(request, task_id):
    task = Task.objects.filter(id=task_id).first()
    
    print("task!!!!!!!!")
    print(task)

    return render(request, 'dashboard/task_detail.html', {
        'task': task,
    })


async def chart(request, plan_id):

    print("plan_id")
    print(plan_id)

    qs = (
        Task.objects
        .filter(plan_id=plan_id, plan__user=request.user)
        .values('genre')
        .annotate(
            total=Count('id'),
            notStarted=Count('id', filter=Q(task_detail__evaluation=0)),
            unclear=Count('id', filter=Q(task_detail__evaluation=1)),
            partial=Count('id', filter=Q(task_detail__evaluation=2)),
            understood=Count('id', filter=Q(task_detail__evaluation=3)),
        )
        .order_by('genre')
    )

    subjects = []
    data = []

    for row in qs:
        total = row['total'] or 1

        subjects.append(row['genre'])
        data.append({
            'notStarted': round(row['notStarted'] / total * 100),
            'unclear': round(row['unclear'] / total * 100),
            'partial': round(row['partial'] / total * 100),
            'understood': round(row['understood'] / total * 100),
        })

    return JsonResponse({
        'subjects': subjects,
        'data': data,
    })


def _process_plans(ai_plans):
    """AI生成プランをフロントエンド用にフォーマット"""
    plans = []
    for plan in ai_plans:
        formatted_plan = {
            'id': plan.get('index', ''),
            'planname': plan.get('planname', ''),
            'tasks': [],
        }
        
        for t in plan.get('tasks', []):
            genre = t.get('genre')
            start = t.get('task_start_date')
            end = t.get('task_end_date')
            days = ''
            try:
                if start and end:
                    d1 = datetime.strptime(start, '%Y-%m-%d').date()
                    d2 = datetime.strptime(end, '%Y-%m-%d').date()
                    days = (d2 - d1).days + 1
            except Exception:
                days = ''

            formatted_plan['tasks'].append({
                'id': t.get('id'),
                'name': t.get('name'),
                'genre': genre,
                'start_date': start,
                'end_date': end,
                'days': days,
            })
        
        formatted_plan['json_data'] = json.dumps(formatted_plan, ensure_ascii=False)
        plans.append(formatted_plan)
    
    return plans


def _process_tasks_to_plans(tasks):
    """タスク一覧をプランに分割"""
    plans = []
    num_plans = 3
    total = len(tasks)
    if total == 0:
        return []
    
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
    
    return plans