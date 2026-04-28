from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def setup_driver():
    """Setup Chrome WebDriver with WebDriver Manager."""
    print("Setting up Chrome WebDriver...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("WebDriver setup complete.")
    return driver

def login(driver, email, password):
    """Login to LinkedIn."""
    print("Navigating to LinkedIn login page...")
    driver.get('https://www.linkedin.com/login')
    print("Waiting for login form...")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'username')))
    print("Entering credentials...")
    driver.find_element(By.ID, 'username').send_keys(email)
    driver.find_element(By.ID, 'password').send_keys(password)
    print("Submitting login...")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    # Wait for successful login
    print("Waiting for login to complete...")
    WebDriverWait(driver, 10).until(EC.url_contains('feed'))
    print("Login successful.")

def search_jobs(driver, keywords):
    """Search for jobs on LinkedIn."""
    print(f"Searching for jobs with keywords: {keywords}")
    driver.get('https://www.linkedin.com/jobs/')
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search jobs']"))
    )
    search_box.send_keys(keywords)
    search_box.submit()
    # Wait for results to load
    print("Loading job results...")
    time.sleep(5)
    # Parse the page
    print("Parsing job listings...")
    soup = BeautifulSoup(driver.page_source, 'lxml')
    jobs = soup.find_all('div', class_='job-card-container')
    job_data = []
    for job in jobs:
        title_elem = job.find('h3', class_='job-card-list__title')
        company_elem = job.find('h4', class_='job-card-container__company-name')
        location_elem = job.find('span', class_='job-card-container__metadata-item')
        title = title_elem.text.strip() if title_elem else 'N/A'
        company = company_elem.text.strip() if company_elem else 'N/A'
        location = location_elem.text.strip() if location_elem else 'N/A'
        job_data.append({'Title': title, 'Company': company, 'Location': location})
    df = pd.DataFrame(job_data)
    df.to_csv('jobs.csv', index=False)
    print(f"Scraped {len(job_data)} jobs and saved to jobs.csv")

if __name__ == '__main__':
    email = input('Enter your LinkedIn email: ')
    password = input('Enter your LinkedIn password: ')
    keywords = input('Enter job keywords: ')
    driver = setup_driver()
    try:
        login(driver, email, password)
        search_jobs(driver, keywords)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()