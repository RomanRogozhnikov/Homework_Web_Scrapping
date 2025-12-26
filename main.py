import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import time
import os
import sys

#Ключевые слова:
KEYWORDS = ['дизайн', 'фото', 'web', 'python']

# URL статей
BASE_URL = 'https://habr.com'
ARTICLES_URL = urljoin(BASE_URL, '/ru/articles/')


def setup_browser():
    #Настройка браузера
    try:
        #Полный путь к msedgedriver.exe
        EDGE_DRIVER_PATH = r'C:\path\to\msedgedriver.exe'  # ЗАМЕНИТЕ НА РЕАЛЬНЫЙ ПУТЬ

        if not os.path.exists(EDGE_DRIVER_PATH):
            print("Драйвер Edge не найден по указанному пути!")
            print("Пожалуйста:")
            print(
                "1. Скачайте msedgedriver.exe с https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
            print(f"2. Сохраните его в папку и укажите правильный путь в переменной EDGE_DRIVER_PATH")
            return None

        from selenium import webdriver
        from selenium.webdriver.edge.service import Service as EdgeService
        from selenium.webdriver.edge.options import Options as EdgeOptions

        options = EdgeOptions()
        options.add_argument('--start-maximized')
        service = EdgeService(executable_path=EDGE_DRIVER_PATH)

        return webdriver.Edge(service=service, options=options)

    except Exception as e:
        print(f"Ошибка при настройке браузера: {e}")
        return None


def show_parsing_process():
    #Визуализация в браузере
    print("\nДемонстрация парсинга")

    driver = setup_browser()
    if not driver:
        print("Не удалось запустить браузер. Продолжаю без визуализации.")
        return

    try:
        print("1. Открываю страницу Habr...")
        driver.get(ARTICLES_URL)
        time.sleep(3)

        print("2. Начинаю демонстрацию элементов...")

        articles = driver.find_elements_by_tag_name('article')
        if articles:
            driver.execute_script("arguments[0].style.border='3px solid red'", articles[0])
            print("   - Статьи (красная рамка)")
            time.sleep(2)

        titles = driver.find_elements_by_css_selector('h2')
        if titles:
            driver.execute_script("arguments[0].style.background='yellow'", titles[0])
            print("   - Заголовки (жёлтый фон)")
            time.sleep(2)

        print("\nДемонстрация завершена. Закрываю браузер через 5 секунд...")
        time.sleep(5)

    except Exception as e:
        print(f"Ошибка при демонстрации: {str(e)[:200]}")
    finally:
        driver.quit()


def parse_habr_articles():
    #Парсинг
    try:
        print("\nПарсинг.......")

        #Использование html.parser
        parser = 'html.parser'

        response = requests.get(ARTICLES_URL, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, parser)
        articles = soup.find_all('article')
        found_articles = []

        for article in articles:
            try:
                title_elem = article.find('h2')
                if not title_elem:
                    continue

                preview_elem = article.find('div', class_='article-formatted-body')
                hubs_elems = article.find_all('a', class_='tm-article-snippet__hubs-item-link')

                search_text = ' '.join([
                    title_elem.get_text(),
                    preview_elem.get_text() if preview_elem else '',
                    ' '.join(hub.get_text() for hub in hubs_elems)
                ]).lower()

                if any(keyword.lower() in search_text for keyword in KEYWORDS):
                    title = title_elem.find('span').get_text()
                    relative_link = title_elem.find('a')['href']
                    link = urljoin(BASE_URL, relative_link)

                    time_tag = article.find('time')
                    date = datetime.fromisoformat(time_tag['datetime']).strftime(
                        '%Y-%m-%d') if time_tag and 'datetime' in time_tag.attrs else 'дата недоступна'

                    found_articles.append(f'{date} – {title} – {link}')
            except Exception as e:
                continue

        return found_articles

    except requests.exceptions.RequestException as e:
        print(f'Ошибка при запросе к Habr: {e}')
        return []
    except Exception as e:
        print(f'Произошла ошибка: {e}')
        return []


if __name__ == '__main__':
    # Запуск визуализации
    show_parsing_process()

    #Парсинг
    results = parse_habr_articles()

    #Вывод результатов
    print("\nРезультат парсинга")
    for i, article in enumerate(results, 1):
        print(f"{i}. {article}")