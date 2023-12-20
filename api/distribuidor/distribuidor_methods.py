from flask import Blueprint, render_template
from config.database import connect_to_database
from flask import Flask, Response, jsonify, request
from utils.time import convert_milliseconds_to_datetime,convert_milliseconds_to_time_string
from utils.time import convert_milliseconds_to_datetime,convert_milliseconds_to_time_string,timedelta_to_milliseconds

distribuidor_fl2=Blueprint('distribuidor_methods', __name__)



# @distribuidor_fl2.route('/distribuidor', methods=['POST'])
# async def crear_distribuidor():
#     try:
#         async with connect_to_database() as connection:
#             data = request.json
#             campos_requeridos = [
#                 'gerente', 'logo_image', 'coordenadas', 'direccion',
#                 'nombre', 'url_paginaWeb', 'telefono', 'email', 'horarioAtencion',
#             ]
            
#             if not all(campo in data for campo in campos_requeridos):
#                 return jsonify({"error": "Faltan campos requeridos"}), 400
                
#             async with connection.cursor() as cursor:
#                 sql = """INSERT INTO distribuidor (
#                              gerente, logo_image, coordenadas, direccion,
#                              nombre, url_paginaWeb, telefono, email, horarioAtencion
#                          ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
#                 valores = (
#                     data['gerente'],
#                     data['logo_image'],
#                     data['coordenadas'],
#                     data['direccion'],
#                     data['nombre'],
#                     data['url_paginaWeb'],
#                     data['telefono'],
#                     data['email'],
#                     data['horarioAtencion']
#                 )
#                 await cursor.execute(sql, valores)
#                 await connection.commit()

#             return jsonify({"success": True, "message": "Distribuidor creado exitosamente"}), 201

#     except Exception as e:
#         return jsonify({"error": f"Error en la base de datos: {e}"}), 500

