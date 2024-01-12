from flask import Flask, request, jsonify
from flask import Blueprint
from config.database import connect_to_database
from utils.time import convert_milliseconds_to_datetime,convert_milliseconds_to_time_string
from datetime import datetime
articulo_fl2 = Blueprint('articulo_post', __name__)
from utils.serializer import resultados_a_json, convertir_a_datetime

# @articulo_fl2.route('/articulo', methods=['POST'])
# def crear_articulo():
#     try:
#         with connect_to_database() as connection:
#             data = request.json
#             campos_requeridos = ['marca', 'modelo', 'categoria', 'ano', 
#                                  'precio', 'kilometraje', 'descripcion', 'enable', 'color']

#             if not all(campo in data for campo in campos_requeridos):
#                 return jsonify({"error": "Faltan campos requeridos"}), 400

#             with connection.cursor() as cursor:
#                 sql = """INSERT INTO articulo (
#                              marca, modelo, categoria, ano, precio, 
#                              kilometraje, descripcion, enable, color
#                          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
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
#                 cursor.execute(sql, valores)
#                 connection.commit()
#                 rows_affected = cursor.rowcount

#             return jsonify({"success": True, "message": "Artículo creado exitosamente"}), 201

#     except Exception as e:
#         return jsonify({"error": f"Error en la base de datos: {e}"}), 500



def get_default_expedition_date():
    now = datetime.now()
    timestamp_seconds = datetime.timestamp(now)
    timestamp_milliseconds = int(timestamp_seconds * 1000)
    return timestamp_milliseconds

@articulo_fl2.route('/especificaciones/<string:name_tipo>', methods=['GET'])
def get_subespecificaciones_por_tipo(name_tipo):
    try:
        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_especificacion FROM especificaciones_adm WHERE tipo = ?", (name_tipo,))
                id_result = resultados_a_json(cursor, unico_resultado=True)
                print(id_result)
                if id_result:
                    id_especificacion = id_result['id_especificacion']
                    print(id_especificacion)
                    cursor.execute("SELECT clave, valor FROM subespecificaciones_adm WHERE id_especificacion = ?", (id_especificacion,))
                    subespecificaciones_raw = resultados_a_json(cursor)
                    print(subespecificaciones_raw)
                    subespecificaciones = {item['clave']: item['valor'] for item in subespecificaciones_raw}

                    respuesta = {
                        "especificaciones": [
                            {
                                "subespecificaciones": subespecificaciones,
                                "tipo": name_tipo
                            }
                        ]
                    }
                else:
                    respuesta = {"error": f"No se encontraron especificaciones para el tipo '{name_tipo}'"}
                    return jsonify(respuesta)
        return jsonify(respuesta)
    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500


@articulo_fl2.route('/options', methods=['GET'])
def options_filter():
    try:
        consulta1 = "SELECT DISTINCT ano FROM articulo ORDER BY ano"
        consulta2 = "SELECT DISTINCT categoria FROM articulo ORDER BY categoria"
        consulta3 = "SELECT DISTINCT marca FROM articulo ORDER BY marca"
        consulta4 = "SELECT DISTINCT modelo FROM articulo ORDER BY modelo"
        consulta5 = "SELECT DISTINCT color FROM articulo ORDER BY color"

        opciones = {'ano': [], 'categoria': [], 'marca': [], 'modelo': [], 'color': []}

        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                # Año
                cursor.execute(consulta1)
                resultados = resultados_a_json(cursor)
                opciones['ano'] = [ano['ano'] for ano in resultados if ano['ano'] is not None]

                # Categoría
                cursor.execute(consulta2)
                resultados = resultados_a_json(cursor)
                opciones['categoria'] = [categoria['categoria'] for categoria in resultados if categoria['categoria'] is not None]

                # Marca
                cursor.execute(consulta3)
                resultados = resultados_a_json(cursor)
                opciones['marca'] = [marca['marca'] for marca in resultados if marca['marca'] is not None]

                # Modelo
                cursor.execute(consulta4)
                resultados = resultados_a_json(cursor)
                opciones['modelo'] = [modelo['modelo'] for modelo in resultados if modelo['modelo'] is not None]

                # Color
                cursor.execute(consulta5)
                resultados = resultados_a_json(cursor)
                opciones['color'] = [color['color'] for color in resultados if color['color'] is not None]

        return jsonify(opciones)           

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500
   
      
@articulo_fl2.route('/filters', methods=['GET'])
def buscar_articulos():
    try:
        anos = request.args.getlist('ano')  
        categorias = request.args.getlist('categoria')
        marcas = request.args.getlist('marca')
        modelos = request.args.getlist('modelo')
        colores = request.args.getlist('color')

        consulta = "SELECT * FROM articulo WHERE 1=1"
        parametros = []

        if anos:
            consulta += f" AND ano IN ({','.join(['?'] * len(anos))})"
            parametros.extend(anos)
        if categorias:
            consulta += f" AND categoria IN ({','.join(['?'] * len(categorias))})"
            parametros.extend(categorias)
        if marcas:
            consulta += f" AND marca IN ({','.join(['?'] * len(marcas))})"
            parametros.extend(marcas)
        if modelos:
            consulta += f" AND modelo IN ({','.join(['?'] * len(modelos))})"
            parametros.extend(modelos)
        if colores:
            consulta += f" AND color IN ({','.join(['?'] * len(colores))})"
            parametros.extend(colores)

        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                cursor.execute(consulta, parametros)
                resultados = resultados_a_json(cursor)
                return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500

