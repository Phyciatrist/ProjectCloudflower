# /run.py

from app import create_app

app = create_app()

if __name__ == '__main__':
    # '0.0.0.0' makes the server accessible from other devices on your network
    # 'debug=True' enables auto-reloading when you save code changes
    app.run(host='0.0.0.0', port=5000, debug=True)
