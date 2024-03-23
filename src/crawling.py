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
import argparse
import sys

parser = argparse.ArgumentParser()
print(sys.executable)

parser.add_argument('--province_name', type=str, required=True)# Province name to search
args = parser.parse_args()
province_name = '-'.join(args.province_name.lower().split())

#Initialize chrome web driver 
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 100)
driver.implicitly_wait(100)
web_url = f'https://www.timeanddate.com/weather/vietnam/{province_name}/historic'
driver.get(web_url)

#Initialize dataframe
dataset = pd.DataFrame(columns = ['Province','Year','Date','Time', 'Temp', 'Weather', 'Wind_speed','Wind_direct', 'Humidity', 'Barometer', 'Visibility'])
dataset.loc[len(dataset)]=['','','','', '°F', '', 'mph','', '%', 'Hg', 'mi']

#START CRAWLING
# select MONTH dropdown
current_month_index=1
current_month_name = ''
number_of_month=0
ran = False
while True:
  if current_month_index == (44 + 1):
    break
  try:
    time.sleep(10)
    print("current_month_index: ", current_month_index)
    ele_month = driver.find_element(By.ID,'month')
    select_month = Select(ele_month)
    month =  select_month.options[current_month_index]
    if not ran:
      number_of_month=len(select_month.options)
      print("Number of month: ", len(select_month.options))
      ran=True
    time.sleep(10)
    month.click # Click on that month
    current_month_name = month.text
    print("Selected month:", current_month_name)
    select_month.select_by_visible_text(current_month_name) # Choose a  SPECIFIC month
    # SELECT DAY DROPDOWN
    ele_day = driver.find_element(By.ID,'wt-his-select')
    select_day = Select(ele_day)
    # Take all data of a day
    for day in select_day.options[1:]:
      time.sleep(2)
      day.click
      day_name = day.text
      print("Selected day:", day_name)
      #Find data of hours in day
      # day.select_by_visible_text(day_name)
      elements = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'tr')))
      # elements=driver.find_elements(By.TAG_NAME,"tr")#Find all hours
      count_row=7
      for element_details in elements[7:-1]:#Loop through hours
        print(element_details.text)
        children = element_details.find_elements(By.XPATH, "./*")
        # children = wait.until(EC.visibility_of_all_elements_located(By.XPATH, "./*"))
        detail_list = [province_name,current_month_name.split()[1], day_name.split(', ')[0]]
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
          dataset.to_csv(f'/kaggle/working/Timeanddate_Crawler/timeanddate_dataset_{province_name}.csv',)
    current_month_index+=1
  except Exception as e:
    print(e)
    driver.get(web_url)