@articulo_fl2.route('/especificaciones', methods=['GET'])
def get_tipos_especificaciones():
    try:
        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT tipo FROM especificaciones_adm")
                tipos_raw  = resultados_a_json(cursor)
                if tipos_raw:
                    tipos = [registro['tipo'] for registro in tipos_raw]
                print(tipos)
                return jsonify(tipos)
    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500
    
@articulo_fl2.route('/subespecificaciones', methods=['GET'])
def get_tipos_sub_especificaciones():
    try:
        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT clave FROM subespecificaciones")
                subespecificaciones_raw = resultados_a_json(cursor)
                if subespecificaciones_raw:
                    subespecificaciones = [registro['clave'] for registro in subespecificaciones_raw]
                return jsonify({"especificaciones": subespecificaciones})
    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500

    
# @articulo_fl2.route('/articulo/<int:id_articulo>', methods=['PUT'])
# def actualizar_articulo(id_articulo):
# @articulo_fl2.route('/especificaciones/<int:id_especificacion>', methods=['GET'])
# def get_tipos_especificaciones_by_id(id_especificacion):
#     try:
#         with connect_to_database() as connection:
#             with connection.cursor() as cursor:
#                 # Obtener el tipo de la especificación
#                 cursor.execute("SELECT *.tipo FROM especificaciones_adm")
#                 tipos = resultados_a_json(cursor, unico_resultado=True)

#                 cursor.execute("SELECT tipo FROM especificaciones_adm WHERE id_especificacion = ?", (id_especificacion,))
#                 tipo_raw = resultados_a_json(cursor, unico_resultado=True)
#                 if not tipo_raw:
#                     return jsonify({"error": "Especificación no encontrada"}), 404
#                 tipo = tipo_raw['tipo']
#                 cursor.execute("SELECT clave, valor FROM subespecificaciones_adm WHERE id_especificacion = ?", (id_especificacion,))
#                 subespecificaciones_raw = resultados_a_json(cursor)
#                 subespecificaciones = {registro['clave']: registro['valor'] for registro in subespecificaciones_raw}

#                 # Obtener marcas
#                 cursor.execute("SELECT marca FROM marcas_adm WHERE id_especificacion = ?", (id_especificacion,))
#                 marcas_raw = resultados_a_json(cursor)
#                 marcas = [registro['marca'] for registro in marcas_raw]
#                 respuesta = {
#                     "especificaciones": [
#                         {
#                             "tipo": tipo,
#                             "subespecificaciones": subespecificaciones,
#                             "marcas": marcas
#                         }
#                     ]
#                 }
#                 return jsonify(respuesta)
#     except Exception as e:
#         return jsonify({"error": f"Error en la base de datos: {e}"}), 500
    
@articulo_fl2.route('/especificaciones', methods=['GET'])
def get_todas_especificaciones():
    try:
        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                # Obtener todas las especificaciones
                cursor.execute("SELECT * FROM especificaciones_adm")
                todas_especificaciones_raw = resultados_a_json(cursor)
                
                especificaciones = []
                for espec in todas_especificaciones_raw:
                    id_especificacion = espec['id_especificacion']
                    tipo = espec['tipo']

                    # Obtener subespecificaciones
                    cursor.execute("SELECT clave, valor FROM subespecificaciones_adm WHERE id_especificacion = ?", (id_especificacion,))
                    subespecificaciones_raw = resultados_a_json(cursor)
                    subespecificaciones = {registro['clave']: registro['valor'] for registro in subespecificaciones_raw}

                    # Obtener marcas
                    cursor.execute("SELECT marca FROM marcas_adm WHERE id_especificacion = ?", (id_especificacion,))
                    marcas_raw = resultados_a_json(cursor)
                    marcas = [registro['marca'] for registro in marcas_raw]

                    especificaciones.append({
                        "tipo": tipo,
                        "subespecificaciones": subespecificaciones,
                        "marcas": marcas
                    })

                return jsonify({"especificaciones": especificaciones})
    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500

