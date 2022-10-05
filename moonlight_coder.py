from cgitb import html
from flask import Flask, render_template

app = Flask(__name__)

class MoonLightCoder:

    def __init__(self):
        pass

@app.route('/')
def learn_python(name=None):
    return render_template('main.html', name=name, file='home.html')



if __name__ == 'main':
    moonLightCoder = MoonLightCoder()
    moonLightCoder.learn_python()
