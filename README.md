# devops-web-app

## Варіант (N=4)

| Параметр | Формула | Значення | Опис |
|---|---|---|---|
| V2 | (4 % 2) + 1 | 1 | Конфігурація через аргументи командного рядка, БД — MariaDB |
| V3 | (4 % 3) + 1 | 2 | Task Tracker |
| V5 | (4 % 5) + 1 | 5 | Порт 5000 |

## Опис застосунку

Task Tracker — веб-сервіс для відстеження задач. Дозволяє створювати задачі, переглядати їх список та позначати як виконані. Дані зберігаються у MariaDB.

## Середовище для розробки

Вимоги: Python 3.10+

```bash
cd app
python -m venv venv
venv\Scripts\activate        # Windows
# або
source venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
```

## Запуск застосунку локально

Потрібна запущена MariaDB з базою даних `mywebapp`.

```bash
python app/app.py \
  --host 127.0.0.1 \
  --port 5000 \
  --db-host 127.0.0.1 \
  --db-port 3306 \
  --db-user <користувач> \
  --db-password <пароль> \
  --db-name mywebapp
```

## API

### Health

| Метод | Шлях | Опис | Відповідь |
|---|---|---|---|
| GET | /health/alive | Перевірка що сервіс живий | 200 OK |
| GET | /health/ready | Перевірка підключення до БД | 200 OK або 500 з описом помилки |

### Бізнес-логіка

Ендпоінти бізнес-логіки підтримують заголовок `Accept`:
- `Accept: application/json` — відповідь у форматі JSON
- `Accept: text/html` — відповідь у вигляді HTML-сторінки

| Метод | Шлях | Тіло запиту | Опис |
|---|---|---|---|
| GET | / | — | Список усіх ендпоінтів (тільки text/html) |
| GET | /tasks | — | Список усіх задач |
| POST | /tasks | `{"title": "назва"}` | Створити нову задачу |
| POST | /tasks/\<id\>/done | — | Позначити задачу виконаною |

### Приклади

```bash
curl -H "Accept: application/json" http://localhost/tasks

curl -X POST http://localhost/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Купити каву"}'

curl -X POST http://localhost/tasks/1/done
```

### Формат задачі

```json
{
  "id": 1,
  "title": "Купити каву",
  "status": "pending",
  "created_at": "2026-05-29T10:00:00"
}
```

Поле `status` може мати значення `pending` або `done`.

## Розгортання

### Образ віртуальної машини

Ubuntu Server 24.04 LTS — завантажити з офіційного сайту: [https://ubuntu.com/download/server](https://ubuntu.com/download/server)

Обирай варіант **Option 2 - Manual server installation**, завантажуй `.iso` файл.

### Вимоги до ресурсів ВМ

| Ресурс | Мінімум |
|---|---|
| CPU | 1 ядро |
| RAM | 1 GB |
| Диск | 10 GB |

### Встановлення OS

Спеціальних налаштувань при встановленні не потрібно. Використовуй стандартні параметри інсталятора. При виборі профілю — обирай **Ubuntu Server** (без додаткових снапів).

### Вхід на ВМ

Після розгортання автоматизації входь під користувачем `student`:

| Параметр | Значення |
|---|---|
| Користувач | student |
| Пароль | student |

Підключення через консоль VirtualBox або SSH:
```bash
ssh student@<ip-адреса-вм>
```

### Розгортання автоматизацією

На віртуальній машині виконай:

```bash
sudo apt-get install -y git
git clone https://github.com/ivan-hrytsenko/devops-web-app.git
cd devops-web-app
sudo bash deploy/install.sh
```

Скрипт автоматично:
- встановить необхідні пакети (Python, Nginx, MariaDB)
- створить користувачів (`student`, `teacher`, `app`, `operator`)
- створить базу даних
- розгорне застосунок і запустить його через systemd
- налаштує Nginx як reverse proxy
- заблокує дефолтного користувача `ubuntu`

### Користувачі в системі

| Користувач | Пароль | Примітка |
|---|---|---|
| student | student | Основний користувач, права sudo |
| teacher | 12345678 | Права sudo, пароль потрібно змінити при першому вході |
| operator | 12345678 | Обмежений sudo, пароль потрібно змінити при першому вході |
| app | — | Системний користувач без shell, запускає застосунок |

## Тестування

Детальна інструкція з тестування: [docs/testing.md](docs/testing.md)