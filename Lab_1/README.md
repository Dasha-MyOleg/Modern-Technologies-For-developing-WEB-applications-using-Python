# DragonCollect — Каталог фігурок з мультфільму «Як приборкати дракона» (тимчасово котиками)

## Доступ до акаунтів

- **Адміністратор**  
  Логін: `admin`  
  Пароль: `admin123`

- **Користувач**  
  Логін: `user1`  
  Пароль: `user234`

## Виконання вимог лабораторної

### 1. Контент генерується на сервері
Шаблони генеруються на сервері у функціях:

- `/` — головна сторінка
- `/part1`, `/part2`, `/part3` — сторінки частин
- `/create_form`, `/edit/{id}` — форми створення та редагування
- `/about.html`, `/support.html` — статичні сторінки


### 2. Дані зберігаються у реляційній базі даних (SQLite)
База `figurines.db` містить щонайменше **3 сутності**:
- `Figure` — фігурки
- `Part` — частини фільму
- `User` — акаунти користувачів
- (також: `UserFigure` — зв'язок між користувачами та фігурками)

### 3. Використання SQLAlchemy ORM
Всі операції з базою виконуються через SQLAlchemy:
- створення сесії: `SessionLocal`
- моделі наслідують від `Base`
- використовується ORM-запити: `.query(...).filter(...)`, `.add(...)`, `.commit()`

### 4. Реалізовано ролі: адміністратор і користувач
- `User` має поле `is_admin`
- Сторінки `/create_form`, `/edit`, `/delete`, `/manage_users` доступні лише адміністраторам
- Вхід через `/login`, сесія зберігає роль

### 5. CRUD-операції для `Figure`
- **Create:** `/create`  
- **Read:** `/`, `/part1`, `/part2`, `/part3`  
- **Update:** `/update/{id}`  
- **Delete:** `/delete/{id}`

### 6. OpenAPI документація модифікована
Маршрути мають опис:

```python
@app.get(
    "/about.html",
    summary="Про застосунок",
    description="Сторінка з описом предметної галузі, цілей та логіки застосунку DragonCollect."
)
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})