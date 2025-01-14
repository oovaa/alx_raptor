import json
import os
import requests
import re
import sys
from getpass import getpass
from bs4 import BeautifulSoup
import time

session = requests.Session()
user_db = ".data.sec"
json_db = "alx.json"
intranet = "https://intranet.alxswe.com"


def check_or_create_user_data(user_db):
    # Check if file exists
    if not os.path.exists(user_db) or os.path.getsize(user_db) == 0:
        # If not, prompt the user to enter their email and password
        email = input("Please enter your email: ")
        password = getpass(prompt="Please enter your password: ")

        # Store the email and password in the file
        with open(user_db, "w") as file:
            file.write(email + "\n")
            file.write(password + "\n")

        print(
            "\033[91m"
            + "user_data stored in data.sec. Do not share this file."
            + "\033[0m"
        )

    # If file exists, read the user_data
    with open(user_db, "r") as file:
        email = file.readline().strip()
        password = file.readline().strip()

    return email, password


def log_into_alx(email, password, session):
    # URL for login
    login_url = "https://intranet.alxswe.com/auth/sign_in"

    # Perform login
    login_data = {"user[email]": email, "user[password]": password}
    # Get the login page
    login_page_response = session.get(login_url)

    # Parse the HTML content
    soup = BeautifulSoup(login_page_response.content, "html.parser")

    # Get the CSRF token
    csrf_token = soup.find("meta", {"name": "csrf-token"})["content"]

    # Include the CSRF token in the login datao
    login_data["authenticity_token"] = csrf_token

    # Now you can send the POST request with the login data
    login_response = session.post(
        login_url,
        data=login_data,
        allow_redirects=True,
        headers={"Referer": "https://intranet.alxswe.com/"},
    )
    return login_response
    # Check if login was successful (you may need to customize this
    # based on the website's response)


# fix projects names and remove and wanted characters
def sanitize_project_name(project_name):
    # Remove characters not allowed in folder names
    sanitized_name = re.sub(r"[^\w\s.-]", "", project_name)
    return sanitized_name.strip()


def get_project_ids_to_alx_json(session, json_flag):
    # Scrap the project infos
    response = session.get("https://intranet.alxswe.com/projects/current")
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all anchor tags with hrefs that start with "/projects/"
    project_tags = soup.select('a[href^="/projects/"]')

    # Extract the project IDs and names
    project_info = {
        (tag["href"].split("/")[-1], sanitize_project_name(tag.text))
        for tag in project_tags
    }

    project_dict = {project[0]: {"name": project[1]} for project in project_info}
    # Write to JSON file only if flag is provided or file does not exist
    if json_flag or not os.path.exists(json_db):
        create_json_file(project_dict)

    # Create dictionary from project_info
    return project_dict


def get_qa_reviews(soup):
    # Find all QA review buttons
    qa_review_buttons = soup.find_all(
        "button", class_="btn btn-default btn-sm", attrs={"data-target": True}
    )

    qa_reviews_html = ""

    for button in qa_review_buttons:
        # Check if the button is for a QA review
        data_target = button["data-target"]
        if data_target.startswith("#task-qa-review-"):
            # Find the corresponding modal
            # Remove the '#' from the start of the ID
            qa_review_modal = soup.find(id=data_target[1:])

            # Add the HTML of the modal to the QA reviews HTML
            qa_reviews_html += str(qa_review_modal)

    # Return the HTML of the QA reviews
    return qa_reviews_html


def enter_projects(project_details):
    # Create directory if it doesn't exist
    if not os.path.exists("./projects_html"):
        os.makedirs("./projects_html")

    for id, info in project_details.items():
        visit_prj = intranet + "/projects/" + id
        response = session.get(visit_prj)
        # Save file in projects_html directory
        htmlname = os.path.join("projects_html", info["name"] + ".html")
        soup = BeautifulSoup(response.content, "html.parser")

        with open(htmlname, "w") as htmlcontent:
            htmlcontent.write(response.text)
        # Parse and update concepts, resources, and extra resources
        concepts, resources, extra_res = parse_project_details(soup)

        # Get QA reviews
        qa_reviews_html = get_qa_reviews(soup)
        if qa_reviews_html:
            # Save QA reviews in a separate HTML file
            qa_htmlname = os.path.join("projects_html", info["name"] + "QA.html")
            with open(qa_htmlname, "w") as qa_htmlcontent:
                qa_htmlcontent.write(qa_reviews_html)

        if concepts:
            project_details[id]["concepts"] = concepts
        if resources:
            project_details[id]["resources"] = resources
        if extra_res:
            project_details[id]["extra_res"] = extra_res

    # Dump the updated project_details into json_db file
    create_json_file(project_details)