@articulo_fl2.route('/especificaciones/<int:id_especificacion>', methods=['PUT'])
def actualizar_especificacion(id_especificacion):
    try:
        # Obtener los datos enviados en la solicitud
        datos = request.get_json()

        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                # Actualizar datos de la especificación
                if 'tipo' in datos:
                    cursor.execute("UPDATE especificaciones_adm SET tipo = ? WHERE id_especificacion = ?", (datos['tipo'], id_especificacion))

                # Actualizar subespecificaciones (si se proporcionan)
                if 'subespecificaciones' in datos:
                    for clave, valor in datos['subespecificaciones'].items():
                        cursor.execute("UPDATE subespecificaciones_adm SET valor = ? WHERE id_especificacion = ? AND clave = ?", (valor, id_especificacion, clave))

              
                if 'marcas' in datos:
                    # Primero, eliminar marcas existentes
                    cursor.execute("DELETE FROM marcas_adm WHERE id_especificacion = ?", (id_especificacion,))
                    # Luego, insertar nuevas marcas
                    for marca in datos['marcas']:
                        cursor.execute("INSERT INTO marcas_adm (id_especificacion, marca) VALUES (?, ?)", (id_especificacion, marca))

                connection.commit()

        return jsonify({"success": "Especificación actualizada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al actualizar la especificación: {e}"}), 500
   
@articulo_fl2.route('/especificaciones', methods=['POST'])
def post_especificaciones():
    data = request.json
    try:
        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                for especificacion in data['especificaciones']:
                    sql_especificaciones = """INSERT INTO especificaciones_adm (tipo) VALUES (?)"""
                    cursor.execute(sql_especificaciones, (especificacion['tipo'],))
                    id_especificacion = cursor.lastrowid

                    for clave, valor in especificacion['subespecificaciones'].items():
                        sql_subespecificaciones = """INSERT INTO subespecificaciones_adm (clave, valor, id_especificacion) VALUES (?, ?, ?)"""
                        cursor.execute(sql_subespecificaciones, (clave, valor, id_especificacion))

                    for marca in especificacion.get('marcas', []):
                        sql_marcas = """INSERT INTO marcas_adm (marca, id_especificacion) VALUES (?, ?)"""
                        cursor.execute(sql_marcas, (marca, id_especificacion))

                    connection.commit()

            return jsonify({"success": True, "message": "Especificacion creado exitosamente" ,"id_especificacione": id_especificacion}), 201


    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500
    
# @articulo_fl2.route('/especificaciones', methods=['POST'])
# def post_especificaciones():
#     data = request.json
#     try:
#         with connect_to_database() as connection:
#             with connection.cursor() as cursor:
#                 for especificacion in data['especificaciones']:
#                     sql_especificaciones = """INSERT INTO especificaciones_adm (tipo) VALUES (?)"""
#                     cursor.execute(sql_especificaciones, (especificacion['tipo'],))
#                     id_especificacion = cursor.lastrowid

#                     for clave, valor in especificacion['subespecificaciones'].items():
#                         sql_subespecificaciones = """INSERT INTO subespecificaciones_adm (clave, valor, id_especificacion) VALUES (?, ?, ?)"""
#                         cursor.execute(sql_subespecificaciones, (clave, valor, id_especificacion))

#                     connection.commit()

#             return jsonify({"success": True, "message": "Especificacion creado exitosamente" ,"id_especificacione": id_especificacion}), 201


#     except Exception as e:
#         return jsonify({"error": f"Error en la base de datos: {e}"}), 500

    




