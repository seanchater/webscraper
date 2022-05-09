from flask import Flask, redirect, render_template, url_for, request
from scraper import scrape_github, github_api

app = Flask(__name__)

@app.route('/scraper', methods=["POST", "GET"])
def scraper_results():
	if request.method == "POST":
		#get the search query from user input text box
		form_response = request.form["search_term"]
		results = scrape_github(form_response, 1)
		return render_template("results.html", search_term=form_response,\
			method="scraping", items_list=results)
	else:
		return "error in scraper results"

@app.route('/api', methods=["POST", "GET"])
def api_results():
	if request.method == "POST":
		form_response = request.form["search_term"]
		results = github_api(form_response, 1)
		return render_template("results.html", search_term=form_response,\
		method="API search", items_list=results)
	else:
		return "error in api results"

@app.route('/')
def startup():
	return render_template("startup.html")

if __name__ == "__main__":
	app.run(debug=True)
