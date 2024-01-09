from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import os

def is_html_file(filename):
    """Prüft, ob eine Datei eine HTML-Datei ist."""
    _, ext = os.path.splitext(filename)
    return ext in ['.html', '.htm']

def parse_html_file(file_path):
    """Liest und parst eine HTML-Datei, gibt die BeautifulSoup-Instanz zurück."""
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    print(f"Successfully read: {file_path}")
    return BeautifulSoup(html_content, 'html.parser')

def extract_problem_links(soup):
    """Extrahiert Problem-Links aus der BeautifulSoup-Instanz."""
    hrefs = set()
    divs = soup.find_all('div', class_="inline-block min-w-full")
    for div in divs:
        links = div.find_all('a', href=True)
        for link in links:
            href = str(link['href'])
            if href.startswith('https://leetcode.com/problems/') and not href.endswith('/solution'):
                hrefs.add(href)
    return hrefs

def fetch_problem_links(directory="html_files"):
    """Sammelt alle Problem-Links aus HTML-Dateien im angegebenen Verzeichnis."""
    problem_links = set()
    for filename in os.listdir(directory):
        if is_html_file(filename):
            file_path = os.path.join(directory, filename)
            soup = parse_html_file(file_path)
            hrefs = extract_problem_links(soup)
            problem_links.update(hrefs)
    return problem_links

def init_driver():
    """Initialisieren des Chrome WebDriver"""
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def extract_data_from_page(driver, url):
    """Funktion, um Daten aus den angegebenen Klassen zu extrahieren"""
    driver.get(url)
    time.sleep(2)  # Wartezeit für das Laden der Seite

    try:
        premium_message_xpath = '//*[@id="qd-content"]/div[4]/div/div[2]'
        premium_message = driver.execute_script(
            "return document.evaluate(arguments[0], document, null, XPathResult.STRING_TYPE, null).stringValue;",
            premium_message_xpath)

    except Exception as e:
        premium_message = ""

    if premium_message:
        return True, "", "", "", "", "", "", "", ""

    try:
        # Extrahieren des Inhalts und prüfen ob Inhalt ein Bild enthält
        content_element = driver.find_element(By.CLASS_NAME, "px-5.pt-4")
        content = content_element.text

        if content_element.find_elements(By.TAG_NAME, "img"):
            content_image = True
            return "", "", "", "", content_image, "", "", "", ""
        else:
            content_image = False

    except Exception as e:
        content = ""
        content_image = False

    try:
        # Extrahiere die difficulty des Problems
        difficulty_xpath = '//*[@id="qd-content"]/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div[1]'
        difficulty = driver.execute_script(
            "return document.evaluate(arguments[0], document, null, XPathResult.STRING_TYPE, null).stringValue;",
            difficulty_xpath)

    except Exception as e:
        difficulty = ""

    try:
        # Extrahiere die ID des Problems
        id_xpath = "//*[@id='qd-content']//a/text()[1]"
        problem_id = driver.execute_script(
            "return document.evaluate(arguments[0], document, null, XPathResult.STRING_TYPE, null).stringValue;",
            id_xpath)

        # Extrahiere den Namen des Problems
        name_xpath = "//*[@id='qd-content']//a/text()[4]"
        problem_name = driver.execute_script(
            "return document.evaluate(arguments[0], document, null, XPathResult.STRING_TYPE, null).stringValue;",
            name_xpath)

        title = problem_id + " " + problem_name
    except Exception as e:
        title = ""

    def extract_code_for_language(language):
        """Hilfsfunktion, um den Code für eine bestimmte Sprache zu extrahieren"""

        try:
            # Wählen Sie den Button aus, dessen ID mit "headlessui-listbox-button-" beginnt
            button_css_selector = "[id^='headlessui-listbox-button-']"
            button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, button_css_selector))
            )
            button.click()

            # Warte auf das Laden der Liste und wähle die Sprache aus
            language_option_xpath = f"//div[contains(@class, 'whitespace-nowrap') and text()='{language}']"
            language_option = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, language_option_xpath))
            )
            language_option.click()

            time.sleep(2)

            # Extrahiere den Text aus der Klasse 'view-lines monaco-mouse-cursor-text'
            code_text_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, "view-lines.monaco-mouse-cursor-text"))
            )
            return code_text_element.text

        except Exception as e:
            return ""

    # Extrahiere den Code für die verschiedenen Sprachen
    javascript_code_text = extract_code_for_language("JavaScript")
    java_code_text = extract_code_for_language("Java")
    erlang_code_text = extract_code_for_language("Erlang")
    elixir_code_text = extract_code_for_language("Elixir")

    return premium_message, title, content, difficulty, content_image, javascript_code_text, java_code_text, erlang_code_text, elixir_code_text

