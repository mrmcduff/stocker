"""
Tab completion functionality for the interactive shell.
"""

from prompt_toolkit.completion import Completer, Completion

class TickerCompleter(Completer):
    """
    Completer for stock ticker symbols.
    """
    def __init__(self):
        # Common US stock tickers - this is a subset to keep things fast
        # Load the most popular/common tickers
        self.tickers = {
            # Big Tech / Major companies
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corporation",
            "GOOGL": "Alphabet Inc. (Google) Class A",
            "GOOG": "Alphabet Inc. (Google) Class C",
            "AMZN": "Amazon.com Inc.",
            "META": "Meta Platforms Inc. (Facebook)",
            "TSLA": "Tesla Inc.",
            "NVDA": "NVIDIA Corporation",
            "NFLX": "Netflix Inc.",
            "DIS": "The Walt Disney Company",
            "ADBE": "Adobe Inc.",
            "INTC": "Intel Corporation",
            "CSCO": "Cisco Systems Inc.",
            "IBM": "International Business Machines",
            "AMD": "Advanced Micro Devices Inc.",
            "ORCL": "Oracle Corporation",
            "CRM": "Salesforce Inc.",
            "PYPL": "PayPal Holdings Inc.",
            "SHOP": "Shopify Inc.",
            "V": "Visa Inc.",
            "MA": "Mastercard Incorporated",
            "JPM": "JPMorgan Chase & Co.",
            "BAC": "Bank of America Corporation",
            "WFC": "Wells Fargo & Company",
            "GS": "The Goldman Sachs Group Inc.",
            "MS": "Morgan Stanley",
            "C": "Citigroup Inc.",
            "BRK.A": "Berkshire Hathaway Inc. Class A",
            "BRK.B": "Berkshire Hathaway Inc. Class B",
            "JNJ": "Johnson & Johnson",
            "PG": "The Procter & Gamble Company",
            "UNH": "UnitedHealth Group Incorporated",
            "HD": "The Home Depot Inc.",
            "WMT": "Walmart Inc.",
            "COST": "Costco Wholesale Corporation",
            "MCD": "McDonald's Corporation",
            "KO": "The Coca-Cola Company",
            "PEP": "PepsiCo Inc.",
            "NKE": "NIKE Inc.",
            "SBUX": "Starbucks Corporation",
            "T": "AT&T Inc.",
            "VZ": "Verizon Communications Inc.",
            "CMCSA": "Comcast Corporation",
            "XOM": "Exxon Mobil Corporation",
            "CVX": "Chevron Corporation",
            "GE": "General Electric Company",
            "BA": "The Boeing Company",
            "F": "Ford Motor Company",
            "GM": "General Motors Company",
            "UBER": "Uber Technologies Inc.",
            "LYFT": "Lyft Inc.",
            "ABNB": "Airbnb Inc.",
            "ZM": "Zoom Video Communications Inc.",
            "SPOT": "Spotify Technology S.A.",
            # Index ETFs
            "SPY": "SPDR S&P 500 ETF Trust",
            "QQQ": "Invesco QQQ Trust (Nasdaq-100 Index)",
            "DIA": "SPDR Dow Jones Industrial Average ETF",
            "IWM": "iShares Russell 2000 ETF",
            "VTI": "Vanguard Total Stock Market ETF",
            "VOO": "Vanguard S&P 500 ETF",
            # Bond ETFs
            "AGG": "iShares Core U.S. Aggregate Bond ETF",
            "BND": "Vanguard Total Bond Market ETF",
            "TLT": "iShares 20+ Year Treasury Bond ETF",
            # Sector ETFs
            "XLF": "Financial Select Sector SPDR Fund",
            "XLK": "Technology Select Sector SPDR Fund",
            "XLE": "Energy Select Sector SPDR Fund",
            "XLV": "Health Care Select Sector SPDR Fund",
            "XLP": "Consumer Staples Select Sector SPDR Fund",
            # International ETFs
            "EFA": "iShares MSCI EAFE ETF",
            "EEM": "iShares MSCI Emerging Markets ETF",
            "VEU": "Vanguard FTSE All-World ex-US ETF",
            # Cryptocurrencies
            "BTC-USD": "Bitcoin USD",
            "ETH-USD": "Ethereum USD",
            # Add more as needed
        }

        # Create a fast lookup dictionary by first letters
        self.ticker_by_prefix = {}
        for ticker, name in self.tickers.items():
            for i in range(1, len(ticker) + 1):
                prefix = ticker[:i]
                if prefix not in self.ticker_by_prefix:
                    self.ticker_by_prefix[prefix] = []
                self.ticker_by_prefix[prefix].append((ticker, name))

    def get_completions(self, document, complete_event):
        # Get word being completed
        word = document.get_word_before_cursor()
        word = word.upper()

        if not word:
            # Show a warning for empty input - would return too many options
            yield Completion('', 0, display='Type at least one letter to see suggestions')
            return

        # Find matching tickers
        matches = self.ticker_by_prefix.get(word, [])

        # Threshold for warning about too many results
        many_results_threshold = 15

        if len(matches) > many_results_threshold:
            yield Completion('', 0, display=f'Too many matches ({len(matches)}). Type more letters to narrow down.')

        # Sort matches alphabetically
        for ticker, company in sorted(matches):
            # Calculate how many characters user has already typed
            display = f"{ticker} - {company}"
            # Completion returns the remaining characters to complete the word
            yield Completion(ticker[len(word):], display=display)