@articulo_fl2.route('/articulo', methods=['POST'])
def crear_articulo():
    try:
        with connect_to_database() as connection:
            data = request.json
            expedition_date = data['expedition_date'] if 'expedition_date' in data else get_default_expedition_date()
            campos_requeridos = ['ano', 'categoria', 'color', 
                                 'descripcion', 'enable', 'mainImage', 'marca', 
                                 'modelo','precio','created',
                                 'lastUpdate','lastInventoryUpdate','kilometraje']   
            if not all(campo in data for campo in campos_requeridos):
                return jsonify({"error": "Faltan campos requeridos"}), 400
                
            with connection.cursor() as cursor:
                sql_articulo = """INSERT INTO articulo (
                                      ano, categoria, color, descripcion, enable, mainImage, 
                                      marca, modelo, precio, expedition_date, 
                                      created, lastUpdate, lastInventoryUpdate, kilometraje
                                  ) VALUES (?, ?, ?, ?, ?, ?, ?, ?,  ?, ?, ?, ?, ?, ?)"""
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
                cursor.execute(sql_articulo, valores_articulo)
                id_articulo = cursor.lastrowid

                if 'sucursal_id' in data:
                    sql_articulo_sucursal = """INSERT INTO articulo_sucursal (id_articulo, id_sucursal) VALUES (?, ?)"""
                    cursor.execute(sql_articulo_sucursal, (id_articulo, data['sucursal_id']))
                    
                if 'especificaciones' in data:
                    for especificacion in data['especificaciones']:
                        sql_especificaciones = """INSERT INTO especificaciones (tipo, id_articulo) VALUES (?, ?)"""
                        cursor.execute(sql_especificaciones, (especificacion['tipo'], id_articulo))
                        id_especificacion = cursor.lastrowid

                        for clave, valor in especificacion['subespecificaciones'].items():
                            sql_subespecificaciones = """INSERT INTO subespecificaciones (clave, valor, id_especificacion) VALUES (?, ?, ?)"""
                            cursor.execute(sql_subespecificaciones, (clave, valor, id_especificacion))

                if 'imagenes' in data:
                    for imagen in data['imagenes']:
                        sql_images_articulo = """INSERT INTO images_articulo (url_image, descripcion, id_articulo) VALUES (?, ?, ?)"""
                        cursor.execute(sql_images_articulo, (imagen['url_image'], imagen['descripcion'], id_articulo))

                    connection.commit()
                

            return jsonify({"success": True, "message": "Artículo creado exitosamente", "id_articulo": id_articulo}), 201

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500


