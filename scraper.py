from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class ScraperResult:
    def __init__(self, result, grade, final_gpa):
        self.class_names = result
        self.grade = grade
        self.final_gpa = final_gpa
      
def scrape(username, password):
  email = username
  password = password

  def GPACalc(ggrade, gweight):
    gvalue = {
      'A+': 4.0,
      'A': 4.0,
      'A-': 3.7,
      'B+': 3.3,
      'B': 3.0,
      'B-': 2.7,
      'C+': 2.3,
      'C': 2.0,
      'C-': 1.7,
      'D+': 1.3,
      'D': 1.0,
      'E': 0.0
    }
    total = sum(gweight)
    weight_grade = sum(gvalue[grade[0]] * credit
                       for grade, credit in zip(ggrade, gweight))
    gpa = weight_grade / total
    return gpa

  class Browser:
    browser = None
    service = None

    def __init__(self) -> None:
      self.service = Service()
      options = webdriver.ChromeOptions()
      options.add_argument("--headless=new")  
      # Run in headless mode, without opening a browser window
      #options.add_argument('--window-size=1920,1080')
      options.add_argument('--disable-dev-shm-usage')
      #options.add_argument("--start-maximized")
      options.add_argument('--no-sandbox')
      self.browser = webdriver.Chrome(service=self.service, options=options)
      #Add options = options

    def open_page(self, url: str):
      self.browser.get(url)

    def close_browser(self):
      self.browser.close()

    def add_input(self, by: By, value: str, text: str):
      field = self.browser.find_element(by=by, value=value)
      field.send_keys(text)
      time.sleep(1)

    def click_button(self, by: By, value: str):
      button = self.browser.find_element(by=by, value=value)
      button.click()
      time.sleep(1)

    def enter(self, by: By, value : str):
      enter = self.browser.find_element(by=by, value=value)
      enter.send_keys(Keys.ENTER)
      
    def login(self, username: str, password: str):
      self.add_input(by=By.NAME, value="username", text=username)
      self.add_input(by=By.NAME, value="password", text=password)

      self.click_button(by=By.XPATH,
                        value="//button[contains(text(),'Log in')]")
      self.click_button(by=By.XPATH, value="//a[contains(text(), 'Classes')]")

    def login2(self, link: str):
      self.add_input(by = By.ID, value = "input", text=link)
      self.enter(by=By.NAME, value="u")
      time.sleep(1)


    def get_page_source(self):
      return self.browser.page_source

    def go_to_split(self):
      self.click_button(by=By.CSS_SELECTOR, value="a.no-warn")
      time.sleep(1)

      page_source = self.get_page_source()
      soup = BeautifulSoup(page_source, 'html.parser')

      weight_elements = soup.findAll('span', class_='credit-hours charcoal')
      weight = [element.text for element in weight_elements]
      weighted = []
      for weight_count in weight:
        inner_list = [
          float(item) for item in weight_count.split(":")[-1].split()
        ]
        weighted += inner_list
      return weighted

  #Start of scraping
  try:
  
    browser = Browser()
    #Enter web proxy
    browser.open_page("https://proxy.web.id")
    #Go to Alma
    browser.login2(
      link=
      "https://cbcs.getalma.com/home/switch-school-year?id=611c8bde78cd730d85457d71"
    )
    #Login
    browser.login(username=email, password=password)
    time.sleep(2)
    page_source = browser.get_page_source()
    soup = BeautifulSoup(page_source, 'html.parser')
  
    ##Class Names only
    class_names = []
    class_elements = soup.find_all('th', class_='name')
    for class_element in class_elements:
      class_name = class_element.find('a',
                                      attrs={'data-track': 'Class Home Page'})
      if class_name:
        class_names.append(class_name.text.split())
  
    ##Grade
    grade = []
    grades_elements = soup.find_all('td', class_='grade snug')
    for grades_element in grades_elements:
      if grades_element:
        grade.append(grades_element.text.split()[:1])
    grade = [item for item in grade if item != ['-']]
  
    ##Class Name
    result = []
    for sublist in class_names:
      if len(sublist) >= 2:
        result.append(sublist[0] + ' ' + sublist[1])
      else:
        result.append(sublist[0])
    if "Homeroom 10A" in result:
      result.remove("Homeroom 10A")
    weight = browser.go_to_split()
  
    ##Combined Lesson + Grade
    final = []
    for i, item in enumerate(result):
      final.append(item + " " + grade[i][0])
  
    ##Final GPA
    gpa = GPACalc(grade, weight)
    final_gpa = round(gpa, 2)
    print(result)
    print(grade)
    print(weight)
    print(final_gpa)
    browser.close_browser()
  except:
    print("Invalid username/password")

scrape("ryan.2025", "Bruhlmao69420!")
