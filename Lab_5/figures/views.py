from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Figure, UserFigure

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import User

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User


from django.shortcuts import render, redirect
from .models import Feedback
from django.views.decorators.csrf import csrf_exempt


from .models import Figure, Part, UserFigure
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def home(request):
    return HttpResponse("Це головна сторінка Django-застосунку.")

def index_view(request):
    #figures = Figure.objects.all()
    figures = Figure.objects.filter(part__title="Фільм 1")

    owned_map = {}
    if request.user.is_authenticated:
        user_figures = UserFigure.objects.filter(user=request.user)
        owned_map = {uf.figure.id: uf.owned for uf in user_figures}

    context = {
        "figures": figures,
        "owned_map": owned_map,
    }
    return render(request, "index.html", context)


def part1_view(request):
    figures = Figure.objects.filter(part__title="Частина 1")

    owned_map = {}
    if request.user.is_authenticated:
        user_figures = UserFigure.objects.filter(user=request.user)
        owned_map = {uf.figure.id: uf.owned for uf in user_figures}

    return render(request, "part1.html", {
        "figures": figures,
        "owned_map": owned_map,
    })


def part2_view(request):
    figures = Figure.objects.filter(part__title="Частина 2")

    owned_map = {}
    if request.user.is_authenticated:
        user_figures = UserFigure.objects.filter(user=request.user)
        owned_map = {uf.figure.id: uf.owned for uf in user_figures}

    return render(request, "part2.html", {
        "figures": figures,
        "owned_map": owned_map,
    })


def part3_view(request):
    figures = Figure.objects.filter(part__title="Частина 3")

    owned_map = {}
    if request.user.is_authenticated:
        user_figures = UserFigure.objects.filter(user=request.user)
        owned_map = {uf.figure.id: uf.owned for uf in user_figures}

    return render(request, "part3.html", {
        "figures": figures,
        "owned_map": owned_map,
    })




def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect("index")
        else:
            return render(request, "login.html", {"error": "Неправильні дані"})
    return render(request, "login.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        role = request.POST.get("role", "user")

        is_superuser = True if role == "admin" else False
        is_staff = is_superuser  # або False, якщо хочеш більш жорстке розмежування

        if User.objects.filter(username=username).exists():
            return HttpResponse("Користувач з таким іменем уже існує")

        user = User.objects.create_user(
            username=username,
            password=password,
            is_superuser=is_superuser,
            is_staff=is_staff,
        )
        user.save()
        return redirect("login")
    return render(request, "register.html")


def logout_view(request):
    auth_logout(request)
    return redirect("index")



@login_required
def manage_users_view(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, "manage_users.html", {"users": users})



@login_required
def delete_user_view(request, user_id):
    if request.method == "POST":
        print(f"Намагаємось видалити user_id={user_id}")
        if user_id != request.user.id:
            try:
                user_to_delete = User.objects.get(id=user_id)
                user_to_delete.delete()
                print("Успішно видалено")
            except User.DoesNotExist:
                print("Користувача не знайдено")
    return redirect("manage_users")


def about_view(request):
    return render(request, "about.html")




def support_view(request):
    sent = False
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        if name and email and message:
            Feedback.objects.create(name=name, email=email, message=message)
            sent = True
    return render(request, "support.html", {"sent": sent})

def feedbacks_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("/")
    feedbacks = Feedback.objects.all().order_by("-created_at")
    return render(request, "feedbacks.html", {"feedbacks": feedbacks})

@csrf_exempt
def delete_feedback_view(request):
    if request.method == "POST" and request.user.is_superuser:
        feedback_id = request.POST.get("id")
        try:
            Feedback.objects.get(id=feedback_id).delete()
        except Feedback.DoesNotExist:
            pass
    return redirect("feedbacks")



# Форма створення
@login_required
def create_figure_form(request):
    if not request.user.is_superuser:
        return redirect("/")
    parts = Part.objects.all()
    return render(request, "create_figure.html", {"parts": parts})


# Обробка створення
@csrf_exempt
@login_required
def create_figure_view(request):
    if request.method == "POST" and request.user.is_superuser:
        name = request.POST["name"]
        img_url = request.POST["img_url"]
        hover_img_url = request.POST["hover_img_url"]
        part_id = request.POST["part_id"]
        owned = request.POST.get("owned") == "on"

        figure = Figure.objects.create(
            name=name,
            img_url=img_url,
            hover_img_url=hover_img_url,
            part_id=part_id
        )

        if owned:
            UserFigure.objects.create(user=request.user, figure=figure, owned=True)

    return redirect("/")


# Форма редагування
@login_required
def edit_figure_form(request, figure_id):
    if not request.user.is_superuser:
        return redirect("/")
    figure = Figure.objects.get(id=figure_id)
    parts = Part.objects.all()
    try:
        owned = UserFigure.objects.get(user=request.user, figure=figure).owned
    except UserFigure.DoesNotExist:
        owned = False
    return render(request, "edit_figure.html", {
        "figure": figure,
        "parts": parts,
        "owned": owned
    })


# Обробка оновлення
@csrf_exempt
@login_required
def update_figure_view(request, figure_id):
    if request.method == "POST" and request.user.is_superuser:
        figure = Figure.objects.get(id=figure_id)
        figure.name = request.POST["name"]
        figure.img_url = request.POST["img_url"]
        figure.hover_img_url = request.POST["hover_img_url"]
        figure.part_id = request.POST["part_id"]
        figure.save()

        owned = request.POST.get("owned") == "on"
        uf, _ = UserFigure.objects.get_or_create(user=request.user, figure=figure)
        uf.owned = owned
        uf.save()

    return redirect("/")


# Видалення
@csrf_exempt
@login_required
def delete_figure_view(request, figure_id):
    if request.method == "POST" and request.user.is_superuser:
        Figure.objects.filter(id=figure_id).delete()
    return redirect("/")



@csrf_exempt
@login_required
def toggle_owned(request, figure_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            owned = data.get("owned", False)

            user_figure, created = UserFigure.objects.get_or_create(
                user=request.user,
                figure_id=figure_id,
                defaults={'owned': owned}
            )
            if not created:
                user_figure.owned = owned
                user_figure.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid method"})
