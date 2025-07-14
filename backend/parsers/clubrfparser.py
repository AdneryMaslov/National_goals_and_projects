import requests
from bs4 import BeautifulSoup
import time

# Базовый URL сайта
BASE_URL = 'http://club-rf.ru'
# URL страницы с новостями
NEWS_URL = f'{BASE_URL}/news'

# Заголовки для HTTP-запроса, чтобы имитировать браузер
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_news_list():
    """
    Получает список новостей с главной новостной страницы.
    Возвращает список словарей, где каждый словарь содержит заголовок, дату и ссылку на новость.
    """
    try:
        print(f"Загружаю страницу со списком новостей: {NEWS_URL}")
        response = requests.get(NEWS_URL, headers=HEADERS, verify=False)
        response.raise_for_status()  # Проверка на ошибки HTTP (например, 404, 500)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке страницы: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    news_items = soup.find_all('div', class_='news-item')
    
    news_list = []
    if not news_items:
        print("Не удалось найти новостные блоки на странице.")
        return []

    for item in news_items:
        title_tag = item.find('a', class_='news-item__title')
        date_tag = item.find('span', class_='news-item__date')

        if title_tag and date_tag:
            title = title_tag.get_text(strip=True)
            link = BASE_URL + title_tag['href']
            date = date_tag.get_text(strip=True)
            
            news_list.append({
                'title': title,
                'date': date,
                'link': link
            })
            
    return news_list

def get_news_content(news_url):
    """
    Получает полный текст новости по ее URL.
    Возвращает строку с текстом статьи.
    """
    try:
        # Небольшая задержка перед каждым запросом, чтобы не перегружать сервер
        time.sleep(1) 
        
        print(f"  Парсинг статьи: {news_url}")
        response = requests.get(news_url, headers=HEADERS, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  Не удалось загрузить статью по ссылке {news_url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    article_text_div = soup.find('div', class_='article__text')
    
    if article_text_div:
        # Собираем все текстовые блоки из <p> внутри основного контейнера
        paragraphs = article_text_div.find_all('p')
        full_text = '\n'.join([p.get_text(strip=True) for p in paragraphs])
        return full_text
    else:
        print(f"  Не удалось найти текст статьи на странице: {news_url}")
        return None

def main():
    """
    Основная функция для запуска парсера.
    """
    news_list = get_news_list()
    
    if not news_list:
        print("Новостей для парсинга не найдено. Программа завершена.")
        return
        
    all_news_data = []

    # Для примера ограничимся первыми 5 новостями
    for news in news_list[:5]:
        content = get_news_content(news['link'])
        if content:
            all_news_data.append({
                'title': news['title'],
                'date': news['date'],
                'link': news['link'],
                'content': content
            })

    # Вывод результата
    print("\n--- Результаты парсинга ---\n")
    for i, data in enumerate(all_news_data, 1):
        print(f"Новость #{i}")
        print(f"Заголовок: {data['title']}")
        print(f"Дата: {data['date']}")
        print(f"Ссылка: {data['link']}")
        # Выводим только первые 200 символов для краткости
        print(f"Текст: {data['content'][:200]}...") 
        print("-" * 30 + "\n")


if __name__ == '__main__':
    main()