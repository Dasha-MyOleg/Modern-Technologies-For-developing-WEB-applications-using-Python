from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from models import Part, Figure
from fastapi import Form
from fastapi.responses import RedirectResponse
from database import SessionLocal, engine
from models import Base
import crud
from fastapi import Body
from starlette.middleware.sessions import SessionMiddleware
from models import User
from models import Part, Figure, User, UserFigure


app = FastAPI(title="DragonCollect", description="Фігурки з мультфільму", version="1.0")
app.add_middleware(SessionMiddleware, secret_key="very-secret-key")

# створення таблиць
Base.metadata.create_all(bind=engine)

# шаблони + статика
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")



# сесія до БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.on_event("startup")
def add_default_parts():
    """
    🛠️ Ініціалізація частин фільму при першому запуску застосунку.

    Ця функція автоматично створює стандартні частини ("Фільм 1", "Частина 1", "Частина 2", "Частина 3"),
    якщо таблиця parts ще порожня.
    """
    db = SessionLocal()
    if db.query(Part).count() == 0:
        db.add_all([
            Part(title="Фільм 1"),
            Part(title="Частина 1"),
            Part(title="Частина 2"),
            Part(title="Частина 3")
        ])
        db.commit()
    db.close()




@app.post(
    "/toggle_owned/{figure_id}",
    summary="Оновлення статусу володіння фігуркою",
    description="Користувач ставить або знімає позначку 'маю/не маю' для фігурки. "
                "Ця інформація зберігається індивідуально для кожного користувача."
)
def toggle_owned(
    figure_id: int,
    request: Request,
    payload: dict = Body(...),
    db: Session = Depends(get_db)
):
    user_data = request.session.get("user")
    if not user_data:
        return {"success": False, "error": "Unauthorized"}

    user = db.query(User).filter(User.username == user_data["username"]).first()
    if not user:
        return {"success": False, "error": "User not found"}

    owned = payload.get("owned", False)

    user_fig = db.query(UserFigure).filter_by(user_id=user.id, figure_id=figure_id).first()
    if user_fig:
        user_fig.owned = owned
    else:
        user_fig = UserFigure(user_id=user.id, figure_id=figure_id, owned=owned)
        db.add(user_fig)

    db.commit()
    return {"success": True, "owned": owned}




@app.get(
    "/",
    summary="Головна сторінка каталогу",
    description="Показує фігурки з частини 'Фільм 1' та позначки 'маю/не маю' для авторизованого користувача."
)
def read_root(request: Request, db: Session = Depends(get_db)):
    part = db.query(Part).filter(Part.title == "Фільм 1").first()
    if not part:
        return templates.TemplateResponse("index.html", {"request": request, "figures": []})

    figures = db.query(Figure).filter(Figure.part_id == part.id).all()

    user_data = request.session.get("user")
    owned_map = {}

    if user_data:
        user = db.query(User).filter_by(username=user_data["username"]).first()
        if user:
            user_figs = db.query(UserFigure).filter_by(user_id=user.id).all()
            owned_map = {uf.figure_id: uf.owned for uf in user_figs}

    return templates.TemplateResponse("index.html", {
        "request": request,
        "figures": figures,
        "owned_map": owned_map
    })



@app.post(
    "/create",
    summary="Додати нову фігурку",
    description="Цей маршрут дозволяє адміністратору створити нову фігурку з назвою, зображенням, альтернативним зображенням при наведенні та вказати, до якої частини фільму вона належить."
)
def create_figure(
    request: Request,
    name: str = Form(...),
    img_url: str = Form(...),
    hover_img_url: str = Form(...),
    part_id: int = Form(...),
    owned: bool = Form(False),
    db: Session = Depends(get_db)
):
    if not request.session.get("user", {}).get("is_admin", False):
        return RedirectResponse(url="/", status_code=302)
    
    new_figure = Figure(
        name=name,
        img_url=img_url,
        hover_img_url=hover_img_url,
        part_id=part_id,
        owned=owned
    )
    db.add(new_figure)
    db.commit()
    return RedirectResponse(url="/", status_code=302)



