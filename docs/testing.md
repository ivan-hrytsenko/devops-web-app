# Інструкція з тестування

Всі команди виконуються на віртуальній машині після запуску `deploy/install.sh`.

## 1. Перевірка стану сервісів

```bash
sudo systemctl status mywebapp
sudo systemctl status mywebapp.socket
sudo systemctl status nginx
sudo systemctl status mariadb
```

Очікуваний результат: всі сервіси у стані `active (running)` або `active (listening)` для сокету.

## 2. Health-ендпоінти

Health-ендпоінти доступні лише напряму через Unix socket, бо nginx блокує `/health` ззовні.

```bash
sudo curl --unix-socket /run/mywebapp.sock http://localhost/health/alive
```
Очікувано: `OK`

```bash
sudo curl --unix-socket /run/mywebapp.sock http://localhost/health/ready
```
Очікувано: `OK`

## 3. Кореневий ендпоінт

```bash
curl -H "Accept: text/html" http://localhost/
```
Очікувано: HTML-сторінка зі списком ендпоінтів.

```bash
curl -H "Accept: application/json" http://localhost/
```
Очікувано: `406 Not Acceptable`

## 4. Список задач

```bash
curl -H "Accept: application/json" http://localhost/tasks
```
Очікувано: JSON-масив (порожній якщо задач ще немає).

```bash
curl -H "Accept: text/html" http://localhost/tasks
```
Очікувано: HTML-таблиця із задачами.

## 5. Створення задачі

```bash
curl -X POST http://localhost/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Test task"}'
```
Очікувано:
```json
{"created_at": "...", "id": 1, "status": "pending", "title": "Test task"}
```

## 6. Позначення задачі виконаною

```bash
curl -X POST http://localhost/tasks/1/done
```
Очікувано:
```json
{"created_at": "...", "id": 1, "status": "done", "title": "Test task"}
```

## 7. Перевірка nginx-логів

```bash
sudo tail -f /var/log/nginx/mywebapp.access.log
```

Виконай кілька запитів і переконайся що вони з'являються в логах.

## 8. Перевірка користувачів

```bash
id student
id teacher
id app
id operator
```

Перевір що `student` і `teacher` мають групу `sudo`:
```bash
groups student
groups teacher
```

Перевір що `app` — системний користувач без shell:
```bash
getent passwd app
```
Очікувано: рядок із `/usr/sbin/nologin` в кінці.

## 9. Перевірка sudo-прав operator

```bash
su - operator
```
Пароль: `12345678` (система попросить змінити при першому вході).

Після входу перевір доступні команди:
```bash
sudo systemctl status mywebapp
sudo systemctl restart mywebapp
sudo systemctl reload nginx
```

Перевір що інші команди недоступні:
```bash
sudo systemctl status nginx
```
Очікувано: помилка `not allowed`.

## 10. Перевірка файлу залікової книжки

```bash
cat /home/student/gradebook
```
Очікувано: `4`

## 11. Перевірка блокування ubuntu

```bash
getent passwd ubuntu
```
Якщо користувач існує — перевір що він заблокований:
```bash
sudo passwd -S ubuntu
```
Очікувано: `L` у другому полі (locked).