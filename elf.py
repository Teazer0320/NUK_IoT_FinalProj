from flask import Flask, render_template

web = Flask(__name__)

@web.route("/")
def homepage():
	return render_template("Home.html")


if __name__ == "__main__":
	web.run(port=5050)
