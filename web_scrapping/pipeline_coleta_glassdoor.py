import csv
import json
import os
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def find_key_recursive(dictionary, target_key):
    for key, value in dictionary.items():
        if key == target_key:
            return value
        elif isinstance(value, dict):
            result = find_key_recursive(value, target_key)
            if result is not None:
                return result
    return None

def escrever_csv(linha):
    file_exists = os.path.isfile('dados.csv')

    with open('glassdoor.csv', 'a', newline='') as file:
        fieldnames = list(linha.keys())
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(linha)


cookie = {"name": "at", "value": "lZSwvBfP1zAnSADH5mRoQAAQRMMQ9ttnOw5znTxmYP5mbNImuimeItwVjr9jLMIUR93mjQgt_7hQyyqnPHJ8mL_Ir587qJOB3uiQS61elbrxzdwQW6WiO5fj3NhY6wYjsN3ZCfQKlX6-x_Bw-p9EuO0NlZChgi1xmcXMqDPQzW-eUaM54G0H49ch3gC-jkfdCG-HU4Kx-Ng_pDPbFytdVn13pCnVI2L_5cH1PT0Z9vMfDEBbqf2qTKpzWrkwXPAqPxGekUBMwCjix5ZzJ--HTRBxXpTduCXdrk4phP__7qG0xt2GWfogVkP5xL1KOQ3GACtSihN4uEkZ0bJL9EUfAoX0YiaS15cAXw7NfHa8t7O5ygEVlyrzPBc9UlNdVDVuTcv-wkStwPg_Ldxh_Fq1sXb6ruDcccr1NqKWDJU1ZMT9pAS6KbT0lKnlf9q8p4-5buQqOWLwkosWbBXEAikUyXdSGV0cNOAXsiWJXiUQIReF6AoILQ7O3XZy0Em2i1cAmLVtTaBTut6SXGcPH8XyXUAGRID0cauPmddtnY5d7tF9rVm6er_vKiF8ZPvBg2i9xQza8tlbgtG8dEuq62GudrGFySpLTgxGIRkD-aHpAyq9Ca-hDoezI89sV5rp8AgMnFgY-3KX64mbNmoUc2LmGUg_qBubzoqvgRcPqt0EMnj_j7x5c8gkbYpdN-lFzCzZimScu1cXUkgCcvjbIDGbdO79x5unwk_SWEiE2iLhyhxrLgMZ-0eYeo3gcWtTZXJvUHrp4_ofHlet2inVMYSt2tYI9I3VYgFe1JQxpQkkmRr8pb8Cm7E2IJeIe6mmRfAfVaEoS5A5jC1FFpEkI8HQnTfwF6nd2_rhMjBoEIk_DiDJt0Kdc-Yl60qh"}


my_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={my_agent}")
options.add_argument("--lang=pt-BR")

service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(options=options, service=service)
driver.get('https://www.glassdoor.com.br/Vaga/index.htm')

driver.add_cookie(cookie)

driver.refresh()

wait = WebDriverWait(driver, 20)

barra_pesquisa = driver.find_element(
    'xpath', '//input[@id="searchBar-jobTitle"]')

barra_pesquisa.send_keys('Cientista de Dados')
barra_pesquisa.send_keys(Keys.ENTER)

sleep(3)

qnt_vagas = driver.find_element(
    'xpath',
    '//h1[@data-test="search-title"]'
).get_attribute('innerHTML').split()[0]

while True:
    sleep(1)

    try:
        load_button = wait.until(
            EC.presence_of_element_located(
                (By.XPATH,
                 '//button[@data-test="load-more"]')
            )
        )
        load_button.click()

    except TimeoutException:
        continue

    try:
        wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 'button[data-test="load-more"][data-loading="false"]')
            )
        )
    except TimeoutException:
        continue

    job_urls = driver.find_elements(
        'xpath',
        './/a[contains(@id, "job-title")]'
    )

    if len(job_urls) >= int(qnt_vagas):
        break

for url in job_urls:
    link = url.get_attribute('href')

    while True:

        driver.execute_script(f"window.open('{link}', '_blank');")

        try:
            wait.until(
                lambda driver: driver.execute_script(
                    "return document.readyState") == "complete"
            )

            driver.switch_to.window(driver.window_handles[1])

            wait.until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     '//script[contains(text(), "props")]')
                )
            )
            break
        except TimeoutException:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            continue

    script_tag = driver.find_element(
        'xpath',
        '//script[contains(text(), "props")]'
    ).get_attribute('innerHTML')

    data = json.loads(script_tag)

    job_json = find_key_recursive(data, 'job')
    header_json = find_key_recursive(data, 'header')

    dados = {
        'site_da_vaga': 'Glassdoor',
        'link': link,
        'data_publicacao': datetime.strptime(
            job_json['discoverDate'], '%Y-%m-%dT%H:%M:%S').date(),
        'data_coleta': datetime.now().date(),
        'titulo_da_vaga': header_json['jobTitleText'],
        'local': header_json['locationName'],
        'modalidade': '',
        'contrato': '',
        'acessibilidade': '',
        'nome_empresa': header_json['employerNameFromSearch'],
        'codigo_vaga': job_json['listingId'],
        'descricao': job_json['description']
    }

    escrever_csv(dados)

    driver.close()

    driver.switch_to.window(driver.window_handles[0])

sleep(10)
