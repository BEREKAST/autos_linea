from flask import Flask, request, jsonify
from flask import Blueprint
from config.database import connect_to_database
from utils.serializer import resultados_a_json

usuario_fl2 = Blueprint('usuario_post', __name__)

@usuario_fl2.route('/usuario', methods=['POST'])
def crear_usuario():
    try:
        with connect_to_database() as connection:
            data = request.json
            campos_requeridos = [
                                 'rol', 'nombres', 'apellidos',
                                   'correo_electronico', 'num_telefono']
            
            if not all(campo in data for campo in campos_requeridos):
                return jsonify({"error": "Faltan campos requeridos"}), 400
            print(data)        
            with connection.cursor() as cursor:
                sql = """INSERT INTO usuario (
                             rol, nombres, apellidos, 
                             correo_electronico, num_telefono, url_logo, 
                             coordenadas, id_sucursal, id_distribuidor, created, lastUpdate, id_usuario_firebase
                         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)"""
                valores = (
                    data['rol'],
                    data['nombres'],
                    data['apellidos'],
                    data['correo_electronico'],
                    data['num_telefono'],
                    data.get('url_logo', ''),
                    data.get('coordenadas', ''),
                    data.get('id_sucursal'),
                    data.get('id_distribuidor'),
                    data.get('id_usuario_firebase','')
                )
                cursor.execute(sql, valores)
                connection.commit()

            return jsonify({"success": True, "message": "Usuario creado exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500
    
@usuario_fl2.route('/usuario/<int:id_usuario>', methods=['PUT'])
def actualizar_usuario(id_usuario):
    try:
        with connect_to_database() as connection:
            data = request.json
            campos_permitidos = ['rol', 'nombres', 'apellidos', 'correo_electronico',
                                 'num_telefono', 'url_logo', 'coordenadas', 
                                 'id_sucursal', 'id_distribuidor', 'id_usuario_firebase']
            cambios = []
            valores = []
            for campo in campos_permitidos:
                if campo in data:
                    cambios.append(f"{campo} = ?")
                    valores.append(data[campo])

            if not cambios:
                return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

            cambios.append("lastUpdate = CURRENT_TIMESTAMP")
            
            sql_update = "UPDATE usuario SET " + ", ".join(cambios) + " WHERE id_usuario = ?"
            valores.append(id_usuario)
            
            with connection.cursor() as cursor:
                cursor.execute(sql_update, valores)
                connection.commit()

            return jsonify({"success": True, "message": f"Usuario con ID {id_usuario} actualizado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500
    

@usuario_fl2.route('/usuario/<int:id_usuario>', methods=['DELETE'])
def eliminar_usuario(id_usuario):
    try:
        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                sql_delete = "DELETE FROM usuario WHERE id_usuario = ?"
                cursor.execute(sql_delete, (id_usuario,))
                connection.commit()

            return jsonify({"success": True, "message": f"Usuario con ID {id_usuario} eliminado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500


@usuario_fl2.route('/usuario_existe', methods=['GET'])
def usuario_existe_por_telefono():
    num_telefono = request.args.get('num_telefono')
    if not num_telefono:
        return jsonify({"error": "Número de teléfono requerido"}), 400
    try:
        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                print(num_telefono)
                sql = "SELECT COUNT(*) FROM usuario WHERE num_telefono = ?"
                cursor.execute(sql, (num_telefono,))
                result = resultados_a_json(cursor, unico_resultado=True)
              
                existe = result['COUNT(*)'] > 0
                id_usuario = None
                if existe:
                    sql_firebase = "SELECT * FROM usuario WHERE num_telefono = ?"
                    cursor.execute(sql_firebase, (num_telefono,))
                    result_firebase = resultados_a_json(cursor, unico_resultado=True)
                    id_usuario = result_firebase['id_usuario'] if result_firebase else None
                    return jsonify({"existe": existe, "data": result_firebase}), 200
                else:
                    id_usuario="No Existe"
                    return jsonify({"existe": existe, "id_usuario": id_usuario}), 200
                
        
    except Exception as e:
        print(e)
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500

@usuario_fl2.route('/<int:id_usuario>/favoritos', methods=['GET'])
def obtener_autos_favoritos_usuario(id_usuario): 
    try:
        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                # Obtener todos los artículos favoritos
                sql = """
                    SELECT 
                        articulo.*, 
                        favoritos.enable as favorite
                    FROM 
                        articulo
                    JOIN 
                        favoritos ON articulo.id_articulo = favoritos.id_articulo
                    WHERE 
                        favoritos.enable = 1 AND favoritos.id_usuario = ? 
                    ORDER BY 
                        articulo.id_articulo
                """
                cursor.execute(sql, (id_usuario,))
                articulos_raw = resultados_a_json(cursor)
                if not articulos_raw:
                    return jsonify({"error": f"No se encontraron autos favoritos para el usuario con ID {id_usuario}"}), 404
                 
                # Procesar cada artículo
                articulos_favoritos = []
                for articulo in articulos_raw:
                    id_articulo = articulo['id_articulo']
                    # Obtener especificaciones para el artículo
                    sql_especificaciones = """
                        SELECT especificaciones.*, subespecificaciones.clave, subespecificaciones.valor
                        FROM especificaciones
                        LEFT JOIN subespecificaciones ON especificaciones.id_especificacion = subespecificaciones.id_especificacion
                        WHERE especificaciones.id_articulo = ?
                    """
                    cursor.execute(sql_especificaciones, (id_articulo,))
                    especificaciones_raw = resultados_a_json(cursor)
                    
                    # Agrupar subespecificaciones por especificación
                    especificaciones = {}
                    for esp in especificaciones_raw:
                        id_esp = esp['id_especificacion']
                        if id_esp not in especificaciones:
                            especificaciones[id_esp] = {'tipo': esp['tipo'], 'subespecificaciones': {}}
                        especificaciones[id_esp]['subespecificaciones'][esp['clave']] = esp['valor']

                    # Obtener imágenes para el artículo
                    sql_imagenes = """
                        SELECT url_image, descripcion
                        FROM images_articulo
                        WHERE id_articulo = ?
                    """
                    cursor.execute(sql_imagenes, (id_articulo,))
                    imagenes = resultados_a_json(cursor)

                    # Agregar datos al artículo
                    articulo['especificaciones'] = list(especificaciones.values())
                    articulo['imagenes'] = imagenes
                    articulos_favoritos.append(articulo)

                return jsonify({"success": True, "autos_favoritos": articulos_favoritos}), 200

    except Exception as e:
        return jsonify({"error": f"Error en la base de datos: {e}"}), 500