@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.get(
    "/edit/{id}",
    summary="Редагувати фігурку",
    description="Доступно лише для адміністратора. Завантажує сторінку з формою редагування фігурки за її ID."
)
def edit_figure(id: int, request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user", {}).get("is_admin", False):
        return RedirectResponse(url="/", status_code=302)
    
    figure = db.query(Figure).filter(Figure.id == id).first()
    parts = db.query(Part).all()
    if not figure:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("edit_figure.html", {
        "request": request,
        "figure": figure,
        "parts": parts
    })



@app.post(
    "/delete/{id}",
    summary="Видалити фігурку",
    description="Видаляє фігурку за вказаним ID. Доступно лише для адміністратора."
)
def delete_figure(id: int, db: Session = Depends(get_db)):
    if not request.session.get("user", {}).get("is_admin", False):
         return RedirectResponse(url="/", status_code=302)

    figure = db.query(Figure).filter(Figure.id == id).first()
    if figure:
        db.delete(figure)
        db.commit()
    return RedirectResponse(url="/", status_code=302)



@app.post(
    "/toggle_owned/{figure_id}",
    summary="Перемкнути стан фігурки",
    description="Змінює стан 'маю / не маю' для фігурки. У цьому варіанті зміна глобальна (не індивідуальна для користувача)."
)
def toggle_owned(figure_id: int, db: Session = Depends(get_db)):
    figure = db.query(Figure).filter(Figure.id == figure_id).first()
    if not figure:
        return {"success": False}
    figure.owned = not figure.owned
    db.commit()
    return {"success": True, "owned": figure.owned}



@app.post(
    "/toggle_owned/{figure_id}",
    summary="Змінити стан фігурки",
    description="Оновлює поле 'owned' фігурки для заданого ID. Увага: змінює глобально, а не для окремого користувача!"
)
def toggle_owned(figure_id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    figure = db.query(Figure).filter(Figure.id == figure_id).first()
    if not figure:
        return {"success": False}
    figure.owned = payload.get("owned", False)
    db.commit()
    return {"success": True, "owned": figure.owned}



@app.get(
    "/create_admin",
    summary="Створити адміністратора",
    description="Якщо в системі ще немає адміністратора, створює користувача з логіном 'admin' і паролем 'admin123'."
)
def create_admin(db: Session = Depends(get_db)):
    from models import User

    existing_admin = db.query(User).filter(User.is_admin == True).first()
    if existing_admin:
        return {"message": "Адміністратор уже існує"}

    admin = User(username="admin", password="admin123", is_admin=True)
    db.add(admin)
    db.commit()
    return {"message": "Адміністратора створено"}



@app.get(
    "/login",
    summary="Форма входу",
    description="Повертає HTML-сторінку з формою входу для користувача або адміністратора."
)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post(
    "/login",
    summary="Увійти",
    description="Перевіряє логін і пароль, зберігає статус у сесії. Переадресація на головну сторінку після успіху."
)
def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(username=username, password=password).first()
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Невірні дані"
        })
    
    # Збереження статусу у сесію
    request.session["user"] = {
        "username": user.username,
        "is_admin": user.is_admin
    }

    return RedirectResponse(url="/", status_code=302)



@app.get(
    "/logout",
    summary="Вийти",
    description="Очищає сесію користувача і повертає його на головну сторінку."
)
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)




@app.get(
    "/register",
    summary="Форма реєстрації",
    description="Повертає HTML-сторінку для створення нового користувача або адміністратора."
)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})




@app.post(
    "/register",
    summary="Зареєструвати нового користувача",
    description="Створює нового користувача або адміністратора, перевіряє унікальність логіну, зберігає інформацію у БД і файл."
)
def register_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db)
):
    # Перевірка унікальності
    existing = db.query(User).filter_by(username=username).first()
    if existing:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Такий користувач уже існує"
        })

    new_user = User(
        username=username,
        password=password,
        is_admin=(role == "admin")
    )
    db.add(new_user)
    db.commit()

    # Додавання в users.txt
    with open("users.txt", "a", encoding="utf-8") as f:
        f.write(f"{username} | {password} | {'admin' if role == 'admin' else 'user'}\n")

    return RedirectResponse(url="/login", status_code=302)




@app.get(
    "/manage_users",
    summary="Керування користувачами",
    description="Сторінка доступна лише адміністратору. Дозволяє переглядати список усіх користувачів у системі."
)
def manage_users(request: Request, db: Session = Depends(get_db)):
    user = request.session.get("user")
    if not user or not user["is_admin"]:
        return RedirectResponse(url="/", status_code=302)

    users = db.query(User).all()
    return templates.TemplateResponse("manage_users.html", {
        "request": request,
        "users": users
    })




@app.post(
    "/delete_user/{user_id}",
    summary="Видалити користувача",
    description="Адміністратор може видалити будь-якого користувача, крім самого себе. Після видалення оновлюється текстовий файл зі списком користувачів."
)
def delete_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = request.session.get("user")
    if not current_user or not current_user["is_admin"]:
        return RedirectResponse(url="/", status_code=302)

    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if user_to_delete and user_to_delete.username != current_user["username"]:
        db.delete(user_to_delete)
        db.commit()

    # після видалення — оновити текстовий файл
    users = db.query(User).all()
    with open("user_list.txt", "w", encoding="utf-8") as f:
        for u in users:
            f.write(f"{u.username} | {u.password} | {'admin' if u.is_admin else 'user'}\n")

    return RedirectResponse(url="/manage_users", status_code=302)






