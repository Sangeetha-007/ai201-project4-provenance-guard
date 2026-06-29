from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Provenance Guard is running."

@app.route("/log", methods=["GET"])
def get_log():
    ...

@app.route("/submit", methods=["POST"])
def submit():
    ...

if __name__ == "__main__":
    app.run(port=5000, debug=True)

