import os
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright
from datetime import datetime
import random
import time

# ===========================
# Random sleep for hourly randomness
# ===========================
# # Sleep 0–59 minutes at the start
# sleep_seconds = random.randint(0, 59 * 60)
# print(f"Sleeping {sleep_seconds // 60} minutes and {sleep_seconds % 60} seconds before checking...")
# time.sleep(sleep_seconds)

# ===========================
# Email setup
# ===========================
EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_TO = os.environ["EMAIL_TO"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
    print("Email sent successfully!")

# ===========================
# John Pennekamp availability check
# ===========================
ARRIVAL_DATE = "04/04/2026"
NIGHTS = "1"
URL = "https://www.floridastateparks.org/stay-night"
PARK_NAME = "John Pennekamp Coral Reef State Park"

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)
        page.wait_for_timeout(5000)  # let JS render

        # ===========================
        # Click "Book your overnight stay today!"
        # ===========================
        page.locator("text=Book Your Overnight Stay Today").click()
        page.wait_for_timeout(3000)

        # ===========================
        # Enter park name with autocomplete handling
        # ===========================
        input_locator = page.locator("#home-search-location-input")
        input_locator.wait_for(timeout=15000)

        # Type slowly so autocomplete triggers
        for char in PARK_NAME:
            input_locator.type(char, delay=100)
        
        # Wait for suggestion and click it
        suggestion_locator = page.locator(f"li:has-text('{PARK_NAME}')")
        suggestion_locator.wait_for(timeout=10000)
        suggestion_locator.click()
        page.wait_for_timeout(2000)

        # ===========================
        # Enter arrival date and nights
        # ===========================
        page.fill("#arrivaldate", ARRIVAL_DATE)
        page.fill("#nights", NIGHTS)

        # ===========================
        # Click Show Results
        # ===========================
        page.locator("text=Show Results").click()
        page.wait_for_timeout(5000)

        # ===========================
        # Get availability from aria-label
        # ===========================
        park_card = page.locator(f"a[aria-label*='{PARK_NAME}']")
        label = park_card.get_attribute("aria-label")
        import re
        match = re.search(r'(\d+)\s+sites', label)
        available_sites = int(match.group(1)) if match else 0

        # ===========================
        # Send email
        # ===========================
        if available_sites > 0:
            subject = f"🚨 John Pennekamp Available: {available_sites} sites!"
            body = f"✅ {available_sites} sites available at {PARK_NAME} for April 4-5, 2026.\nChecked at {datetime.now()}"
            send_email(subject, body)
        else:
            subject = f"{PARK_NAME} Update: 0 Sites"
            body = f"❌ No availability yet for April 4-5, 2026.\nChecked at {datetime.now()}"
            send_email(subject, body)

        browser.close()

except Exception as e:
    send_email(f"{PARK_NAME} Script Error", f"Something went wrong:\n{e}")
    raise
