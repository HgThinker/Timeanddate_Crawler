import requests
import PIL
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import requests
import PIL
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#Initialize chrome web driver 
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 100)
driver.implicitly_wait(100)
web_url = 'https://www.timeanddate.com/weather/vietnam/ho-chi-minh/historic?month=3&year=2024'
driver.get(web_url)

#Initialize dataframe
dataset = pd.DataFrame(columns = ['Year','Date','Time', 'Temp', 'Weather', 'Wind_speed','Wind_direct', 'Humidity', 'Barometer', 'Visibility'])
dataset.loc[len(dataset)]=['','','', '°F', '', 'mph','', '%', 'Hg', 'mi']

#START CRAWLING
# select MONTH dropdown
time.sleep(100)
ele_month = driver.find_element(By.ID,'month')
# ele_month = wait.until(EC.visibility_of_all_elements_located((By.ID,'month')))
# ele_month=wait.until(EC.visibility_of_element_located(ele_month))
select_month = Select(ele_month)
for month in select_month.options[1:]:
  time.sleep(100)
  wait.until(EC.element_to_be_clickable(month))
  month_name = month.text
  print("Selected month:", month_name)
  # wait.until(EC.visibility_of_any_elements_located((By.NAME,month.text)))
  select_month.select_by_visible_text(month_name) # Choose a  SPECIFIC month
  month.click # Click on that month
  # SELECT DAY DROPDOWN
  ele_day = driver.find_element(By.ID,'wt-his-select')
  # ele_day = wait.until(EC.visibility_.textof_any_elements_located((By.ID,'wt-his-select')))
  select_day = Select(ele_day)
  # Take all data of a day
  for day in [option for option in select_day.options]:
    day_name = day.text
    print("Selected day:", day_name)
    #Find data of hours in day
    select_day.select_by_visible_text(day_name)
    elements = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'tr')))
    # elements=driver.find_elements(By.TAG_NAME,"tr")#Find all hours
    count_row=7
    for element_details in elements[7:-1]:#Loop through hours
      print(element_details.text)
      children = element_details.find_elements(By.XPATH, "./*")
      # children = wait.until(EC.visibility_of_all_elements_located(By.XPATH, "./*"))
      detail_list = [month_name.split()[1], day_name.split(', ')[0]]
      count=0
      if count_row==7:# if it is the first hours, It is a special case
        detail_list.append(children[0].text.replace('°F','').replace('mph','').replace('\"Hg','').replace('%','')[:8])# cut off the first data
        for children_index in range(1,len(children)):#Get the left over data
          if children_index == 5:
            detail_list.append(children[children_index].find_element(By.XPATH, "./*").get_attribute('title').split()[3])
          else:
            detail_list.append(children[children_index].text.replace('°F','').replace('mph','').replace('\"Hg','').replace('%',''))

      else:
        for children_index in range(0,len(children)):#Get all data of hour
          if children_index == 5:
            detail_list.append(children[children_index].find_element(By.XPATH, "./*").get_attribute('title').split()[3])
          else:
            detail_list.append(children[children_index].text.replace('°F','').replace('mph','').replace('\"Hg','').replace('%',''))
      detail_list = [x for x in detail_list if x]
      dataset.loc[len(dataset)] = detail_list#Add new row to dataset
      count_row+=1
      if count_row % 5 ==0:
        dataset.to_csv('/content/drive/MyDrive/Reeco/timeanddate_dataset.csv')