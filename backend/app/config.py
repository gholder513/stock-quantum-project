from typing import List

# Universe of tickers will add back and expand to 200 later
TICKERS: List[str] = [
    "WMT",    # Walmart Inc.
    "AMZN",   # Amazon.com, Inc.
    "UNH",    # UnitedHealth Group Incorporated
    "AAPL",   # Apple Inc.
    "CVS",    # CVS Health Corporation
    "BRK.B",  # Berkshire Hathaway Inc. (Class B)
    "GOOGL",  # Alphabet Inc. (Class A)
    "XOM",    # Exxon Mobil Corporation
    "MCK",    # McKesson Corporation
    "CNC",    # Cencora, Inc.
    "COST",   # Costco Wholesale Corporation
    "JPM",    # JPMorgan Chase & Co.
    "MSFT",   # Microsoft Corporation
    "CAH",    # Cardinal Health, Inc.
    "CVX",    # Chevron Corporation
    "CI",     # Cigna Corporation
    "F",      # Ford Motor Company
    "BAC",    # Bank of America Corporation
    "GM",     # General Motors Company
    "ELV",    # Elevance Health, Inc.
    "HD",     # The Home Depot, Inc.
    "PFE",    # Pfizer Inc.
    "VZ",     # Verizon Communications Inc.
    "T",      # AT&T Inc.
    "MRK",    # Merck & Co., Inc.
    "JNJ",    # Johnson & Johnson
    "META",   # Meta Platforms, Inc.
    "NVDA",   # NVIDIA Corporation
    "TSLA",   # Tesla, Inc.
    "INTC",   # Intel Corporation
    "CSCO",   # Cisco Systems, Inc.
    "ORCL",   # Oracle Corporation
    "PEP",    # PepsiCo, Inc.
    "KO",     # The Coca-Cola Company
    "PG",     # Procter & Gamble Company
    "ABBV",   # AbbVie Inc.
    # "WBA",    # Walgreens Boots Alliance, Inc.
    "LOW",    # Lowe's Companies, Inc.
    "TGT",    # Target Corporation
    "UNP",    # Union Pacific Corporation
    "CAT",    # Caterpillar Inc.
    "UPS",    # United Parcel Service, Inc.
    "MA",     # Mastercard Incorporated
    "V",      # Visa Inc.
    "DUK",    # Duke Energy Corporation
    "MMM",    # 3M Company
    "RTX",    # RTX Corporation (Raytheon Technologies)
    "AMAT",   # Applied Materials, Inc.
    "HON",    # Honeywell International Inc.
    "BMY",    # Bristol-Myers Squibb Company
    "LLY",    # Eli Lilly and Company
    "NKE",    # NIKE, Inc.
    "SBUX",   # Starbucks Corporation
    "BK",     # Bank of New York Mellon Corporation
    "GS",     # Goldman Sachs Group, Inc.
    "MS",     # Morgan Stanley
    "SCHW",   # Charles Schwab Corporation
    "C",      # Citigroup Inc.
    "USB",    # U.S. Bancorp
    "SLB",    # Schlumberger Limited
    "COP",    # ConocoPhillips
    "ADM",    # Archer-Daniels-Midland Company
    "PLD",    # Prologis, Inc.
    "AMGN",   # Amgen Inc.
    "MDLZ",   # Mondelez International, Inc.
    "SPGI",   # S&P Global, Inc.
    "ICE",    # Intercontinental Exchange, Inc.
    "TMO",    # Thermo Fisher Scientific Inc.
    "ZBH",    # Zimmer Biomet Holdings, Inc.
    "CIEN",   # Ciena Corporation
    "MU",     # Micron Technology, Inc.
    "ADP",    # Automatic Data Processing, Inc.
    "PLTR",   # Palantir Technologies Inc.
    "AON",    # Aon plc
    "MMC",    # Marsh & McLennan Companies, Inc.
    "AXP",    # American Express Company
    "BKNG",   # Booking Holdings Inc.
    "EQT",    # EQT Corporation
    "CRM",    # Salesforce, Inc.
    "DE",     # Deere & Company
    "TJX",    # TJX Companies, Inc.
    "GILD",   # Gilead Sciences, Inc.
    "SYK",    # Stryker Corporation
    "BLK",    # BlackRock, Inc.
    "BDX",    # Becton, Dickinson and Company
    "VRTX",   # Vertex Pharmaceuticals Incorporated
    "SO",     # The Southern Company
    "EL",     # The Estée Lauder Companies Inc.
    "DHR",    # Danaher Corporation
    "FIS",    # FIS (Fidelity National Information Services, Inc.)
    "LMT",    # Lockheed Martin Corporation
    "CSX",    # CSX Corporation
    "FDX",    # FedEx Corporation
    "PNC",    # The PNC Financial Services Group, Inc.
    "MET",    # MetLife, Inc.
    "PNR",    # Pentair plc
    "CL",     # Colgate-Palmolive Company
    "NEM",    # Newmont Corporation
    "ROP",    # Roper Technologies, Inc.
    "KMB",    # Kimberly-Clark Corporation
    "REGN",   # Regeneron Pharmaceuticals, Inc.
    "HUM",    # Humana Inc.
    "ES",     # Eversource Energy
    "ECL",    # Ecolab Inc.
    "LHX",    # L3Harris Technologies, Inc.
    "HCA",    # HCA Healthcare, Inc.
    "SYY",    # Sysco Corporation
    "MCO",    # Moody's Corporation
    "FISV",   # Fiserv, Inc.
    "KMI",    # Kinder Morgan, Inc.
    "EXC",    # Exelon Corporation
    "ALL",    # Allstate Corporation
    "CME",    # CME Group Inc.
    "BAX",    # Baxter International Inc.
    "EW",     # Edwards Lifesciences Corporation
    "ABT",    # Abbott Laboratories
    "TFC",    # Truist Financial Corporation
    "HSY",    # The Hershey Company
    "CTSH",   # Cognizant Technology Solutions Corporation
    "ETN",    # Eaton Corporation plc
    "A",      # Agilent Technologies, Inc.
    "APD",    # Air Products and Chemicals, Inc.
    "SPG",    # Simon Property Group, Inc.
    "MTB",    # M&T Bank Corporation
    "IFF",    # International Flavors & Fragrances Inc.
    "XYL",    # Xylem Inc.
    "PH",     # Parker-Hannifin Corporation
    "PGR",    # The Progressive Corporation
    "HIG",    # The Hartford Financial Services Group, Inc.
    "HII",    # Huntington Ingalls Industries, Inc.
    "NOC",    # Northrop Grumman Corporation
    "D",      # Dominion Energy, Inc.
    "PRU",    # Prudential Financial, Inc.
    "ITW",    # Illinois Tool Works Inc.
    "PAYX",   # Paychex, Inc.
    "GLW",    # Corning Inc.
    "RCL",    # Royal Caribbean Group
    "MOS",    # The Mosaic Company
    "WM",     # Waste Management, Inc.
    "CHTR",   # Charter Communications, Inc.
    # "CERN",   # Cerner Corporation
    "MTD",    # Mettler-Toledo International Inc.
    "K",      # Kellogg Company
    "VLO",    # Valero Energy Corporation
    "CF",     # CF Industries Holdings, Inc.
    "COO",    # The Cooper Companies, Inc.
    "MAS",    # Masco Corporation
    "TXT",    # Textron Inc.
    "TSN",    # Tyson Foods, Inc.
    "AEP",    # American Electric Power Company, Inc.
    "DOW",    # Dow Inc.
    "MSCI",   # MSCI Inc.
    "MKC",    # McCormick & Company, Incorporated
    "PHM",    # PulteGroup, Inc.
    "ORLY",   # O'Reilly Automotive, Inc.
    "TEL",    # TE Connectivity Ltd.
    "HWM",    # Howmet Aerospace Inc.
    "WEC",    # WEC Energy Group, Inc.
    "WY",     # Weyerhaeuser Company
    "PCAR",   # PACCAR Inc.
    "AES",    # The AES Corporation
    "EXR",    # Extra Space Storage, Inc.
    "ODFL",   # Old Dominion Freight Line, Inc.
    "AFL",    # Aflac Incorporated
    "CDW",    # CDW Corporation
    "RSG",    # Republic Services, Inc.
    "PAYC",   # Paycom Software, Inc.
    "FMC",    # FMC Corporation
    "BKR",    # Baker Hughes Company
    "ROST",   # Ross Stores, Inc.
    "AME",    # AMETEK, Inc.
    # "COG",    # Cabot Oil & Gas Corporation
    "KR",     # The Kroger Co.
    "CNP",    # CenterPoint Energy, Inc.
    "WELL",   # Welltower Inc.
    "DLR",    # Digital Realty Trust, Inc.
    "VTR",    # Ventas, Inc.
    "EOG",    # EOG Resources, Inc.
    "SLG",    # SL Green Realty Corp.
    "STZ",    # Constellation Brands, Inc.
    "DTE",    # DTE Energy Company
    "SEE",    # Sealed Air Corporation
    "DOV",    # Dover Corporation
    # "BLL",    # Ball Corporation
    "URI",    # United Rentals, Inc.
    "SWK",    # Stanley Black & Decker, Inc.
]


START_DATE = "2015-01-01"
END_DATE = "2020-12-31"

# Labeling configuration
LABEL_HORIZON_DAYS = 2      # look-ahead window
BUY_THRESHOLD = 0.01          # +1%
SELL_THRESHOLD = -0.01        # -1%

# Features used for model training
FEATURE_COLS = [
    "daily_return",
    "ma_5",
    "ma_10",
    "momentum_14",
    "volume_zscore_20",
]
