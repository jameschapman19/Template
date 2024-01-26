from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/process', methods=['POST'])
def process_files():
    return jsonify({"message": "Hello from Flask!"})

if __name__ == '__main__':
    app.run(debug=True, port=5328)
