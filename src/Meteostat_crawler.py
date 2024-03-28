import requests
import PIL
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import pandas as pd
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, timedelta
import os
import shutil
import glob
import unidecode
import argparse
import sys

def preprocess_province_name(province_name):
    provinces=['Hà Nội', 'Hồ Chí Minh', 'Hải Phòng', 'Đà Nẵng', 'Hà Giang', 'Cao Bằng', 'Lai Châu', 'Lào Cai', 'Tuyên Quang', 'Lạng Sơn', 'Bắc Kạn', 'Thái Nguyên', 'Yên Bái', 'Sơn La', 'Phú Thọ', 'Vĩnh Phúc', 'Bắc Giang', 'Bắc Ninh', 'Quảng Ninh', 'Hà Nam', 'Hòa Bình', 'Nam Định', 'Ninh Bình', 'Thái Bình', 'Thanh Hóa', 'Nghệ An', 'Hà Tĩnh', 'Quảng Bình', 'Quảng Trị', 'Thừa Thiên Huế', 'Quảng Nam', 'Quảng Ngãi', 'Bình Định', 'Phú Yên', 'Khánh Hòa', 'Ninh Thuận', 'Bình Thuận', 'Kon Tum', 'Gia Lai', 'Đắk Lắk', 'Đắk Nông', 'Lâm Đồng', 'Bình Phước', 'Tây Ninh', 'Bình Dương', 'Đồng Nai', 'Bà Rịa - Vũng Tàu', 'Long An', 'Tiền Giang', 'Bến Tre', 'Trà Vinh', 'Vĩnh Long', 'Đồng Tháp', 'An Giang', 'Kiên Giang', 'Cần Thơ', 'Hậu Giang', 'Sóc Trăng', 'Bạc Liêu', 'Cà Mau']
    new_province_name = unidecode.unidecode(province_name).lower().replace(" ", "")
    for province in provinces:
      if unidecode.unidecode(province).lower().replace(" ", "") == new_province_name:
        return province

parser = argparse.ArgumentParser()
print(sys.executable)
parser.add_argument('--province_name', type=str, required=True)# Province name to search
parser.add_argument('--days', type=int, required=True)# Days to search
args = parser.parse_args()
province_name = preprocess_province_name(args.province_name)
days = args.days


pd.set_option("display.width",None)
dir_path = os.path.join(os.getcwd(),'data/Meteostat')
os.chdir(dir_path)


def Initialize_driver():
  chrome_options = webdriver.ChromeOptions()
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument("--headless")
  chrome_options.add_argument("--disable-gpu")
  chrome_options.add_argument("--start-maximized")
  chrome_options.add_argument("--disable-infobars")
  chrome_options.add_argument("--disable-extensions")
  chrome_options.add_argument("--window-size=1366x768") # this should be your screen size
  driver = webdriver.Chrome(options=chrome_options)
  wait = WebDriverWait(driver, 20)
  driver.implicitly_wait(20)
  return driver,wait

def download_csv(dir_path,province_name,wait,driver):
  old_filepath = os.path.join(dir_path,'export.csv')# This is where the downloaded save
  new_filepath = os.path.join(dir_path,f'{province_name}.csv')# This is where and new name we want to save it
  #Find download button
  download_but = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div/main/div/div/div/div[1]/div[1]/div[1]/button[1]')))
  if(download_but.is_enabled()):
    driver.execute_script("arguments[0].click();", download_but)# click on download button
    csv_button = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="formatSelect"]/option[4]')))# Choose csv as file format
    csv_button.click()
    save_button = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="export-modal"]/div/div/div[3]/button')))#Find save button
    driver.execute_script("arguments[0].click();", save_button)# click on save button
    #Wait until the file is downloaded
    while not os.path.exists(old_filepath):
      print('wait')
      time.sleep(1)
    #Rename the file
    shutil.copyfile(old_filepath,new_filepath)
    os.remove(old_filepath)

def merge_csv(province_name):
  province_dataset_path = os.path.join(dir_path,province_name)
  csv_files = glob.glob(f'{province_dataset_path}*.csv')# Get all .csv file that contain province_name in its name
  if len(csv_files)>1:# If we found more than 1 file, we need to concatenate them together
    df_csv_concat = pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True).sort_values(by='time').reset_index(drop=True)
    df_csv_concat.to_csv(f'{dir_path}/meteostat_dataset_{province_name}.csv')
  elif len(csv_files)==1:# If only 1 file, just rename it
    shutil.copyfile(csv_files[0],f'{dir_path}/meteostat_dataset_{province_name}.csv')
  else: # If there is no file, return 
    return
  for csv_file in csv_files:# Remove all file we found
    os.remove(csv_file)

