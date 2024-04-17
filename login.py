import asyncio
from playwright.async_api import async_playwright, Playwright


async def login():
    async with async_playwright() as p:
        firefox = p.firefox
        browser = await firefox.launch(headless=False, args=["--kiosk"], timeout=0)

        # Saved cookies and local storage
        context = await browser.new_context(
            storage_state="playwright/canva_state.json",
            no_viewport=True,
        )
        page = await context.new_page()

        await page.goto("https://canva.com/", timeout=0)

        # Add any additional navigation or actions here
        input1 = input(str("Press Enter to continue if logged in ..."))
        storage = await page.context.storage_state(
            path="playwright/canva_state.json"
        )
        # Close the browser
        await browser.close()


if __name__ == "__main__":
    asyncio.run(login())
