import selenium.common.exceptions
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Firefox(executable_path="../data_handling/geckodriver.exe")


class ContUpdatedPrice:
    def __init__(self):
        driver.get('https://www.bseindia.com/')

    # def resetVariables(self):
    #     self.suggestions = None
    #     self.unfiltered_list = []
    #     self.suggestions_symbol_list = []
    #     self.suggestions_company_list = []

    def setup(self, company_name: str):
        self.suggestions_empty = False
        self.left_out_suggestions_empty = False
        self.suggestions = None
        self.left_out_suggestions = None
        self.unfiltered_list = []
        self.suggestions_symbol_list = []
        self.suggestions_company_list = []
        search_box = driver.find_element_by_xpath("//input[@id='getquotesearch']")
        search_box.send_keys(f'{company_name}')
        time.sleep(5)
        try:
            self.suggestions = driver.find_elements_by_xpath("//li[@class='quotemenu']")
        except selenium.common.exceptions.NoSuchElementException:
            print("No Matches 1")
            self.suggestions_empty = True
        try:
            self.left_out_suggestions = driver.find_elements_by_xpath("/ html / body / div / div[4] / div / div[3] / "
                                                                     "div / section / form / div[1] / ul / li[1]")

        except selenium.common.exceptions.NoSuchElementException:
            print("No Matches 2")
            self.left_out_suggestions_empty = True

        if not self.suggestions_empty:
            for value in self.suggestions:
                if company_name.upper() in value.text:
                    self.unfiltered_list.append(value.text)

        if not self.left_out_suggestions_empty:
            for value in self.left_out_suggestions:
                if company_name.upper() in value.text:
                    self.unfiltered_list.insert(0, value.text)

        if self.suggestions_empty and self.left_out_suggestions_empty:
            self.unfiltered_list.append('')

        for value in self.unfiltered_list:
            split = value.split("\n")
            self.suggestions_company_list.append(split[0])
            self.suggestions_symbol_list.append(split[1])

    def getSuggestions(self):
        return [self.suggestions_company_list, self.suggestions_symbol_list]

    def selectAndClickSuggestions(self, index: int):
        # print(self.suggestions_company_list)
        to_search = self.suggestions_company_list[index]
        # search_box = driver.find_element_by_xpath("//input[@id='getquotesearch']")
        # search_box.clear()
        # search_box.send_keys(f"{to_search}")
        # click = driver.find_element_by_xpath(f"//*[contains(text(), '{to_search}')]")
        # click.click()
        link = "https://www.bseindia.com/stock-share-price/{0}/{1}/{2}"
        unclean = self.suggestions_symbol_list[index].split(" ")
        clean = [v for v in unclean if v != ""]
        required_link = link.format(f"{to_search.replace(' ', '-').lower()}", f"{clean[0].lower()}", f"{clean[2]}")
        driver.get(required_link)

    def getUpdatedPrice(self):
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//strong[@id='idcrval']"))
            )
        except selenium.common.exceptions.TimeoutException:
            print("timeout")

        price = driver.find_element_by_xpath("//strong[@id='idcrval']")
        return float(price.text)