from flask import Flask
app = Flask(__name__)


from api import routes

@app.route('/')
def hello_world():
    return 'Hello,  eWorld!  '
# Route for entering the details of various screens one at a time

if __name__ == '__main__':
    app.run(host='localhost', port=8080,debug=True)
