#!/bin/bash
set -e

DB_PASSWORD="SecurePass123!"
APP_DIR="/opt/mywebapp"
GRADEBOOK_N=4
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== 1. Встановлення пакетів ==="
apt-get update -y
apt-get install -y python3 python3-pip python3-venv nginx mariadb-server

echo "=== 2. Створення користувачів ==="

if ! id student &>/dev/null; then
    useradd -m -s /bin/bash student
    usermod -aG sudo student
    echo "student:student" | chpasswd
fi

if ! id teacher &>/dev/null; then
    useradd -m -s /bin/bash teacher
    usermod -aG sudo teacher
    echo "teacher:12345678" | chpasswd
    chage -d 0 teacher
fi

if ! id app &>/dev/null; then
    useradd -r -s /usr/sbin/nologin app
fi

if ! id operator &>/dev/null; then
    useradd -m -s /bin/bash -N -g users operator
    echo "operator:12345678" | chpasswd
    chage -d 0 operator
fi

echo "=== 3. Sudo-правила для operator ==="
cat > /etc/sudoers.d/operator << 'EOF'
operator ALL=(ALL) NOPASSWD: \
    /bin/systemctl start mywebapp, \
    /bin/systemctl stop mywebapp, \
    /bin/systemctl restart mywebapp, \
    /bin/systemctl status mywebapp, \
    /bin/systemctl reload nginx
EOF
chmod 440 /etc/sudoers.d/operator

echo "=== 4. Створення бази даних ==="
systemctl start mariadb
systemctl enable mariadb

mysql -u root << EOF
CREATE DATABASE IF NOT EXISTS mywebapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'mywebapp'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON mywebapp.* TO 'mywebapp'@'localhost';
FLUSH PRIVILEGES;
EOF

echo "=== 5. Розгортання застосунку ==="
mkdir -p "$APP_DIR"
cp -r "$SCRIPT_DIR/../app/"* "$APP_DIR/"

python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

chown -R app:app "$APP_DIR"

echo "=== 6. Встановлення systemd-сервісу ==="
sed "s/REPLACE_WITH_PASSWORD/${DB_PASSWORD}/g" \
    "$SCRIPT_DIR/mywebapp.service" > /etc/systemd/system/mywebapp.service

cp "$SCRIPT_DIR/mywebapp.socket" /etc/systemd/system/mywebapp.socket

echo "=== 7. Запуск сервісу ==="
systemctl daemon-reload
systemctl enable mywebapp.socket
systemctl start mywebapp.socket
systemctl enable mywebapp
systemctl start mywebapp

echo "=== 8. Налаштування nginx ==="
cp "$SCRIPT_DIR/nginx.conf" /etc/nginx/sites-available/mywebapp
ln -sf /etc/nginx/sites-available/mywebapp /etc/nginx/sites-enabled/mywebapp
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl enable nginx
systemctl restart nginx

echo "=== 9. Файл залікової книжки ==="
echo "$GRADEBOOK_N" > /home/student/gradebook
chown student:student /home/student/gradebook

echo "=== 10. Блокування дефолтного користувача ubuntu ==="
if id ubuntu &>/dev/null; then
    usermod -L ubuntu
    usermod -s /usr/sbin/nologin ubuntu
fi

echo "=== Готово! ==="