@distribuidor_fl2.route('/distribuidor', methods=['POST'])
async def crear_distribuidor():
    try:
        async with connect_to_database() as connection:
            data = request.json
            campos_requeridos = [
                'gerente', 'logo_image', 'coordenadas' ,'direccion',
                'nombre', 'url_paginaWeb', 'telefono', 'email', 'horarioAtencion','created','lastUpdate'
            ]
            
            if not all(campo in data for campo in campos_requeridos) or not all(dia in data['horarioAtencion'] for dia in ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']):
                return jsonify({"error": "Faltan campos requeridos"}), 400
                
            async with connection.cursor() as cursor:
                sql_distribuidor = """INSERT INTO distribuidor (
                                          gerente, logo_image, coordenadas, direccion,
                                          nombre, url_paginaWeb, telefono, email,created,lastUpdate
                                      ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s)"""
                valores_distribuidor = (
                    data['gerente'],
                    data['coordenadas'],
                    data['logo_image'],
                    data['direccion'],
                    data['nombre'],
                    data['url_paginaWeb'],
                    data['telefono'],
                    data['email'],
                    convert_milliseconds_to_datetime(data['created']),
                    convert_milliseconds_to_datetime(data['lastUpdate'])
                )
                await cursor.execute(sql_distribuidor, valores_distribuidor)
                id_distribuidor = cursor.lastrowid  # Obtener el ID del distribuidor insertado

                # Insertar relaciones distribuidor-sucursal
                if 'sucursales' in data and isinstance(data['sucursales'], list):
                    for id_sucursal in data['sucursales']:
                        sql_distribuidor_sucursal = """INSERT INTO distribuidor_sucursal (id_distribuidor, id_sucursal)
                                                       VALUES (%s, %s)"""
                        await cursor.execute(sql_distribuidor_sucursal, (id_distribuidor, id_sucursal))

                # Insertar horarios de atención del distribuidor
                for dia, horarios in data['horarioAtencion'].items():
                    open_time = convert_milliseconds_to_time_string(horarios['open'])
                    close_time = convert_milliseconds_to_time_string(horarios['close'])
                    sql_horarios = """INSERT INTO horarios_distribuidor (id_distribuidor, day, open, close) 
                                      VALUES (%s, %s, %s, %s)"""
                    await cursor.execute(sql_horarios, (id_distribuidor, dia, open_time, close_time))

                await connection.commit()

            return jsonify({"success": True, "message": "Distribuidor creado exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500

@distribuidor_fl2.route('/distribuidor/<int:id_distribuidor>', methods=['PUT'])
async def actualizar_distribuidor(id_distribuidor):
    try:
        async with connect_to_database() as connection:
            data = request.json
            campos_permitidos = [
                'gerente', 'logo_image', 'coordenadas', 'direccion',
                'nombre', 'url_paginaWeb', 'telefono', 'email', 'horarioAtencion','lastUpdate','created'
            ]

            if not any(campo in data for campo in campos_permitidos):
                return jsonify({"error": "Se requiere al menos un campo para actualizar"}), 400

            async with connection.cursor() as cursor:
                sql_update = "UPDATE distribuidor SET "
                valores = []

                for campo in campos_permitidos:
                    if campo in data:
                        sql_update += f"{campo} = %s, "
                        valores.append(data[campo])

                sql_update = sql_update.rstrip(', ')
                sql_update += " WHERE id_distribuidor = %s"
                valores.append(id_distribuidor)

                await cursor.execute(sql_update, valores)
                await connection.commit()

            return jsonify({"success": True, "message": f"Distribuidor con ID {id_distribuidor} actualizado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500

    
@distribuidor_fl2.route('/distribuidor/<int:id_distribuidor>', methods=['DELETE'])
async def eliminar_distribuidor(id_distribuidor):
    try:
        async with connect_to_database() as connection:
            async with connection.cursor() as cursor:
                sql_delete = "DELETE FROM distribuidor WHERE id_distribuidor = %s"
                await cursor.execute(sql_delete, (id_distribuidor,))
                await connection.commit()

            return jsonify({"success": True, "message": f"Distribuidor con ID {id_distribuidor} eliminado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500
    
@distribuidor_fl2.route('/<int:id_distribuidor>/usuarios', methods=['GET'])
async def obtener_usuarios_por_distribuidor(id_distribuidor):
    try:
        async with connect_to_database() as connection:
            async with connection.cursor() as cursor:
              
                sql = """
                    SELECT * FROM usuario
                    WHERE id_distribuidor = %s
                """
                await cursor.execute(sql, (id_distribuidor,))
                usuarios = await cursor.fetchall()

                if not usuarios:
                    return jsonify({"error": f"No se encontraron usuarios para el distribuidor con ID {id_distribuidor}"}), 404

                return jsonify({"success": True, "usuarios": usuarios}), 200

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500


@distribuidor_fl2.route('/<int:id_distribuidor>/articulos', methods=['GET'])
async def obtener_articulos_por_distribuidor(id_distribuidor):
    try:
        async with connect_to_database() as connection:
            async with connection.cursor() as cursor:
                sql_query = """
                    SELECT a.*
                    FROM articulo a
                    JOIN articulo_sucursal asu ON a.id_articulo = asu.id_articulo
                    JOIN distribuidor_sucursal ds ON asu.id_sucursal = ds.id_sucursal
                    WHERE ds.id_distribuidor = %s;
                """
                await cursor.execute(sql_query, (id_distribuidor,))
                articulos = await cursor.fetchall()

                articulos_procesados = []
                for articulo_record in articulos:
                    articulo_procesado = await procesar_articulo(cursor, articulo_record['id_articulo'])
                    articulos_procesados.append(articulo_procesado)

                return jsonify({"success": True, "articulos": articulos_procesados}), 200

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500

async def procesar_articulo(cursor, id_articulo):
    sql_articulo = """
        SELECT a.*, 
            e.id_especificacion, e.tipo, 
            img.url_image, img.descripcion as img_descripcion
        FROM articulo a
        LEFT JOIN especificaciones e ON a.id_articulo = e.id_articulo
        LEFT JOIN images_articulo img ON a.id_articulo = img.id_articulo
        WHERE a.id_articulo = %s
    """
    await cursor.execute(sql_articulo, (id_articulo,))
    resultados_crudos = await cursor.fetchall()
    if not resultados_crudos:
        return None  
    articulo_resultado = {
        'id_articulo': resultados_crudos[0]['id_articulo'],
        'marca': resultados_crudos[0]['marca'],
        'modelo': resultados_crudos[0]['modelo'],
        'categoria': resultados_crudos[0]['categoria'],
        'ano': resultados_crudos[0]['ano'],
        'precio': resultados_crudos[0]['precio'],
        'kilometraje': resultados_crudos[0]['kilometraje'],
        'created': int(resultados_crudos[0]['created'].timestamp() * 1000),
        'lastUpdate': int(resultados_crudos[0]['lastUpdate'].timestamp() * 1000),
        'lastInventoryUpdate': int(resultados_crudos[0]['lastInventoryUpdate'].timestamp() * 1000),
        'enable': resultados_crudos[0]['enable'],
        'descripcion': resultados_crudos[0]['descripcion'],
        'color': resultados_crudos[0]['color'],  
        'mainImage': resultados_crudos[0]['mainImage'],      
        'especificaciones': [],
        'imagenes': []
    }

    ids_especificaciones_procesadas = set()
    for fila in resultados_crudos:
        id_especificacion = fila.get('id_especificacion')
        if id_especificacion and id_especificacion not in ids_especificaciones_procesadas:
            ids_especificaciones_procesadas.add(id_especificacion)
            sql_subespecificaciones = """
                SELECT * FROM subespecificaciones
                WHERE id_especificacion = %s
            """
            await cursor.execute(sql_subespecificaciones, (id_especificacion,))
            subespecificaciones_raw = await cursor.fetchall()
            subespecificaciones = {sub['clave']: sub['valor'] for sub in subespecificaciones_raw}

            especificacion = {
                'tipo': fila['tipo'],
                'subespecificaciones': subespecificaciones
            }
            articulo_resultado['especificaciones'].append(especificacion)

        if fila['url_image'] and not any(imagen['url_image'] == fila['url_image'] for imagen in articulo_resultado['imagenes']):
            imagen = {
                'url_image': fila['url_image'],
                'descripcion': fila['img_descripcion'],
            }
            articulo_resultado['imagenes'].append(imagen)

    return articulo_resultado

    
# @distribuidor_fl2.route('/<int:id_distribuidor>/articulos', methods=['GET'])
# async def obtener_articulos_por_distribuidor(id_distribuidor):
#     try:
#         async with connect_to_database() as connection:
#             async with connection.cursor() as cursor:
#                 sql_query = """
#                     SELECT a.*
#                     FROM articulo a
#                     JOIN articulo_sucursal asu ON a.id_articulo = asu.id_articulo
#                     JOIN distribuidor_sucursal ds ON asu.id_sucursal = ds.id_sucursal
#                     WHERE ds.id_distribuidor = %s;
#                 """
#                 await cursor.execute(sql_query, (id_distribuidor,))
#                 articulos = await cursor.fetchall()
#                 articulos_processed = []
#                 for articulo_record in articulos:
#                     id_articulo=articulo_record['id_articulo']
#                     sql_articulo = """
#                         SELECT a.*, 
#                             e.id_especificacion, e.tipo, 
#                             img.url_image, img.descripcion as img_descripcion
#                         FROM articulo a
#                         LEFT JOIN especificaciones e ON a.id_articulo = e.id_articulo
#                         LEFT JOIN images_articulo img ON a.id_articulo = img.id_articulo
#                         WHERE a.id_articulo = %s
#                     """
#                     await cursor.execute(sql_articulo, (id_articulo,))
#                     raw_results = await cursor.fetchall()
#                     print(raw_results)
#                     if not raw_results:
#                         return None  # No se encontró el artículo

#                     articulo_resultado = {
#                         'id_articulo': raw_results[0]['id_articulo'],
#                         'marca': raw_results[0]['marca'],
#                         'modelo': raw_results[0]['modelo'],
#                         'categoria': raw_results[0]['categoria'],
#                         'ano': raw_results[0]['ano'],
#                         'precio': raw_results[0]['precio'],
#                         'kilometraje': raw_results[0]['kilometraje'],
#                         'created': int(raw_results[0]['created'].timestamp() * 1000),
#                         'lastUpdate': int(raw_results[0]['lastUpdate'].timestamp() * 1000),
#                         'lastInventoryUpdate':int(raw_results[0]['lastInventoryUpdate'].timestamp() * 1000),
#                         'enable': raw_results[0]['enable'],
#                         'descripcion': raw_results[0]['descripcion'],
#                         'enable': raw_results[0]['enable'],
#                         'color': raw_results[0]['color'],  
#                         'mainImage': raw_results[0]['mainImage'],      
#                         'especificaciones': [],
#                         'imagenes': []
#                     }
#                     processed_especificaciones = set()
#                     for row in raw_results:
#                         id_especificacion = row.get('id_especificacion')

#                         if id_especificacion and id_especificacion not in processed_especificaciones:
#                             processed_especificaciones.add(id_especificacion)

#                             sql_subespecificaciones = """
#                                 SELECT * FROM subespecificaciones
#                                 WHERE id_especificacion = %s
#                             """
#                             await cursor.execute(sql_subespecificaciones, (id_especificacion,))
#                             subespecificaciones_raw = await cursor.fetchall()
#                             subespecificaciones = {sub['clave']: sub['valor'] for sub in subespecificaciones_raw}

#                             especificacion = {
#                                 'tipo': row['tipo'],
#                                 'subespecificaciones': subespecificaciones
#                             }
#                             articulo_resultado['especificaciones'].append(especificacion)
#                         if row['url_image'] and not any(img['url_image'] == row['url_image'] for img in articulo_resultado['imagenes']):
#                             imagen = {
#                                 'url_image': row['url_image'],
#                                 'descripcion': row['img_descripcion'],
#                             }
#                             articulo_resultado['imagenes'].append(imagen)
#                         articulos_processed.append(articulo_resultado)
                

#                 return jsonify({"success": True, "articulos": articulos}), 200

#     except Exception as e:
#         return jsonify({"error": f"Error en la base de datos: {e}"}), 500




@distribuidor_fl2.route('/<int:id_distribuidor>/sucursales', methods=['GET'])
async def obtener_sucursales_por_distribuidor(id_distribuidor):
    try:
        async with connect_to_database() as connection:
            async with connection.cursor() as cursor:
                sql_query = """
                    SELECT s.*
                    FROM distribuidor_sucursal ds
                    JOIN sucursal s ON ds.id_sucursal = s.id_sucursal
                    WHERE ds.id_distribuidor = %s;
                """
                await cursor.execute(sql_query, (id_distribuidor,))
                sucursales_raw = await cursor.fetchall()

                sucursales_processed = []
                for sucursal_record in sucursales_raw:
                    id_sucursal = sucursal_record['id_sucursal']

                    for key in ['created', 'lastUpdate']:
                        if sucursal_record[key]:
                            sucursal_record[key] = int(sucursal_record[key].timestamp() * 1000)

                    sql_sucursales_imagenes = "SELECT * FROM images_sucursal WHERE id_sucursal = %s;"
                    await cursor.execute(sql_sucursales_imagenes, (id_sucursal,))
                    sucursal_images = await cursor.fetchall()
                    sucursal_record['sucursal_images'] = sucursal_images

                    sql_articulos = """
                        SELECT articulo.* FROM articulo
                        JOIN articulo_sucursal ON articulo.id_articulo = articulo_sucursal.id_articulo
                        WHERE articulo_sucursal.id_sucursal = %s;
                    """
                    await cursor.execute(sql_articulos, (id_sucursal,))
                    articulos_list = await cursor.fetchall()
                    for articulo in articulos_list:
                        for key in ['created', 'lastUpdate', 'lastInventoryUpdate']:
                            if articulo[key]:
                                articulo[key] = int(articulo[key].timestamp() * 1000)

                    sucursal_record['sucursal_articulos'] = articulos_list

                    sql_horarios_sucursal = "SELECT * FROM horarios_sucursal WHERE id_sucursal = %s"
                    await cursor.execute(sql_horarios_sucursal, (id_sucursal,))
                    horarios_raw = await cursor.fetchall()
                    horarios_sucursal = {}
                    for horario in horarios_raw:
                        dia = horario['day']
                        horarios_sucursal[dia] = {
                            'open': timedelta_to_milliseconds(horario['open']),
                            'close': timedelta_to_milliseconds(horario['close'])
                        }

                    sucursal_record['horarios_sucursal'] = horarios_sucursal
                    sucursales_processed.append(sucursal_record)

            return jsonify(sucursales_processed)
    finally:
        connection.close()

# @distribuidor_fl2.route('/<int:id_distribuidor>/sucursales', methods=['GET'])
# async def obtener_sucursales_por_distribuidor(id_distribuidor):
#     try:
#         async with connect_to_database() as connection:
#             async with connection.cursor() as cursor:
#                 sql_query = """
#                     SELECT s.*
#                     FROM distribuidor_sucursal ds
#                     JOIN sucursal s ON ds.id_sucursal = s.id_sucursal
#                     WHERE ds.id_distribuidor = %s;
#                 """
#                 await cursor.execute(sql_query, (id_distribuidor,))
#                 sucursales_raw = await cursor.fetchall()

#                 sucursales_processed = []
#                 for sucursal_record in sucursales_raw:
#                     id_sucursal=sucursal_record['id_sucursal']
#                     sql_sucursal = "SELECT * FROM sucursal WHERE id_sucursal = %s;"
#                     await cursor.execute(sql_sucursal, (id_sucursal,))
#                     sucursal_record = await cursor.fetchone()

#                     if sucursal_record:
#                         for key in ['created', 'lastUpdate']:
#                             if sucursal_record[key]:
#                                 sucursal_record[key] = int(sucursal_record[key].timestamp() * 1000)

#                         sql_sucursales_imagenes = "SELECT * FROM images_sucursal WHERE id_sucursal = %s;"
#                         await cursor.execute(sql_sucursales_imagenes, (id_sucursal,))
#                         sucursal_images = await cursor.fetchall()
#                         sucursal_record['sucursal_images'] = sucursal_images

#                         sql_articulos = """SELECT articulo.* FROM articulo
#                                         JOIN articulo_sucursal ON articulo.id_articulo = articulo_sucursal.id_articulo
#                                         WHERE articulo_sucursal.id_sucursal = %s;"""
#                         await cursor.execute(sql_articulos, (id_sucursal,))
#                         articulos_list = await cursor.fetchall()

#                         for articulo in articulos_list:
#                             for key in ['created', 'lastUpdate', 'lastInventoryUpdate']:
#                                 if articulo[key]:
#                                     articulo[key] = int(articulo[key].timestamp() * 1000)

                

#                         sucursal_record['sucursal_articulos'] = articulos_list
#                         sql_horarios_sucursal = "SELECT * FROM horarios_sucursal WHERE id_sucursal = %s"
#                         await cursor.execute(sql_horarios_sucursal, (id_sucursal,))
#                         horarios_raw = await cursor.fetchall()
#                         horarios_sucursal = {}
#                         for horario in horarios_raw:
#                             dia = horario['day']
#                             horarios_sucursal[dia] = {
#                                 'open': timedelta_to_milliseconds(horario['open']),
#                                 'close': timedelta_to_milliseconds(horario['close'])
#                             }

#                         sucursal_record['horarios_sucursal'] = horarios_sucursal
#                         sucursales_processed.append(sucursal_record)

#             return jsonify(sucursales_processed)
#     finally:
#         connection.close()


# @distribuidor_fl2.route('/<int:id_distribuidor>/sucursales', methods=['GET'])
# async def obtener_sucursales_por_distribuidor(id_distribuidor):
#     try:
#         async with connect_to_database() as connection:
#             async with connection.cursor() as cursor:
#                 sql = """
#                     SELECT sucursal.* FROM sucursal
#                     JOIN distribuidor_sucursal ON sucursal.id_sucursal = distribuidor_sucursal.id_sucursal
#                     WHERE distribuidor_sucursal.id_distribuidor = %s
#                 """
#                 await cursor.execute(sql, (id_distribuidor,))
#                 sucursales = await cursor.fetchall()

#                 if not sucursales:
#                     return jsonify({"error": f"No se encontraron sucursales para el distribuidor con ID {id_distribuidor}"}), 404

#                 return jsonify({"success": True, "sucursales": sucursales}), 200

#     except Exception as e:
#         return jsonify({"error": f"Error en la base de datos: {e}"}), 500
        

# @distribuidor_fl2.route('/<int:id_distribuidor>/articulos', methods=['GET'])
# async def obtener_articulos_por_distribuidor(id_distribuidor):
#     try:
#         async with connect_to_database() as connection:
#             async with connection.cursor() as cursor:
#                 sql = """
#                     SELECT articulo.* FROM articulo
#                     JOIN articulo_sucursal ON articulo.id_articulo = articulo_sucursal.id_articulo
#                     JOIN distribuidor_sucursal ON articulo_sucursal.id_sucursal = distribuidor_sucursal.id_sucursal
#                     WHERE distribuidor_sucursal.id_distribuidor = %s
#                 """
#                 await cursor.execute(sql, (id_distribuidor,))
#                 articulos = await cursor.fetchall()

#                 if not articulos:
#                     return jsonify({"error": f"No se encontraron artículos para el distribuidor con ID {id_distribuidor}"}), 404

#                 return jsonify({"success": True, "articulos": articulos}), 200

#     except Exception as e:
#         return jsonify({"error": f"Error en la base de datos: {e}"}), 500