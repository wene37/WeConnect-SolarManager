import os
from flask import Flask, render_template

templateDir = os.path.join(os.path.dirname(__file__), "templates")
staticDir = os.path.join(os.path.dirname(__file__), "static")
app = Flask("WeConnect-SolarManager", template_folder=templateDir, static_folder=staticDir)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')