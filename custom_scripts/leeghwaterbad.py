import argparse
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import orjson
import pytz
import requests
from bs4 import BeautifulSoup

# Constants
TOKEN_FIELD = "__RequestVerificationToken"
LOGIN_URL = "https://spurd.booqi.me/client/login"
ORDERS_URL = "https://spurd.booqi.me/client/orders"
SUBSCRIPTIONS_URL = "https://spurd.booqi.me/client/subscriptions"
TIMEZONE = "Europe/Amsterdam"


@dataclass
class Abonnement:
    beschikbaar: int | None = None
    totaal: int | None = None
    procent: int | None = None
    verloopdatum: str | None = None


@dataclass
class Bestelling:
    volgende: str | None = None
    product: str | None = None
    aantal: int | None = None
    ordernummer: str | None = None
    status: str | None = None
    ticket: str | None = None


def login(session: requests.Session, email: str, password: str) -> None:
    """Handles login to the portal."""
    response = session.get(LOGIN_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    payload = {
        "email": email,
        "password": password,
    }

    response = session.post(LOGIN_URL, data=payload)
    soup = BeautifulSoup(response.text, "html.parser")

    # Check if login was successful
    if "Mijn gegevens" not in soup.text:
        raise Exception("Login failed or user is not logged in.")


def get_page(session: requests.Session, url: str) -> BeautifulSoup:
    """Fetches the transactions page."""
    response = session.get(url)
    if response.status_code != 200:
        raise Exception("Failed to retrieve page")
    return BeautifulSoup(response.text, "html.parser")


def parse_datetime(date_string: str, timezone: str, string_date_format: str) -> str:
    """Parses date time string into ISO format (UTC)."""
    parsed = datetime.strptime(date_string, string_date_format)
    local_tz = pytz.timezone(timezone)
    parsed_local = local_tz.localize(parsed)
    parsed_utc = parsed_local.astimezone(pytz.utc)
    return parsed_utc.isoformat()


def get_subscription_details(soup: BeautifulSoup) -> Abonnement:
    """Extracts subscription details from the subscriptions page."""
    active = len(soup.select("#subscriptions_active > div > div")) - 1 # Exclude the header row
    if active == 0:
        return Abonnement(
            beschikbaar=0,
            totaal=0,
            procent=0,
            verloopdatum="1970-01-01T00:00:00+00:00",
        )

    details = soup.select_one("#subscriptions_active > div > div:nth-child(2) > div:nth-child(3)").get_text(strip=True)
    match = re.match(r"(\d+)/(\d+)-\s+(\d+)%", details)
    if match:
        beschikbaar = int(match.group(1))
        totaal = int(match.group(2))
        percent = int(match.group(3))

    verloopdatum = soup.select_one("#subscriptions_active > div > div:nth-child(2) > div:nth-child(4)").get_text(strip=True)

    return Abonnement(
        beschikbaar=beschikbaar,
        totaal=totaal,
        procent=percent,
        verloopdatum=parse_datetime(verloopdatum, TIMEZONE, "%d-%m-%Y"),
    )


def get_order_details(soup: BeautifulSoup) -> Bestelling:
    """Extracts order details from the subscriptions page."""
    rows = soup.select("#orders_usable > table tbody > tr")
    if len(rows) == 0:
        return Bestelling(
            volgende="1970-01-01T00:00:00+00:00",
            product=None,
            aantal=None,
            ordernummer=None,
            status=None,
            ticket=None,
        )

    volgende = soup.select_one("#orders_usable > table > tbody > tr > td:nth-child(4)").get_text(strip=True)
    product = soup.select_one("#orders_usable > table > tbody > tr > td:nth-child(1) > span > span > strong").get_text(strip=True)
    aantal = soup.select_one("#orders_usable > table > tbody > tr > td:nth-child(3) > span:nth-child(1)").get_text(strip=True)
    ordernummer = soup.select_one("#orders_usable > table > tbody > tr > td:nth-child(1) > span > span > small").get_text(strip=True)
    status = soup.select_one("#orders_usable > table > tbody > tr > td:nth-child(2) > span").get_text(strip=True)
    ticket = soup.select_one("#orders_usable > table > tbody > tr > td.nk-tb-col.nk-tb-col-tools.align-middle > ul > li:nth-child(2) > a").get("href")

    return Bestelling(
        volgende=parse_datetime(volgende, TIMEZONE, "%d-%m-%Y %H:%M"),
        product=product,
        aantal=aantal,
        ordernummer=ordernummer,
        status=status,
        ticket=f"https://spurd.booqi.me/{ticket}",
    )


def main(email: str, password: str):
    session = requests.Session()

    login(session, email, password)

    response = get_page(session, ORDERS_URL)
    bestelling = get_order_details(response)

    response = get_page(session, SUBSCRIPTIONS_URL)
    abonnement = get_subscription_details(response)

    print(orjson.dumps({"abonnement": abonnement, "bestelling": bestelling}).decode("utf-8"))


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Leeghwaterbad Data Scraper")
    parser.add_argument("email", type=str, help="Your email for the Leeghwaterbad portal")
    parser.add_argument("password", type=str, help="Your password for the Leeghwaterbad portal")

    args = parser.parse_args()
    main(args.email, args.password)
