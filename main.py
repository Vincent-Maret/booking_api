from flask import Flask
from flask import request
from flask import Response

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
