# from flask import Flask, request, jsonify
# from flask import Blueprint
# from config.database import connect_to_database

# images_catalogo_fl2 = Blueprint('images_catalogo', __name__)

    
# @images_catalogo_fl2.route('/images', methods=['GET'])
# async def get_all_images():
#     try:
#         async with connect_to_database() as con:
#             async with con.cursor() as cursor:
#                 sql_id_catalogo="""
#                                 SELECT * FROM images_catalogo 
#                             """
#                 await cursor.execute(sql_id_catalogo)
#                 catalogo_images= await cursor.fetchall()  
#                 return jsonify(catalogo_images)
#     except Exception as e:
#         return jsonify({"error":f"Error en la conexion a la bd: {e}"}),500
    
# @images_catalogo_fl2.route('/images/<int:catalogo_id>', methods=['GET'])
# async def get_all_images_by_id(catalogo_id):
#     try:
#         async with connect_to_database() as con:
#             async with con.cursor() as cursor:
#                 sql_id_catalogo="""
#                                 SELECT * FROM images_catalogo WHERE id_catalogo =%s
#                             """
#                 await cursor.execute(sql_id_catalogo, catalogo_id)
#                 catalogo_images= await cursor.fetchall()  
#                 return jsonify(catalogo_images)
#     except Exception as e:
#         return jsonify({"error":f"Error en la conexion a la bd: {e}"}),500

    
# @images_catalogo_fl2.route('/images_catalogo', methods=['POST'])
# async def crear_images_catalogo():
#     try:
#         async with connect_to_database() as connection:
#             data = request.json
#             campos_requeridos = [ 'id_images_catalogo','url_image',
#                                   'descripcion', 'id_catalogo']
#             if not all(campo in data for campo in campos_requeridos):
#                 return jsonify({"error": "Faltan campos requeridos"}), 400
                
#             async with connection.cursor() as cursor:
#                 sql = """INSERT INTO images_catalogo (
#              id_images_catalogo, url_image,
#              descripcion, id_catalogo
#          ) VALUES (%s, %s, %s, %s)"""

#                 valores=(
#                     data['id_images_catalogo'],
#                     data['url_image'],
#                     data['descripcion'],
#                     data['id_catalogo'],
#                 )
#                 await cursor.execute(sql, valores)
#                 await connection.commit()

#             return jsonify({"success": True, "message": "images_catalogo creado exitosamente"}), 201

#     except Exception as e:
#         return jsonify({"error": f"Error en la base de datos: {e}"}), 500
    
# @images_catalogo_fl2.route('/images/<int:id_images_catalogo>', methods=['PUT'])
# async def actualizar_images_catalogo(id_images_catalogo):
#     try:
#         async with connect_to_database() as connection:
#             data = request.json
#             campos_permitidos = ['url_image', 'descripcion', 'id_catalogo']
            
#             if not any(campo in data for campo in campos_permitidos):
#                 return jsonify({"error": "Se requiere al menos un campo para actualizar"}), 400
                
#             async with connection.cursor() as cursor:
#                 sql_update = "UPDATE images_catalogo SET "
#                 valores = []

#                 for campo in campos_permitidos:
#                     if campo in data:
#                         sql_update += f"{campo} = %s, "
#                         valores.append(data[campo])

#                 sql_update = sql_update.rstrip(', ')

#                 sql_update += " WHERE id_images_catalogo = %s"
#                 valores.append(id_images_catalogo)

#                 await cursor.execute(sql_update, valores)
#                 await connection.commit()

#             return jsonify({"success": True, "message": f"Registro con ID {id_images_catalogo} actualizado exitosamente"}), 200

#     except Exception as e:
#         return jsonify({"error": f"Error en la base de datos: {e}"}), 500


# @images_catalogo_fl2.route('/images/<int:id_images_catalogo>', methods=['DELETE'])
# async def eliminar_images_catalogo(id_images_catalogo):
#     try:
#         async with connect_to_database() as connection:
#             async with connection.cursor() as cursor:
#                 sql_delete = "DELETE FROM images_catalogo WHERE id_images_catalogo = %s"
#                 await cursor.execute(sql_delete, (id_images_catalogo,))
#                 await connection.commit()

#             return jsonify({"success": True, "message": f"Registro con ID {id_images_catalogo} eliminado exitosamente"}), 200

#     except Exception as e:
#         return jsonify({"error": f"Error en la base de datos: {e}"}), 500
