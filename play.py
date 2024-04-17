import asyncio
import time
import json
import random
import zipfile
import os
import cv2

import numpy as np

from playwright.async_api import async_playwright
from rich.console import Console
from concurrent.futures import ThreadPoolExecutor

from utils.generating_utils import (
    isolate,
    clean_content,
)

from utils.canny_utils import svg_to_canny


class CanvaAutomation(object):
    """
    This class is used to automate the process of scraping links from Canva and downloading their SVG files.

    Methods:
        start: Starts the automation process
        scrape_links: Scrapes the links from the Canva page
        download_images: Downloads the SVG files from the Canva page
        click_on_button: Clicks on the button using the given xpath
        open_page: Opens the given URL in the browser
        _scroll: Scrolls the page by the given amount
        _init_browser: Initializes the browser instance
        _close_browser: Closes the browser instance

    init:
        url (str): The URL to start the automation process
    """
    
    def __init__(
        self,
        url: str,
    ) -> None:
        self.URL = url

    async def start(self):
        """
        Starts the automation process by initializing the browser, opening the page, and scraping the links.
        """
        await self._init_browser()
        await self.open_page(self.URL)
        await self.scrape_links()

    async def scrape_links(self):
        """
        Scrapes the logo template links from the Canva page and saves them in the links/starter_links.json file.
        """
        time.sleep(random.randint(2, 3))
        await self._scroll(delta_y=6175.0)

        iteration = 1
        logo = {"urls": [], "names": []}

        with console.status("\n[bold purple]Scraping Links...") as status:
            while True:
                console.log(f"[bold green]Iteration: [bold blue]{iteration}")
                for i in range(1, 6):
                    url = "https://canva.com" + (
                        await self.page.locator(
                            f"xpath=/html/body/div[2]/div/div/div/main/div/div/div/div[2]/div[6]/div/div/div[1]/div/section/div/div/div/div[1]/div[2]/div/div[2]/div[{i}]/div[2]/div/div[2]/div[2]/a[1]"
                        ).get_attribute("href")
                    )
                    name = (
                        await self.page.locator(
                            f"xpath=/html/body/div[2]/div/div/div/main/div/div/div/div[2]/div[6]/div/div/div[1]/div/section/div/div/div/div[1]/div[2]/div/div[2]/div[{i}]/div[2]/div/div[2]/div[2]/a[1]/p"
                        ).all_inner_texts()
                    )[0]

                    if (
                        "video" in name
                        or "Video" in name
                        or "animated" in name
                        or "Animated" in name
                        or "gif" in name
                        or "GIF" in name
                    ):
                        continue

                    logo["urls"].append(url)
                    logo["names"].append(name)

                await self._scroll(delta_y=400.8)
                iteration += 1

                if iteration % 10 == 0:
                    console.log(f"[bold purple]Saving Links...")
                    with open("links/starter_links.json", "r") as f:
                        data = json.load(f)
                        for i in range(0, len(logo["urls"])):
                            data["urls"].append(logo["urls"][i])
                            data["names"].append(logo["names"][i])

                    with open("links/starter_links.json", "w") as f:
                        json.dump(data, f)

                    logo = {"urls": [], "names": []}

    async def download_images(self):
        """
        Downloads the SVG files from the Canva page and saves them in the images directory.
        """

        await self._init_browser()
        await self.open_page(self.URL)

        # Go to the page
        async with self.context.expect_page() as new_page_info:
            await self.click_on_button(
                xpath="/html/body/div[2]/div/div/div/main/div/div/div/div/div[2]/div/div[2]/div/div[3]/div[1]"
            )

        new_page = await new_page_info.value
        await new_page.wait_for_load_state()
        self.page = new_page

        # Click on the share button:
        await self.click_on_button(
            xpath="/html/body/div[2]/div/div/div/div/div[4]/header/div/nav/div[3]/div[5]/div/div/div/div/div/div"
        )

        # Click on the download option:
        await self.click_on_button(
            xpath="/html/body/div[2]/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div[2]/div/div/div/div[4]/ul/li[1]"
        )

        # Click on the drop-down menu:
        time.sleep(0.4)
        await self.click_on_button(
            xpath="/html/body/div[2]/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div/form/div/div/div[2]/div[1]/div[2]/div/div/div[1]/label/div/div"
        )

        # Select the SVG option:
        await self.click_on_button(
            xpath="/html/body/div[2]/div[1]/div/div/div/div/div/div[2]/div/div/div/ul/li[5]/button"
        )

        # Start waiting for the download
        async with self.page.expect_download() as download_info:
            button = self.page.locator(
                "xpath=/html/body/div[2]/div/div/div/div/div/div[2]/div/div/div/div/div[2]/div/form/div/div/div[2]/div[2]/div/div/div/div/div/div/div/div/div/button"
            )
            await button.click()
        download = await download_info.value

        # Wait for the download process to complete and save the downloaded file somewhere
        await download.save_as("images/" + download.suggested_filename)

        await self._close_browser()

    async def click_on_button(self, xpath: str):
        """
        Clicks on the button using the given xpath

        Args:
            xpath (str): The xpath of the element to click
        """
        time.sleep(0.5)
        button = self.page.locator(f"xpath={xpath}")
        await button.click(timeout=0)

    async def open_page(self, url: str):
        """
        Opens the given URL in the browser

        Args:
            url (str): The URL to open in the browser
        """
        await self.page.goto(url=url)

    async def _scroll(self, delta_y: float = 0.0):
        """
        Scrolls the page by the given amount.

        Args:
            delta_y (float): The amount to scroll the page by
        """
        steps = int(delta_y // 200)
        for _ in range(0, steps):
            await self.page.mouse.wheel(
                delta_x=0, delta_y=200
            )  # Scroll down by 200 pixels
            time.sleep(np.random.random_sample())

        await self.page.mouse.wheel(delta_x=0, delta_y=delta_y - 200 * (delta_y // 200))

    async def _init_browser(self):
        """
        Initialises a browser instance using Playwright and opens a new page.
        """
        self.playwright = await async_playwright().start()
        firefox = self.playwright.firefox
        self.browser = await firefox.launch(headless=True, args=["--kiosk"])
        storage_state = "playwright_state/canva_state.json"

        self.context = await self.browser.new_context(
            storage_state=storage_state,
            no_viewport=True,
        )

        self.page = await self.context.new_page()

    async def _close_browser(self):
        """
        Closes the browser instance and stops Playwright.
        """
        await self.browser.close()
        await self.playwright.stop()


def download(url: str):
    """
    Downloads the SVG file from the given URL

    Args:
        url (str): The Canva URL to download the SVG from

    Returns: The URL
    """
    scraper = CanvaAutomation(url=url)
    try:
        asyncio.run(scraper.download_images())
    except Exception as e:
        print(f"Error: {e}")
    return url


def generate(input_dir, dataset_dir):
    """
    Generates the dataset from the input directory containing SVG files

    Args:
        input_dir (str): The input directory containing SVG files
        dataset_dir (str): The directory to save the generated dataset

    Returns: None
    """
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)

    console.log(f"[bold purple]Generating dataset from: [bold yellow]{input_dir}")

    for filename in os.listdir(input_dir):
        if filename.endswith(".svg"):
            input_path = os.path.join(input_dir, filename)
            file_name_without_extension = os.path.splitext(filename)[0]

            console.log(
                f"[bold green]Processing: [bold blue]{file_name_without_extension}"
            )

            output_dir = os.path.join(dataset_dir, file_name_without_extension)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            with open(input_path, "r") as input_file:
                svg_content = input_file.read()

            iteration = 1
            while True:
                start_index_clip_path = svg_content.find("<g clip-path")
                start_index_mask = svg_content.find("<g mask")

                # Select minimum of the two indices
                start_index = min(start_index_clip_path, start_index_mask)
                if start_index == -1:
                    start_index = max(start_index_clip_path, start_index_mask)
                if start_index == -1:
                    # No clip-path or mask found/left
                    break

                # Fetch the end index of the clip-path or mask and remove the content
                svg_content = isolate(svg_content, start_index + 1)

                # Save modified content to new file in respective directory
                output_path = os.path.join(
                    output_dir, f"{file_name_without_extension}_{iteration}.png"
                )

                # Convert the SVG content to Canny Edge Image
                canny = svg_to_canny(content=svg_content)

                # Save the Canny Edge Image
                cv2.imwrite(output_path, canny)
                iteration += 1

            # Finally, remove all possible rouge instances and convert the content to white text and black background
            cleaned_content = clean_content(svg_content)

            # Save modified content to new file in respective directory
            output_path = os.path.join(
                output_dir, f"{file_name_without_extension}_{iteration-1}.png"
            )

            # Convert the cleaned content to Canny Edge Image
            canny = svg_to_canny(content=cleaned_content)

            # Save the Canny Edge Image
            cv2.imwrite(output_path, canny)


if __name__ == "__main__":
    console = Console()
    loop = asyncio.get_event_loop()

    while True:
        stage = console.input(
            "[bold yellow] Select the Stage [bold blue]:\n[bold green]1. [bold blue]Scrape Links\n[bold green]2. [bold blue]Download Images\n[bold green]3. [bold blue]Create the dataset\n\n[bright_magenta]Choice: "
        )

        if stage == "1":
            scraper = CanvaAutomation(url="https://www.canva.com/logos/templates/")
            loop.run_until_complete(scraper.start())
            break

        elif stage == "2":
            with open("links/starter_links.json", "r") as f:
                links = json.load(f)
            p_flag = console.input(
                "[bold yellow] Do you want to download images in parallel? [bold blue] (y/n): "
            )

            if p_flag.lower() == "n":
                for i in range(0, len(links["urls"])):
                    url = download(url=links["urls"][i])
                    console.log(f"[bold green] Downloaded .svg from: [bold blue]{url}")
            else:
                workers = int(
                    console.input("[bold yellow] Enter the number of workers: ")
                )

                # Parallel downloading by making use of workers using ThreadPoolExecutor and mapping the download function to the list of links
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    executor.map(download, links["urls"])

            for file in os.listdir("images"):
                if file.endswith(".zip"):
                    with zipfile.ZipFile("images/" + file, "r") as zip_ref:
                        zf = zip_ref.namelist()[0]
                        with open(
                            "images/" + file.split(".")[0] + ".svg",
                            "w",
                        ) as f:
                            f.write(zip_ref.read(zf).decode("utf-8"))
                    os.remove("images/" + file)
            break

        elif stage == "3":
            input_dir = "images"
            output_dir = "dataset"
            generate(input_dir=input_dir, dataset_dir=output_dir)
            break
        else:
            console.print(
                "[bold bright_red] Invalid Stage Selection: Please Enter 1, 2, or 3!\nk0"
            )
