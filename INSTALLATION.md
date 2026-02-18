# 📦 Подробная инструкция по установке KUR VPN Bot

Эта инструкция проведёт вас через все шаги установки бота на сервер.

## 🖥 Требования к серверу

### Минимальные характеристики:
- **OS:** Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **RAM:** 1 GB (рекомендуется 2 GB)
- **CPU:** 1 core (рекомендуется 2 cores)
- **Disk:** 10 GB свободного места
- **Network:** Стабильное интернет-соединение

### Программное обеспечение:
- Python 3.10 или выше
- Git
- 3x-ui панель (будет установлена далее)

---

## 📝 Шаг 1: Подключение к серверу

```bash
ssh root@your-server-ip
```

Обновите систему:
```bash
apt update && apt upgrade -y  # Debian/Ubuntu
# или
yum update -y  # CentOS/RHEL
```

---

## 🐍 Шаг 2: Установка Python 3.10+

### Ubuntu/Debian:
```bash
apt install python3 python3-pip python3-venv git -y
```

### CentOS/RHEL:
```bash
yum install python3 python3-pip git -y
```

Проверка версии:
```bash
python3 --version  # Должно быть 3.10+
```

---

## 🔐 Шаг 3: Установка 3x-ui панели

Установите 3x-ui:
```bash
bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)
```

После установки:
1. Откройте в браузере: `http://your-server-ip:2053`
2. Войдите (логин/пароль по умолчанию: `admin/admin`)
3. **Обязательно смените пароль!**

### Настройка Inbound (обязательно):

1. В панели 3x-ui перейдите в **Inbounds** → **Add Inbound**
2. Настройки:
   - **Protocol:** VLESS
   - **Network:** TCP
   - **Security:** Reality
   - **Port:** 443 (или любой другой)
   - **Enable:** ✅
3. Нажмите **Create**
4. Запомните/скопируйте:
   - Public Key
   - Short ID
   - Server Name (SNI)

---

## 📥 Шаг 4: Клонирование проекта

Создайте папку для бота:
```bash
mkdir -p /opt/kur_vpn
cd /opt/kur_vpn
```

Клонируйте репозиторий (или загрузите архив):
```bash
git clone https://github.com/ваш-username/KUR_VPN.git .
# Или распакуйте архив:
# unzip kur_vpn.zip
```

---

## 🔧 Шаг 5: Настройка виртуального окружения

Создайте виртуальное окружение:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Установите зависимости:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ⚙️ Шаг 6: Конфигурация бота

Создайте `.env` файл:
```bash
cp .env.example .env
nano .env  # или используйте vim/vi
```

Заполните данные:
```env
TOKEN=ваш_токен_от_botfather
API_HOST=http://127.0.0.1:2053
API_USERNAME=admin
API_PASSWORD=ваш_пароль_3xui
```

**Получение токена бота:**
1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`
3. Введите имя и username бота
4. Скопируйте токен в `.env`

Сохраните файл: `Ctrl+X` → `Y` → `Enter`

---

## 🗄 Шаг 7: Инициализация базы данных

Примените миграции:
```bash
alembic upgrade head
```

Должно появиться:
```
INFO  [alembic.runtime.migration] Running upgrade  -> xxxxx, init
```

---

## 🚀 Шаг 8: Первый запуск

Запустите бота вручную для проверки:
```bash
python aiogbot.py
```

Вы должны увидеть:
```
INFO - Bot starting...
INFO - Bot polling started
```

Откройте Telegram, найдите вашего бота и отправьте `/start`.

Если всё работает — нажмите `Ctrl+C` для остановки.

---

## 🔄 Шаг 9: Запуск в фоне (systemd)

Создайте systemd service:
```bash
nano /etc/systemd/system/kur_vpn_bot.service
```

Вставьте:
```ini
[Unit]
Description=KUR VPN Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/kur_vpn
Environment="PATH=/opt/kur_vpn/.venv/bin"
ExecStart=/opt/kur_vpn/.venv/bin/python /opt/kur_vpn/aiogbot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Сохраните и активируйте:
```bash
systemctl daemon-reload
systemctl enable kur_vpn_bot
systemctl start kur_vpn_bot
```

Проверка статуса:
```bash
systemctl status kur_vpn_bot
```

Просмотр логов:
```bash
journalctl -u kur_vpn_bot -f
# Или
tail -f /opt/kur_vpn/bot.log
```

---

## 🛠 Управление ботом

**Остановить бота:**
```bash
systemctl stop kur_vpn_bot
```

**Перезапустить бота:**
```bash
systemctl restart kur_vpn_bot
```

**Посмотреть логи:**
```bash
journalctl -u kur_vpn_bot -n 100 --no-pager
```

---

## 🔥 Настройка Firewall

Откройте необходимые порты:
```bash
# UFW (Ubuntu/Debian)
ufw allow 2053/tcp  # 3x-ui panel
ufw allow 443/tcp   # VPN port
ufw enable

# Firewalld (CentOS/RHEL)
firewall-cmd --permanent --add-port=2053/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --reload
```

---

## 📊 Мониторинг и обслуживание

### Проверка работы бота:
```bash
systemctl status kur_vpn_bot
```

### Просмотр активных пользователей:
```bash
sqlite3 kur_vpn.db "SELECT COUNT(*) FROM users;"
```

### Бэкап базы данных (рекомендуется делать регулярно):
```bash
cp kur_vpn.db kur_vpn_backup_$(date +%Y%m%d).db
```

### Обновление бота:
```bash
cd /opt/kur_vpn
git pull  # или загрузите новую версию
source .venv/bin/activate
pip install -r requirements.txt --upgrade
alembic upgrade head
systemctl restart kur_vpn_bot
```

---

## 🐛 Решение проблем

### Бот не запускается
```bash
# Проверьте логи
journalctl -u kur_vpn_bot -n 50

# Проверьте .env файл
cat .env

# Попробуйте запустить вручную
cd /opt/kur_vpn
source .venv/bin/activate
python aiogbot.py
```

### Ошибка подключения к 3x-ui
```bash
# Проверьте что 3x-ui запущен
systemctl status x-ui

# Проверьте доступность панели
curl http://127.0.0.1:2053
```

### База данных повреждена
```bash
# Восстановите из бэкапа
cd /opt/kur_vpn
cp kur_vpn_backup_YYYYMMDD.db kur_vpn.db
systemctl restart kur_vpn_bot
```

---

## ✅ Финальная проверка

Убедитесь что всё работает:

1. ✅ Бот отвечает на `/start`
2. ✅ Создание нового пользователя работает
3. ✅ VPN ключ выдаётся
4. ✅ QR-код генерируется
5. ✅ Реферальная ссылка создаётся
6. ✅ systemd сервис запускается автоматически

---

## 📞 Поддержка

Если возникли проблемы при установке — свяжитесь с продавцом.

Предоставьте:
- Версию ОС (`cat /etc/os-release`)
- Версию Python (`python3 --version`)
- Логи бота (`journalctl -u kur_vpn_bot -n 100`)

---

**Успешной установки! 🚀**
