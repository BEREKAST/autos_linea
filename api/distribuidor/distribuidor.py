from datetime import datetime, time,timedelta
from flask import Blueprint, render_template
from config.database import connect_to_database
from flask import Flask, Response, jsonify, request
from .distribuidor_id import distribuidor_fl1
from .distribuidor_methods import distribuidor_fl2
# from api.sucursal.sucursal_id import get_sucursal_for_distribuidor
from utils.time import timedelta_to_string,timedelta_to_milliseconds


distribuidor_fl = Blueprint('distribuidor', __name__)
distribuidor_fl.register_blueprint(distribuidor_fl1,)
distribuidor_fl.register_blueprint(distribuidor_fl2,)




def process_distribuidor(connection):
    try:
        with connection.cursor() as cursor:
            sql_distribuidor = "SELECT * FROM distribuidor"
            cursor.execute(sql_distribuidor)
            distribuidores = cursor.fetchall()
            
            for distribuidor in distribuidores:
                id_distribuidor = distribuidor['id_distribuidor']

                for key, value in distribuidor.items():
                    if isinstance(value, datetime):
                        distribuidor[key] = int(value.timestamp() * 1000)

                sql_sucursales = """
                    SELECT s.* FROM sucursal s
                    JOIN distribuidor_sucursal ds ON s.id_sucursal = ds.id_sucursal
                    WHERE ds.id_distribuidor = ?
                """
                cursor.execute(sql_sucursales, (id_distribuidor,))
                sucursales = cursor.fetchall()

                for sucursal in sucursales:
                    for key, value in sucursal.items():
                        if isinstance(value, datetime):
                            sucursal[key] = int(value.timestamp() * 1000)

                distribuidor['sucursales'] = sucursales


                sql_horarios = "SELECT * FROM horarios_distribuidor WHERE id_distribuidor = ?"
                cursor.execute(sql_horarios, (id_distribuidor,))
                horarios_raw = cursor.fetchall()
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
                marcas_raw = cursor.fetchall()
                marcas = [marca['marca'] for marca in marcas_raw]  

                distribuidor['marcas'] = marcas

            return distribuidores
    finally:
        connection.close()




    
@distribuidor_fl.route('/', methods=['GET'])
def get_distribuidor():
    with connect_to_database() as connection:
        try:
            # Obtener información de los pedidos del proveedor
            distribuidor = process_distribuidor(connection)
            return jsonify({"success": True, "data": distribuidor})
        except Exception as e:
            return jsonify({"error": "Database error: {}".format(e)}), 500