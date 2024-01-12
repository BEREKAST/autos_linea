import datetime
from flask import Blueprint, render_template
from config.database import connect_to_database
from flask import Flask, Response, jsonify, request
from .sucursal_id import sucursal_fl1
from .sucursal_methods import sucursal_fl2
from .images_sucursal import images_sucursal_fl2
from utils.time import timedelta_to_string,timedelta_to_milliseconds
from utils.serializer import resultados_a_json, convertir_a_datetime

sucursal_fl = Blueprint('sucursal', __name__)


sucursal_fl.register_blueprint(sucursal_fl1)
sucursal_fl.register_blueprint(sucursal_fl2)
sucursal_fl.register_blueprint(images_sucursal_fl2)

def process_sucursal(connection):
    try:
        with connection.cursor() as cursor:
            sql_sucursal = """SELECT * FROM sucursal;"""
            cursor.execute(sql_sucursal)
            sucursal_results = resultados_a_json(cursor)

            for sucursal_record in sucursal_results:

                for key in ['created', 'lastUpdate']: 
                    if sucursal_record[key]:
                        sucursal_record_2=convertir_a_datetime(sucursal_record[key])
                        sucursal_record[key] = int(sucursal_record_2.timestamp() * 1000)


                id_sucursal = sucursal_record['id_sucursal']

                sql_sucursales_imagenes = """SELECT * FROM images_sucursal
                                             WHERE id_sucursal = ?;"""
                cursor.execute(sql_sucursales_imagenes, (id_sucursal,))
                sucursal_images = resultados_a_json(cursor)
                sucursal_record['sucursal_images'] = sucursal_images

                sql_articulos = """SELECT articulo.ano,articulo.categoria, articulo.color,articulo.created,articulo.descripcion,
                articulo.enable,articulo.id_articulo,
                articulo.kilometraje,articulo.lastInventoryUpdate,articulo.lastUpdate,articulo.mainImage,
                articulo.marca,articulo.modelo,articulo.precio
                FROM articulo 
                                   JOIN articulo_sucursal ON articulo.id_articulo = articulo_sucursal.id_articulo
                                   WHERE articulo_sucursal.id_sucursal = ?;"""
                cursor.execute(sql_articulos, (id_sucursal,))
                articulos_list = resultados_a_json(cursor)
                for articulos in articulos_list:
                    for key in ['created', 'lastUpdate']: 
                        if articulos[key]:
                            usuarios_info_2=convertir_a_datetime(articulos[key])
                            articulos[key] = int(usuarios_info_2.timestamp() * 1000)

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

            return sucursal_results
    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500



    
@sucursal_fl.route('/', methods=['GET'])
def get_sucursal_all():
    with connect_to_database() as connection:
        try:
            # Obtener información de los pedidos del proveedor
            sucursales = process_sucursal(connection)
            return jsonify({"success": True, "data": sucursales})
        except Exception as e:
            return jsonify({"error": "Database error: {}".format(e)}), 500