@articulo_fl2.route('/articulo/<int:id_articulo>', methods=['PUT'])
def actualizar_articulo(id_articulo):
    try:
        with connect_to_database() as connection:
            data = request.json
            campos_permitidos = ['ano', 'categoria', 'color', 
                                 'descripcion', 'enable', 'mainImage', 'marca', 'expedition_date',
                                 'modelo', 'precio', 'lastInventoryUpdate', 'kilometraje']
            cambios = []
            valores = []
            for campo in campos_permitidos:
                if campo in data:
                    cambios.append(f"{campo} = ?")
                    valores.append(data[campo])

            if not cambios:
                return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

            # Agregar actualización de lastUpdate
            cambios.append("lastUpdate = CURRENT_TIMESTAMP")
            
            sql_update_articulo = "UPDATE articulo SET " + ", ".join(cambios) + " WHERE id_articulo = ?"
            valores.append(id_articulo)
            
            with connection.cursor() as cursor:
                cursor.execute(sql_update_articulo, valores)

                # Actualizar o insertar especificaciones
                # if 'especificaciones' in data:
                #     for especificacion in data['especificaciones']:
                #         if 'id_especificacion' in especificacion:
                #             # Actualizar especificación existente
                #             sql_update_especificacion = """UPDATE especificaciones SET tipo = ? WHERE id_especificacion = ? AND id_articulo = ?"""
                #             cursor.execute(sql_update_especificacion, (especificacion['tipo'], especificacion['id_especificacion'], id_articulo))
                #         else:
                #             # Insertar nueva especificación
                #             sql_insert_especificacion = """INSERT INTO especificaciones (tipo, id_articulo) VALUES (?, ?)"""
                #             cursor.execute(sql_insert_especificacion, (especificacion['tipo'], id_articulo))
                #             id_especificacion = cursor.lastrowid

                #         # Actualizar o insertar subespecificaciones
                #         # for subespecificacion in especificacion.get('subespecificaciones', []):
                #         #     if 'id_subespecificacion' in subespecificacion:
                #         #         # Actualizar subespecificación existente
                #         #         sql_update_subespecificacion = """UPDATE subespecificaciones SET clave = ?, valor = ? WHERE id_subespecificacion = ? AND id_especificacion = ?"""
                #         #         cursor.execute(sql_update_subespecificacion, (subespecificacion['clave'], subespecificacion['valor'], subespecificacion['id_subespecificacion'], id_especificacion))
                #         #     else:
                #         #         # Insertar nueva subespecificación
                #         #         sql_insert_subespecificacion = """INSERT INTO subespecificaciones (clave, valor, id_especificacion) VALUES (?, ?, ?)"""
                #         #         cursor.execute(sql_insert_subespecificacion, (subespecificacion['clave'], subespecificacion['valor'], id_especificacion))
                #         for clave, valor in especificacion['subespecificaciones'].items():
                #             # Aquí, asumo que no tienes IDs para subespecificaciones individuales,
                #             # por lo que siempre las insertarás como nuevas.
                #             # Necesitarías ajustar esto si también necesitas actualizarlas.
                #             sql_insert_subespecificaciones = """INSERT INTO subespecificaciones (clave, valor, id_especificacion) VALUES (?, ?, ?)"""
                #             cursor.execute(sql_insert_subespecificaciones, (clave, valor, id_especificacion))


                # if 'imagenes' in data:
                #     for imagen in data['imagenes']:
                #         if 'id_imagen' in imagen:
                #             sql_update_imagen = """UPDATE images_articulo SET url_image = ?, descripcion = ? WHERE id_images_articulo = ? AND id_articulo = ?"""
                #             cursor.execute(sql_update_imagen, (imagen['url_image'], imagen['descripcion'], imagen['id_imagen'], id_articulo))
                #         else:
                #             sql_insert_imagen = """INSERT INTO images_articulo (url_image, descripcion, id_articulo) VALUES (?, ?, ?)"""
                #             cursor.execute(sql_insert_imagen, (imagen['url_image'], imagen['descripcion'], id_articulo))

                connection.commit()

            return jsonify({"success": True, "message": f"Artículo con ID {id_articulo} actualizado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500



@articulo_fl2.route('/articulo/<int:id_articulo>', methods=['DELETE'])
def eliminar_articulo(id_articulo):
    try:
        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                sql_delete = "DELETE FROM articulo WHERE id_articulo = ?"
                cursor.execute(sql_delete, (id_articulo,))
                connection.commit()

            return jsonify({"success": True, "message": f"articulo con ID {id_articulo} eliminado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500

# @articulo_fl2.route('/<str:id_usuario>/<int:id_articulo>', methods=['POST'])
# def aritulo_favorito(id_articulo,id_usuario):
# {
#   "especificaciones": [
#     "Motor":"motor1",
#     "Motor":"motor2",
#     "Motor":"algunmotor",
#     "Potencia",
#     "Asientos",
#     "Interior",
#     "Transmisión",
#     "Tracción",
#     "Capacidad de carga",
#     "Altura del suelo",
#     "esecificaion1",
#     "esecificaion2",
#     "Software"
#   ]
# }
@articulo_fl2.route('/<int:id_articulo>/<int:id_usuario>', methods=['POST'])
def articulo_favorito(id_usuario, id_articulo):
    try:
        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                sql_check = """SELECT enable FROM favoritos WHERE id_usuario = ? AND id_articulo = ?"""
                cursor.execute(sql_check, (id_usuario, id_articulo))
                result = resultados_a_json(cursor, unico_resultado=True)

                if result:
                    new_enable_status = not result['enable']
                    sql_update = """UPDATE favoritos SET enable =
                      ? WHERE id_usuario = ? AND id_articulo = ?"""
                    cursor.execute(sql_update, (new_enable_status, id_usuario, id_articulo))
                else:
                    sql_insert = """INSERT INTO favoritos (id_usuario, id_articulo, fecha_agregado, enable) 
                    VALUES (?, ?, ?, ?)"""
                    fecha_agregado = datetime.now().strftime('%Y-%m-%d %H:%M:?')
                    cursor.execute(sql_insert, (id_usuario, id_articulo, fecha_agregado, True))

                connection.commit()
            return jsonify({"success": True, "message": "Estado de favorito actualizado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500
    
@articulo_fl2.route('/<int:id_articulo>/referencia', methods=['GET'])
def articulo_referencia(id_articulo):
    try:
        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                sql = """SELECT s.* FROM sucursal s
                         INNER JOIN articulo_sucursal a_s ON s.id_sucursal = a_s.id_sucursal
                         WHERE a_s.id_articulo = ?"""
                cursor.execute(sql, (id_articulo,))
                sucursales_raw = resultados_a_json(cursor)
                print(sucursales_raw)
                if not sucursales_raw:
                    return jsonify({"error": "No se encontraron sucursales para el artículo"}), 404

                sucursales = [dict(sucursal) for sucursal in sucursales_raw]

                return jsonify(sucursales)
    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500
