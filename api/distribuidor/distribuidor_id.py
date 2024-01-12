from flask import Blueprint, render_template
from config.database import connect_to_database
from flask import Flask, Response, jsonify, request
from utils.time import timedelta_to_string,timedelta_to_milliseconds
from utils.serializer import resultados_a_json, convertir_a_datetime

distribuidor_fl1=Blueprint('distribuidor_id', __name__)


def process_distribuidor_por_id(connection, id_distribuidor):
    try:
        with connection.cursor() as cursor:
            sql_distribuidor = "SELECT * FROM distribuidor WHERE id_distribuidor = ?"
            cursor.execute(sql_distribuidor, (id_distribuidor,))
            distribuidor = resultados_a_json(cursor, unico_resultado=True)
            if distribuidor:
                for key in ['created', 'lastUpdate']:
                    if distribuidor[key]:
                        usuarios_info_2=convertir_a_datetime(distribuidor[key])

                        distribuidor[key] = int(usuarios_info_2.timestamp() * 1000)

                sql_sucursales = """
                    SELECT s.* FROM sucursal s
                    JOIN distribuidor_sucursal ds ON s.id_sucursal = ds.id_sucursal
                    WHERE ds.id_distribuidor = ?
                """
                cursor.execute(sql_sucursales, (id_distribuidor,))
                sucursales = resultados_a_json(cursor)

                for sucursal in sucursales:
                    for key in ['created', 'lastUpdate']:
                        if sucursal[key]:
                            usuarios_info_2=convertir_a_datetime(sucursal[key])
                            sucursal[key] = int(usuarios_info_2.timestamp() * 1000)

                distribuidor['sucursales'] = sucursales

                sql_horarios = "SELECT * FROM horarios_distribuidor WHERE id_distribuidor = ?"
                cursor.execute(sql_horarios, (id_distribuidor,))

                horarios_raw = resultados_a_json(cursor)
                horarios_distribuidor= {}
                for horario in horarios_raw:
                    dia = horario['day']
                    horarios_distribuidor[dia] = {
                        'open': int(timedelta_to_milliseconds(horario['open'])),
                        'close': int(timedelta_to_milliseconds(horario['close']))
                    }

                distribuidor['horarios_distribuidor'] = horarios_distribuidor
                
                sql_marcas = "SELECT marca FROM marcas_distribuidor WHERE id_distribuidor = ?"
                cursor.execute(sql_marcas, (id_distribuidor,))
                marcas_raw = resultados_a_json(cursor)
                marcas = [marca['marca'] for marca in marcas_raw]  

                distribuidor['marcas'] = marcas
            return distribuidor
    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500



    
@distribuidor_fl1.route('/<int:distribuidor_id>', methods=['GET'])
def get_distribuidor_by_id(distribuidor_id):
    with connect_to_database() as con:
        try:
            distribuidor_by_id= process_distribuidor_por_id(con,distribuidor_id)
            if distribuidor_by_id:
                return jsonify({"success": True, "data": distribuidor_by_id})
            else:
                return jsonify({"error": f"distribuidor with ID {distribuidor_id} not found"}), 404
        except Exception as e :
            return jsonify({"error":"Data Base erorr {}".format(e)})