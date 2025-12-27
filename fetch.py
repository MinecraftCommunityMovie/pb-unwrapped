# Zero-Clause BSD
# =============
#
# Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE
# FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
# AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import requests
import json

# Base api url
API_URL = "https://youtrack.projectbeacon.world/api"
# Bearer token for authentication
API_KEY = open("youtrack-api-key", "r").readline().replace("\n", "")
# Standard headers used within the script
HEADERS = {"Authorization": "Bearer " + API_KEY,
           "Content-Type": "application/json"}


# Function to get all projects
def get_projects():
    r = requests.get(API_URL + "/admin/projects?fields=id,name,shortName",
                     headers=HEADERS)
    if r.status_code != 200:
        print("Failed to get projects")
        exit(1)
    return r.json()

# Function to get all issues globally or from a project
def get_issues(project=None):
    if project == None:
        r = requests.get(API_URL + "/issues?fields=id,commentsCount,resolved",
                         headers=HEADERS)
    else:
        r = requests.get(API_URL + "/admin/projects/"
                         + project
                         + "/issues?fields=id,commentsCount,resolved",
                         headers=HEADERS)
    if r.status_code != 200:
        print("Failed to get issues:")
        print("Status code: " + str(r.status_code))
        exit(1)
    return r.json()


# Data dictionary to be outputted, see comments below for each value
# total_projects - the total number of projects
# total_issues - the total number of issues across all projects
# total_open_issues - the total number of open issues
# total_resolved_issues - the total number of closed issues
# total_comments - the total number of comments
# project_issues - a dictionary containing:
# -> project_name - the name of the project
# -> project_total_issues - the total number of issues within the project
# -> project_total_comments - the total number of comments within project issues
# -> project_open_issues - the number of open issues within the project
# -> project_resolved_issues - the number of closed issues within the project
data = {}

# Fetch all projects
projects = get_projects()

# Add number of projects to the data output
data["total_projects"] = len(projects)

# Initialise a list of projects to store their data
project_data = []
for proj in projects:
    project = {}
    open_issues = 0  # Number of open issues within the project
    resolved_issues = 0  # number of closed issues within the project
    comments = 0  # Total number of comments within project issues
    proj_issues = get_issues(proj["id"])

    # Extract project issue data
    for issue in proj_issues:

        # Check whether the issue is open or closed and increment
        # the corresponding variable
        if issue["resolved"] is None:
            open_issues += 1
        else:
            resolved_issues += 1

        # Add the number of comments from the issue
        comments += issue["commentsCount"]

    # Create dictionary for the project
    project["project_name"] = proj["name"]
    project["project_total_issues"] = len(proj_issues)
    project["project_total_comments"] = comments
    project["project_open_issues"] = open_issues
    project["project_resolved_issues"] = resolved_issues

    # Add the dictionary to the list of projects
    project_data.append(project)

# Add project data to data dictionary
data["project_issues"] = project_data

# Get all issues
issues = get_issues()

# Add total number of issues to data output
data["total_issues"] = len(issues)

# Calculate the global number of open and closed issues

open_issues = 0  # Number of open issues
resolved_issues = 0  # Number of closed issues
comments = 0  # Number of comments

for issue in issues:
    if issue["resolved"] is None:
        open_issues += 1
    else:
        resolved_issues += 1

    comments += issue["commentsCount"]

data["total_open_issues"] = open_issues
data["total_resolved_issues"] = resolved_issues
data["total_comments"] = comments

# Output data to output.json
with open("output.json", "w") as f:
    f.write(json.dumps(data))

