import requests
from bs4 import BeautifulSoup
import urllib.parse

def get_baidu_search_results(keyword):
    # Base URL for Baidu search
    base_url = "https://www.baidu.com/s"
    
    # Parameters for the search query
    params = {"wd": keyword}
    
    # Send the GET request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    }
    response = requests.get(base_url, params=params, headers=headers)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to fetch results for keyword: {keyword}")
        return []
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract the search results
    results = []
    for item in soup.find_all("div", class_="result"):
        title_tag = item.find("h3")
        if title_tag:
            title = title_tag.get_text(strip=True)
            link_tag = title_tag.find("a")
            if link_tag:
                url = link_tag["href"]
                results.append({"title": title, "url": url})
    
    return results


def main():
    # Read keywords from keyword.txt
    try:
        with open("keyword.txt", "r", encoding="utf-8") as file:
            keywords = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print("The file 'keyword.txt' was not found.")
        return
    
    # Collect results for each keyword
    all_results = {}
    for keyword in keywords:
        print(f"Fetching results for keyword: {keyword}")
        results = get_baidu_search_results(keyword)
        all_results[keyword] = results
    
    # Save results to a file
    with open("baidu_results.txt", "w", encoding="utf-8") as file:
        print("sdfsdfsdf")
        for keyword, results in all_results.items():
            file.write(f"Keyword: {keyword}\n")
            for result in results:
                file.write(f"Title: {result['title']}\n")
                file.write(f"URL: {result['url']}\n")
            file.write("\n")
    
    print("Search results have been saved to 'baidu_results.txt'.")

if __name__ == "__main__":
    main()
