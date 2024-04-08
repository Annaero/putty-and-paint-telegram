from http.server import BaseHTTPRequestHandler
import asyncio
from bs4 import BeautifulSoup
import requests
import os
from telegram import Bot
from urllib.parse import urljoin

ROOT_URL = os.environ["PUTTY_AND_PAINT"]
PROJECTS_URL = urljoin(ROOT_URL, os.environ["PROJECTS_URL"])
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
print(BOT_TOKEN)


async def send_photo(photo, msg):
    await Bot(BOT_TOKEN).send_photo(chat_id=CHAT_ID, photo=photo, caption=msg)


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
            else:
                href = project_link.attrs["href"]
                title = project_link.attrs["title"]
                caption = "\n".join([title, href])
            print(project_link.attrs["href"])
            try:
                image = project_link.find("img")
                image_path = image.attrs["src"]
            except Exception as e:
                print("WARNING:", f"Failed get image for {project_link} with error {e}")

        image_url = urljoin(ROOT_URL, image_path)
        asyncio.run(send_photo(image_url, caption))

        return
