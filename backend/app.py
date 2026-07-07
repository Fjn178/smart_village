from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({"code": 0, "message": "智联乡策后端已启动"})

@app.route('/api/health')
def health():
    return jsonify({"code": 0, "data": {"status": "ok"}})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)