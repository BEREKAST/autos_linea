# from flask import Flask, request, jsonify
# from flask import Blueprint
# from config.database import connect_to_database

# catalogo_fl2 = Blueprint('catalogo_post', __name__)

# @catalogo_fl2.route('/catalogo', methods=['POST'])
# async def crear_catalogo():
#     try:
#         async with connect_to_database() as connection:
#             data = request.json
#             campos_requeridos = [ 'id_catalogo','especificaciones',
#                                   'main_image', 'descripcion']
#             print(data)
#             if not all(campo in data for campo in campos_requeridos):
#                 return jsonify({"error": "Faltan campos requeridos"}), 400
                
#             async with connection.cursor() as cursor:
#                 sql = """INSERT INTO catalogo (
#              id_catalogo, especificaciones,
#              main_image, descripcion,  created, lastUpdate,lastInventoryUpdate
#          ) VALUES (%s, %s, %s, %s, 
#          CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)"""

#                 valores=(
#                     data['id_catalogo'],
#                     data['especificaciones'],
#                     data['main_image'],
#                     data['descripcion'],
#                 )
#                 await cursor.execute(sql, valores)
#                 await connection.commit()

#             return jsonify({"success": True, "message": "catalogo creado exitosamente"}), 201

#     except Exception as e:
#         return jsonify({"error": f"Error en la base de datos: {e}"}), 500

# @catalogo_fl2.route('/catalogo/<int:id_catalogo>', methods=['PUT'])
# async def actualizar_catalogo(id_catalogo):
#     try:
#         async with connect_to_database() as connection:
#             data = request.json
#             campos_permitidos = ['especificaciones', 'main_image', 'descripcion']
            
#             if not any(campo in data for campo in campos_permitidos):
#                 return jsonify({"error": "Se requiere al menos un campo para actualizar"}), 400
                
#             async with connection.cursor() as cursor:
#                 sql_update = "UPDATE catalogo SET "
#                 valores = []

#                 for campo in campos_permitidos:
#                     if campo in data:
#                         sql_update += f"{campo} = %s, "
#                         valores.append(data[campo])

#                 sql_update = sql_update.rstrip(', ')

#                 sql_update += " WHERE id_catalogo = %s"
#                 valores.append(id_catalogo)

#                 await cursor.execute(sql_update, valores)
#                 await connection.commit()

#             return jsonify({"success": True, "message": f"Catálogo con ID {id_catalogo} actualizado exitosamente"}), 200

#     except Exception as e:
#         return jsonify({"error": f"Error en la base de datos: {e}"}), 500


# @catalogo_fl2.route('/catalogo/<int:id_catalogo>', methods=['DELETE'])
# async def eliminar_catalogo(id_catalogo):
#     try:
#         async with connect_to_database() as connection:
#             async with connection.cursor() as cursor:
#                 sql_delete = "DELETE FROM catalogo WHERE id_catalogo = %s"
#                 await cursor.execute(sql_delete, (id_catalogo,))
#                 await connection.commit()

#             return jsonify({"success": True, "message": f"Catálogo con ID {id_catalogo} eliminado exitosamente"}), 200

#     except Exception as e:
#         return jsonify({"error": f"Error en la base de datos: {e}"}), 500
