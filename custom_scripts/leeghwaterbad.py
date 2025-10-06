import argparse
import re
from dataclasses import dataclass, asdict
from datetime import datetime

import orjson
import pytz
import requests
from bs4 import BeautifulSoup

# Constants
LOGIN_URL = "https://spurd.booqi.me/client/login"
ORDERS_URL = "https://spurd.booqi.me/client/orders"
SUBSCRIPTIONS_URL = "https://spurd.booqi.me/client/subscriptions"
TIMEZONE = "Europe/Amsterdam"


@dataclass
class Abonnement:
    beschikbaar: int | None = None
    totaal: int | None = None
    procent: int | None = None
    verloopdatum: datetime | None = None


@dataclass
class Bestelling:
    volgende: datetime | None = None
    product: str | None = None
    aantal: list[str] | None = None
    ordernummer: str | None = None
    status: str | None = None
    ticket: str | None = None


def login(session: requests.Session, email: str, password: str) -> None:
    """Handles login to the portal."""
    response = session.get(LOGIN_URL)
    if response.status_code != 200:
        raise Exception(f"Login page not reachable (status {response.status_code})")

    payload = {"email": email, "password": password}
    response = session.post(LOGIN_URL, data=payload)
    soup = BeautifulSoup(response.text, "html.parser")

    # Check if login was successful
    if "Mijn gegevens" not in soup.text:
        raise Exception("Login failed or user is not logged in.")


def get_page(session: requests.Session, url: str) -> BeautifulSoup:
    """Fetches a portal page and returns a BeautifulSoup tree."""
    response = session.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve {url} (status {response.status_code})")
    return BeautifulSoup(response.text, "html.parser")


def parse_datetime(date_string: str, timezone: str, string_date_format: str) -> datetime:
    """Parses a datetime string into a timezone-aware UTC datetime."""
    parsed = datetime.strptime(date_string, string_date_format)
    local_tz = pytz.timezone(timezone)
    parsed_local = local_tz.localize(parsed)
    return parsed_local.astimezone(pytz.utc)


def safe_text(node, default: str | None = None) -> str | None:
    """Extracts and cleans text from a BeautifulSoup node, or returns a default."""
    return node.get_text(strip=True) if node else default


def get_subscription_details(soup: BeautifulSoup) -> Abonnement:
    """Extracts subscription details from the subscriptions page."""
    active = max(len(soup.select("#subscriptions_active > div > div")) - 1, 0)
    if active == 0:
        return Abonnement(
            beschikbaar=0,
            totaal=0,
            procent=0,
            verloopdatum=datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc),
        )

    details = safe_text(
        soup.select_one("#subscriptions_active > div > div:nth-child(2) > div:nth-child(3)")
    )
    beschikbaar = totaal = percent = None
    if details:
        match = re.match(r"(\d+)/(\d+)-\s+(\d+)%", details)
        if match:
            beschikbaar = int(match.group(1))
            totaal = int(match.group(2))
            percent = int(match.group(3))

    verloopdatum_text = safe_text(
        soup.select_one("#subscriptions_active > div > div:nth-child(2) > div:nth-child(4)")
    )
    verloopdatum = (
        parse_datetime(verloopdatum_text, TIMEZONE, "%d-%m-%Y") if verloopdatum_text else None
    )

    return Abonnement(
        beschikbaar=beschikbaar,
        totaal=totaal,
        procent=percent,
        verloopdatum=verloopdatum,
    )


def get_order_details(soup: BeautifulSoup) -> Bestelling:
    """Extracts the next order (closest future date) from the orders page."""
    rows = soup.select("#orders_usable > table tbody > tr")
    if not rows:
        return Bestelling(
            volgende=datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc),
        )

    orders: list[Bestelling] = []
    for row in rows:
        volgende_text = safe_text(row.select_one("td:nth-child(4)"))
        if not volgende_text:
            continue

        volgende = parse_datetime(volgende_text, TIMEZONE, "%d-%m-%Y %H:%M")

        product = safe_text(row.select_one("td:nth-child(1) strong"))
        aantal = safe_text(row.select_one("td:nth-child(3) span"))
        ordernummer = safe_text(row.select_one("td:nth-child(1) small"))
        status = safe_text(row.select_one("td:nth-child(2) span"))
        # Find ticket link by looping over all li elements and checking href
        ticket_href = None
        li_nodes = row.select("td.nk-tb-col-tools ul li")
        for li in li_nodes:
            a = li.find("a", href=True)
            if a and a["href"].startswith("/assets/order/tickets/"):
                ticket_href = a["href"]
                break

        orders.append(
            Bestelling(
                volgende=volgende,
                product=product,
                aantal=aantal,
                ordernummer=ordernummer,
                status=status,
                ticket=f"https://spurd.booqi.me/{ticket_href}" if ticket_href else None,
            )
        )

    return min(orders, key=lambda o: o.volgende)


def to_serializable(obj):
    """Helper for orjson to handle datetime and dataclasses."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    raise TypeError


def main(email: str, password: str):
    session = requests.Session()

    login(session, email, password)

    bestelling = get_order_details(get_page(session, ORDERS_URL))
    abonnement = get_subscription_details(get_page(session, SUBSCRIPTIONS_URL))

    data = {"abonnement": abonnement, "bestelling": bestelling}
    print(orjson.dumps(data, default=to_serializable, option=orjson.OPT_INDENT_2).decode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Leeghwaterbad Data Scraper")
    parser.add_argument("email", type=str, help="Your email for the Leeghwaterbad portal")
    parser.add_argument("password", type=str, help="Your password for the Leeghwaterbad portal")

    args = parser.parse_args()
    main(args.email, args.password)
