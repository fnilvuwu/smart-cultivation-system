import os
from flask import Flask
from socket_io import socketio
from config import CONFIG

from index import bp as index_bp
from errors import bp as error_bp
from smart_cultivation_system import bp as llt_bp
from receive_data import bp as rd_bp
from insert_tracker import bp as db_bp

from cache import init_cache_app
from compress import init_compress_app
from rate_limiter import init_rate_limiter
from database.mysql import init_db, init_db_command, drop_db_command


app = Flask(__name__)
app.config.update(CONFIG)

# Register Blueprint
app.register_blueprint(index_bp)
app.register_blueprint(error_bp)
app.register_blueprint(llt_bp)
app.register_blueprint(rd_bp)
app.register_blueprint(db_bp)

# Initializing
init_cache_app(app)
init_compress_app(app)
init_rate_limiter(app)
init_db(app)

# CLI Command
app.cli.add_command(init_db_command)
app.cli.add_command(drop_db_command)

if __name__ == "__main__":
    socketio.run(
        app, debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080))
    )
