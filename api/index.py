from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/process', methods=['POST'])
def process_files():
    files = request.files.getlist('files')
    query = request.form.get('query')

    # TODO: Process files and query here
    # Example: Just return the filenames and query
    filenames = [file.filename for file in files]
    return jsonify({"filenames": filenames, "query": query})

if __name__ == '__main__':
    app.run(debug=True, port=5328)
