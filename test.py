from ldap3 import Server, Connection, NTLM, ALL, Tls
import ssl

# Параметры из .env
AD_SERVER   = "dc01.metal.loc"
AD_PORT     = 389
AD_START_TLS= True
AD_USER     = "metal.loc\\Administrator"
AD_PASSWORD = "Root0000"
BASE_DN     = "DC=metal,DC=loc"

# Настройка TLS (без валидации, в продакшене стоит валидировать)
tls_config = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLS)

# Создаём сервер
server = Server(AD_SERVER, port=AD_PORT, use_ssl=False, get_info=ALL, tls=tls_config)
# Готовим соединение
conn = Connection(server, user=AD_USER, password=AD_PASSWORD, authentication=NTLM, auto_bind=False)

# StartTLS
conn.open()
conn.start_tls()
conn.bind()

# ДН пользователя, у которого сбрасываем пароль:
user_dn = f"CN=rab1,CN=Users,{BASE_DN}"

# Сброс пароля
conn.extend.microsoft.modify_password(user_dn, 'Aa123456')
print(conn.result)
