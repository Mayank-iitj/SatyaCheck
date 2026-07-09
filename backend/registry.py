import os
from typing import Dict, List, Optional
from pydantic import BaseModel

class Intermediary(BaseModel):
    registration_number: str
    name: str
    category: str  # Broker, RIA, IA, Research Analyst, Mutual Fund
    domain: str
    upi_handle: str
    public_key_hex: str

class CorporateFiling(BaseModel):
    id: str
    company_name: str
    symbol: str
    title: str
    date: str
    content_summary: str
    source_url: str

class SebiCircular(BaseModel):
    circular_id: str
    title: str
    date: str
    content: str
    signature: Optional[str] = None  # Ed25519 signature

# Mock Database of SEBI-Registered Intermediaries
# For the demo, we generate Ed25519 public/private keypairs.
# Private keys are held securely by the mock signing service, public keys are here in the registry.
INTERMEDIARIES_DB: Dict[str, Intermediary] = {
    "INZ000123456": Intermediary(
        registration_number="INZ000123456",
        name="Zerodha Broking Ltd.",
        category="Broker",
        domain="zerodha.com",
        upi_handle="zerodha@valid",
        public_key_hex="5ad9c4f103089362d0ed3b09fb32d41c54809ceebe25726b54e825781f5be91a"
    ),
    "INZ000987654": Intermediary(
        registration_number="INZ000987654",
        name="Groww (Nextbillion Technology)",
        category="Broker",
        domain="groww.in",
        upi_handle="groww@valid",
        public_key_hex="ee48ec2af549521c102000faca10cf6bedea2a7c26fb9f062c7146f40fbca514"
    ),
    "INA000011111": Intermediary(
        registration_number="INA000011111",
        name="NiftyWealth Advisers",
        category="Investment Adviser",
        domain="niftywealth.com",
        upi_handle="niftywealth@valid",
        public_key_hex="08610cd15a8590da0682ce6ce283e09e42b7fda30931cc4305efdb33ecabe0cc"
    )
}

# Mock Database of Corporate Filings (Official filings with Stock Exchanges BSE/NSE)
CORPORATE_FILINGS: List[CorporateFiling] = [
    CorporateFiling(
        id="FIL-2026-001",
        company_name="Reliance Industries Limited",
        symbol="RELIANCE",
        title="RIL Board approves Buyback of equity shares worth Rs. 15,000 Crores at Rs. 3,200 per share",
        date="2026-07-01",
        content_summary="Reliance Industries Limited has announced a share buyback program for up to Rs. 15,000 crore at a maximum price of Rs. 3,200 per equity share through the open market route.",
        source_url="https://www.nseindia.com/get-corporate-filing/ril-buyback"
    ),
    CorporateFiling(
        id="FIL-2026-002",
        company_name="Tata Consultancy Services Limited",
        symbol="TCS",
        title="TCS announces Q1 FY27 results with 12% revenue growth YoY",
        date="2026-07-05",
        content_summary="TCS reported consolidated revenue of Rs. 62,500 Crores, up 12% YoY, and Net Profit of Rs. 12,200 Crores, up 9% YoY. Dividend of Rs. 10 per share declared.",
        source_url="https://www.nseindia.com/get-corporate-filing/tcs-q1-fy27"
    ),
    CorporateFiling(
        id="FIL-2026-003",
        company_name="Infosys Limited",
        symbol="INFY",
        title="Infosys bags $1.5 Billion multi-year digital transformation contract with European bank",
        date="2026-07-08",
        content_summary="Infosys has signed a strategic partnership with a leading European bank to accelerate its digital transformation journey over the next 5 years.",
        source_url="https://www.nseindia.com/get-corporate-filing/infosys-deal"
    )
]

# Mock Database of SEBI Circulars
SEBI_CIRCULARS: Dict[str, SebiCircular] = {
    "SEBI/HO/MIRSD/CIR/P/2026/88": SebiCircular(
        circular_id="SEBI/HO/MIRSD/CIR/P/2026/88",
        title="Mandatory Two-Factor Authentication for Login to Trading Accounts",
        date="2026-06-15",
        content="All registered stockbrokers must implement mandatory Two-Factor Authentication (2FA) for clients logging into trading applications by September 1, 2026."
    ),
    "SEBI/HO/IMD/DF2/CIR/P/2026/102": SebiCircular(
        circular_id="SEBI/HO/IMD/DF2/CIR/P/2026/102",
        title="Disclosure of Risk Factors in Small-Cap Mutual Fund Advertisements",
        date="2026-07-01",
        content="Asset Management Companies (AMCs) must prominently display a standardized small-cap investment risk warning covering at least 30% of the visual space in all advertisements."
    )
}

def lookup_intermediary(query: str) -> Optional[Intermediary]:
    """Search for intermediary by registration number, name, or domain."""
    query_lower = query.lower()
    for reg, item in INTERMEDIARIES_DB.items():
        if (query_lower == reg.lower() or 
            query_lower in item.name.lower() or 
            query_lower == item.domain.lower() or
            query_lower == item.upi_handle.lower()):
            return item
    return None

def lookup_filing(query: str) -> List[CorporateFiling]:
    """Retrieve corporate filings containing relevant keywords or symbols."""
    query_lower = query.lower()
    results = []
    for filing in CORPORATE_FILINGS:
        if (query_lower in filing.company_name.lower() or 
            query_lower in filing.symbol.lower() or 
            query_lower in filing.title.lower() or
            query_lower in filing.content_summary.lower()):
            results.append(filing)
    return results
