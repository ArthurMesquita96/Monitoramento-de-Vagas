import csv
import os
from abc import ABCMeta, abstractmethod

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from user_agent import generate_user_agent
from webdriver_manager.chrome import ChromeDriverManager


class JobScraper(metaclass=ABCMeta):

    JOB_TITLES = ['Analista de Dados', 'Cientista de Dados',
                  'Engenheiro de Dados']

    def __init__(self, site_name) -> None:
        self.site_name: str = site_name

    def _init_selenium(self, headless=False):

        my_agent = generate_user_agent()

        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={my_agent}")
        options.add_argument("--lang=pt-BR")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--incognito")
        options.add_argument('--disable-blink-features=AutomationControlled')

        if headless:
            options.add_argument('--headless')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(options=options, service=service)

        return driver

    def save_csv(self, linha):

        directory = os.path.join('data', 'data_raw')
        filepath = os.path.join(
            directory, f'vagas_{self.site_name.lower()}_raw.csv')
        file_exists = os.path.isfile(filepath)

        with open(filepath, 'a', newline='') as file:
            fieldnames = list(linha.keys())
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(linha)

    @abstractmethod
    def scrape_jobs(self):
        pass

    @abstractmethod
    def get_links(self):
        pass
