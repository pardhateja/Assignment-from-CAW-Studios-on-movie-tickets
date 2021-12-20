from flask import Flask
app = Flask(__name__)

#The main class which needs to be runned at the beginning
from api import routes

@app.route('/')
def hello_world():
    return 'Hello,  eWorld!'

if __name__ == '__main__':
    app.run(host='localhost', port=8080,debug=True)
