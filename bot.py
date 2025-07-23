#!/usr/bin/env python3
import os
import logging
import ssl
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters
from ldap3 import Server, Connection, ALL, SIMPLE, Tls

load_dotenv()
TG_TOKEN = os.getenv('TG_TOKEN')
AD_SERVER = os.getenv('AD_SERVER')
AD_PORT = int(os.getenv('AD_PORT', 636))
AD_USE_SSL = os.getenv('AD_USE_SSL', 'true').lower() == 'true'
AD_START_TLS = os.getenv('AD_START_TLS', 'false').lower() == 'true'
AD_USER = os.getenv('AD_USER')
AD_PASSWORD = os.getenv('AD_PASSWORD')
BASE_DN = os.getenv('BASE_DN')
ALLOWED_ADMINS = {int(x) for x in os.getenv('ALLOWED_ADMINS', '').split(',') if x.strip()}

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

tls_config = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLS)

def create_and_bind_connection():
    bind_user = AD_USER
    if '\\' in bind_user:
        domain, user = bind_user.split('\\', 1)
        bind_user = f'{user}@{domain}'
    server = Server(AD_SERVER, port=AD_PORT, use_ssl=AD_USE_SSL, get_info=ALL, tls=tls_config)
    conn = Connection(server, user=bind_user, password=AD_PASSWORD, authentication=SIMPLE, auto_bind=False)
    if AD_START_TLS:
        conn.open()
        conn.start_tls()
    conn.bind()
    return conn

def reset_password(update: Update, context: CallbackContext):
    user = update.effective_user
    logger.info(f"[RESET] {datetime.now().isoformat()} - User {user.id}")
    if user.id not in ALLOWED_ADMINS:
        update.message.reply_text('❌ У вас нет прав.')
        return
    if len(context.args) != 2:
        update.message.reply_text('Использование:\n/reset <username> <new_password>')
        return
    username, new_password = context.args
    user_dn = f'CN={username},CN=Users,{BASE_DN}'
    try:
        conn = create_and_bind_connection()
        conn.extend.microsoft.modify_password(user_dn, new_password)
        if conn.result.get('result') == 0:
            update.message.reply_text(
                f'✅ Пароль `{username}` сброшен на `{new_password}`',
                parse_mode='Markdown'
            )
        else:
            update.message.reply_text(f'❌ {conn.result.get("message", "")}')
    except Exception as e:
        logger.exception('')
        update.message.reply_text(f'❌ {e}')
    finally:
        if 'conn' in locals() and conn.bound:
            conn.unbind()

if __name__ == '__main__':
    updater = Updater(TG_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(
        CommandHandler(
            'reset', reset_password,
            filters=Filters.chat_type.private | Filters.chat_type.group
        )
    )
    updater.start_polling()
    updater.idle()
