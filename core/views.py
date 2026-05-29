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
from core.models import Task, Plan, Link, TaskDetail
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core import serializers
from django.db.models import Prefetch, Count, Q
from django.shortcuts import get_object_or_404
from django.contrib import messages


# Create your views here.
@login_required
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
        prompt = Prompt.generate_prompt(plan_name, plan_date, daily_available_minutes)
    elif request.method == "POST" and request.POST.get('regenerate') == 'regenerate':
        plan_name = request.session.get('plan_name', None)
        plan_date = request.session.get('plan_date', None)
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
    
    # プランデータをセッションに保存して select へリダイレクト
    request.session['ai_generated_plans'] = data.get('plans', [])
    
    return redirect('select')


@login_required
def regenerate(request):

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

        user = _authenticate_with_email(email, password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "ユーザー名またはパスワードが違います。")

    return render(request, "auth/login.html")


@login_required
def menu(request):
    return render(request, 'dashboard/menu.html')


@login_required
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


@login_required
def form(request):
    return render(request, 'createplan/form.html')


@login_required
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

    return render(request, 'dashboard/home.html', {
        'plans': plans if plans.exists() else None
    })


@login_required
def delete_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id, user=request.user)
    plan.delete()

    return redirect('home')


@login_required
def select(request):
    # POSTで選択プランデータが送られたらセッションに保存してリダイレクト
    if request.method == 'POST':
        selected_plan_index = request.POST.get('selected_plan_index')

        ai_plans = request.session.pop('ai_generated_plans', None)

        if selected_plan_index and ai_plans:
            try:
                # インデックスに対応するプランを取得                
                selected_index = int(selected_plan_index)
                selected_plan = ai_plans[selected_index]

                request.session['selected_plan'] = selected_plan

                user = request.user

                plan = Plan.objects.create(
                    user=user,
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
                # データベースから Task を再取得（ID が設定される）
                created_tasks = Task.objects.filter(plan=plan)  
                for task in created_tasks:
                    TaskDetail.objects.create(task=task)
            except Exception as e:
                request.session['selected_plan'] = None
                print(f"Error: {e}") 
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


@login_required
def plan_table(request, plan_id):
    plan = Plan.objects.filter(id=plan_id).prefetch_related('tasks').filter(user=request.user).first() 

    today = timezone.now().date()
    today_task = Task.objects.filter(
        plan=plan,
        plan__user=request.user,
        task_start_date__date__lte=today,
        task_end_date__date__gte=today,
    ).order_by('task_start_date').first()

    return render(request, 'dashboard/plan_table.html', {
        'plan': plan,
        'today_task': today_task
    })


@login_required
def task_detail(request, task_id):

    task = get_object_or_404(Task, id=task_id, plan__user=request.user)

    if request.method == 'POST':

        task_detail, created = TaskDetail.objects.update_or_create(
            task_id=task_id,
            defaults={
                'evaluation': int(request.POST.get("evaluation", "0")),
                'memo': request.POST.get("memo", "")
            }
        )

        return redirect('plan_table', task.plan.id)

    
    return render(request, 'dashboard/task_detail.html', {
        'plan': task.plan,
        'task': task
    })


@login_required
def chart(request, plan_id):
    plan = Plan.objects.filter(id=plan_id).prefetch_related('tasks').filter(user=request.user).first()

    return render(request, 'dashboard/chart.html', {
        'plan': plan,
        'plan_id': plan_id,
    })


@login_required
def api_chart(request, plan_id):

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


@login_required
def link(request):
    if request.method == "POST":

        plan_id = request.POST.get('plan_id')

        created = Link.objects.create(
            plan_id=int(plan_id),
            url=request.POST.get('url', ""),
            link_name=request.POST.get("link_name", "")
        )

        return redirect('link')

    plans = Plan.objects.filter(user=request.user)


    return render(request, 'dashboard/link.html', {
        'plans': plans
    })


@login_required
def delete_link(request, link_id):
    link = get_object_or_404(Link, id=link_id, plan__user=request.user)
    link.delete()

    return redirect('link')


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

# エラーページ
def custom_400(request, exception):
    return render(request, "error/error.html",
                    { "error_status": "400 Bad Request","error_message": "指定されたページを表示できません。" },
                    status=400
                )

def custom_403(request, exception):
    return render(request, "error/error.html",
                    { "error_status": "403 Forbidden","error_message": "指定されたページを表示できません。" },
                    status=403
                )

def custom_404(request, exception):
    return render(request, "error/error.html",
                    { "error_status": "404 Not Found","error_message": "ページが見つかりませんでした。" },
                    status=404
                )

def custom_500(request):
    return render(request, "error/error.html",
                    { "error_status": "500 Internal Server Error", "error_message": "サーバー内部エラー、ページを表示できません。" },
                    status=500
                )