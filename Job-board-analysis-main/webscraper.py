from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv


# fist page current

def extraction(soup):  # control what information is extracted here
    data_list = []

    job_results_container = soup.find('div', {'id': 'mosaic-jobResults'})
    selected_elements = job_results_container.select('.resultContent.css-1qwrrf0.eu4oa1w0')  # creates an array

    for element in selected_elements:
        Title = element.find('h2')
        #
        # Location = element.find('div', class_="css-1p0sjhy eu4oa1w0")
        # Company = soup.find('span', class_='css-92r8pb')  # identify by test ID
        #
        # Skills = ""
        # wage_element = element.find('div', class_="metadata salary-snippet-container css-5zy3wz eu4oa1w0")
        # wage = wage_element.text.strip() if wage_element else "N/A"
        link = driver.find_element(By.LINK_TEXT, Title.text)
        link.click()
        time.sleep(2)
        Title = soup.find('h2', class_='jobsearch-JobInfoHeader-title')
        Company = soup.find('a', class_='css-775knl e19afand0')
        Location = soup.find('div', class_='css-1ikmi61 eu4oa1w0')
        wage = soup.find('span', class_='css-19j1a75 eu4oa1w0')
        des = soup.find('div', {'id': 'jobDescriptionText'})
        Skills = ""
        print(Title.text + "\n" + des.text)
        print("\n - - - - - - - - - - - ")
        src = driver.page_source  # update html
        soup = BeautifulSoup(src, 'html.parser')
        # print(Company.text + "\n")
        # print(des.text.strip())

        data = {"Title": Title.text, "Location": Location.text, "Company": Company.text, "Skills": Skills, "wage": wage}
        data_list.append(data)
    return data_list


def loop_thru(n):  #
    with open('output5.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Title", "Location", "Company", "Skills", "wage"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for x in range(n):

            next_button = driver.find_element(By.CSS_SELECTOR,
                                              'a[data-testid="pagination-page-next"]')  # find next button
            driver.execute_script("arguments[0].scrollIntoView();", next_button)  # avoid interception by cookie button
            next_button.click()  # click on next button
            page_source = driver.page_source  # access the webiste using selenium
            soup = BeautifulSoup(page_source, 'html.parser')
            time.sleep(5)

            data_list = extraction(soup)
            for entry in data_list:  # write down all the entries in that page
                writer.writerow(entry)


driver = webdriver.Chrome()
driver.get("https://www.indeed.com/jobs?q=computer+science+intern&l=us&vjk=e316f20d407cdb99")
page_source = driver.page_source  # access the webiste using selenium
soup = BeautifulSoup(page_source, 'html.parser')  # use bs4 since js has been rendered by selenium
extraction(soup)
loop_thru(1)  # loop thru links of current page

driver.close()