def parse_project_details(soup):
    concepts_section = soup.find("h3", class_="panel-title", string="Concepts")
    resources_section = soup.find("h2", string="Resources")
    extra_res_section = soup.find("h2", string="Additional Resources")

    concepts = parse_section(concepts_section)
    resources = parse_section(resources_section)
    extra_res = parse_section(extra_res_section)

    return concepts, resources, extra_res


def parse_section(section):
    items = {}
    if section:
        section_list = section.find_next("ul")
        if section_list:
            item_tags = section_list.find_all("li")
            for item in item_tags:
                a_tag = item.find("a")
                if a_tag:
                    item_name = a_tag.text.strip()
                    item_link = intranet + a_tag["href"]
                    items[item_name] = item_link
    return items


def create_json_file(dict):
    with open(json_db, "w") as file:
        json.dump(dict, file, indent=3)


# def parse_cons(soup):
#     concepts_section = soup.find('h3', class_='panel-title',
#       string='Concepts')
#     concepts = {}
#     if concepts_section:
#         concepts_list = concepts_section.find_next('ul')
#         if concepts_list:
#             concept_items = concepts_list.find_all('li')
#             for item in concept_items:
#                 a_tag = item.find('a')
#                 if a_tag:
#                     cons_name = a_tag.text.strip()
#                     cons_link = intranet + a_tag['href']
#                     concepts[cons_name] = cons_link
#     return concepts

# def parse_res(soup):
#     resources_section = soup.find('h2', string='Resources')
#     resources = {}
#     if resources_section:
#         resources_list = resources_section.find_next('ul')
#         if resources_list:
#             resource_items = resources_list.find_all('li')
#             resources = {}
#             for item in resource_items:
#                 a_tag = item.find('a')
#                 if a_tag:
#                     res_name = a_tag.text.strip()
#                     res_link = intranet + a_tag['href']
#                     resources[res_name] = res_link
#     return resources

# def parse_extra_res(soup):
#     resources_section = soup.find('h2', string='Additional Resources')
#     add_res = {}
#     if resources_section:
#         resources_list = resources_section.find_next('ul')
#         if resources_list:
#             resource_items = resources_list.find_all('li')
#             for item in resource_items:
#                 a_tag = item.find('a')
#                 if a_tag:
#                     res_name = a_tag.text.strip()
#                     res_link = intranet + a_tag['href']
#                     add_res[res_name] = res_link
#     return add_res


# TODO:
# def scrap_projects(login_response):
#     if not login_response.ok:
#       pass


def main():
    start_time = time.time()
    email, password = check_or_create_user_data(user_db)
    login_response = log_into_alx(email, password, session)

    if login_response.ok:
        print("Login successful")
        # Check if '-j' flag is present in command line arguments
        json_flag = "-j" in sys.argv
        print("Getting project details...")
        project_details = get_project_ids_to_alx_json(session, json_flag)
        print("Entering projects...")
        enter_projects(project_details)
    execution_time = time.time() - start_time
    print(f"Execution time: {execution_time:.2f} seconds")


if __name__ == "__main__":
    main()

    # print("Login successful")

    # response = session.get('https://intranet.alxswe.com')
    # print(response)

    # project_page = session.get('https://intranet.alxswe.com/projects/299')

    # print(project_page.content.decode("UTF-8"))

    # with open('alx.json', 'r') as alxjs:
    #     ids_from_js = json.load(alxjs)
    #     pure_projects_ids = list(ids_from_js.keys())

    # Remove 'current' from the list
    # if 'current' in pure_projects_ids:
    #     pure_projects_ids.remove('current')

    # print(pure_projects_ids)

    # i could access every project site
    # for projict_id in pure_projects_ids:
    #     respond = requests.get(
    #         f'https://intranet.alxswe.com/projects/{projict_id}')

    #     print(respond)
