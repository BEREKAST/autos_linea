from contextlib import asynccontextmanager
import pyodbc
from dotenv import load_dotenv
import os
from contextlib import contextmanager
# Carga las variables de entorno del archivo .env
load_dotenv()

# Obtén las variables de entorno
driver = os.getenv('DB_DRIVER', '{SQL Server}')  # Usa un valor por defecto en caso de que no esté definido en .env
server = os.getenv('DB_SERVER')
database = os.getenv('DB_DATABASE')
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')

# Cadena de conexión usando variables de entorno
connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

@contextmanager
def connect_to_database():
    connection = None
    try:
        connection = pyodbc.connect(connection_string)
        yield connection
    except Exception as ex:
        print("Error durante la conexión:", ex)
        if connection is not None:
            connection.close()
    finally:
        if connection is not None:
            connection.close()
            print("La conexión ha finalizado.")

# from contextlib import asynccontextmanager
# import asyncio
# import pyodbc
# from dotenv import load_dotenv
# import os

# load_dotenv()

# driver = os.getenv('DB_DRIVER', '{SQL Server}')  
# server = os.getenv('DB_SERVER')
# database = os.getenv('DB_DATABASE')
# username = os.getenv('DB_USERNAME')
# password = os.getenv('DB_PASSWORD')

# connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# # Define una función síncrona para conectar a la base de datos
# def sync_db_connect(connection_str):
#     return pyodbc.connect(connection_str)

# # Utiliza asynccontextmanager para crear un administrador de contexto asíncrono
# @asynccontextmanager
# async def connect_to_database():
#     loop = asyncio.get_running_loop()
#     connection = await loop.run_in_executor(None, sync_db_connect, connection_string)
#     try:
#         yield connection
#     except Exception as ex:
#         print("Error durante la conexión:", ex)
#     finally:
#         connection.close()
#         print("La conexión ha finalizado.")



# @asynccontextmanager
# async def connect_to_database():
#     connection = await aiomysql.connect(


#         host=os.getenv('DB_HOST'),
#         port=int(os.getenv('DB_PORT')),  
#         user=os.getenv('DB_USER'),
#         password=os.getenv('DB_PASS'),
#         db=os.getenv('DB_NAME'),
#         cursorclass=aiomysql.DictCursor
#     )
#     try:
#         yield connection
#         print("Conexión establecida")
#     finally:
#         connection.close()


        # host='viaduct.proxy.rlwy.net',
        # port=44970,
        # user='root',
        # password='CG-AeB51DAfgCcb2A5-g32EabBcaEBAC',
        # db='railway',
        # cursorclass=aiomysql.DictCursor

        # host='containers-us-west-24.railway.app',
        # port=5828,
        # user='root',
        # password='IJDLZQVMpvbnBAuOsGBg',
        # db='railway',
        # cursorclass=aiomysql.DictCursor
                # host='127.0.0.1',
        # port=3306,
        # user='admin_autos',
        # password='zzE]vjfK[AzkAGXg',
        # db='autos_api',
        # cursorclass=aiomysql.DictCursor