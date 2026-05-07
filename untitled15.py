!pip install flask pyngrok

from flask import Flask, request, jsonify
from pyngrok import ngrok
import os

app = Flask(__name__)

usuarios = []
tareas = []

# ------------------ CONFIGURACIÓN SEGURA ------------------

# Guardar token en variable de entorno
NGROK_TOKEN = os.getenv("NGROK_AUTHTOKEN")

if NGROK_TOKEN:
    ngrok.set_auth_token(NGROK_TOKEN)

# ------------------ FUNCIONES AUXILIARES ------------------

def validar_campos(data, campos):
    for campo in campos:
        if not data.get(campo) or str(data.get(campo)).strip() == "":
            return False, campo
    return True, None

# ------------------ USUARIOS ------------------

@app.route('/register', methods=['POST'])
def register():

    data = request.json

    # Validar JSON
    if not data:
        return jsonify({
            "error": "No se enviaron datos en formato JSON"
        }), 400

    # Validar campos obligatorios
    valido, campo = validar_campos(data, ["email", "password"])

    if not valido:
        return jsonify({
            "error": f"El campo '{campo}' es obligatorio"
        }), 400

    usuarios.append(data)

    return jsonify({
        "msg": "Usuario registrado correctamente",
        "data": data
    }), 201


@app.route('/login', methods=['POST'])
def login():

    data = request.json

    # Validar JSON
    if not data:
        return jsonify({
            "error": "No se envió JSON"
        }), 400

    # Validar campos
    valido, campo = validar_campos(data, ["email", "password"])

    if not valido:
        return jsonify({
            "error": f"El campo '{campo}' es obligatorio"
        }), 400

    for u in usuarios:

        if (
            u.get("email") == data.get("email") and
            u.get("password") == data.get("password")
        ):

            return jsonify({
                "msg": "Login exitoso"
            }), 200

    return jsonify({
        "error": "Credenciales incorrectas"
    }), 401


# ------------------ TAREAS ------------------

@app.route('/tasks', methods=['POST'])
def crear_tarea():

    data = request.json

    # Validar JSON
    if not data:
        return jsonify({
            "error": "No se enviaron datos"
        }), 400

    # Validar campos obligatorios
    valido, campo = validar_campos(
        data,
        ["titulo", "descripcion"]
    )

    if not valido:
        return jsonify({
            "error": f"El campo '{campo}' es obligatorio"
        }), 400

    tareas.append(data)

    return jsonify({
        "msg": "Tarea creada correctamente",
        "tarea": data
    }), 201


@app.route('/tasks', methods=['GET'])
def obtener_tareas():

    estado = request.args.get("estado")
    fecha = request.args.get("fecha")

    resultado = tareas

    if estado:
        resultado = [
            t for t in resultado
            if t.get("estado") == estado
        ]

    if fecha:
        resultado = [
            t for t in resultado
            if t.get("fecha") == fecha
        ]

    return jsonify(resultado), 200


@app.route('/tasks/<int:id>', methods=['PUT'])
def editar_tarea(id):

    if id >= len(tareas):

        return jsonify({
            "error": "La tarea no existe"
        }), 404

    data = request.json

    if not data:
        return jsonify({
            "error": "No se enviaron datos"
        }), 400

    tareas[id].update(data)

    return jsonify({
        "msg": "Tarea actualizada correctamente",
        "tarea": tareas[id]
    }), 200


@app.route('/tasks/<int:id>', methods=['DELETE'])
def eliminar_tarea(id):

    if id >= len(tareas):

        return jsonify({
            "error": "La tarea no existe"
        }), 404

    tareas.pop(id)

    return jsonify({
        "msg": "Tarea eliminada correctamente"
    }), 200


# ------------------ ASIGNACIÓN ------------------

@app.route('/tasks/<int:id>/assign', methods=['POST'])
def asignar_tarea(id):

    if id >= len(tareas):

        return jsonify({
            "error": "La tarea no existe"
        }), 404

    data = request.json

    if not data:
        return jsonify({
            "error": "No se enviaron datos"
        }), 400

    valido, campo = validar_campos(data, ["email"])

    if not valido:
        return jsonify({
            "error": f"El campo '{campo}' es obligatorio"
        }), 400

    tareas[id]["usuario"] = data.get("email")

    return jsonify({
        "msg": "Tarea asignada correctamente",
        "tarea": tareas[id]
    }), 200


# ------------------ START SERVER ------------------

public_url = ngrok.connect(5000)

print("URL pública:", public_url)

app.run(port=5000)