def crawl_meteostat_data(province_name, days):
  print(province_name)
  #We can search the province name by 2 ways:
  # - With no space between letters: hochiminh
  # - With space between letters: ho chi minh
  # province name need to be in lowercase, and need to be removed Vietnamese Accents
  province_name_types=[province_name,''.join(unidecode.unidecode(province_name).split()).lower(),unidecode.unidecode(province_name).lower()]
  continual_error=0
  num_unsearchable=0
  success= False #We only need 1 time succeed
  while (not success) and (continual_error<3) and (num_unsearchable<3):# search until we succeed or we get 5 errors
    for province_name_type in province_name_types:# Search with 3 ways
      ran = False
      start_date='' #The start day of our historical data
      end_date=''   #The end day of our historical data
      hold_date=date.today()  #This will hold the start day everytime you get error
      # The maximum of every search is about 10 years
      # Show if we search more than 10 years, we need to search more than 1 time
      remain_days = days# The day remain after every time we search
      driver,wait = Initialize_driver()#Innitial driver
      search_url = 'https://meteostat.net/en/'
      driver.get(search_url)  # Get the website
      while remain_days > 0:#Loop until we get all days of data
        print('Number of countinual error:',continual_error,"\tNumber of Unsearchable times:",num_unsearchable)
        print("Remain days:", remain_days)
        try:#we may get error, when it does we need to start again
            if not ran:#If this is the first time we access https://meteostat.net/en/ in a specific way of searching
              ran =True
              #Click on reject cookie button
              wait.until(EC.element_to_be_clickable((By.XPATH,"//*[@id='cookieModal']/div/div/div[3]/button[1]"))).click()
              #Find search text box
              inputElement = driver.find_element(By.XPATH, "//*[@id='search']")
              inputElement.click()#click on search text box
              #Searching
              inputElement.send_keys(province_name_type)
              #Get first result
              time.sleep(3)
              results = driver.find_elements(By.XPATH,"//*[@id='app']/div/div[2]/nav/div/div[1]/div/a[1]")
              if len(results)==0:
                print("Province unsearchable!!!")
                num_unsearchable+=1
                break        
              # print(len(first_result))
              results[0].click()#click on first result
              #Switch to the result window
              wait.until(EC.new_window_is_opened(driver.window_handles))  
              window_after = driver.window_handles[0]
              driver.switch_to.window(window_after)
              end_date = date.today()#So the end day would be today
            else:
              end_date = start_date - timedelta(days=1)# If this is not the first time, the end_date is to continue the last start day we searched
            #The search range is 7 days or less
            start_date = end_date - timedelta(days=min(7,remain_days)-1)
            print("From ",start_date,"to ",end_date )
            #Get the url to the result window
            print('Search result page:',driver.current_url)
            new_page_url = driver.current_url.split('?')[0]+f'?t={start_date}/{end_date}'
            # driver.get_screenshot_as_file("/content/screenshot.png")
            driver.close()
            driver.quit()
            #Incase of getting error: Max retries exceeded, we need to close and reinitalize the driver
            driver,wait = Initialize_driver()
            driver.get(new_page_url) # access the result website
            print(driver.current_url)
            wait.until(EC.element_to_be_clickable((By.XPATH,"//*[@id='cookieModal']/div/div/div[3]/button[1]"))).click()#Click the reject cookie button
            time.sleep(2)
            province_name_type=unidecode.unidecode(province_name_type).lower().replace(" ", "")#remove space from province_name_type
            download_csv(dir_path,f'{province_name_type}-{remain_days}',wait,driver)# Download the result csv file
            hold_date = start_date
            continual_error=0
            remain_days-= 7 #update the remain_days after we search
        except Exception as err:
            print(f"{type(err).__name__} was raised: {err}")#print the error
            # if type(err).__name__=='ElementClickInterceptedException':
            #   num_Element_error+=1
            # if type(err).__name__=='IndexError':
            #   num_Index_error+=1
            # if type(err).__name__=='TimeoutException':
            #   break
            start_date = hold_date
            continual_error+=1
      if remain_days <=0:
        success=True #mark that we succeed
        break
  time.sleep(10)
  merge_csv(unidecode.unidecode(province_name).lower().replace(" ", ""))# merge all csv file belonged to the same province after we search
crawl_meteostat_data(province_name,days)# crawl 20 years = 7305 days
