# Сервис управления рассылками

Django-приложение для управления email-рассылками: клиенты, сообщения, рассылки, статистика, роли пользователей, кеширование и подтверждение email.

## Стек

- Python 3.10+
- Django 5.0
- SQLite (по умолчанию)
- Bootstrap 5 (CDN)
- python-dotenv (конфигурация через `.env`)

## Возможности

### Часть 1 — Базовый сервис
- CRUD получателей (email, Ф.И.О., комментарий)
- CRUD сообщений (тема, тело письма)
- CRUD рассылок (период, статус, сообщение, получатели)
- Валидация: `start_time` не в прошлом, `start_time < end_time`
- Динамический статус рассылки (`Создана` / `Запущена` / `Завершена`)
- Ручной запуск рассылки из интерфейса и через команду `send_mailing`
- История попыток отправки с batch-созданием (`bulk_create`)
- Главная страница со счётчиками (всего рассылок, активных, уникальных получателей)

### Часть 2 — Расширение
- Регистрация с подтверждением email
- Вход/выход, восстановление пароля
- Статистика по успешным/неуспешным попыткам
- Роли: **Пользователь** (свои данные) и **Менеджер** (все данные + блокировка пользователей и отключение рассылок)
- Кеширование: серверное (`LocMemCache`) + клиентское (`cache_page`, `cache_control`)

## Установка

### 1. Клонировать / распаковать проект

```bash
cd mailing_project
```

### 2. Создать виртуальное окружение и активировать

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

Если `requirements.txt` нет:
```bash
pip install Django==5.0.6 python-dotenv
pip freeze > requirements.txt
```

### 4. Создать файл `.env` в корне проекта

```env
SECRET_KEY=django-insecure-замени-на-длинную-случайную-строку
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@mailing.local
```

> В dev-режиме письма **печатаются в консоль** PyCharm, а не отправляются по-настоящему. Для реальной отправки задай `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` и замени `EMAIL_BACKEND` на `django.core.mail.backends.smtp.EmailBackend`.

### 5. Применить миграции

```bash
python manage.py makemigrations users
python manage.py makemigrations mailing
python manage.py migrate
```

### 6. Создать суперпользователя (менеджера)

```bash
python manage.py createsuperuser
```
Введи email и пароль. Суперпользователь автоматически получает роль **Менеджер** и подтверждённый email.

### 7. Запустить сервер

```bash
python manage.py runserver
```

Открой: http://127.0.0.1:8000/

## Структура проекта

```
mailing_project/
├── config/                  # настройки и корневые URL
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── users/                   # кастомный пользователь, роли, аутентификация
│   ├── models.py            # User (email вместо username, роли)
│   ├── backends.py          # EmailVerifiedBackend
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── templates/users/
├── mailing/                 # получатели, сообщения, рассылки, попытки
│   ├── models.py            # Recipient, Message, Mailing, Attempt
│   ├── forms.py             # MailingForm с валидацией
│   ├── views.py             # CRUD + Home + Statistics + Send + Disable
│   ├── services.py          # send_mailing (batch-создание Attempt)
│   ├── mixins.py            # Owner* mixins для прав доступа
│   ├── urls.py
│   ├── management/commands/send_mailing.py
│   └── templates/mailing/
├── templates/base.html      # общий layout с Bootstrap
├── manage.py
├── requirements.txt
├── .env
└── README.md
```

## Роли и права

| Действие | Пользователь | Менеджер |
|----------|--------------|----------|
| Создание/редактирование/удаление своих получателей | ✅ | ✅ |
| Просмотр всех получателей | ❌ | ✅ |
| Создание/редактирование/удаление своих рассылок | ✅ | ✅ |
| Просмотр всех рассылок | ❌ | ✅ |
| Просмотр статистики по своим рассылкам | ✅ | ✅ |
| Просмотр списка всех пользователей | ❌ | ✅ |
| Блокировка пользователей | ❌ | ✅ |
| Отключение рассылок | ❌ | ✅ |

- Обычный пользователь видит только **свои** получателей, сообщения и рассылки.
- Менеджер видит всё, но **редактировать и удалять чужие данные не может** (кнопки есть только у владельца).
- Заблокированный или неподтверждённый пользователь **не может войти** (`EmailVerifiedBackend`).

## Полезные команды

| Команда | Что делает |
|---------|------------|
| `python manage.py runserver` | Запустить dev-сервер |
| `python manage.py migrate` | Применить миграции |
| `python manage.py createsuperuser` | Создать менеджера |
| `python manage.py send_mailing <id>` | Отправить рассылку по ID из консоли |
| `python manage.py shell` | Интерактивная консоль |

## Проверка работоспособности (чек-лист)

1. **Главная** `/` — навбар Bootstrap, 3 карточки со счётчиками, заголовок `Cache-Control: public, max-age=60` в DevTools → Network.
2. **Регистрация** `/users/register/` — письмо со ссылкой появляется **в консоли** PyCharm; переход по ссылке → «Email подтверждён ✅».
3. **Вход** `/users/login/` — по email и паролю. Неподтверждённый пользователь не пускается.
4. **Восстановление пароля** `/users/password_reset/` — письмо-ссылка в консоль, сброс работает.
5. **Получатели** `/recipients/` — CRUD работает.
6. **Сообщения** `/messages/` — CRUD работает.
7. **Создание рассылки** `/mailings/create/`:
   - `start_time` в прошлом → ошибка валидации;
   - `start_time >= end_time` → ошибка валидации;
   - корректный диапазон → создаётся.
8. **Детали рассылки** `/mailings/<id>/`:
   - статус пересчитывается автоматически (`update_status()` в `get_object`);
   - кнопка «Отправить сейчас»:
     - вне окна времени → ошибка, попыток нет;
     - внутри окна → письма в консоль, попытки со статусом «Успешно».
9. **Статистика** `/statistics/` — счётчики совпадают с реальностью.
10. **Права** — зайди под менеджером → «Пользователи» → заблокируй обычного юзера → он не сможет войти.
11. **Команда** `python manage.py send_mailing 1` (id активной рассылки) — отправляет.
12. **Кеш** — главная отдаётся из кеша 60 секунд (`cache_page` + `cache_control`).

## Примечания

- База данных — SQLite (`db.sqlite3`), создаётся автоматически после `migrate`.
- Письма в dev-режиме идут в консоль через `console.EmailBackend`.
- Кеш в dev-режиме — `LocMemCache` (в памяти процесса), сбрасывается при перезапуске сервера.
- Секреты (`SECRET_KEY`, пароли почты) хранятся в `.env`, файл **не коммитится** в репозиторий.