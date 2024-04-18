import asyncio
import time
import json
import random
import zipfile
import os
import cv2
import yaml

import numpy as np

from playwright.async_api import async_playwright
from rich.console import Console
import concurrent.futures
from pathlib import Path

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
        scroll: Scrolls the page by the given amount
        init_browser: Initializes the browser instance
        close_browser: Closes the browser instance

    init:
        url (str): The URL to start the automation process
        count (int): The number of links to scrape
    """

    def __init__(
        self,
        url: str,
        count: int = 1,
    ) -> None:
        self.URL = url
        self.count = count
        self.count = count
        self.pid = os.getpid()

        try:
            self.filter = self.URL.split("&fTheme=THEME_")[1].split(",")[0].strip()
        except:
            self.filter = "NA"

    async def start(self):
        """
        Starts the automation process by initializing the browser, opening the page, and scraping the links.
        """
        await self.init_browser()
        await self.open_page(self.URL)
        await self.scrape_links()

    async def scrape_links(self):
        """
        Scrapes the logo template links from the Canva page and saves them in the links/starter_links.json file.
        """
        time.sleep(random.randint(2, 3))
        await self.scroll(delta_y=6175.0)

        iteration = 1
        logo = {}

        console.log("\n[bold purple]Scraping Links...")
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

                logo[url] = name

            await self.scroll(delta_y=400.8)

            if iteration % 10 == 0:
                console.log(f"[bold purple]Saving Links...")
                data = {}
                try:
                    with open(f"links/links_{self.pid}_{self.filter}.json", "r") as f:
                        data = json.load(f)
                except Exception as e:
                    print("Error: ", e)

                for i in logo.items():
                    data[i[0]] = i[1]

                with open(f"links/links_{self.pid}_{self.filter}.json", "w") as f:
                    json.dump(data, f)

                logo = {}

                if iteration * 5 >= self.count:
                    break

            iteration += 1


    async def download_images(self):
        """
        Downloads the SVG files from the Canva page and saves them in the images directory.
        """
        await self.init_browser()
        await self.open_page(self.URL)

        # Go to the page
        try:
            async with self.context.expect_page() as new_page_info:
                await self.page.get_by_text(
                    "Customise this template", exact=True
                ).click()
        except Exception as e:
            print(f"Error: {e}")
            await self.close_browser()
            return

        new_page = await new_page_info.value
        await new_page.wait_for_load_state()
        self.page = new_page

        # Click on the share button:
        await self.page.get_by_text("Share", exact=True).click()

        # Click on the download option:
        time.sleep(0.1)
        await self.page.get_by_text("Download", exact=True).click()

        # Click on the drop-down menu:
        time.sleep(0.4)
        await self.page.get_by_text("Suggested", exact=True).click()

        # Select the SVG option:
        await self.page.get_by_text("SVG", exact=True).click()

        # Start waiting for the download
        async with self.page.expect_download() as download_info:
            await self.page.get_by_text("Download", exact=True).nth(1).click()
        download = await download_info.value

        # Wait for the download process to complete and save the downloaded file somewhere
        await download.save_as("images/" + download.suggested_filename)

        await self.close_browser()

    async def click_on_button(self, xpath: str):
        """
        Clicks on the button using the given xpath

        Args:
            xpath (str): The xpath of the element to click
        """
        time.sleep(0.5)
        button = self.page.locator(f"xpath={xpath}")
        await button.click()

    async def open_page(self, url: str):
        """
        Opens the given URL in the browser

        Args:
            url (str): The URL to open in the browser
        """
        await self.page.goto(url=url)

    async def scroll(self, delta_y: float = 0.0):
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
            time.sleep(np.random.random_sample() * 1.5)

        await self.page.mouse.wheel(delta_x=0, delta_y=delta_y - 200 * (delta_y // 200))

    async def init_browser(self):
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

    async def close_browser(self):
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
    try:
        scraper = CanvaAutomation(url=url)
        asyncio.run(scraper.download_images())
    except Exception as e:
        print(f"Error: {e}")
    return url


def generate(input_dir, dataset_dir, index: int = 0):
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

    paths = sorted(Path(input_dir).iterdir(), key=os.path.getmtime)

    for i, filename in enumerate(paths):
        if index > 0 and i < index:
            continue

        input_path = os.path.join(input_dir, filename.stem + ".svg")
        file_name_without_extension = filename.stem

        console.log(f"[bold green]Processing: [bold blue]{file_name_without_extension}")

        output_dir = os.path.join(dataset_dir, file_name_without_extension)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(input_path, "r") as input_file:
            svg_content = input_file.read()

        # Save this as png in ground truth directory
        gt = svg_to_canny(content=svg_content, save_only=True)
        cv2.imwrite(os.path.join(output_dir, "gt.png"), gt)

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


def scrape(url: str, count: int):
    """
    Scrapes the links from the given URL

    Args:
        url (str): The URL to scrape the links from

    Returns: None
    """
    scraper = CanvaAutomation(url=url, count=count)
    asyncio.run(scraper.start())


if __name__ == "__main__":
    console = Console()

    # Open config.yaml file and read the configuration
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    STAGE = config["STAGE"]
    PARALLEL = config["PARALLEL"]
    WORKERS = config["WORKERS"]
    INPUT_DIR = config["INPUT_DIR"]
    OUTPUT_DIR = config["OUTPUT_DIR"]

    console.log(
        f"[bold yellow]Stages [bold blue]:\n[bold green]1. [bold blue]Scrape Links\n[bold green]2. [bold blue]Download Images\n[bold green]3. [bold blue]Create the dataset\n\n[bright_magenta]Choice: {STAGE}"
    )

    if STAGE == "1":
        urls = []
        with open("links/targets.txt", "r") as f:
            targets = f.readlines()

        for target in targets:
            urls.append(target.strip().split(","))
        
        if PARALLEL == "n":
            for url in urls:
                scrape(url[0], int(url[1]))
        else:
            with concurrent.futures.ProcessPoolExecutor(max_workers=WORKERS) as executor:
                futures = [
                    executor.submit(scrape, url[0], int(url[1]))
                    for url in urls
                ]
                concurrent.futures.wait(futures)
        
        lists = {}
        for file in os.listdir("links"):
            if file.endswith("json") and file.startswith("links_"):
                with open("links/" + file, "r") as f:
                    data = json.load(f)
                    for i in data.items():
                        lists[i[0]] = i[1]
                os.remove("links/" + file)
        
        with open("links/links.json", "w") as f:
            json.dump(lists, f)

    elif STAGE == "2":
        with open("links/links.json", "r") as f:
            links = json.load(f)

        console.log(
            f"[bold green] You have opted for [bold blue]'{PARALLEL}' [bold green] for parallelisation."
        )

        if PARALLEL == "n":
            for i in links.items():
                url = download(url=i[0])
                console.log(f"[bold green] Downloaded .svg from: [bold blue]{url}")
            pass
        else:
            console.log(
                f"[bold yellow]You have opted for [bold blue]Parallel Downloading [bold yellow]with [bold blue]{WORKERS} [bold yellow]workers."
            )

            # Parallel downloading by making use of workers using ProcessPoolExecutor and mapping the download function to the list of links
            with concurrent.futures.ProcessPoolExecutor(
                max_workers=WORKERS
            ) as executor:
                futures = [executor.submit(download, url) for url in links.keys()]

                concurrent.futures.wait(futures)

        # Clean up the downloaded zip files, choose only the first of the images stored in it
        for file in os.listdir(INPUT_DIR):
            if file.endswith(".zip"):
                with zipfile.ZipFile(INPUT_DIR + "/" + file, "r") as zip_ref:
                    zf = zip_ref.namelist()[0]
                    with open(
                        INPUT_DIR + "/" + file.split(".")[0] + ".svg",
                        "w",
                    ) as f:
                        f.write(zip_ref.read(zf).decode("utf-8"))
                os.remove(INPUT_DIR + "/" + file)

    elif STAGE == "3":
        input_dir = INPUT_DIR
        output_dir = OUTPUT_DIR
        generate(input_dir=input_dir, dataset_dir=output_dir)

    else:
        console.log(
            "[bold bright_red] Invalid Stage Selection: Please Select 1, 2, or 3!\n"
        )
