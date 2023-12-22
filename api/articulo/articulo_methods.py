from flask import Flask, request, jsonify
from flask import Blueprint
from config.database import connect_to_database
from utils.time import convert_milliseconds_to_datetime,convert_milliseconds_to_time_string
from datetime import datetime
articulo_fl2 = Blueprint('articulo_post', __name__)

# @articulo_fl2.route('/articulo', methods=['POST'])
# async def crear_articulo():
#     try:
#         async with connect_to_database() as connection:
#             data = request.json
#             campos_requeridos = ['marca', 'modelo', 'categoria', 'ano', 
#                                  'precio', 'kilometraje', 'descripcion', 'enable', 'color']

#             if not all(campo in data for campo in campos_requeridos):
#                 return jsonify({"error": "Faltan campos requeridos"}), 400

#             async with connection.cursor() as cursor:
#                 sql = """INSERT INTO articulo (
#                              marca, modelo, categoria, ano, precio, 
#                              kilometraje, descripcion, enable, color
#                          ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
#                 valores = (
#                     data['marca'],
#                     data['modelo'],
#                     data['categoria'],
#                     data['ano'],
#                     data['precio'],
#                     data['kilometraje'],
#                     data['descripcion'],
#                     data['enable'],
#                     data['color']
#                 )
#                 await cursor.execute(sql, valores)
#                 await connection.commit()
#                 rows_affected = cursor.rowcount

#             return jsonify({"success": True, "message": "Artículo creado exitosamente"}), 201

#     except Exception as e:
#         return jsonify({"error": f"Error en la base de datos: {e}"}), 500
def get_default_expedition_date():
    now = datetime.now()
    timestamp_seconds = datetime.timestamp(now)
    timestamp_milliseconds = int(timestamp_seconds * 1000)
    return timestamp_milliseconds

@articulo_fl2.route('/articulo', methods=['POST'])
async def crear_articulo():
    try:
        async with connect_to_database() as connection:
            data = request.json
            expedition_date = data['expedition_date'] if 'expedition_date' in data else get_default_expedition_date()
            campos_requeridos = ['ano', 'categoria', 'color', 
                                 'descripcion', 'enable', 'mainImage', 'marca', 
                                 'modelo','precio','created',
                                 'lastUpdate','lastInventoryUpdate','kilometraje']   
            if not all(campo in data for campo in campos_requeridos):
                return jsonify({"error": "Faltan campos requeridos"}), 400
                
            async with connection.cursor() as cursor:
                sql_articulo = """INSERT INTO articulo (
                                      ano, categoria, color, descripcion, enable, mainImage, 
                                      marca, modelo, precio, expedition_date, 
                                      created, lastUpdate, lastInventoryUpdate, kilometraje
                                  ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,  %s, %s, %s, %s, %s, %s)"""
                valores_articulo = (
                    data['ano'], 
                    data['categoria'], 
                    data['color'], 
                    data['descripcion'],
                    data['enable'], 
                    data['mainImage'],
                    data['marca'], 
                    data['modelo'],
                    data['precio'], 
                    convert_milliseconds_to_datetime(expedition_date),
                    convert_milliseconds_to_datetime(data['created']),
                    convert_milliseconds_to_datetime(data['lastUpdate']), 
                    convert_milliseconds_to_datetime(data['lastInventoryUpdate']), 
                    data['kilometraje']
                )
                await cursor.execute(sql_articulo, valores_articulo)
                id_articulo = cursor.lastrowid

                if 'sucursal_id' in data:
                    sql_articulo_sucursal = """INSERT INTO articulo_sucursal (id_articulo, id_sucursal) VALUES (%s, %s)"""
                    await cursor.execute(sql_articulo_sucursal, (id_articulo, data['sucursal_id']))
                if 'especificaciones' in data:
                    for especificacion in data['especificaciones']:
                        sql_especificaciones = """INSERT INTO especificaciones (tipo, id_articulo) VALUES (%s, %s)"""
                        await cursor.execute(sql_especificaciones, (especificacion['tipo'], id_articulo))
                        id_especificacion = cursor.lastrowid

                        for clave, valor in especificacion['subespecificaciones'].items():
                            sql_subespecificaciones = """INSERT INTO subespecificaciones (clave, valor, id_especificacion) VALUES (%s, %s, %s)"""
                            await cursor.execute(sql_subespecificaciones, (clave, valor, id_especificacion))

                if 'imagenes' in data:
                    for imagen in data['imagenes']:
                        sql_images_articulo = """INSERT INTO images_articulo (url_image, descripcion, id_articulo) VALUES (%s, %s, %s)"""
                        await cursor.execute(sql_images_articulo, (imagen['url_image'], imagen['descripcion'], id_articulo))

                    await connection.commit()
                

            return jsonify({"success": True, "message": "Artículo creado exitosamente", "id_articulo": id_articulo}), 201

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500