@app.get(
    "/",
    summary="Головна сторінка — Фільм 1",
    description="Показує всі фігурки, які належать до першого фільму."
)
def read_root(request: Request, db: Session = Depends(get_db)):
    part = db.query(Part).filter(Part.title == "Фільм 1").first()
    if not part:
        return templates.TemplateResponse("index.html", {"request": request, "figures": []})
    figures = db.query(Figure).filter(Figure.part_id == part.id).all()
    return templates.TemplateResponse("index.html", {"request": request, "figures": figures})



@app.get(
    "/part1",
    summary="Фігурки з Частини 1",
    description="Виводить фігурки, що належать до Частини 1 мультфільму."
)
def part1_page(request: Request, db: Session = Depends(get_db)):
    part = db.query(Part).filter(Part.title == "Частина 1").first()
    if not part:
        return templates.TemplateResponse("part1.html", {"request": request, "figures": []})

    figures = db.query(Figure).filter(Figure.part_id == part.id).all()

    user_data = request.session.get("user")
    owned_map = {}

    if user_data:
        user = db.query(User).filter_by(username=user_data["username"]).first()
        if user:
            user_figs = db.query(UserFigure).filter_by(user_id=user.id).all()
            owned_map = {uf.figure_id: uf.owned for uf in user_figs}

    return templates.TemplateResponse("part1.html", {
        "request": request,
        "figures": figures,
        "owned_map": owned_map
    })



@app.get(
    "/part2",
    summary="Фігурки з Частини 2",
    description="Виводить фігурки, що належать до Частини 2 мультфільму."
)
def part2_page(request: Request, db: Session = Depends(get_db)):
    part = db.query(Part).filter(Part.title == "Частина 2").first()
    if not part:
        return templates.TemplateResponse("part2.html", {"request": request, "figures": []})

    figures = db.query(Figure).filter(Figure.part_id == part.id).all()

    user_data = request.session.get("user")
    owned_map = {}

    if user_data:
        user = db.query(User).filter_by(username=user_data["username"]).first()
        if user:
            user_figs = db.query(UserFigure).filter_by(user_id=user.id).all()
            owned_map = {uf.figure_id: uf.owned for uf in user_figs}

    return templates.TemplateResponse("part2.html", {
        "request": request,
        "figures": figures,
        "owned_map": owned_map
    })




@app.get(
    "/part3",
    summary="Фігурки з Частини 3",
    description="Виводить фігурки, що належать до Частини 3 мультфільму."
)
def part3_page(request: Request, db: Session = Depends(get_db)):
    part = db.query(Part).filter(Part.title == "Частина 3").first()
    if not part:
        return templates.TemplateResponse("part3.html", {"request": request, "figures": []})

    figures = db.query(Figure).filter(Figure.part_id == part.id).all()

    user_data = request.session.get("user")
    owned_map = {}

    if user_data:
        user = db.query(User).filter_by(username=user_data["username"]).first()
        if user:
            user_figs = db.query(UserFigure).filter_by(user_id=user.id).all()
            owned_map = {uf.figure_id: uf.owned for uf in user_figs}

    return templates.TemplateResponse("part3.html", {
        "request": request,
        "figures": figures,
        "owned_map": owned_map
    })




@app.get(
    "/create_form",
    summary="Форма для додавання фігурки",
    description="Відображає HTML-форму для створення нової фігурки з вибором частини фільму."
)
def show_create_form(request: Request, db: Session = Depends(get_db)):
    parts = db.query(Part).all()
    return templates.TemplateResponse("create_figure.html", {"request": request, "parts": parts})


@app.get(
    "/debug_parts",
    summary="Вивід частин (debug)",
    description="Повертає кількість та список назв усіх частин, що є в базі даних. Використовується для відладки."
)
def debug_parts(db: Session = Depends(get_db)):
    parts = db.query(Part).all()
    return {"count": len(parts), "titles": [p.title for p in parts]}


@app.post(
    "/update/{id}",
    summary="Оновити фігурку",
    description="Оновлює дані про фігурку за її ID: ім’я, зображення, частину та статус 'маю/не маю'."
)
def update_figure(
    id: int,
    name: str = Form(...),
    img_url: str = Form(...),
    hover_img_url: str = Form(...),
    part_id: int = Form(...),
    owned: bool = Form(False),
    db: Session = Depends(get_db)
):
    figure = db.query(Figure).filter(Figure.id == id).first()
    if figure:
        figure.name = name
        figure.img_url = img_url
        figure.hover_img_url = hover_img_url
        figure.part_id = part_id
        figure.owned = owned
        db.commit()
    return RedirectResponse(url="/", status_code=302)


@app.get(
    "/support.html",
    summary="Служба підтримки",
    description="Відображає HTML-сторінку з інформацією про підтримку для користувачів застосунку."
)
def support_page(request: Request):
    return templates.TemplateResponse("support.html", {"request": request})


@app.get(
    "/about.html",
    summary="Про застосунок",
    description="Сторінка з описом предметної галузі, цілей та логіки застосунку DragonCollect."
)
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})