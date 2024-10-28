from flask import Flask, render_template

app = Flask(__name__)

# Home page with 3 red buttons
@app.route('/')
def menu():
    return render_template('modern_homepage.html')

# Page with 4 green stars
# @app.route('/emotion-influence')
# def emotion_influence():
#     return render_template('emotion_influence.html')

if __name__ == '__main__':
    app.run(debug=True)
