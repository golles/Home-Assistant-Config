import argparse
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import orjson
import pytz
import requests
from bs4 import BeautifulSoup

# Constants
TOKEN_FIELD = "__RequestVerificationToken"
LOGIN_URL = "https://carwashplus.carwash-cms.com/customerportal/Account/Login"
TRANSACTIONS_URL = "https://carwashplus.carwash-cms.com/customerportal/Transaction"
TIMEZONE = "Europe/Amsterdam"


@dataclass
class Data:
    saldo: float | None = None
    pasnummer: str | None = None
    laatste_bezoek: str | None = None
    vestiging: str | None = None
    product: str | None = None
    bedrag: float | None = None
    betaald: str | None = None


def login(session: requests.Session, username: str, password: str) -> requests.Response:
    """Handles login to the portal."""
    response = session.get(LOGIN_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    token = soup.find("input", {"name": TOKEN_FIELD})["value"]

    payload = {
        TOKEN_FIELD: token,
        "UserName": username,
        "Password": password,
    }

    return session.post(LOGIN_URL, data=payload)


def get_saldo(soup: BeautifulSoup) -> float:
    """Extracts the saldo value from the page."""
    saldo_element = soup.select_one("body > div > div > div.row.mb-3.align-items-center > div.col-lg-6.text-lg-right > div:nth-child(1) > div > h4")
    if saldo_element:
        h4_text = saldo_element.get_text(separator=" ", strip=True)
        saldo_value_str = h4_text.split("€")[1].strip().replace(",", ".")
        return float(saldo_value_str)
    raise Exception("Failed to retrieve saldo")


def get_passnummer(soup: BeautifulSoup) -> str:
    """Extracts the passnummer from the page."""
    return soup.select_one("body > div > div > div:nth-child(3) > div:nth-child(1) > div > table > thead > tr > th:nth-child(2)").get_text(strip=True)


def get_transactions_page(session: requests.Session) -> BeautifulSoup:
    """Fetches the transactions page."""
    response = session.get(TRANSACTIONS_URL)
    if response.status_code != 200:
        raise Exception("Failed to retrieve transactions")
    return BeautifulSoup(response.text, "html.parser")


def parse_datetime(bezoek_text: str) -> str:
    """Parses the visit date time into ISO format (UTC)."""
    bezoek_datetime = datetime.strptime(bezoek_text, "%d-%m-%Y %H:%M:%S")
    local_tz = pytz.timezone(TIMEZONE)
    bezoek_datetime_local = local_tz.localize(bezoek_datetime)
    bezoek_datetime_utc = bezoek_datetime_local.astimezone(pytz.utc)
    return bezoek_datetime_utc.isoformat()


def get_transaction_details(soup: BeautifulSoup) -> Data:
    """Extracts transaction details from the transactions page."""
    laatste_bezoek = soup.select_one("body > div > div > div.table-responsive-lg > table > tbody > tr:nth-child(1) > td:nth-child(2)").get_text(
        strip=True
    )
    laatste_bezoek_iso = parse_datetime(laatste_bezoek)

    vestiging = soup.select_one("body > div > div > div.table-responsive-lg > table > tbody > tr:nth-child(1) > td:nth-child(1)").get_text(strip=True)
    product = soup.select_one("body > div > div > div.table-responsive-lg > table > tbody > tr:nth-child(1) > td:nth-child(4)").get_text(strip=True)
    bedrag = soup.select_one("body > div > div > div.table-responsive-lg > table > tbody > tr:nth-child(1) > td:nth-child(5)").get_text(strip=True)
    betaald = soup.select_one("body > div > div > div.table-responsive-lg > table > tbody > tr:nth-child(1) > td:nth-child(6)").get_text(strip=True)

    # Clean and convert bedrag to float
    bedrag_value_str = bedrag.replace("€", "").strip().replace(".", "").replace(",", ".")
    bedrag_value = float(bedrag_value_str)

    return Data(
        saldo=None,  # Placeholder, will be set later
        pasnummer=None,  # Placeholder, will be set later
        laatste_bezoek=laatste_bezoek_iso,
        vestiging=vestiging,
        product=product,
        bedrag=bedrag_value,
        betaald=betaald,
    )


def main(username: str, password: str):
    session = requests.Session()

    response = login(session, username, password)
    soup = BeautifulSoup(response.text, "html.parser")

    # Check if login was successful
    if "Mijn gegevens" not in soup.text:
        raise Exception("Login failed or user is not logged in.")

    # Get saldo and passnummer from logged page
    saldo = get_saldo(soup)
    passnummer = get_passnummer(soup)

    # Fetch transactions
    transactions_soup = get_transactions_page(session)
    transaction_data = get_transaction_details(transactions_soup)

    # Add saldo and passnummer to transaction data
    transaction_data.saldo = saldo
    transaction_data.pasnummer = passnummer

    # Output data as JSON
    print(orjson.dumps(transaction_data).decode("utf-8"))


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Carwash Plus Data Scraper")
    parser.add_argument("username", type=str, help="Your username for the Carwash Plus portal")
    parser.add_argument("password", type=str, help="Your password for the Carwash Plus portal")

    args = parser.parse_args()
    main(args.username, args.password)
