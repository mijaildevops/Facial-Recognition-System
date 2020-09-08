from flask import Flask, request, jsonify
# DB
import pymysql
# ENCRIPTAR VARIABLES
from werkzeug.security import generate_password_hash, check_password_hash

from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

# Guid aletoreo
import uuid

from settings import Conexion, server
Conexion = Conexion
 
#MAIN 
app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)


#////////////////////////////////////////////////////////////////////////////////   
# HOME PAGE
#////////////////////////////////////////////////////////////////////////////////  
@app.route('/')
def home():
    return {'message': 'Home Page'}
     
#//////////////////////////////////////////////////////////////////////////////// 
# Web Services "USERS"  
# METODO GET
#////////////////////////////////////////////////////////////////////////////////  
@app.route('/users', methods=['GET'])
@jwt_required
def obtener_user():


    # Connect to the database
    connection = pymysql.connect(host=Conexion[0],
                        user=Conexion[1],
                        password=Conexion[2],
                        db=Conexion[3],
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)

    user = get_jwt_identity()
    print(user)
    

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
# Web Services "USERS"   
# METODO GET by ID
#////////////////////////////////////////////////////////////////////////////////  
@app.route('/users/<userid>', methods=['GET'])
@jwt_required
def obtener_userById(userid):


    # Connect to the database
    connection = pymysql.connect(host=Conexion[0],
                        user=Conexion[1],
                        password=Conexion[2],
                        db=Conexion[3],
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)

    user = get_jwt_identity()
    print(user)
    

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
# Web Services "USERS"  
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

        # Generar Guid o APIKey aleatoreo
        ApiKey = str(uuid.uuid4())

        with connection.cursor() as cursor:
            # Si el Usuario no existe en la DB, procede a Crear el registro 
            sql = "INSERT INTO `usuario` (username, password, email, ApiKey) Values (%s, %s,%s,%s)"
            cursor.execute(sql, (username, hashed_password, email, ApiKey))
            connection.commit()

        return {'message': 'Usuario creado con exito', 'username': username,'password': hashed_password, 'email': email, 'ApiKey': ApiKey}
        
    else:
        return not_found()
     
#////////////////////////////////////////////////////////////////////////////////   
# Web Services "USERS"  
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

#////////////////////////////////////////////////////////////////////////////////   
# Web Services "USERS"  
# METODO DELETE
#////////////////////////////////////////////////////////////////////////////////  
@app.route('/delete_users/<userid>', methods=['DELETE'])
@jwt_required
def borrar_user(userid):


    connection = pymysql.connect(host=Conexion[0],
                        user=Conexion[1],
                        password=Conexion[2],
                        db=Conexion[3],
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)

    user = get_jwt_identity()
    print(user)

    with connection.cursor() as cursor:

                # Delete data User
        sql = "DELETE FROM `usuario` WHERE Id = %s"
        cursor.execute(sql, userid)
        connection.commit()

    return {'message': 'Usuario eliminado'}

#////////////////////////////////////////////////////////////////////////////////   
# Web Services "TOKEN"  
# Generar Token 
#////////////////////////////////////////////////////////////////////////////////  
@app.route('/token', methods=['POST'])
def obtener_token():
    
    # valores recibidos en la request
    ApiKey = request.json['ApiKey']
    email = request.json['email']

    # Inicializar variable
    EmailDB = None
    KeyDB = None

     # Connect to the database
    connection = pymysql.connect(host=Conexion[0],
                        user=Conexion[1],
                        password=Conexion[2],
                        db=Conexion[3],
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)

  
    with connection.cursor() as cursor:
        #SENTENCIA SQL
        query = "SELECT email, ApiKey FROM usuario where email = %s"
        cursor.execute(query, email)
        resultados = cursor.fetchone()
        connection.commit()
        
        try:
            # Verificamos si el email existe
            EmailDB = resultados["email"]
            KeyDB = resultados["ApiKey"]
        except:
            print('User not found in db')

        # comparamos los datos recidos contra los datos de la DB (deben ser iguales)
        if (email == EmailDB and ApiKey==KeyDB):
            # Generamos el Token
            access_token = create_access_token(identity={"email": email})
            return {"Token": access_token}
        else:
            # Respuesta si la validacion es incorrecta
            return {"Error": "Token No Generado, Datos Invalidos"}

    

#//////////////////////////////////////////////////////////////////////////////// 
# MANEJO DE ERRORES
#//////////////////////////////////////////////////////////////////////////////// 
@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'message': 'Pagina no encontrada ' + request.url,
        'status': 404
    })
    response.status_code = 404
    return response



if __name__ == "__main__":
    app.run(port = 5080, debug = True, host=server) # PC Main
