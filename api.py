import requests
import logging
from typing import Dict, Any

_LOGGER = logging.getLogger(__name__)

class BankOfIsraelAPI:
    def __init__(self, hass, domain: str):
        self._hass = hass
        self._domain = domain
        self._base_url = "https://boi.org.il/PublicApi/GetExchangeRate?key="

    async def get_exchange_rates(self) -> Dict[str, float]:
        """Fetch and return the latest exchange rates for the specified currencies."""
        currencies = self._hass.data[self._domain]["currencies"]
        exchange_rates = {}

        for currency in currencies:
            try:
                response = await self._hass.async_add_executor_job(
                    requests.get, f"{self._base_url}{currency}"
                )
                response.raise_for_status()
                data = response.json()
                exchange_rate = self._parse_exchange_rate(data, currency)
                if exchange_rate is not None:
                    exchange_rates[currency] = exchange_rate
            except requests.exceptions.RequestException as err:
                _LOGGER.error(f"Error fetching data for {currency}: {err}")
            except (ValueError, KeyError) as err:
                _LOGGER.error(f"Error parsing data for {currency}: {err}")

        return exchange_rates

    async def get_available_currencies(self) -> Dict[str, str]:
        """Fetch and return a dictionary of available currencies."""
        try:
            response = await self._hass.async_add_executor_job(
                requests.get, "https://boi.org.il/PublicApi/GetExchangeRates"
            )
            response.raise_for_status()
            data = response.json()
            return self._parse_available_currencies(data)
        except requests.exceptions.RequestException as err:
            _LOGGER.error(f"Error fetching available currencies: {err}")
            return {}
        except (ValueError, KeyError) as err:
            _LOGGER.error(f"Error parsing available currencies: {err}")
            return {}
        
    @staticmethod
    def _parse_exchange_rate(data: Dict[str, Any], currency: str) -> float:
        """Parse the exchange rate from the API response."""
        try:
            return round(float(data["currentExchangeRate"]), 2)
        except (ValueError, KeyError) as err:
            _LOGGER.error(f"Error parsing exchange rate for {currency}: {err}")
            return None

    @staticmethod
    def _parse_available_currencies(data: Dict[str, Any]) -> Dict[str, str]:
        """Parse available currencies from the API response."""
        try:
            return {rate["key"]: rate["key"] for rate in data["exchangeRates"]}
        except (ValueError, KeyError) as err:
            _LOGGER.error(f"Error parsing available currencies: {err}")
            return {}