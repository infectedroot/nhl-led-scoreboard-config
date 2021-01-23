import flask, time

from flask import request, jsonify, Flask, send_from_directory

configFile = "config.json.sample"

app = flask.Flask(__name__, static_url_path='', static_folder='.')
app.config["DEBUG"] = True


@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