def scrape_and_save(problem_links, save_directory="scraped_data"):
    """Hauptfunktion, um die Webseiten zu durchlaufen und die Daten zu extrahieren"""

    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    driver = init_driver()

    for url in problem_links:
        difficulty_levels = ['Easy', 'Medium', 'Hard']
        file_name = url.split('/')[-1]
        if any(os.path.exists(f"./scraped_data/{level}/{file_name}") for level in difficulty_levels):
            print("Data already extracted")
            continue

        premium_message, title, content, difficulty, content_image, javascript_code_text, java_code_text, erlang_code_text, elixir_code_text = extract_data_from_page(driver, url)

        if premium_message:
            print("Premium problem. SKIP")
            continue

        if content_image:
            print("Image in content. SKIP")
            continue

        if any(text == "" for text in [javascript_code_text, java_code_text, erlang_code_text, elixir_code_text]):
            print("Not all languages available. SKIP")
            continue


        file_path_of_difficulty = os.path.join(save_directory, difficulty)

        if not os.path.exists(file_path_of_difficulty):
            os.makedirs(file_path_of_difficulty)

        file_path_of_name = os.path.join(file_path_of_difficulty, file_name)

        if not os.path.exists(file_path_of_name):
            os.makedirs(file_path_of_name)

        file_path_of_content = os.path.join(file_path_of_name, f"{title}.txt")

        with open(file_path_of_content, 'w', encoding='utf-8') as file:
            file.write(title + "\n\n" + content)
            print(f"Data saved: {file_path_of_content}")

        file_path_of_javascript_code_text = os.path.join(file_path_of_name, "javascript_code_text.txt")

        with open(file_path_of_javascript_code_text, 'w', encoding='utf-8') as file:
            file.write(f"Solve the following problem in JavaScript. Use the template as a starting point\n\nTemplate:\n\n{javascript_code_text}\n\nProblem:\n\n{content}")
            print(f"Data saved: {file_path_of_javascript_code_text}")

        file_path_of_java_code_text = os.path.join(file_path_of_name, "java_code_text.txt")

        with open(file_path_of_java_code_text, 'w', encoding='utf-8') as file:
            file.write(f"Solve the following problem in Java. Use the template as a starting point\n\nTemplate:\n\n{java_code_text}\n\nProblem:\n\n{content}")
            print(f"Data saved: {file_path_of_java_code_text}")

        file_path_of_erlang_code_text = os.path.join(file_path_of_name, "erlang_code_text.txt")

        with open(file_path_of_erlang_code_text, 'w', encoding='utf-8') as file:
            file.write(f"Solve the following problem in Erlang. Use the template as a starting point\n\nTemplate:\n\n{erlang_code_text}\n\nProblem:\n\n{content}")
            print(f"Data saved: {file_path_of_erlang_code_text}")

        file_path_of_elixir_code_text = os.path.join(file_path_of_name, "elixir_code_text.txt")

        with open(file_path_of_elixir_code_text, 'w', encoding='utf-8') as file:
            file.write(f"Solve the following problem in Elixir. Use the template as a starting point\n\nTemplate:\n\n{elixir_code_text}\n\nProblem:\n\n{content}")
            print(f"Data saved: {file_path_of_elixir_code_text}")

    driver.quit()

if __name__ == '__main__':
    problem_links = fetch_problem_links()
    scrape_and_save(problem_links)
