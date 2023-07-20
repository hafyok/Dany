import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver


def get_data(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    projects_data_list = []
    current_page = 1  # Текущая страница поиска

    while True:
        # req = requests.get(url + f"&page={current_page}", headers)
        # src = req.text

        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get(url + f"&page={current_page}")
        pageSource = driver.page_source
        fileToWrite = open("project.html", "w", encoding="utf-8")
        fileToWrite.write(pageSource)
        fileToWrite.close()
        fileToRead = open("project.html", "r", encoding="utf-8")
        fileToRead.close()
        driver.quit()

        # Читаем содержимое файла "project.html"
        with open("project.html", encoding="utf-8") as file:
            src = file.read()

        soup1 = BeautifulSoup(src, "html.parser")
        articles = soup1.find_all("article", class_="product-card product-card product")
        project_urls = []

        for article in articles:
            project_url = "https://www.chitai-gorod.ru" + article.find("a").get("href")
            project_urls.append(project_url)

        for project_url in project_urls:
            req = requests.get(project_url, headers)
            src = req.text

            soup = BeautifulSoup(src, "html.parser")

            try:
                project_name = soup.find("div", class_="product-detail-title").find("h1").\
                    get_text(strip=True)
            except Exception:
                project_name = "No info"

            try:
                project_year = soup.find("div", class_="product-detail-characteristics"). \
                    find("span", itemprop="datePublished").get_text(strip=True)
            except Exception:
                project_year = "No available info"

            try:
                project_pages = soup.find("div", class_="product-detail-characteristics"). \
                    find("span", itemprop="numberOfPages").get_text(strip=True)
            except Exception:
                project_pages = "No available info"

            try:
                project_publish = soup.find("div", class_="product-detail-characteristics"). \
                    find("a", itemprop="publisher").get_text(strip=True)
            except Exception:
                project_publish = "No available info"

            try:
                project_age = soup.find("div", class_="product-detail-characteristics"). \
                    find("span", itemprop="typicalAgeRange").get_text(strip=True)
            except Exception:
                project_age = "No available info"

            projects_data_list.append(
                {
                    "Имя книги": project_name,
                    "Год издания": project_year,
                    "Количество страниц": project_pages,
                    "Издатель": project_publish,
                    "Возрастные ограничения": project_age
                }
            )

        # Проверяем, есть ли еще страницы путем проверки наличия элементов пагинации
        try:
            pagination = soup1.find("div", class_="pagination__button pagination__button--icon").find("svg", alt=">")
        except Exception:
            if not pagination:
                break  # Если элементов пагинации нет, выходим из цикла

        current_page += 1  # Увеличиваем номер текущей страницы

    return projects_data_list


def create_table(list):
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.options.display.width = None

    df = pd.DataFrame(list)
    df.columns = ['Имя книги', 'Год издания', 'Количество страниц', 'Издатель', 'Возрастные ограничения']
    df.to_csv("books.csv", encoding="utf-8-sig", sep=';', index=False)

    print(df)


def get_word():
    word = input("Введите поисковое слово: ")
    return word


# Вызываем функции для получения данных
word = get_word()
book_list = get_data("https://www.chitai-gorod.ru/search?phrase=" + word)
create_table(book_list)
