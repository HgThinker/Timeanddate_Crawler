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
import os
import unidecode
from selenium_stealth import stealth

parser = argparse.ArgumentParser()
print(sys.executable)

parser.add_argument('--province_name', type=str, required=True)# Province name to search
parser.add_argument('--days', type=int, required=True)# Province name to search

args = parser.parse_args()
province_name = '-'.join(args.province_name.lower().split())
days = args.days

def preprocess_province_name(province_name):
    provinces=["An Giang", "Bắc Giang", "Bắc Kạn", "Bạc Liêu", "Bắc Ninh", "Vũng Tàu", 
    "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước", "Bình Thuận", "Cà Mau", 
    "Cao Bằng", "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai", 
    "Hà Giang", "Hà Nam", "Hà Tĩnh", "Hậu Giang", "Hòa Bình", "Hưng Yên", "Khánh Hòa", 
    "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Long An", 
    "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên", "Quảng Bình", 
    "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sóc Trăng", "Sơn La", 
    "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Huế", "Tiền Giang", 
    "Trà Vinh", "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái", "Cần Thơ", "Hải Phòng", 
    "Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Hải Dương"]
    new_province_name = unidecode.unidecode(province_name).lower().replace(" ", "")
    for province in provinces:
      element_province_name =unidecode.unidecode(province).lower().replace(" ", "")
      if element_province_name == new_province_name:
        return province

dir_path = os.path.join(os.getcwd(),'data/timeanddate/un_preprocessed')
csv_path= os.path.join(dir_path,f'timeanddate_dataset_{province_name}.csv')

#Initialize chrome web driver 
my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('log-level=3')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument(f"--user-agent={my_user_agent}")
driver = webdriver.Chrome(options=chrome_options)
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True)
wait = WebDriverWait(driver, 100)
driver.implicitly_wait(100)

web_url = f'https://www.timeanddate.com/weather/vietnam/{province_name}/historic'
driver.get(web_url)

print("Crawling:",preprocess_province_name(province_name=province_name))
print("Link:", driver.current_url)
dataset = pd.DataFrame()
#Initialize dataframe
dataset = pd.DataFrame(columns = ['Year','Date','Time', 'Temp', 'Weather', 'Wind_speed','Wind_direct', 'Humidity', 'Barometer', 'Visibility'])

#START CRAWLING
# select MONTH dropdown
current_month_index=1
current_month_name = ''
number_of_month=0
count_days = 0

ran = False
while True:
  try:
    time.sleep(5)
    # print("current_month_index: ", current_month_index)
    ele_month = driver.find_element(By.ID,'month')
    select_month = Select(ele_month)
    month =  select_month.options[current_month_index]
    if not ran:
      number_of_month=len(select_month.options)
      # print("Number of month: ", len(select_month.options))
      ran=True
    time.sleep(10)
    month.click # Click on that month
    current_month_name = month.text
    # print("Selected month:", current_month_name)
    select_month.select_by_visible_text(current_month_name) # Choose a  SPECIFIC month
    # SELECT DAY DROPDOWN
    ele_day = driver.find_element(By.ID,'wt-his-select')
    select_day = Select(ele_day)
    # Take all data of a day
    for day in select_day.options[::-1]:
      time.sleep(2)
      day.click()
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
        detail_list = [current_month_name.split()[1], day_name.split(', ')[0]]
        count=0
        if count_row==7:# if it is the first hours, It is a special case
          detail_list.append(children[0].text.replace('°C','').replace('°','').replace('mph','').replace('mbar','').replace('km','').replace('%','').replace('/h','')[:5])# cut off the first data
          for children_index in range(1,len(children)):#Get the left over data
            if children_index == 5:
              detail_list.append(children[children_index].find_element(By.XPATH, "./*").get_attribute('title').split()[3])        
            elif children_index == 1 :
              continue
            else:
              detail_list.append(children[children_index].text.replace('°C','').replace('°','').replace('mph','').replace('mbar','').replace('km','').replace('%','').replace('/h',''))
        else:
          for children_index in range(0,len(children)):#Get all data of hour
            if children_index == 5:
              detail_list.append(children[children_index].find_element(By.XPATH, "./*").get_attribute('title').split()[3])
            elif children_index == 1 :
              continue
            else:
              detail_list.append(children[children_index].text.replace('°C','').replace('°','').replace('mph','').replace('mbar','').replace('km','').replace('%','').replace('/h',''))
        print(detail_list)
        dataset.loc[len(dataset)] = detail_list
        # dataset = dataset.append(pd.Series(detail_list, index=dataset.columns[:len(detail_list)]), ignore_index=True)
        count_row+=1
      count_days+=1
      if(count_days == days):
        # os.remove(os.path.join(dir_path,f'timeanddate_dataset_{province_name}.csv'))
        dataset.to_csv(os.path.join(dir_path,f'timeanddate_dataset_{province_name}.csv'),mode='w',index=False)
        print(f"Finished crawling {province_name}!!!")
        break    
    current_month_index+=1
  except Exception as err:
    print(f"{type(err).__name__} was raised {err}")
    driver.get(web_url)
  if current_month_index == number_of_month or count_days == days :
    break
