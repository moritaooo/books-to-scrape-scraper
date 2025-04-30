import requests
from bs4 import BeautifulSoup
import csv
import os
from urllib.parse import urljoin

BASE_URL = "https://books.toscrape.com/"
START_URL = urljoin(BASE_URL, "index.html")


def get_categories():
    res = requests.get(START_URL)
    soup = BeautifulSoup(res.text, "html.parser")
    category_list = soup.select("div.side_categories ul li ul li a")

    categories = []
    for cat in category_list:
        name = cat.text.strip()
        rel_url = cat["href"]
        full_url = urljoin(BASE_URL, rel_url)
        categories.append({"name": name, "url": full_url})
    return categories


def scrape_category(category):
    print(f"カテゴリ処理中：{category['name']}")
    books = []
    current_page = category["url"]

    while True:
        res = requests.get(current_page)
        soup = BeautifulSoup(res.text, "html.parser")

        for book in soup.select("article.product_pod"):
            title = book.h3.a["title"]
            price = book.find("p", class_="price_color").text
            availability = book.find("p", class_="instock availability").text.strip()
            rel_url = book.h3.a["href"]
            detail_url = urljoin(BASE_URL + "catalogue/", rel_url.replace("../", ""))

            books.append({
                "タイトル": title,
                "価格": price,
                "在庫状況": availability,
                "詳細URL": detail_url
            })

        next_btn = soup.find("li", class_="next")
        if next_btn:
            next_url = urljoin(current_page, next_btn.a["href"])
            current_page = next_url
        else:
            break

    return books


def save_to_csv(category_name, books):
    os.makedirs("book_csv", exist_ok=True)
    filename = f"book_csv/{category_name.replace(' ', '_')}.csv"
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["タイトル", "価格", "在庫状況", "詳細URL"])
        writer.writeheader()
        writer.writerows(books)
    print(f"→ 保存完了：{filename}（{len(books)}冊）")


def main():
    categories = get_categories()
    for category in categories:
        books = scrape_category(category)
        save_to_csv(category["name"], books)


if __name__ == "__main__":
    main()
