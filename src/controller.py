from flask import Flask, jsonify, request
from data_handler import DataHandler

app = Flask(__name__)
data_handler = DataHandler()

@app.route("/usuarios", methods=["POST"])
def crear_usuario():
    data = request.json
    if not data.get("alias") or not data.get("nombre") or not data.get("email"):
        return jsonify({"error": "Datos incompletos"}), 422
    if any(u["alias"] == data["alias"] for u in data_handler.users):
        return jsonify({"error": "Alias ya registrado"}), 422

    usuario = {
        "alias": data["alias"],
        "nombre": data["nombre"],
        "email": data["email"],
        "stats": {
            "total": 0,
            "completed": 0,
            "missing": 0,
            "not_marked": 0,
            "rejected": 0
        }
    }
    data_handler.users.append(usuario)
    data_handler.save_data()
    return jsonify(usuario), 201


@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    return jsonify(data_handler.users), 200


@app.route("/usuarios/<alias>", methods=["GET"])
def obtener_usuario(alias):
    user = next((u for u in data_handler.users if u["alias"] == alias), None)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(user), 200


@app.route("/usuarios/<alias>/rides", methods=["GET"])
def obtener_rides_usuario(alias):
    rides = [r for r in data_handler.rides if r["driver"] == alias]
    return jsonify(rides), 200


@app.route("/usuarios/<alias>/rides/<int:ride_id>", methods=["GET"])
def obtener_ride_detallado(alias, ride_id):
    ride = next((r for r in data_handler.rides if r["id"] == ride_id and r["driver"] == alias), None)
    if not ride:
        return jsonify({"error": "Ride no encontrado"}), 404

    participantes = [
        rp for rp in data_handler.ride_participants if rp["ride_id"] == ride_id
    ]

    ride_copy = ride.copy()
    ride_copy["participants"] = []

    for p in participantes:
        stats = next((u["stats"] for u in data_handler.users if u["alias"] == p["alias"]), {})
        ride_copy["participants"].append({
            "confirmation": p["confirmation"],
            "participant": {
                "alias": p["alias"],
                "previousRidesTotal": stats.get("total", 0),
                "previousRidesCompleted": stats.get("completed", 0),
                "previousRidesMissing": stats.get("missing", 0),
                "previousRidesNotMarked": stats.get("not_marked", 0),
                "previousRidesRejected": stats.get("rejected", 0),
            },
            "destination": p["destination"],
            "occupiedSpaces": p["occupiedSpaces"],
            "status": p["status"]
        })

    return jsonify({"ride": ride_copy}), 200


@app.route("/usuarios/<alias>/rides", methods=["POST"])
def crear_ride(alias):
    data = request.json
    if not any(u["alias"] == alias for u in data_handler.users):
        return jsonify({"error": "Usuario no existe"}), 404

    ride_id = len(data_handler.rides) + 1
    ride = {
        "id": ride_id,
        "driver": alias,
        "rideDateAndTime": data["rideDateAndTime"],
        "finalAddress": data["finalAddress"],
        "capacity": data["capacity"],
        "status": "ready",
        "participants": []
    }
    data_handler.rides.append(ride)
    data_handler.save_data()
    return jsonify({"id": ride_id}), 201


@app.route("/usuarios/<alias>/rides/<int:ride_id>/requestToJoin/<participant_alias>", methods=["POST"])
def solicitar_unirse(alias, ride_id, participant_alias):
    ride = next((r for r in data_handler.rides if r["id"] == ride_id and r["driver"] == alias), None)
    if not ride:
        return jsonify({"error": "Ride no encontrado"}), 404
    if ride["status"] != "ready":
        return jsonify({"error": "Ride no está en estado 'ready'"}), 422
    if any(rp["ride_id"] == ride_id and rp["alias"] == participant_alias for rp in data_handler.ride_participants):
        return jsonify({"error": "Ya existe una solicitud para este participante"}), 422

    data = request.json
    nuevo = {
        "ride_id": ride_id,
        "alias": participant_alias,
        "destination": data["destination"],
        "occupiedSpaces": data["occupiedSpaces"],
        "confirmation": None,
        "status": "waiting"
    }
    data_handler.ride_participants.append(nuevo)
    data_handler.save_data()
    return jsonify({"message": "Solicitud enviada"}), 200


