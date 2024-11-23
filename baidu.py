import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from multiprocessing import Pool, cpu_count

# Xiequ API credentials
XIEQU_API = "http://api.xiequ.cn/VAD/GetIp.aspx"
XIEQU_PARAMS = {
    "act": "getturn51",
    "uid": "108483",  # Replace with your UID
    "vkey": "54C830C2659ADAE3F42CFA321AECA31F",  # Replace with your VKEY
    "num": 200,  # Number of proxies to fetch
    "time": 6,  # Proxy validity in minutes
    "plat": 1,
    "re": 0,
    "type": 7,  # HTTP/HTTPS proxies
    "so": 1,
    "group": 51,
    "ow": 1,
    "spl": 1,
    "addr": "",
    "db": 1,
}

MAX_RETRIES = 3  # Maximum retries for resolving redirects
REQUEST_TIMEOUT = 15  # Timeout for requests in seconds

# Function to fetch proxies from Xiequ
def fetch_proxies():
    try:
        response = requests.get(XIEQU_API, params=XIEQU_PARAMS)
        response.raise_for_status()
        proxies = response.text.strip().split("\r\n")
        return proxies
    except requests.RequestException as e:
        print(f"Error fetching proxies: {e}")
        return []

# Function to resolve Baidu redirect URL with retries
def resolve_redirect(url, proxy):
    proxy_config = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.head(url, proxies=proxy_config, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            return response.url
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1}/{MAX_RETRIES} failed resolving redirect for URL '{url}': {e}")
            time.sleep(random.uniform(1, 2))  # Short delay before retrying
    print(f"Failed to resolve redirect for URL '{url}' after {MAX_RETRIES} attempts.")
    return url  # Return original URL if resolution fails

# Function to scrape Baidu for a single keyword
def scrape_keyword(keyword, proxy):
    base_url = "https://www.baidu.com/s"
    params = {"wd": keyword}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    }
    proxy_config = {"http": f"http://{proxy}", "https": f"http://{proxy}"}

    try:
        response = requests.get(base_url, params=params, headers=headers, proxies=proxy_config, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for item in soup.find_all("div", class_="result"):
            title_tag = item.find("h3")
            if title_tag:
                title = title_tag.get_text(strip=True)
                link_tag = title_tag.find("a")
                if link_tag:
                    url = link_tag["href"]
                    real_url = resolve_redirect(url, proxy)  # Resolve the redirect URL
                    results.append({"keyword": keyword, "title": title, "url": real_url})
        return results
    except requests.RequestException as e:
        print(f"Error scraping keyword '{keyword}' with proxy {proxy}: {e}")
        return []

# Process a batch of keywords
def process_keyword_batch(batch):
    proxies = fetch_proxies()  # Fetch proxies for the batch
    if not proxies:
        print("No proxies available for this batch.")
        return []

    results = []
    for keyword in batch:
        proxy = random.choice(proxies)  # Randomly select a proxy
        result = scrape_keyword(keyword, proxy)
        results.extend(result)
        time.sleep(random.uniform(0.5, 2))  # Random delay to mimic human behavior
    return results

# Main function
def main():
    # Load keywords from keyword.txt
    try:
        with open("keyword.txt", "r", encoding="utf-8") as file:
            keywords = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print("The file 'keyword.txt' was not found.")
        return

    # Split keywords into smaller batches
    batch_size = 500  # Adjust batch size based on memory and performance
    keyword_batches = [keywords[i:i + batch_size] for i in range(0, len(keywords), batch_size)]

    # Use multiprocessing to process batches
    num_workers = min(cpu_count(), 4)  # Use up to 4 workers or CPU count
    with Pool(processes=num_workers) as pool:
        all_results = []
        for batch_results in pool.imap_unordered(process_keyword_batch, keyword_batches):
            all_results.extend(batch_results)

    # Save results to an Excel file
    if all_results:
        df = pd.DataFrame(all_results)
        df.to_excel("baidu_results.xlsx", index=False)
        print("Search results have been saved to 'baidu_results.xlsx'.")
    else:
        print("No results found to save.")

if __name__ == "__main__":
    main()
