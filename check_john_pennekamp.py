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

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)
        page.wait_for_timeout(5000)  # let JS render

        # Click "Book Your Overnight Stay Today"
        page.locator("text=Book Your Overnight Stay Today").click()
        page.wait_for_timeout(3000)

        # Enter park name
        input_selector = "#home-search-location-input"
        page.fill(input_selector, "John Pennekamp Coral Reef State Park")
        page.keyboard.press("Enter")
        page.wait_for_timeout(2000)

        # Enter arrival date and nights
        page.fill("#arrivaldate", ARRIVAL_DATE)
        page.fill("#nights", NIGHTS)

        # Click Show Results
        page.locator("text=Show Results").click()
        page.wait_for_timeout(5000)

        # Get availability from aria-label
        park_card = page.locator("a[aria-label*='John Pennekamp Coral Reef State Park']")
        label = park_card.get_attribute("aria-label")
        import re
        match = re.search(r'(\d+)\s+sites', label)
        available_sites = int(match.group(1)) if match else 0

        # Send email
        if available_sites > 0:
            subject = f"🚨 John Pennekamp Available: {available_sites} sites!"
            body = f"✅ {available_sites} sites available at John Pennekamp Coral Reef State Park for April 4-5, 2026.\nChecked at {datetime.now()}"
            send_email(subject, body)
        else:
            subject = f"John Pennekamp Update: 0 Sites"
            body = f"❌ No availability yet for April 4-5, 2026.\nChecked at {datetime.now()}"
            send_email(subject, body)

        browser.close()

except Exception as e:
    send_email("John Pennekamp Script Error", f"Something went wrong:\n{e}")
    raise
