import asyncio
import json
import sys
from datetime import datetime, timedelta
from undetected_playwright.async_api import async_playwright, Playwright


def validate_city_code(name):
    if not name or not isinstance(name, str):
        return False

    name = name.strip()

    for char in name:
        if not char.isalpha() and char != " " and char != "-":
            return False
    return True


def validate_date(date_str):
    try:
        flight_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.today().date()
        max_date = today + timedelta(days=90)
        return today <= flight_date <= max_date
    except ValueError:
        return False


def input_data():
    if len(sys.argv) > 1:
        from_city = sys.argv[1]
        to_city = sys.argv[2]
        date_str = sys.argv[3]
    else:
        from_city = input("Provide origin city (e.g. PAR, SFO, LAX)\n")
        to_city = input("Provide destination city (e.g. PAR, SFO, LAX)\n")
        date_str = input("Provide date, use this format YYYY-MM-DD\n")

    if not (validate_city_code(from_city) and validate_city_code(to_city)):
        print("Wrong city name")
        sys.exit(1)

    if not validate_date(date_str):
        print("Wrong date, use this format YYYY-MM-DD")
        sys.exit(1)

    return from_city, to_city, date_str


async def scrape_data(playwright: Playwright):
    city_from, city_to, date_str = input_data()

    args = ["--disable-blink-features=AutomationControlled"]

    browser = await playwright.chromium.launch(headless=False, slow_mo=50, args=args)
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 800},
    )
    page = await context.new_page()

    url = f"https://www.united.com/en/us/fsr/choose-flights?f={city_from}&t={city_to}&d={date_str}"

    await page.goto(url, timeout=100000)

    try:
        await page.wait_for_selector(
            ".app-components-Shopping-GridItem-styles__flightRow--QbVXL", timeout=50000
        )

        flights = await page.query_selector_all(
            ".app-components-Shopping-GridItem-styles__flightRow--QbVXL"
        )

        flights_result = []

        for flight in flights[:3]:
            departure_el = await flight.query_selector(
                "div.app-components-Shopping-FlightInfoBlock-styles__departTime--cDBWt span.app-components-Shopping-FlightInfoBlock-styles__time--CaNGp"
            )
            departure_val = (
                await departure_el.inner_text()
                if departure_el
                else "No departure time found"
            )

            arrival_el = await flight.query_selector(
                "div.app-components-Shopping-FlightInfoBlock-styles__arrivalTime--AXo5U span[class*='time--CaNGp']"
            )
            arrival_val = (
                await arrival_el.inner_text() if arrival_el else "No arrival time found"
            )

            duration_el = await flight.query_selector(
                "div.app-components-Shopping-FlightInfoBlock-styles__duration--P3ZXi span[aria-hidden='true']"
            )
            duration_val = (
                await duration_el.inner_text() if duration_el else "No duration found"
            )

            price_el = await flight.query_selector(
                "div[class*='btnPriceValue'] span span"
            )
            price_val = await price_el.inner_text() if price_el else "No price found"

            flights_result.append(
                {
                    "flight time": duration_val,
                    "flight cost": price_val,
                    "flight departure time": departure_val,
                    "flight arrival time": arrival_val,
                }
            )

            print(
                f"Flight {city_from} - {city_to}: {departure_val} - {arrival_val}, duration: {duration_val}, price: {price_val}"
            )
        print(flights_result)

        with open("results.json", "a") as f:
            f.write(json.dumps(flights_result))

        return flights_result

    except Exception as e:
        print(f"Parsing finished with error: {e}")

    finally:
        await browser.close()


async def main():
    async with async_playwright() as playwright:
        await scrape_data(playwright)


if __name__ == "__main__":
    asyncio.run(main())