@app.route("/usuarios/<alias>/rides/<int:ride_id>/accept/<participant_alias>", methods=["POST"])
def aceptar_participante(alias, ride_id, participant_alias):
    ride = next((r for r in data_handler.rides if r["id"] == ride_id and r["driver"] == alias), None)
    if not ride:
        return jsonify({"error": "Ride no encontrado"}), 404

    participantes = [
        rp for rp in data_handler.ride_participants if rp["ride_id"] == ride_id
    ]
    confirmed = sum(rp["occupiedSpaces"] for rp in participantes if rp["confirmation"] == "confirmed")

    rp = next((rp for rp in participantes if rp["alias"] == participant_alias), None)
    if not rp:
        return jsonify({"error": "Participante no encontrado"}), 404
    if rp["confirmation"] == "confirmed":
        return jsonify({"error": "Participante ya confirmado"}), 422
    if confirmed + rp["occupiedSpaces"] > ride["capacity"]:
        return jsonify({"error": "No hay asientos suficientes"}), 422

    rp["confirmation"] = "confirmed"
    data_handler.save_data()
    return jsonify({"message": "Participante confirmado"}), 200


@app.route("/usuarios/<alias>/rides/<int:ride_id>/reject/<participant_alias>", methods=["POST"])
def rechazar_participante(alias, ride_id, participant_alias):
    rp = next((rp for rp in data_handler.ride_participants if rp["ride_id"] == ride_id and rp["alias"] == participant_alias), None)
    if not rp:
        return jsonify({"error": "Participante no encontrado"}), 404

    rp["confirmation"] = "rejected"
    rp["status"] = "rejected"
    data_handler.save_data()
    return jsonify({"message": "Participante rechazado"}), 200


@app.route("/usuarios/<alias>/rides/<int:ride_id>/start", methods=["POST"])
def iniciar_ride(alias, ride_id):
    ride = next((r for r in data_handler.rides if r["id"] == ride_id and r["driver"] == alias), None)
    if not ride:
        return jsonify({"error": "Ride no encontrado"}), 404

    participantes = [
        rp for rp in data_handler.ride_participants if rp["ride_id"] == ride_id
    ]
    for rp in participantes:
        if rp["confirmation"] not in ["confirmed", "rejected"]:
            return jsonify({"error": "Hay participantes sin confirmar/rechazar"}), 422

    ride["status"] = "inprogress"
    for rp in participantes:
        if rp["confirmation"] == "confirmed":
            rp["status"] = "inprogress"
        elif rp["confirmation"] == "rejected":
            rp["status"] = "rejected"
        else:
            rp["status"] = "missing"

    data_handler.save_data()
    return jsonify({"message": "Ride iniciado"}), 200


@app.route("/usuarios/<alias>/rides/<int:ride_id>/unloadParticipant", methods=["POST"])
def bajar_participante(alias, ride_id):
    data = request.json
    part_alias = data.get("alias")
    rp = next((rp for rp in data_handler.ride_participants if rp["ride_id"] == ride_id and rp["alias"] == part_alias), None)
    if not rp:
        return jsonify({"error": "Participante no encontrado"}), 404
    if rp["status"] != "inprogress":
        return jsonify({"error": "Participante no está en el ride"}), 422

    rp["status"] = "completed"
    data_handler.save_data()
    return jsonify({"message": "Participante bajó del ride"}), 200


@app.route("/usuarios/<alias>/rides/<int:ride_id>/end", methods=["POST"])
def terminar_ride(alias, ride_id):
    ride = next((r for r in data_handler.rides if r["id"] == ride_id and r["driver"] == alias), None)
    if not ride:
        return jsonify({"error": "Ride no encontrado"}), 404

    participantes = [
        rp for rp in data_handler.ride_participants if rp["ride_id"] == ride_id
    ]
    for rp in participantes:
        if rp["status"] == "inprogress":
            rp["status"] = "notmarked"

    ride["status"] = "finished"
    data_handler.save_data()
    return jsonify({"message": "Ride terminado"}), 200


if __name__ == '__main__':
    app.run(debug=True)