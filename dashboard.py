import os

from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='dashboard')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    # Check if the requested path exists as a file in the 'dashboard' folder
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # For any other route, serve 'index.html' for the SPA
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
