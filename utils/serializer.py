import datetime
import json
import decimal

def convertir_a_datetime(cadena):
    if len(cadena.split('.')[-1]) == 7:
        cadena = cadena[:-1]
    formato_fecha = "%Y-%m-%d %H:%M:%S.%f"
    try:
        return datetime.datetime.strptime(cadena, formato_fecha)
    except ValueError:
        # Intenta un formato sin microsegundos si falla el primero
        formato_fecha = "%Y-%m-%d %H:%M:%S"
        return datetime.datetime.strptime(cadena, formato_fecha)


def serializar_valor(valor):
    """ Convierte valores no serializables en tipos serializables. """
    if isinstance(valor, datetime.datetime):
        # Convierte datetime a timestamp Unix (en segundos)
        print(valor.timestamp())
        return int(valor.timestamp())
    elif isinstance(valor, datetime.date):
        # Convierte date a timestamp Unix (considerando la fecha con hora 00:00:00)
        print(datetime.datetime.combine(valor, datetime.time(0, 0)).timestamp())
        return int(datetime.datetime.combine(valor, datetime.time(0, 0)).timestamp())
    elif isinstance(valor, decimal.Decimal):
        # Convierte Decimal a float
        return float(valor)
    else:
        return valor

def resultados_a_json(cursor, unico_resultado=False):
    """ Convierte los resultados de pyodbc a un formato JSON serializable. """
    columnas = [columna[0] for columna in cursor.description]
    resultados_crudos = cursor.fetchone() if unico_resultado else cursor.fetchall()

    if unico_resultado:
        if resultados_crudos is None:
            return None
        return {columnas[i]: serializar_valor(valor) for i, valor in enumerate(resultados_crudos)}

    return [{columnas[i]: serializar_valor(valor) for i, valor in enumerate(fila)} for fila in resultados_crudos]

# # Ejemplo de uso con fetchall()
# try:
#     with connect_to_database() as connection:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM mi_tabla")
#             resultados = resultados_a_json(cursor)
#             print(json.dumps(resultados))  # Convierte a string JSON para imprimir o enviar en una respuesta
# except Exception as e:
#     print(f"Error: {e}")

# # Ejemplo de uso con fetchone()
# try:
#     with connect_to_database() as connection:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM mi_tabla WHERE id = 1")
#             resultado = resultados_a_json(cursor, unico_resultado=True)
#             if resultado:
#                 print(json.dumps(resultado))  # Convierte a string JSON para imprimir o enviar en una respuesta
#             else:
#                 print("No se encontró el registro.")
# except Exception as e:
#     print(f"Error: {e}")


# from utils.serializer import resultados_a_json, convertir_a_datetime

# resultados_a_json(cursor, unico_resultado=True)


# resultados_a_json(cursor)


# cursor.fetchall()

# cursor.fetchone()

# convertir_a_datetime()

#             if usuario_info:
#                 for key in ['created', 'lastUpdate']: 
#                     if usuario_info[key]:
#                         usuarios_info_2=convertir_a_datetime(usuario_info[key])
#                         usuario_info[key] = int(usuarios_info_2.timestamp() * 1000)


# for usuario_record in usuario_results:
#                  for key in ['created', 'lastUpdate']: 
#                     if usuario_record[key]:
#                         usuarios_info_2=convertir_a_datetime(usuario_record[key])
#                         usuario_record[key] = int(usuarios_info_2.timestamp() * 1000)