import csv
import json
import os
from datetime import datetime
from random import randint
from time import sleep

import psutil
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (StaleElementReferenceException,
                                        TimeoutException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager, ChromeType


class JobScraper:

    job_titles = ['Cientista de Dados',
                  'Engenheiro de Dados', 'Analista de Dados']

    def __init__(self, job_titles, site_name) -> None:
        self.job_titles: list = job_titles
        self.site_name: str = site_name
        self.driver = self.__iniciar_selenium()

    def __iniciar_selenium(self, headless=False):
        my_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={my_agent}")
        options.add_argument("--lang=pt-BR")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--incognito")
        options.add_argument('--disable-blink-features=AutomationControlled')

        if headless:
            options.add_argument('--headless')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(
            options=options, service=service)

        return driver

    def save_csv(self, linha):

        filename = self.site_name.lower() + '.csv'
        diretorio = '../data/data_raw/'

        filepath = os.path.join(diretorio, filename)
        file_exists = os.path.isfile(filepath)

        with open(filename, 'a', newline='') as file:
            fieldnames = list(linha.keys())
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(linha)

    def scrape_jobs(self):
        pass


class GlassdoorScraper(JobScraper):

    def __init__(self, site_name) -> None:
        super().__init__(site_name, 'Glassdoor')
        self.cookie = {"name": "at", "value": "Vffs0MlCIDEfflQ11OInCvejLSP2LJcus1xBWozC4laeA4Xfzb6pv7qDZ_nwxqGx8vddl85T-AGlsgrFvWOm3fmwDp5hZoRrXCoQlk2Xvune7iwSoRLLsAB3X0SorZbu9v_SHQtJ3TH-8DeJGhIUNDFe7nbcqLIDnERzKYMblmuGV7vjGilr4kCHdQsm_TxJu2t9KW2a10gCKYDmmtefQp3RY5JaWyGuy1rFiAbYDs3OnryED52XCKCW-gcOGwrz1mHg6DWAqo87ZwLESUOWplI6L8WSW-F2-K9Z199grBuAb3MLwFokvYoBjWrS8EwgcF0w_cpo3rX9zifSNrvXyp5aFjLXX6gqwbGx5DCikwD423oWNinJ1GC-pZVni0VNPpcJaAy6aIPehY9E0n1c-Fj64lSudtDotmVv1vc5Y7DYjGyCdq2OI24rwf_8We9hupYU9R_45EN869hsAmc57uAG1OXm_AoRH93wbxMxfZSPa2ZBubcFr6UWeGOWM0JLifZjn5ZPmRqBLvNBhfk0V6H9zBsIB8glha60m73wEIBDnxjBc6ysk0JUj6ngOEA9ULt6vtV1_i9dzm3sw4nDaPlJNE7bFNAWX1o0j76pjHRr4ZzWjr52MnqlqcLE3AkMtsStwFGPOjwOny01p-JwXnR7AfmS3dzPgOBdWiDtt-uIATlpy00nZO6azbxMATcPtLj--nrciT6pfzwIUpcMg45SEgbI4qiQnH9RAgw3BiEgXrXDruDhWAdljwePDGJb7GwHUkYGBcgWIqsxah2tRHafGKoBEDLPMV8__Nknbr-OJ-2ppMnCK1jPuR7r9viJUHVEdyCrwpszdwYDe2dvlsGNtIYbDbSGdVk_LaiZscvWdK0EVyHliqxxPQ"}

    def pesquisa_chave(self, dictionario, chave):
        for key, value in dictionario.items():
            if key == chave:
                return value
            elif isinstance(value, dict):
                result = self.pesquisa_chave(value, chave)
                if result is not None:
                    return result
        return None

    def clean_tags(self, text):

        soup = BeautifulSoup(text, 'html.parser')
        clean_text = soup.get_text()
        return clean_text

    def __get_job_urls(self, xpath):

        job_elements = self.driver.find_elements('xpath', xpath)

        job_urls = dict()

        for element in job_elements:
            href = element.get_attribute('href')
            job_id = href.split('=')[-1]
            if href:
                job_urls[job_id] = href

        return job_urls

    def __verify_json(self) -> bool:

        wait = WebDriverWait(self.driver, 50)

        wait.until(
            EC.presence_of_element_located(
                (By.XPATH,
                 '//script[contains(text(), "props")]')
            )
        )

        script_tag = self.driver.find_element(
            'xpath', '//script[contains(text(), "props")]'
        ).get_attribute('innerHTML')
        data = json.loads(script_tag)
        job_json = self.pesquisa_chave(data, 'job')
        header_json = self.pesquisa_chave(data, 'header')

        if job_json is None or header_json is None:
            return True

        return False

    def __iniciar_selenium(self, headless=False):
        my_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={my_agent}")
        options.add_argument("--lang=pt-BR")
        options.add_argument('--disable-dev-shm-usage')

        if headless:
            options.add_argument('--headless')

        service = Service(
            ChromeDriverManager().install()
        )
        driver = webdriver.Chrome(
            options=options, service=service)

        return driver

    def __create_json(self, dictionary, filepath):

        if os.path.exists(filepath):

            with open(filepath, 'r') as f:
                dados_json = json.load(f)

                for chave in dictionary:
                    if chave not in dados_json:
                        dados_json.update(dictionary)

        else:
            dados_json = dictionary

        with open(filepath, 'w') as f:
            json.dump(dados_json, f, indent=4)

    def __get_links(self):

        for job_title in self.job_titles:

            self.driver = self.__iniciar_selenium(False)

            self.driver.get('https://www.glassdoor.com.br/Vaga/index.htm')
            self.driver.add_cookie(self.cookie)
            self.driver.refresh()

            wait = WebDriverWait(self.driver, 50)

            wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//input[@id="searchBar-jobTitle"]')
                )
            )

            barra_pesquisa = self.driver.find_element(
                'xpath', '//input[@id="searchBar-jobTitle"]')
            barra_pesquisa.send_keys(job_title)
            barra_pesquisa.send_keys(Keys.ENTER)

            sleep(3)

            try:
                close_modal = self.driver.find_element(
                    'xpath', '//span[@class="SVGInline modal_closeIcon"]')

                close_modal.click()
            except StaleElementReferenceException:
                pass

            qnt_vagas = self.driver.find_element(
                'xpath',
                '//h1[@data-test="search-title"]').get_attribute(
                    'innerHTML').split()[0].replace('.', '')

            i = 0

            while True:
                sleep(1)

                try:
                    load_button = wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//button[@data-test="load-more"]')
                        )
                    )
                    load_button.click()

                    wait.until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR,
                             'button[data-test="load-more"][data-loading="false"]')
                        )
                    )
                except TimeoutException:
                    if i == 5:
                        break

                    i += 1
                    continue

                qnt_jobs = len(self.driver.find_elements(
                    'xpath', './/a[contains(@id, "job-title")]'))

                if qnt_jobs >= int(qnt_vagas) or \
                        int(qnt_vagas) - qnt_jobs > 10:
                    filepath = 'data/data_raw/tmp/glassdoor.json'

                    links_json = self.__get_job_urls(
                        './/a[contains(@id, "job-title")]')
                    self.__create_json(links_json, filepath)
                    break

            self.driver.quit()

    def get_json_file(self, filepath):
        with open(filepath, 'r') as file:
            dados_json = json.load(file)

        return dados_json

    def scrape_jobs(self):

        self.__get_links()

        sleep(3)

        job_urls = self.get_json_file(
            'data/data_raw/tmp/glassdoor.json')

        urls_processadas = 0

        for url in job_urls.values():

            if urls_processadas % 25 == 0:

                memory_use = psutil.virtual_memory().used / (1024 * 1024)
                print(f"Uso de memória: {memory_use:.2f} MB")

                if self.driver is not None:
                    self.driver.quit()
                    sleep(3)
                    self.driver = self.__iniciar_selenium(False)
                sleep(3)

            self.driver.get(url)
            sleep(3)

            try:
                i = 0
                while True:

                    if not self.__verify_json():
                        break
                    elif i == 10:
                        self.driver.refresh()
                        sleep(5)

                    i += 1

                if self.__verify_json():
                    self.driver.refresh()
                    
                    wait = WebDriverWait(self.driver, 50)
                    wait.until(
                        lambda driver: driver.execute_script(
                            "return document.readyState") == "complete"
                    )

                script_tag = self.driver.find_element('xpath', '//script[contains(text(), "props")]').get_attribute(
                    'innerHTML')
                data = json.loads(script_tag)
                job_json = self.pesquisa_chave(data, 'job')
                header_json = self.pesquisa_chave(data, 'header')
                map_json = self.pesquisa_chave(data, 'map')
                modalidade = self.driver.find_element(
                    'xpath', '//div[@data-test="location"]').text.lower()

            except (TimeoutException, StaleElementReferenceException):
                self.driver.close()
                continue

            try:
                dados = {
                    'site_da_vaga': self.site_name,
                    'link_site': url,
                    'link_origem': 'www.glassdoor.com.br/Vaga/index.htm'
                    + header_json['applyUrl'],
                    'data_publicacao': datetime.strptime(job_json['discoverDate'], '%Y-%m-%dT%H:%M:%S').date(),
                    'data_expiracao': '',
                    'data_coleta': datetime.now().date(),
                    'posicao': job_title.capitalize(),
                    'senioridade': '',
                    'titulo_vaga': header_json['jobTitleText'],
                    'nome_empresa': header_json['employerNameFromSearch'],
                    'cidade': map_json['cityName'],
                    'estado': map_json['stateName'],
                    'modalidade': modalidade.capitalize()
                    if 'remoto' in modalidade else '',
                    'contrato': '',
                    'regime': '',
                    'pcd': '',
                    'codigo_vaga': job_json['listingId'],
                    'descricao': self.clean_tags(job_json['description']),
                    'skills': header_json['indeedJobAttribute']['skillsLabel']
                }
            except TypeError:
                continue

            self.save_csv(dados)

            sleep(randint(1, 20))

            urls_processadas += 1

        sleep(10)
        self.driver.quit()


def main():
    job_titles = ['Cientista de Dados', 'Analista de Dados',
                  'Engenheiro de Dados']

    scraper = GlassdoorScraper(job_titles)
    scraper.scrape_jobs()


if __name__ == '__main__':
    main()
