from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.db import load_db, save_db, load_stats, save_stats, ensure_files

app = Flask(__name__, static_url_path="/static", static_folder="static")
socketio = SocketIO(app, cors_allowed_origins="*")

ensure_files()

@app.route("/")
def home():
    return "Zerduk Web Online 🚀"

@app.route("/game/<code>")
def lobby(code):
    db = load_db()
    game = db.get(code)
    if not game:
        return "❌ Partida no encontrada", 404

    total = len(game.get("players", {}))
    vivos = sum(1 for p in game.get("players", {}).values() if p.get("alive", True))

    # Ranking Top 5
    stats = load_stats()
    ranking = sorted(stats.values(), key=lambda x: x.get("victorias", 0), reverse=True)[:5]

    return render_template(
        "lobby.html",
        code=code,
        game=game,
        total=total,
        vivos=vivos,
        ranking=ranking
    )


@app.route("/role/<code>")
def role(code):
    player_id = request.args.get("user")
    if not player_id:
        return "❌ Falta parámetro ?user=<player_id>", 400
    db = load_db()
    game = db.get(code)
    if not game:
        return "❌ Partida no encontrada", 404
    player = game.get("players", {}).get(player_id)
    if not player:
        return "❌ Jugador no encontrado en esta partida", 404
    return render_template("role.html", player=player, code=code, player_id=player_id)

@app.route("/ranking")
def ranking():
    stats = load_stats()
    ordered = sorted(stats.values(), key=lambda x: x.get("victorias", 0), reverse=True)
    return render_template("ranking.html", ranking=ordered[:10])

# ---------- APIs para acciones desde la web ----------

@app.post("/api/eliminar")
def api_eliminar():
    payload = request.get_json(force=True, silent=True) or {}
    code = payload.get("code")
    player_id = payload.get("player_id")
    requester_id = payload.get("requester_id")  # opcional: validar host/admin
    if not code or not player_id:
        return jsonify({"ok": False, "error": "code y player_id son requeridos"}), 400

    db = load_db()
    game = db.get(code)
    if not game:
        return jsonify({"ok": False, "error": "Partida no encontrada"}), 404

    players = game.get("players", {})
    if player_id not in players:
        return jsonify({"ok": False, "error": "Jugador no encontrado"}), 404

    players[player_id]["alive"] = False
    save_db(db)

    # Notificar a todos los clientes conectados a ese lobby
    socketio.emit("update_game", {"code": code})
    return jsonify({"ok": True})

@app.post("/api/create_game")
def api_create_game():
    # Permite que el bot cree partidas vía HTTP si lo prefieres
    data = request.get_json(force=True, silent=True) or {}
    code = data.get("code")
    host_id = str(data.get("host_id"))
    players = data.get("players")  # dict de player_id -> {name, impostor, champion, alive}
    if not code or not players:
        return jsonify({"ok": False, "error": "code y players son requeridos"}), 400

    db = load_db()
    db[code] = {
        "host_id": host_id,
        "players": players
    }
    save_db(db)
    socketio.emit("update_game", {"code": code})
    return jsonify({"ok": True})

@app.post("/api/update_stats")
def api_update_stats():
    # Permite actualizar stats desde el bot tras finalizar partida
    data = request.get_json(force=True, silent=True) or {}
    stats = load_stats()
    for pid, entry in data.items():
        s = stats.get(str(pid), {"nombre": entry.get("nombre", ""), "partidas": 0, "victorias": 0, "impostor": 0})
        s["nombre"] = entry.get("nombre", s.get("nombre", ""))
        s["partidas"] = s.get("partidas", 0) + entry.get("partidas", 0)
        s["victorias"] = s.get("victorias", 0) + entry.get("victorias", 0)
        s["impostor"] = s.get("impostor", 0) + entry.get("impostor", 0)
        stats[str(pid)] = s
    save_stats(stats)
    socketio.emit("update_ranking", {})
    return jsonify({"ok": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)

