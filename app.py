from flask import Flask, request, jsonify, redirect
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# ------------------- Database Connection -------------------
def get_db_connection():
    return psycopg2.connect(
        host="dpg-d2j4k0er433s73a53icg-a.oregon-postgres.render.com",
        database="postdb_iohr",
        user="postdb_iohr_user",
        password="obGsnQvgZoFnRp1zYDjv947dJD3vo0K6",
        sslmode="require"
    )

# ------------------- Swagger UI Setup -------------------
SWAGGER_URL = '/swagger'  # UI path
API_URL = '/swagger.json'  # JSON path
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL,
    config={'app_name': "Flask Player CRUD API", 'docExpansion': 'list'}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Redirect root to Swagger UI

def create_sessions_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            game_type VARCHAR(50) NOT NULL,
            bet_type VARCHAR(50) NOT NULL,
            features TEXT,
            time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# Call this at startup
create_sessions_table()

@app.route('/')
def root():
    return redirect('/swagger')  # <- Just redirect to the blueprint path

# ------------------- Swagger JSON -------------------
# ------------------- Swagger JSON -------------------
@app.route("/swagger.json")
def swagger_json():
    return jsonify({
        "swagger": "2.0",
        "info": {
            "title": "Flask Player CRUD API",
            "version": "1.0",
            "description": "CRUD API for Player Management and Sessions"
        },
        "schemes": ["http", "https"],  # <-- comma added here
        "paths": {
            "/players": {
                "get": {
                    "summary": "Get all players",
                    "responses": {
                        "200": {
                            "description": "List of players",
                            "schema": {"type": "array", "items": {"$ref": "#/definitions/Player"}}
                        }
                    }
                },
                "post": {
                    "summary": "Create a new player",
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "required": True,
                            "schema": {"$ref": "#/definitions/PlayerCreate"}
                        }
                    ],
                    "responses": {"201": {"description": "Player created"}}
                }
            },
            "/players/{id}": {
                "put": {
                    "summary": "Update a player by ID",
                    "parameters": [
                        {"name": "id", "in": "path", "type": "integer", "required": True},
                        {"name": "body", "in": "body", "required": True, "schema": {"$ref": "#/definitions/PlayerUpdate"}}
                    ],
                    "responses": {"200": {"description": "Player updated"}}
                },
                "delete": {
                    "summary": "Delete a player by ID",
                    "parameters": [{"name": "id", "in": "path", "type": "integer", "required": True}],
                    "responses": {"200": {"description": "Player deleted"}}
                }
            },
            "/sessions": {
                "get": {
                    "summary": "Get all sessions",
                    "responses": {
                        "200": {
                            "description": "List of sessions",
                            "schema": {"type": "array", "items": {"$ref": "#/definitions/Session"}}
                        }
                    }
                },
                "post": {
                    "summary": "Create a new session",
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "required": True,
                            "schema": {"$ref": "#/definitions/SessionCreate"}
                        }
                    ],
                    "responses": {"201": {"description": "Session created"}}
                }
            },
            "/sessions/{id}": {
                "put": {
                    "summary": "Update a session by ID",
                    "parameters": [
                        {"name": "id", "in": "path", "type": "integer", "required": True},
                        {"name": "body", "in": "body", "required": True, "schema": {"$ref": "#/definitions/SessionUpdate"}}
                    ],
                    "responses": {"200": {"description": "Session updated"}}
                },
                "delete": {
                    "summary": "Delete a session by ID",
                    "parameters": [{"name": "id", "in": "path", "type": "integer", "required": True}],
                    "responses": {"200": {"description": "Session deleted"}}
                }
            }
        },
        "definitions": {
            "Player": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "created_at": {"type": "string"},
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "role": {"type": "string"}
                }
            },
            "PlayerCreate": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "role": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["name", "email"]
            },
            "PlayerUpdate": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "role": {"type": "string"},
                    "password": {"type": "string"}
                }
            },
            "Session": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "role": {"type": "string"},
                    "game_type": {"type": "string"},
                    "bet_type": {"type": "string"},
                    "features": {"type": "string"}
                }
            },
            "SessionCreate": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "role": {"type": "string"},
                    "game_type": {"type": "string"},
                    "bet_type": {"type": "string"},
                    "features": {"type": "string"}
                },
                "required": ["name", "role", "game_type", "bet_type"]
            },
            "SessionUpdate": {
                "type": "object",
                "properties": {
                    "game_type": {"type": "string"},
                    "bet_type": {"type": "string"},
                    "features": {"type": "string"}
                }
            }
        }
    })


# ------------------- CRUD Endpoints -------------------
@app.route("/players", methods=["GET"])
def get_players():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, created_at, name, email, role FROM player")
    players = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(players)

@app.route("/players", methods=["POST"])
def add_player():
    data = request.json
    name = data["name"]
    email = data["email"]
    role = data.get("role", "player")
    password = data.get("password", "default123")
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO player (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
        (name, email, hashed, role)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Player created"}), 201

@app.route("/players/<int:id>", methods=["PUT"])
def update_player(id):
    data = request.json
    name = data.get("name")
    email = data.get("email")
    role = data.get("role")
    password = data.get("password")

    conn = get_db_connection()
    cur = conn.cursor()

    if password:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cur.execute(
            "UPDATE player SET name=%s, email=%s, role=%s, password_hash=%s WHERE id=%s",
            (name, email, role, hashed, id)
        )
    else:
        cur.execute(
            "UPDATE player SET name=%s, email=%s, role=%s WHERE id=%s",
            (name, email, role, id)
        )

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Player updated"})

@app.route("/players/<int:id>", methods=["DELETE"])
def delete_player(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM player WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Player deleted"})

    # ------------------- SESSIONS CRUD -------------------
@app.route("/sessions", methods=["GET"])
def get_sessions():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM sessions ORDER BY time DESC")
    sessions = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(sessions)

@app.route("/sessions", methods=["POST"])
def create_session():
    data = request.json
    name = data.get("name")
    role = data.get("role")
    game_type = data.get("game_type")
    bet_type = data.get("bet_type")
    features = data.get("features", "")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO sessions (name, role, game_type, bet_type, features)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, time
        """,
        (name, role, game_type, bet_type, features)
    )
    session_id, session_time = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "message": "Session created",
        "session_id": session_id,
        "time": session_time.isoformat()  # return ISO string for frontend
    }), 201


@app.route("/sessions/<int:id>", methods=["PUT"])
def update_session(id):
    data = request.json
    game_type = data.get("game_type")
    bet_type = data.get("bet_type")
    features = data.get("features")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE sessions
        SET game_type=%s, bet_type=%s, features=%s
        WHERE id=%s
        """,
        (game_type, bet_type, features, id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Session updated"})

@app.route("/sessions/<int:id>", methods=["DELETE"])
def delete_session(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Session deleted"})


# ------------------- Run App -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
