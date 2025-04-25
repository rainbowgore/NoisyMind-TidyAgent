from flask import Flask, Response

app = Flask(__name__)

@app.route('/metrics')
def metrics():
    with open('metrics.txt', 'r') as f:
        data = f.read()
    return Response(data, mimetype='text/plain')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)