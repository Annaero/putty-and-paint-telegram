import asyncio
from http.client import HTTPException
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from telegram import Bot

ROOT_URL = os.environ.get("PUTTY_AND_PAINT")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
KV_REST_API_TOKEN = os.environ.get("KV_REST_API_TOKEN")
KV_REST_API_URL = os.environ.get("KV_REST_API_URL")

PROJECTS_URL = urljoin(ROOT_URL, os.environ.get("PROJECTS_URL"))


async def send_photo(photo: str, msg: str):
    await Bot(BOT_TOKEN).send_photo(chat_id=CHAT_ID, photo=photo, caption=msg)


def increase_kv_id(new_id: int):
    update_url = urljoin(KV_REST_API_URL, f"set/max_proj_id/{new_id}")
    response = requests.get(
        url=update_url, headers={"Authorization": f"Bearer {KV_REST_API_TOKEN}"}
    )
    if response.status_code != 200:
        print("ERROR: can't update value in KV: {response}")


def get_kv_max_id():
    get_url = urljoin(KV_REST_API_URL, "get/max_proj_id")
    response = requests.get(
        url=get_url, headers={"Authorization": f"Bearer {KV_REST_API_TOKEN}"}
    )
    if response.status_code != 200:
        raise Exception(response.text)
    json = response.json()
    result = json["result"]
    print("INFO:", f"Read max_proj_id {result}")
    return int(result) if result else 0


class handler(BaseHTTPRequestHandler):
    def set_headers(self, code: int, message: str):
        self.send_response(code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(message.encode("utf-8"))
        return

    def do_GET(self):

        print(
            "INFO:", f"Requesting projects page {PROJECTS_URL}"
        )  # By some reason `logging` do not works correctly with Vercel
        try:
            response = requests.get(PROJECTS_URL)
        except HTTPException as e:
            print("ERROR:", f"Cont complete request {e}")
            self.set_headers(500, "Job is failed :(")
            return

        if response.status_code != 200:
            print("ERROR:", f"Got response: {response}")
            self.set_headers(500, "Job is failed :(")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        project_links = soup.find_all("a", class_="project-link")
        print("INFO:", f"Found total {len(project_links)} projects")

        try:
            max_processed_id = get_kv_max_id()
        except Exception as e:
            print("ERROR:", f"can't read value from KV: {e}")
            self.set_headers(500, "Job is failed :(")
            return

        new_max_project_id = 0
        for project_link in reversed(project_links):
            if "href" not in project_link.attrs:
                print("WARNING:", f"One of projects does not have href {project_link} ")
                continue
            else:
                href = project_link.attrs["href"]
                title = project_link.attrs["title"]
                caption = "\n".join([title, href])
                project_id = int(urlparse(href).path.split("/")[-1])

            try:
                image = project_link.find("img")
                image_path = image.attrs["src"]
            except Exception as e:
                print("WARNING:", f"Failed get image for {project_link} with error {e}")
                continue

            if project_id > max_processed_id:
                image_url = urljoin(ROOT_URL, image_path)
                print(
                    "INFO:",
                    f"Going to post image with image: {image_url} and caption: {caption}",
                )

                try:
                    asyncio.run(send_photo(image_url, caption))
                except Exception as e:
                    print("WARNING:", f"Failed to post in tg with error {e}")

                new_max_project_id = max(new_max_project_id, project_id)
                print(
                    "INFO:",
                    f"Going to update max_proj_id {max_processed_id}->{new_max_project_id}",
                )
                increase_kv_id(new_max_project_id)

        if not new_max_project_id:
            print(
                "INFO:",
                f"No new projects found",
            )

        self.set_headers(200, "Job is done!")
        print("INFO:", "Routine is done")

        return
