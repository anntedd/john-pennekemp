import os
import smtplib
import time
import random
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import re

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
    print(f"Email sent: {subject}")

# ===========================
# John Pennekamp availability check
# ===========================
ARRIVAL_DATE = "04/04/2026"
NIGHTS = "1"
URL = "https://www.floridastateparks.org/stay-night"

def check_availability():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S CST")
    print(f"Checking John Pennekamp availability at {now_str}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Open main page
            page.goto(URL)
            page.wait_for_timeout(3000)

            # Click "Book Your Overnight Stay Today" and handle popup
            with page.expect_popup() as popup_info:
                page.locator("img[alt='Book Your Overnight Stay Today']").click()
            new_page = popup_info.value
            new_page.wait_for_load_state("networkidle")

            # Fill park search input (autofill)
            input_selector = "#home-search-location-input"
            new_page.wait_for_selector(input_selector, timeout=60000)
            new_page.fill(input_selector, "John Pennekamp Coral Reef State Park")
            time.sleep(1)  # give autofill time
            new_page.keyboard.press("Enter")
            time.sleep(2)

            # Fill arrival date and nights
            new_page.fill("#arrivaldate", ARRIVAL_DATE)
            new_page.fill("#nights", NIGHTS)

            # Click Show Results
            new_page.locator("text=Show Results").click()
            new_page.wait_for_timeout(5000)

            # Extract availability from aria-label
            park_card = new_page.locator("a[aria-label*='John Pennekamp Coral Reef State Park']")
            label = park_card.get_attribute("aria-label")
            match = re.search(r'(\d+)\s+sites', label)
            available_sites = int(match.group(1)) if match else 0

            # Send email
            if available_sites > 0:
                send_email(
                    f"🚨 John Pennekamp Available: {available_sites} sites! ({now_str})",
                    f"✅ {available_sites} sites available at John Pennekamp for April 4-5, 2026.\nChecked at {now_str}"
                )
            else:
                send_email(
                    f"John Pennekamp Updat
