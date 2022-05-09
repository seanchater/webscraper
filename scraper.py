from bs4 import BeautifulSoup as soup
import requests
from urllib.request import urlopen as url_req
import re

import sys

def scrape_github(search_term, num_pages = 1):
	'''Scrapes github for the repos from the given search term

	Parameters
	---------
	'''

	#build the query for the given search term
	query = "https://github.com/search?q=%s&type=Repositories&per_page=10&p="\
		% search_term.replace(' ', '+')
	url_dict = {"query":query, "pgnum": str(num_pages)}
	github_url = url_dict["query"] + url_dict["pgnum"]

	list_repos = []
	for i in range(1, num_pages+1):

		#########update page number of url#########
		url_dict["pgnum"] = str(i)
		github_url = url_dict["query"] + url_dict["pgnum"]
		print(github_url)

		webpage = None 
		try:
			webpage = url_req(github_url) #connct to website
		except:
			print("Error connecting to webpage")
			exit()

		html_soup = soup(webpage, 'html.parser') #parse the html from the page objet

		#get the list of containers of all repos
		all_repos = html_soup.find_all("li", class_="repo-list-item hx_hit-repo "+
		"d-flex flex-justify-start py-4 public source")

		'''for each repo in the list (some pages might not have 10
			repos -> check for this) get the info for that repo and return it as
			a list of items
		'''
		for repo in all_repos:
			list_repos.append(scrape_repo_info(repo))

	return list_repos

''' Gets all the info for a repo and returns it as a list
	in the correct format

	repo_container: a beautiful soup object containing the html for a single
	repo
	returns:
'''
def scrape_repo_info(repo_container):

	fields = {}

	#gets the tags that contain the name of each repo
	repo_name = repo_container.find('a', class_="v-align-middle")
	#used join to print out generator object
	fields["repo_name"] = ''.join(repo_name.stripped_strings)

	#get the container tags that contain the descriptions
	repo_descr = repo_container.find('p', class_="mb-1")
	''' this doesn't
	replace the <em> and </em> tags with a space, just removes them
	completely'''
	if repo_descr != None:
		fields["description"] = repo_descr.text.strip()
	else:
		fields["description"] = None

	#get all the tags of a repo
	tags = repo_container.find_all('a', class_="topic-tag")
	tags_list = []
	for tag in tags:
		tags_list.append(''.join(tag.stripped_strings))
	if len(tags_list) != 0:
		fields["tags"] = tags_list
	else:
		fields["tags"] = None 

	#get the stars of a repo
	stars = repo_container.find('a', class_="Link--muted")
	try:
		fields["num_stars"] = ''.join(stars.stripped_strings)
	except:
		fields["num_stars"] = None

	#gets the programming language
	lang = repo_container.find('span', itemprop="programmingLanguage")
	try:
		fields["language"] = ''.join(lang.stripped_strings)
	except:
		fields["language"] = None

	#gets license
	license = repo_container.find_all(string=re.compile("license"))
	try:
		fields["license"] = license[0].strip()
	except:
		fields["license"] = None

	#get last updated
	updated = repo_container.find("relative-time")
	fields["last_updated"] = updated["datetime"]

	#get issues
	issues = repo_container.find('a', class_="Link--muted f6")
	try:
		issues_num = re.findall('[0-9]+', ''.join(issues.stripped_strings))
		fields["num_issues"] = issues_num[0]
	except:
		fields["num_issues"] = 0

	return fields	

def github_api(search_term, num_pages=1):
	'''Searches for repositories with the given search term using the github
	REST api

	Returns
	------
	repo_info : list
	A list of dictionaries containing the necessary info from the repositories
	'''

	#build the query for the given search term
	github_url = "https://api.github.com/search/repositories?q=%s&p=%s&&per_page=10"\
					%(search_term.replace(' ', '+'), str(num_pages))
	headers = {"Accept":"application/vnd.github.v3+json"}
	
	'''
	connects to the github api site and if an error code is returned that is
	not ok prints out message and exits
	'''
	response = requests.get(github_url, headers=headers);
	if response.status_code != 200:
		print("Error in returned response with code:", response.status_code)
		exit()
	json = response.json()

	repo_list = []
	for repo in json["items"]:
		repo_list.append(get_api_info(repo))

	return repo_list

''' Takes in a json object of a single repo and adds only the fields that
	are needed.  Params: repo: json object of single repo

	Returns : dictionary of correct fields.
'''
def get_api_info(repo):
	fields = {}

	#get the repo full name
	fields["repo_name"] = repo["full_name"]

	#get description
	fields["description"] = repo["description"]

	#num stars
	fields["num_stars"] = repo["stargazers_count"]

	#language
	fields["language"] = repo["language"]

	#license
	license = repo["license"]
	if license != None:
		fields["license"] = license["name"]
	else:
		fields["license"] = None

	#last updated
	fields["last_updated"] = repo["updated_at"]

	#issues
	fields["has_issues"] = repo["has_issues"]

	return fields
