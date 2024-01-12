

# async def get_sucursal(connection, sucursal_id):
#     try:
#         async with connection.cursor() as cursor:
#             # Obtener información de la sucursal
#             sql_sucursal = """SELECT nombre FROM sucursal WHERE id_sucursal = %s"""
#             await cursor.execute(sql_sucursal, (sucursal_id,))
#             sucursal_info = await cursor.fetchone()

#             return sucursal_info
#     except Exception as e:
#         print(f"Error obtaining sucursal info for ID {sucursal_id}: {e}")
#         return None

# async def get_auto(connection, auto_id):
#     try:
#         async with connection.cursor() as cursor:
#             # Obtener información de la sucursal
#             sql_auto = """SELECT marca, modelo,categoria_de_auto,anio,precio,kilometraje FROM auto WHERE id_auto = %s"""
#             await cursor.execute(sql_auto, (auto_id,))
#             sucursal_info = await cursor.fetchone()

#             return sucursal_info
#     except Exception as e:
#         print(f"Error obtaining sucursal info for ID {auto_id}: {e}")
#         return None
 