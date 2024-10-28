from flask import Flask, render_template, redirect, url_for,request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/kpi')
def kpi():
    chosen_option = request.args.get('option', 'No option selected')  # Default if no option is passed
    return render_template('kpi.html', chosen_option=chosen_option)



@app.route('/location')
def location():
    return render_template('location.html')

@app.route('/emotion_influence')
def emotion_influence():
    return render_template('emotion_influence.html')

@app.route('/impact')
def impact():
    return render_template('impact.html')

if __name__ == '__main__':
    app.run(debug=True)
