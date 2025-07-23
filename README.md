# AD Reset Telegram Bot

Бот на Python, позволяющий сбрасывать пароли пользователей Active Directory по команде в Telegram. Поддерживает подключение к AD через LDAPS (порт 636) или LDAP+STARTTLS (порт 389).

## Функциональность

* Принимает команду `/reset <username> <new_password>` от разрешённых администраторов
* Подключается к контроллеру домена через LDAPS или LDAP+STARTTLS
* Преобразует NTLM-пользователя в UPN (`DOMAIN\\user` → `user@DOMAIN`)
* Выполняет сброс пароля и возвращает результат операции в чат

## Требования

* Python 3.11+ или 3.12
* Docker и Docker Compose (опционально)
* Доступ по сети к контроллеру AD (порт 636 или 389)

## Параметры окружения (`.env`)

```dotenv
TG_TOKEN=ваш_токен_бота
AD_SERVER=dc01.metal.loc       # DNS-имя или IP контроллера
AD_PORT=389                    # 636 для LDAPS, 389 для StartTLS
AD_USE_SSL=false               # true для чистого LDAPS
AD_START_TLS=true              # true для LDAP+StartTLS
AD_USER=metal.loc\\rb-bot     # UPN или DOMAIN\\user
AD_PASSWORD=пароль_сервисного_акка
BASE_DN=DC=metal,DC=loc         # Базовый DN
ALLOWED_ADMINS=123456789,987654321  # Telegram user_id администраторов
```

## Установка через Docker Compose

1. Склонируйте репозиторий и перейдите в папку проекта:

   ```bash
   git clone <repo-url>
   cd ad-reset-bot
   ```
2. Создайте файл `.env` с параметрами, приведёнными выше.
3. Подготовьте `requirements.txt` и `Dockerfile`.
4. Запустите контейнеры:

   ```bash
   docker-compose build
   docker-compose up -d
   ```
5. Проверьте логи:

   ```bash
   docker-compose logs -f ad-bot
   ```

## Локальный запуск (без Docker)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Безопасность

* Храните `.env` в защищённом каталоге и с правами `600`.
* Используйте учётную запись с минимально необходимыми правами в AD.
* Настройте TLS-валидацию, заменив `ssl.CERT_NONE` на `ssl.CERT_REQUIRED` после добавления корневого CA.
* Ограничьте доступ к контейнеру/серверу по сетевым политикам.
