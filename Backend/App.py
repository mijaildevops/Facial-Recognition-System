from flask import Flask, request, jsonify
# DB
import pymysql
# ENCRIPTAR VARIABLES
from werkzeug.security import generate_password_hash, check_password_hash

from settings import Conexion, server
Conexion = Conexion
 
#MAIN 
app = Flask(__name__)


#////////////////////////////////////////////////////////////////////////////////   
# HOME PAGE
#////////////////////////////////////////////////////////////////////////////////  
@app.route('/')
def home():
    return {'message': 'Home Page'}


#////////////////////////////////////////////////////////////////////////////////   
# METODO GET
#////////////////////////////////////////////////////////////////////////////////  
@app.route('/users', methods=['GET'])
def obtener_user():


    # Connect to the database
    connection = pymysql.connect(host=Conexion[0],
                        user=Conexion[1],
                        password=Conexion[2],
                        db=Conexion[3],
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        #SENTENCIA SQL
        query = "SELECT * FROM usuario"
        cursor.execute(query)
        resultados = cursor.fetchall()
        connection.commit()
        #JSON DE RESPUESTA
        response = jsonify({
                        'resultados': resultados,
                        'mensaje': 'Datos de usuarios'
                        })
    return response


#////////////////////////////////////////////////////////////////////////////////   
# METODO GETbyID
#////////////////////////////////////////////////////////////////////////////////  
@app.route('/users/<userid>', methods=['GET'])
def obtener_userById(userid):


    # Connect to the database
    connection = pymysql.connect(host=Conexion[0],
                        user=Conexion[1],
                        password=Conexion[2],
                        db=Conexion[3],
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        #SENTENCIA SQL
        query = "SELECT * FROM usuario where Id = %s"
        cursor.execute(query, userid)
        resultados = cursor.fetchone()
        connection.commit()
        #JSON DE RESPUESTA
        response = jsonify({
                        'resultados': resultados,
                        'mensaje': 'Datos de usuarios'
                        })
    return response
        
#////////////////////////////////////////////////////////////////////////////////   
# METODO POST
#////////////////////////////////////////////////////////////////////////////////  
@app.route('/users', methods=['POST'])
def crear_user():

    # Connect to the database
    connection = pymysql.connect(host=Conexion[0],
                        user=Conexion[1],
                        password=Conexion[2],
                        db=Conexion[3],
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)

    #Crear usuario
    print("Funcion de crear usuario")

    

    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    
    print(username, password, email)
        
    if username and email and password:

        hashed_password = generate_password_hash(password)

        with connection.cursor() as cursor:
            # Si el Usuario no existe en la DB, procede a Crear el registro 
            sql = "INSERT INTO `usuario` (username, password, email) Values (%s,%s,%s)"
            cursor.execute(sql, (username, hashed_password, email))
            connection.commit()

        return {'message': 'Usuario creado con exito', 'username': username,'password': hashed_password, 'email': email}
        
    else:
        return not_found()
        print(username)
        return {'error': 'Fallo la operacion, no se puedo crear usuario'}


# MANEJO DE ERRORES
@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'message': 'Pagina no encontrada ' + request.url,
        'status': 404
    })
    response.status_code = 404
    return response
        
#////////////////////////////////////////////////////////////////////////////////   
# METODO DELETE
#////////////////////////////////////////////////////////////////////////////////  
@app.route('/users/<userid>', methods=['DELETE'])
def borrar_user(userid):


    connection = pymysql.connect(host=Conexion[0],
                        user=Conexion[1],
                        password=Conexion[2],
                        db=Conexion[3],
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:

                # Delete data User
        sql = "DELETE FROM `usuario` WHERE Id = %s"
        cursor.execute(sql, userid)
        connection.commit()

    return {'message': 'Usuario eliminado'}

#////////////////////////////////////////////////////////////////////////////////   
# METODO PUT
#////////////////////////////////////////////////////////////////////////////////  
@app.route('/users/<userid>', methods=['PUT'])
def actualizar_user(userid):

    username = request.json['username']
    password = request.json['password']
    email = request.json['email']

    # Connect to the database
    connection = pymysql.connect(host=Conexion[0],
                        user=Conexion[1],
                        password=Conexion[2],
                        db=Conexion[3],
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:

        query = """UPDATE usuario set password = %s, email = %s, username = %s where Id  = %s """
        data_lista = (password, email, username, userid)
        cursor.execute(query, data_lista)
        connection.commit()
        response = jsonify({
                    
                        'mensaje': 'Datos actualizados'
                        })


    return response


if __name__ == "__main__":
    app.run(port = 5080, debug = True, host='') # PC Main