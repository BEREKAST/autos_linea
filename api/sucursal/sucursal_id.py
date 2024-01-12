
from flask import Blueprint, render_template
from config.database import connect_to_database
from flask import Flask, Response, jsonify, request
from utils.time import convert_milliseconds_to_datetime,convert_milliseconds_to_time_string,timedelta_to_milliseconds
from utils.serializer import resultados_a_json, convertir_a_datetime

sucursal_fl1=Blueprint('sucursal_id', __name__)

def get_sucursal_basic(connection, sucursal_id):
    try:
        with connection.cursor() as cursor:
            sql_sucursal = """SELECT * FROM sucursal WHERE id_sucursal = ?"""
            cursor.execute(sql_sucursal, (sucursal_id,))
            sucursal_info = cursor.fetchone()
            return sucursal_info
    except Exception as e:
        print(f"Error obtaining sucursal info for ID {sucursal_id}: {e}")
        return None

def get_sucursal_detail(connection, id_sucursal):
    try:
        with connection.cursor() as cursor:
            sql_sucursal = """SELECT id_sucursal, id_usuario,
                              direccion, telefono, gerente, contacto, 
                              correo_electronico, created, lastUpdate, url_logo, nombre,
                              coordenadas, horarios_de_atencion
                           FROM sucursal
                           WHERE id_sucursal = ?;"""
            cursor.execute(sql_sucursal, (id_sucursal,))
            sucursal_info = cursor.fetchone()

            if sucursal_info:
                sql_sucursales = """SELECT * FROM images_sucursal
                                    WHERE id_sucursal = ?;"""
                cursor.execute(sql_sucursales, (id_sucursal,))
                sucursal_images = resultados_a_json(cursor)
                sql_distribuidor = """SELECT usuario.*
                                      FROM usuario
                                      JOIN distribuidor_sucursal ON usuario.id_usuario = distribuidor_sucursal.id_usuario
                                      WHERE usuario.rol = 'distribuidor' 
                                      AND distribuidor_sucursal.id_sucursal = ?;"""
                cursor.execute(sql_distribuidor, (id_sucursal,))
                distribuidor_list = resultados_a_json(cursor)
                sucursal_info['sucursal_images'] = sucursal_images
                sucursal_info['sucursal_distribuidores'] = distribuidor_list

            return sucursal_info
    except Exception as e:
        print(f"Error obtaining detailed sucursal info for ID {id_sucursal}: {e}")
        return None
    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500

def process_sucursal_por_id(connection, id_sucursal):
    try:
        with connection.cursor() as cursor:
            sql_sucursal = "SELECT * FROM sucursal WHERE id_sucursal = ?;"
            cursor.execute(sql_sucursal, (id_sucursal,))
            sucursal_record = cursor.fetchone()

            if sucursal_record:
                for key in ['created', 'lastUpdate']:
                    if sucursal_record[key]:
                        sucursal_record[key] = int(sucursal_record[key].timestamp() * 1000)

                sql_sucursales_imagenes = "SELECT * FROM images_sucursal WHERE id_sucursal = ?;"
                cursor.execute(sql_sucursales_imagenes, (id_sucursal,))
                sucursal_images = resultados_a_json(cursor)
                sucursal_record['sucursal_images'] = sucursal_images

                sql_articulos = """SELECT articulo.* FROM articulo
                                   JOIN articulo_sucursal ON articulo.id_articulo = articulo_sucursal.id_articulo
                                   WHERE articulo_sucursal.id_sucursal = ?;"""
                cursor.execute(sql_articulos, (id_sucursal,))
                articulos_list = resultados_a_json(cursor)

                for articulo in articulos_list:
                    for key in ['created', 'lastUpdate', 'lastInventoryUpdate']:
                        if articulo[key]:

                            usuarios_info_2=convertir_a_datetime(articulo[key])

                            articulo[key] = int(usuarios_info_2.timestamp() * 1000)

        

                sucursal_record['sucursal_articulos'] = articulos_list
                sql_horarios_sucursal = "SELECT * FROM horarios_sucursal WHERE id_sucursal = ?"
                cursor.execute(sql_horarios_sucursal, (id_sucursal,))
                horarios_raw = resultados_a_json(cursor)
                horarios_sucursal = {}
                for horario in horarios_raw:
                    dia = horario['day']
                    horarios_sucursal[dia] = {
                        'open': timedelta_to_milliseconds(horario['open']),
                        'close': timedelta_to_milliseconds(horario['close'])
                    }

                sucursal_record['horarios_sucursal'] = horarios_sucursal
            return sucursal_record
    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500


@sucursal_fl1.route('/<int:sucursal_id>', methods=['GET'])
def get_sucursal_by_id(sucursal_id):
    with connect_to_database() as con:
        try:
            sucursal_info = process_sucursal_por_id(con, sucursal_id)
            if sucursal_info:
                return jsonify({"success": True, "data": sucursal_info})
            else:
                return jsonify({"error": f"sucursal with ID {sucursal_id} not found"}), 404
        except Exception as e :
            return jsonify({"error":"Data Base erorr {}".format(e)})