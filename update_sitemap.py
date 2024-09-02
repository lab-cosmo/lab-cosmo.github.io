"""
Generates a sitemap.xml containing links to all repositories that publish 
something on github pages.
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


org_name = "lab-cosmo"

def get_last_commit_date(repo_name):
    commits_url = f"https://api.github.com/repos/{org_name}/{repo_name}/commits"
    response = requests.get(commits_url)
    
    if response.status_code == 200:
        commits = response.json()
        if commits:
            # Get the date of the latest commit
            last_commit_date = commits[0]['commit']['committer']['date']
            return last_commit_date.split('T')[0]  # Return just the date part
    return None

def determine_changefreq(last_commit_date):
    if last_commit_date:
        date = datetime.strptime(last_commit_date, "%Y-%m-%d")
        now = datetime.utcnow()
        if date < now - timedelta(days=365):
            return "yearly"
        elif date < now - timedelta(days=30):
            return "monthly"
        else:
            return "weekly"
    return "monthly"  # Default to monthly if no commit date is available    

# GitHub API URL to list public repositories in the organization
api_url = f"https://api.github.com/orgs/lab-cosmo/repos?per_page=100&type=public"

# Request to fetch the list of repositories
response = requests.get(api_url)

# Check if the request was successful
if response.status_code == 200:
    repos = response.json()
    
    # Base URL for your organization's GitHub Pages
    base_url = f"https://{org_name}.github.io/"
    
    # List to hold URLs
    urls = []
    
    for repo in repos:
        # Construct the GitHub Pages URL for each repository
        repo_name = repo['name']
        url = f"{base_url}{repo_name}/"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
           last_commit = get_last_commit_date(repo_name)
           freq = determine_changefreq(last_commit)
           print(f"URL OK: {url}; Last commit {last_commit}; Update {freq}")
           
           urls.append({"url": url, "date": last_commit,
                        "freq": freq})
        elif response.status_code == 404:
           print(f"URL Not Found (404): {url}")

    # Create XML sitemap
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    
    for url_info in urls:
        url, date, freq = url_info["url"], url_info["date"], url_info["freq"]
        url_element = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url_element, "loc")
        loc.text = url
        
        lastmod = ET.SubElement(url_element, "lastmod")
        lastmod.text = date
                
        changefreq = ET.SubElement(url_element, "changefreq")
        changefreq.text = freq

    
    # Save the XML sitemap to a file
    tree = ET.ElementTree(urlset)
    tree.write("sitemap.xml", encoding="utf-8", xml_declaration=True)
    
    print("XML Sitemap generated successfully!")
else:
    print(f"Failed to retrieve repositories: {response.status_code}")

