from flask import Flask, render_template, request, redirect, url_for
from app.agents.pr_review_agent import run_pr_review_agent
from app.agents.test_gen_agent import run_test_gen_agent
from app.agents.cicd_agent import run_cicd_agent
from app.agents.deployment_agent import run_deployment_agent
from app.agents.incident_agent import run_incident_agent

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/app")
def dashboard():
    agent = request.args.get("agent", "review")
    return render_template("index.html", active=agent)

@app.route("/review", methods=["POST"])
def review():
    repo = request.form["repo"]
    pr_number = int(request.form["pr_number"])
    result = run_pr_review_agent(repo, pr_number)
    return render_template("index.html", result=result, active="review")

@app.route("/testgen", methods=["POST"])
def testgen():
    repo = request.form["repo"]
    file_path = request.form["file_path"]
    branch = request.form.get("branch", "main")
    result = run_test_gen_agent(repo, file_path, branch)
    return render_template("index.html", result=result, active="testgen")

@app.route("/cicd", methods=["POST"])
def cicd():
    repo = request.form["repo"]
    result = run_cicd_agent(repo)
    return render_template("index.html", result=result, active="cicd")

@app.route("/deployment", methods=["POST"])
def deployment():
    repo = request.form["repo"]
    result = run_deployment_agent(repo)
    return render_template("index.html", result=result, active="deployment")

@app.route("/incident", methods=["POST"])
def incident():
    repo = request.form["repo"]
    description = request.form["description"]
    result = run_incident_agent(repo, description)
    return render_template("index.html", result=result, active="incident")

if __name__ == "__main__":
    app.run(debug=True)
