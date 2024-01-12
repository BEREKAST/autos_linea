from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from config.database import connect_to_database
# from api.catalogo.catalogo import catalogo_fl
from api.distribuidor.distribuidor import distribuidor_fl
from api.sucursal.sucursal import sucursal_fl
from api.usuario.usuario import usuario_fl
from api.articulo.articulo import articulo_fl

import os

app = Flask(__name__)
app.env = "development"

# CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

CORS(app)
# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#     response.headers.add('Access-Control-Allow-Credentials', 'true')
#     return response

# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#     response.headers.add('Access-Control-Allow-Credentials', 'true')
#     return response

@app.route('/')
def root():
    return '<h1>API DE AUTOS EN LINEA</h1>'
@app.route('/init')
def welcome():
    return '''
        <div style="text-align: center; margin-top:5vh">
            <h1>BIENVENIDOS A LA API DE AUTOS EN LINEA</h1>
            <h3 style="color: dimgray;">ACTUALMENTE SE TIENEN LAS SIGUIENTES ENDPOINTS DISPONIBLES:</h3>
            <ul style="list-style: none;">
                <li><a href="/catalogos">GET: /catalogos</a></li>
                <ul>
                    <li><a href="/catalogos/1">GET: /catalogos/id</a></li>
                </ul>
                <li><a href="/distribuidores">GET: /distribuidores</a></li>
                <ul>
                    <li><a href="/distribuidores/101">GET: /distribuidores/id</a></li>
                </ul>
                <li><a href="/sucursales">GET: /sucursales</a></li>
                <ul>
                    <li><a href="/sucursales/1">GET: /sucursales/id</a></li>
                </ul>
                <li><a href="/usuarios">GET: /usuarios</a></li>
                <ul>
                    <li><a href="/usuarios/102">GET: /usuarios/id</a></li>
                    <li><a href="#">POST: /usuarios/usuario</a></li>
                    <div>       <br>BODY PARA USUARIO:   </br>  {
                "id_usuario":INT,
                "contrasena": str,
                "rol": str,
                "nombres": str,
                "apellidos": str,
                "correo_electronico": str,
                "contacto": str,
                "direccion": str,
                "num_telefono": str,
                "url_logo":str
            }
</div>
<br>  </br> 
                </ul>
                <li><a href="/autos">GET: /autos</a></li>
                <ul>
                    <li><a href="/autos/2">GET: /autos/id</a></li>
                </ul>
            </ul>
            <h3 style="color: dimgray;">LAS MISMAS BAJO LOS MODELOS ENVIADOS</h3>
        </div>
    '''

# app.register_blueprint(catalogo_fl, url_prefix='/catalogos')

app.register_blueprint(distribuidor_fl, url_prefix='/distribuidores')
app.register_blueprint(sucursal_fl, url_prefix='/sucursales')
app.register_blueprint(usuario_fl, url_prefix='/usuarios')
app.register_blueprint(articulo_fl, url_prefix='/articulos')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)