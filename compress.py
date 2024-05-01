from flask_compress import Compress

compress = Compress()


def init_compress_app(app):
    compress.init_app(app)
