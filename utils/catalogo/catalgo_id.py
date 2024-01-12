# from flask import Blueprint, render_template
# from config.database import connect_to_database
# from flask import Flask, Response, jsonify, request
# from api.catalogo.funtions.gets import get_auto,get_sucursal


# catalogo_fl1=Blueprint('catalogo_id', __name__)


# async def process_catalogo_with_sucursal_by_id(connection, catalogo_id):
#     try:
#         async with connection.cursor() as cursor:
#             sql_catalogo = """SELECT id_catalogo, sucursal_id, auto_id, created, lastUpdate, lastInventoryUpdate, especificaciones, main_image, descripcion
#                               FROM catalogo WHERE id_catalogo = %s"""
#             await cursor.execute(sql_catalogo, (catalogo_id,))
#             catalogo_record = await cursor.fetchone()

#             if catalogo_record:
#                 sucursal_id = catalogo_record['sucursal_id']
#                 auto_id = catalogo_record['auto_id']
#                 sucursal_info = await get_sucursal(connection, sucursal_id)
#                 auto_info = await get_auto(connection, auto_id)
#                 catalogo_record['sucursal_info'] = sucursal_info
#                 catalogo_record['auto_info'] = auto_info
#                 return catalogo_record
#             else:
#                 return None
#     except Exception as e:
#         print(f"Error obtaining catalogo info for ID {catalogo_id}: {e}")
#         return None


# @catalogo_fl1.route('/<int:catalogo_id>', methods=['GET'])
# async def get_catalogo_by_id(catalogo_id):
#     async with connect_to_database() as con:
#         try:
#             catalogo_by_id= await process_catalogo_with_sucursal_by_id(con,catalogo_id)
#             if catalogo_by_id:
#                 return jsonify({"success": True, "data": catalogo_by_id})
#             else:
#                 return jsonify({"error": f"catalogo with ID {catalogo_id} not found"}), 404
#         except Exception as e :
#             return jsonify({"error":"Data Base erorr {}".format(e)})