@articulo_fl2.route('/articulo/<int:id_articulo>', methods=['PUT'])
async def actualizar_articulo(id_articulo):
    try:
        async with connect_to_database() as connection:
            data = request.json
            campos_permitidos = ['ano', 'categoria', 'color', 
                                 'descripcion', 'enable', 'mainImage', 'marca', 'expedition_date',
                                 'modelo', 'precio', 'lastInventoryUpdate', 'kilometraje']
            cambios = []
            valores = []
            for campo in campos_permitidos:
                if campo in data:
                    cambios.append(f"{campo} = %s")
                    valores.append(data[campo])

            if not cambios:
                return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

            # Agregar actualización de lastUpdate
            cambios.append("lastUpdate = CURRENT_TIMESTAMP")
            
            sql_update_articulo = "UPDATE articulo SET " + ", ".join(cambios) + " WHERE id_articulo = %s"
            valores.append(id_articulo)
            
            async with connection.cursor() as cursor:
                await cursor.execute(sql_update_articulo, valores)

                # Actualizar o insertar especificaciones
                # if 'especificaciones' in data:
                #     for especificacion in data['especificaciones']:
                #         if 'id_especificacion' in especificacion:
                #             # Actualizar especificación existente
                #             sql_update_especificacion = """UPDATE especificaciones SET tipo = %s WHERE id_especificacion = %s AND id_articulo = %s"""
                #             await cursor.execute(sql_update_especificacion, (especificacion['tipo'], especificacion['id_especificacion'], id_articulo))
                #         else:
                #             # Insertar nueva especificación
                #             sql_insert_especificacion = """INSERT INTO especificaciones (tipo, id_articulo) VALUES (%s, %s)"""
                #             await cursor.execute(sql_insert_especificacion, (especificacion['tipo'], id_articulo))
                #             id_especificacion = cursor.lastrowid

                #         # Actualizar o insertar subespecificaciones
                #         # for subespecificacion in especificacion.get('subespecificaciones', []):
                #         #     if 'id_subespecificacion' in subespecificacion:
                #         #         # Actualizar subespecificación existente
                #         #         sql_update_subespecificacion = """UPDATE subespecificaciones SET clave = %s, valor = %s WHERE id_subespecificacion = %s AND id_especificacion = %s"""
                #         #         await cursor.execute(sql_update_subespecificacion, (subespecificacion['clave'], subespecificacion['valor'], subespecificacion['id_subespecificacion'], id_especificacion))
                #         #     else:
                #         #         # Insertar nueva subespecificación
                #         #         sql_insert_subespecificacion = """INSERT INTO subespecificaciones (clave, valor, id_especificacion) VALUES (%s, %s, %s)"""
                #         #         await cursor.execute(sql_insert_subespecificacion, (subespecificacion['clave'], subespecificacion['valor'], id_especificacion))
                #         for clave, valor in especificacion['subespecificaciones'].items():
                #             # Aquí, asumo que no tienes IDs para subespecificaciones individuales,
                #             # por lo que siempre las insertarás como nuevas.
                #             # Necesitarías ajustar esto si también necesitas actualizarlas.
                #             sql_insert_subespecificaciones = """INSERT INTO subespecificaciones (clave, valor, id_especificacion) VALUES (%s, %s, %s)"""
                #             await cursor.execute(sql_insert_subespecificaciones, (clave, valor, id_especificacion))


                # if 'imagenes' in data:
                #     for imagen in data['imagenes']:
                #         if 'id_imagen' in imagen:
                #             sql_update_imagen = """UPDATE images_articulo SET url_image = %s, descripcion = %s WHERE id_images_articulo = %s AND id_articulo = %s"""
                #             await cursor.execute(sql_update_imagen, (imagen['url_image'], imagen['descripcion'], imagen['id_imagen'], id_articulo))
                #         else:
                #             sql_insert_imagen = """INSERT INTO images_articulo (url_image, descripcion, id_articulo) VALUES (%s, %s, %s)"""
                #             await cursor.execute(sql_insert_imagen, (imagen['url_image'], imagen['descripcion'], id_articulo))

                await connection.commit()

            return jsonify({"success": True, "message": f"Artículo con ID {id_articulo} actualizado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500



@articulo_fl2.route('/articulo/<int:id_articulo>', methods=['DELETE'])
async def eliminar_articulo(id_articulo):
    try:
        async with connect_to_database() as connection:
            async with connection.cursor() as cursor:
                sql_delete = "DELETE FROM articulo WHERE id_articulo = %s"
                await cursor.execute(sql_delete, (id_articulo,))
                await connection.commit()

            return jsonify({"success": True, "message": f"articulo con ID {id_articulo} eliminado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500

# @articulo_fl2.route('/<str:id_usuario>/<int:id_articulo>', methods=['POST'])
# async def aritulo_favorito(id_articulo,id_usuario):

@articulo_fl2.route('/<int:id_articulo>/<int:id_usuario>', methods=['POST'])
async def articulo_favorito(id_usuario, id_articulo):
    try:
        async with connect_to_database() as connection:
            async with connection.cursor() as cursor:
                sql_check = """SELECT enable FROM favoritos WHERE id_usuario = %s AND id_articulo = %s"""
                await cursor.execute(sql_check, (id_usuario, id_articulo))
                result = await cursor.fetchone()

                if result:
                    new_enable_status = not result['enable']
                    sql_update = """UPDATE favoritos SET enable =
                      %s WHERE id_usuario = %s AND id_articulo = %s"""
                    await cursor.execute(sql_update, (new_enable_status, id_usuario, id_articulo))
                else:
                    sql_insert = """INSERT INTO favoritos (id_usuario, id_articulo, fecha_agregado, enable) 
                    VALUES (%s, %s, %s, %s)"""
                    fecha_agregado = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    await cursor.execute(sql_insert, (id_usuario, id_articulo, fecha_agregado, True))

                await connection.commit()

            return jsonify({"success": True, "message": "Estado de favorito actualizado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500