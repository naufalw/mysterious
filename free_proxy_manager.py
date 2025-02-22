import os
import requests
import time
import warnings
from concurrent.futures import ThreadPoolExecutor
from constants import (
    BLACKLISTED_PROXY_PATH,
    MAX_WORKERS,
    WORKING_PROXY_PATH,
)

warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class FreeProxyManager:
    _instance = None
    blacklist_file_path = BLACKLISTED_PROXY_PATH
    working_proxies_file_path = WORKING_PROXY_PATH

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FreeProxyManager, cls).__new__(cls)
            cls._instance.proxies = cls._instance.load_working_proxies()
            cls._instance.blacklist = cls._instance.load_blacklist()
        return cls._instance

    def load_blacklist(self):
        try:
            with open(self.blacklist_file_path, "r") as file:
                return set(line.strip() for line in file if line.strip())
        except FileNotFoundError:
            return set()

    def save_blacklist(self):
        with open(self.blacklist_file_path, "w") as file:
            for proxy in self.blacklist:
                file.write(proxy + "\n")

    def load_working_proxies(self):
        try:
            with open(self.working_proxies_file_path, "r") as file:
                return [
                    (line.strip().split(",")[0], float(line.strip().split(",")[1]))
                    for line in file
                    if line.strip()
                ]
        except FileNotFoundError:
            return []

    def save_working_proxies(self):
        with open(self.working_proxies_file_path, "w") as file:
            for proxy, time_taken in self.proxies:
                file.write(f"{proxy},{time_taken}\n")

    def update_proxy_list(
        self,
        url="https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    ):
        try:
            response = requests.get(url)
            response.raise_for_status()
            proxy_lines = response.text.strip().split("\n")
            proxies_to_test = [
                {"http": f"http://{proxy}", "https": f"http://{proxy}"}
                for proxy in proxy_lines
                if proxy not in self.blacklist
            ]

            max_workers = max(os.cpu_count() * 2, MAX_WORKERS)
            print(
                f"Testing {len(proxies_to_test)} proxies with {max_workers} workers..."
            )
            
            def test_proxy_with_status(proxy):
                proxy_addr = proxy["http"].split("//")[1]
                print(f"Testing proxy: {proxy_addr}...", end=" ", flush=True)
                result = self._test_proxy(proxy)
                if result[0]:
                    print(f"✓ Working (Response time: {result[1]:.2f}s)")
                else:
                    print("✗ Failed")
                return result

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = list(executor.map(test_proxy_with_status, proxies_to_test))

            # Store working proxies with their response times
            self.proxies = [
                (proxy["http"].split("//")[1], time_taken)
                for proxy, (is_working, time_taken) in zip(proxies_to_test, results)
                if is_working
            ]
            # Sort proxies by response time
            self.proxies.sort(key=lambda x: x[1])
            self.save_working_proxies()
            print(f"\nUpdated proxy list with {len(self.proxies)} working proxies.")
            # Update the blacklist
            self.blacklist.update(
                set(proxy_lines) - set(proxy[0] for proxy in self.proxies)
            )
            self.save_blacklist()
        except requests.RequestException as e:
            print(f"Error fetching proxies: {e}")

    def get_proxy(self):
        if self.proxies:
            # Get the proxy with the fastest response time (first in the sorted list)
            fastest_proxy, fastest_time = self.proxies[0]
            print(
                f"Using fastest proxy: {fastest_proxy} with response time: {fastest_time:.2f} seconds"
            )
            return {
                "http": f"http://{fastest_proxy}",
                "https": f"http://{fastest_proxy}",
            }
        else:
            print("Proxy list is empty. Fetching new proxies.")
            self.update_proxy_list()
            return self.get_proxy() if self.proxies else None

    def remove_and_update_proxy(self, non_functional_proxy):
        # Extract the proxy address from the dictionary for consistent handling
        non_functional_proxy_address = non_functional_proxy["http"].split("//")[
            1
        ]  # assuming proxy format is always correct

        # Remove the non-functional proxy by its address and update the blacklist
        self.proxies = [
            proxy for proxy in self.proxies if proxy[0] != non_functional_proxy_address
        ]
        self.blacklist.add(non_functional_proxy_address)
        self.save_blacklist()
        print(
            f"Removed and blacklisted non-functional proxy: {non_functional_proxy_address}"
        )

        # Check if we need to update the proxy list due to a low count
        if len(self.proxies) < 5:  # Threshold to decide when to fetch more
            print("Proxy count low, updating proxy list...")
            self.update_proxy_list()

    def _test_proxy(self, proxy):
        test_url = "https://www.youtube.com"  # Changed to YouTube since we'll use it for that
        try:
            start_time = time.time()
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            response = session.get(test_url, proxies=proxy, timeout=10, verify=False)
            response_time = time.time() - start_time
            return (response.status_code == 200, response_time)
        except Exception:
            return (False, float("inf"))