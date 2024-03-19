from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import textwrap
from IPython.display import Markdown
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from gemini_api_key import get_api_key

import csv

import google.generativeai as genai

GOOGLE_API_KEY = get_api_key()
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')


def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))



# Instantiate Chrome WebDriver with options
options = webdriver.ChromeOptions()
options.add_experimental_option(
    "prefs", {
        # Block image loading
        "profile.managed_default_content_settings.images": 2,
        # Block CSS rendering
        "profile.managed_default_content_settings.stylesheet": 2,
        # Disable browser notifications
        "profile.managed_default_content_settings.notifications": 2,
        # Disable browser plugins
        "profile.managed_default_content_settings.plugins": 2,
    }

)
driver = webdriver.Chrome(
    options=options
)


# driver = webdriver.Chrome()
driver.implicitly_wait(10)
driver.get(
    "https://www.indeed.com/jobs?q=computer+science&l=us&start=650&vjk=964c2e7559651475")

data_list = []


def scrap_website(numeber_of_pages):
    with open('output12.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Title", "Location", "Company", "skills", "wage", "qualifications", "work_place", "job_type"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(numeber_of_pages):
            # Find the job results container using By.ID
            job_results_container = driver.find_element(By.ID, 'mosaic-jobResults')

            # Find all elements with the specified class using By.CSS_SELECTOR
            selected_elements = job_results_container.find_elements(By.CSS_SELECTOR,
                                                                    '.resultContent.css-1qwrrf0.eu4oa1w0')

            # Initialize a list to store the data

            for element in selected_elements:
                title_element = element.find_element(By.TAG_NAME, 'h2')
                Title = title_element.text
                location = element.find_element(By.CSS_SELECTOR, 'div.css-1p0sjhy.eu4oa1w0').text
                company = element.find_element(By.CSS_SELECTOR, 'span.css-92r8pb').text
                try:
                    wage_element = element.find_element(By.CSS_SELECTOR,
                                                        '.metadata.salary-snippet-container.css-5zy3wz.eu4oa1w0')
                    wage = wage_element.text.strip()

                except NoSuchElementException:
                    wage = "N/A"
                link = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.LINK_TEXT, Title))
                )
                driver.execute_script("arguments[0].scrollIntoView();", link)
                link.click()

                job_info_container = driver.find_element(By.CLASS_NAME,
                                                         'fastviewjob.jobsearch-ViewJobLayout--embedded.css-1lo7kga.eu4oa1w0')
                job_info = job_info_container.find_element(By.ID, "jobDescriptionText").text

                response = model.generate_content(
                    f"Extract only the programming languages needed based on job description, only return csv values, if information is not found return N/A {job_info}")
                skills = response.text

                response = model.generate_content(
                    f"Extract only the College Major needed for the job based on the job description, only return csv values, if information is not found return N/A {job_info}")
                qualifications = response.text

                response = model.generate_content(
                    f"Extract only whether the Job is In-person,Remote or Hybrid  based on the job description, only return csv values, if information is not found return N/A {job_info}")
                work_place = response.text

                response = model.generate_content(
                    f"Extract only which of these category the job falls into : full-time,Part-time,Internship  based on the job description, only return csv values, if information is not found return N/A {job_info}")
                job_type = response.text

                data = {"Title": Title, "Location": location, "Company": company, "skills": skills, "wage": wage,
                        "qualifications": qualifications, "work_place": work_place, "job_type": job_type}
                writer.writerow(data)

            next_button = driver.find_element(By.CSS_SELECTOR,
                                              'a[data-testid="pagination-page-next"]')  # find next button
            driver.execute_script("arguments[0].scrollIntoView();", next_button)  # avoid interception by cookie button

            next_button.click()  # click on next button

    # Append the title to the data list


scrap_website(25)

driver.quit()
