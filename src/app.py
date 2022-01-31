from api_server import create_app

from waitress import serve
from config import Config
app = create_app()

if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port=Config.PORT)
    serve(app, host='0.0.0.0', port=Config.PORT, threads=Config.THREAD_COUNT)

