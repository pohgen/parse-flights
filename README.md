# Code Documentation United Airlines Flight Scraper

This script uses `undetected_playwright` to automate a Chromium browser, search for flights on [united.com](https://united.com), and extract key flight information.

---

## 1. `validate_city_code(name)`

**Purpose**: Ensures the provided city string is valid.

**Logic**:
- Checks the input is a string and not empty.
- Allows only letters, spaces, and dashes (`-`).
- Returns `True` if valid, otherwise `False`.

---

## 2. `validate_date(date_str)`

**Purpose**: Validates that the input date is:
- In the correct format: `YYYY-MM-DD`
- Between today and 90 days from today (inclusive)

**Logic**:
- Parses the string to a `datetime.date`.
- Compares it to today's date and the 90-day limit.
- Returns `True` if valid, `False` if out of range or invalid format.

---

## 3. `input_data()`

**Purpose**: Gets and validates user input.

**How it works**:
- If command-line arguments (`sys.argv`) are provided, it reads:
  - `sys.argv[1]` = origin city code (e.g., `"LAX"`)
  - `sys.argv[2]` = destination city code (e.g., `"PAR"`)
  - `sys.argv[3]` = flight date (e.g., `"2025-06-20"`)
- Otherwise, it prompts the user interactively.

**Validations performed**:
- Both cities are passed through `validate_city_code()`
- The date is checked with `validate_date()`
- If any check fails, prints an error and exits with `sys.exit(1)`

**Returns**:
- Tuple: `(from_city, to_city, date_str)`

---

## 4. `scrape_data(playwright: Playwright)`

**Purpose**: The main scraping function.

### Step-by-step:

1. **Reads validated input**:
   - Calls `input_data()` to get city codes and date.

2. **Launches Chromium browser**:
   - `headless=False` to avoid bot detection.
   - Uses argument: `--disable-blink-features=AutomationControlled`.

3. **Creates browser context and page**:
   - Sets a real User-Agent and viewport.
   - Opens a new page to browse the website.

4. **Builds the target URL**:
   - Example:
     ```
     https://www.united.com/en/us/fsr/choose-flights?f=LAX&t=PAR&d=2025-06-20
     ```

5. **Navigates to the page**:
   - Waits for full load using `wait_until="networkidle"`.

6. **Waits for flight search results**:
   - Specifically waits for the selector:
     `.app-components-Shopping-GridItem-styles__flightRow--QbVXL`

7. **Parses the first 3 flight results**:
   For each result:
   - **Departure time**: using `departTime--cDBWt`
   - **Arrival time**: using `arrivalTime--AXo5U`
   - **Duration**: using `duration--P3ZXi`
   - **Price**: using `btnPriceValue`
   - Values are extracted with `.inner_text()`.

8. **Builds and appends flight data**:
   - Appends a dictionary like:
     ```python
     {
       "flight time": "10H, 30M",
       "flight cost": "$2800",
       "flight departure time": "10:45 AM",
       "flight arrival time": "3:15 PM"
     }
     ```

9. **Prints human-readable and structured result**

10. **Handles exceptions gracefully**
    - If a timeout or selector error occurs, prints an error message.

11. **Closes the browser** in a `finally` block

---

## 5. `main()`

**Purpose**: Entry point of the program.

**Logic**:
- Starts an `async_playwright()` session
- Passes the `playwright` object to `scrape_data()`

---


## Future Improvements

The current version of the script is ready to use but can be improved in the following ways:

- Browser page loading performance
- Support full city names (e.g. `"London"`) and auto-convert
- Accept multiple date formats (e.g. `DD-MM-YYYY`, `MM/DD/YYYY`, `YYYY.MM.DD`) and auto-normalize
- Data export in multiple formats
- Save results in structured formats (CSV, XLSX)
- Support for storing data in databases (SQL)

