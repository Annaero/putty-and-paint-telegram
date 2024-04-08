from http.server import BaseHTTPRequestHandler
from bs4 import BeautifulSoup
import requests
import os

ROOT_URL = os.environ["PUTTY_AND_PAINT"]
PROJECTS_URL = ROOT_URL + os.environ["PROJECTS_URL"]


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("Hello, world!".encode("utf-8"))

        print(
            "INFO:", f"Requesting projects page {PROJECTS_URL}"
        )  # By some reason `logging` do not works correctly with Vercel
        response = requests.get(PROJECTS_URL)

        if response.status_code != 200:
            print("ERROR:", f"Got response: {response}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        project_links = soup.find_all("a", class_="project-link")
        for project_link in project_links:
            if "href" not in project_link.attrs:
                print("WARNING:", f"One of project does not have href {project_link} ")
            print(project_link.attrs["href"])
            try:
                image = project_link.find("img")
                print(image.attrs["src"])
            except Exception as e:
                print("WARNING:", f"Failed get image for {project_link} with error {e}")

        return
