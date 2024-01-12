from flask import Flask, request, jsonify
from flask import Blueprint
from config.database import connect_to_database
from utils.serializer import resultados_a_json, convertir_a_datetime

images_sucursal_fl2 = Blueprint('images_sucursal', __name__)


@images_sucursal_fl2.route('/images/<int:sucursal_id>', methods=['GET'])
def get_all_images_by_id(sucursal_id):
    try:
        with connect_to_database() as con:
            with con.cursor() as cursor:
                sql_id_sucursal="""
                                SELECT * FROM images_sucursal WHERE id_sucursal =?
                            """
                cursor.execute(sql_id_sucursal, sucursal_id)
                sucursal_images= resultados_a_json(cursor)  
                return jsonify(sucursal_images)
    except Exception as e:
        return jsonify({"error":f"Error en la conexion a la bd: {e}"}),500
    
@images_sucursal_fl2.route('/images', methods=['GET'])
def get_all_images():
    try:
        with connect_to_database() as con:
            with con.cursor() as cursor:
                sql_id_sucursal="""
                                SELECT * FROM images_sucursal 
                            """
                cursor.execute(sql_id_sucursal)
                sucursal_images= resultados_a_json(cursor)  
                return jsonify(sucursal_images)
    except Exception as e:
        return jsonify({"error":f"Error en la conexion a la bd: {e}"}),500
    
@images_sucursal_fl2.route('/images_sucursal', methods=['POST'])
def crear_images_sucursal():
    try:
        with connect_to_database() as connection:
            data = request.json
            campos_requeridos = [ 'id_images_sucursal','url_image',
                                  'descripcion', 'id_sucursal']
            if not all(campo in data for campo in campos_requeridos):
                return jsonify({"error": "Faltan campos requeridos"}), 400
                
            with connection.cursor() as cursor:
                sql = """INSERT INTO images_sucursal (
             id_images_sucursal, url_image,
             descripcion, id_sucursal
         ) VALUES (?, ?, ?, ?)"""

                valores=(
                    data['id_images_sucursal'],
                    data['url_image'],
                    data['descripcion'],
                    data['id_sucursal'],
                )
                cursor.execute(sql, valores)
                connection.commit()

            return jsonify({"success": True, "message": "images_sucursal creado exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500
    
@images_sucursal_fl2.route('/images/<int:id_images_sucursal>', methods=['PUT'])
def actualizar_images_sucursal(id_images_sucursal):
    try:
        with connect_to_database() as connection:
            data = request.json
            campos_permitidos = ['url_image', 'descripcion', 'id_sucursal']
            
            if not any(campo in data for campo in campos_permitidos):
                return jsonify({"error": "Se requiere al menos un campo para actualizar"}), 400
                
            with connection.cursor() as cursor:
                # Construir la consulta de actualización basada en los campos proporcionados
                sql_update = "UPDATE images_sucursal SET "
                valores = []

                for campo in campos_permitidos:
                    if campo in data:
                        sql_update += f"{campo} = ?, "
                        valores.append(data[campo])

                # Eliminar la coma y espacio finales de la consulta
                sql_update = sql_update.rstrip(', ')

                # Agregar la condición WHERE para el ID
                sql_update += " WHERE id_images_sucursal = ?"
                valores.append(id_images_sucursal)

                # Ejecutar la consulta de actualización
                cursor.execute(sql_update, valores)
                connection.commit()

            return jsonify({"success": True, "message": f"Registro con ID {id_images_sucursal} actualizado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500


@images_sucursal_fl2.route('/images/<int:id_images_sucursal>', methods=['DELETE'])
def eliminar_images_sucursal(id_images_sucursal):
    try:
        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                sql_delete = "DELETE FROM images_sucursal WHERE id_images_sucursal = ?"
                cursor.execute(sql_delete, (id_images_sucursal,))
                connection.commit()

            return jsonify({"success": True, "message": f"Registro con ID {id_images_sucursal} eliminado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500
