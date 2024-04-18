import time
import json
import os
import zipfile
import sys

from concurrent.futures import ThreadPoolExecutor
from rich import console

from play import download, generate

def monitor(workers:int=4):
    index = 0
    while True:
        time.sleep(30)
        with open("links/starter_links.json", "r") as f:
            data = json.load(f)
        
        links = data["urls"]
        if len(links) - index == 0:
            print("No more links to download")
            break
        else:
            links = links[index:]

            # Parallel downloading by making use of workers using ThreadPoolExecutor and mapping the download function to the list of links
            with ThreadPoolExecutor(max_workers=workers) as executor:
                executor.map(download, links)

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
        
        generate("images", "dataset", index=index)
        
        index = len(links)

if __name__ == "__main__":
    # Take sys args for number of workers
    workers = 4
    if len(sys.argv) > 1:
        workers = int(sys.argv[1])

    monitor(workers=workers)
