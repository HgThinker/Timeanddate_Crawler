from selenium import webdriver
from selenium.webdriver.common.by import By
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
  chrome_options.add_argument('--log-level=3')
  chrome_options.set_capability("browserVersion", "117")
  chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
  chrome_options.add_experimental_option("prefs", {
        "download.default_directory": os.path.abspath(dir_path),
        # "download.prompt_for_download": False,
        # "download.directory_upgrade": True,
        # "safebrowsing_for_trusted_sources_enabled": False,
        # "safebrowsing.enabled": False
        })
  chrome_options.add_argument("--window-size=1366x768") # this should be your screen size
  driver = webdriver.Chrome(options=chrome_options)
  wait = WebDriverWait(driver, 20)
  driver.implicitly_wait(20)
  return driver,wait

def download_csv(dir_path,province_name,wait,driver):
  old_filepath = os.path.join(dir_path,'export.csv')# This is where the downloaded save
  new_filepath = os.path.join(dir_path,f'meteostat_dataset_{province_name}.csv')# This is where and new name we want to save it
  #Find download button
  download_but = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div/main/div/div/div/div[1]/div[1]/div[1]/button[1]')))
  if(download_but.is_enabled()):
    driver.execute_script("arguments[0].click();", download_but)# click on download button
    csv_button = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="formatSelect"]/option[4]')))# Choose csv as file format
    csv_button.click()
    save_button = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="export-modal"]/div/div/div[3]/button')))#Find save button
    driver.execute_script("arguments[0].click();", save_button)# click on save button
    #Wait until the file is downloaded
    while not os.path.exists(old_filepath):
      print('Wait until file is download!!!')
      time.sleep(2)
    #Rename the file
    shutil.copy(old_filepath,new_filepath)
    os.remove(old_filepath)

def merge_csv(province_name):
  province_dataset_path = os.path.join(dir_path,f'meteostat_dataset_{province_name}')
  csv_files = glob.glob(f'{province_dataset_path}*.csv')# Get all .csv file that contain province_name in its name
  if len(csv_files)!=0:# If we found more than 1 file, we need to concatenate them together
    df_csv_concat = pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True)
    df_csv_concat = df_csv_concat.loc[:, ~df_csv_concat.columns.str.contains('^Unnamed')]
    df_csv_concat = df_csv_concat.drop_duplicates()
    df_csv_concat = df_csv_concat.sort_values(by='time').reset_index(drop=True)
    for csv_file in csv_files:# Remove all file we found
      os.remove(csv_file)
    df_csv_concat.to_csv(f'{dir_path}/meteostat_dataset_{province_name}.csv')
  # elif len(csv_files)==1:# If only 1 file, just rename it
  #   shutil.copyfile(csv_files[0],f'{dir_path}/meteostat_dataset_{province_name}.csv')
  #   os.remove(csv_files[0])
  else: # If there is no file, return 
    return

def crawl_meteostat_data(province_name, days):
  print(province_name)
  #We can search the province name by 2 ways:
  # - With no space between letters: hochiminh
  # - With space between letters: ho chi minh
  # province name need to be in lowercase, and need to be removed Vietnamese Accents
  province_name_types=[province_name,''.join(unidecode.unidecode(province_name).split()).lower(),unidecode.unidecode(province_name).lower()]
  num_unsearchable=0
  # while (not success) and (num_unsearchable<3):# search until we succeed or we get 5 errors
  for province_name_type in province_name_types:# Search with 3 ways
    continual_error=0
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
    while remain_days > 0 and (continual_error<2):#Loop until we get all days of data
      print('Number of countinual error:',continual_error)
      print("Remain days:", remain_days)
      try:#we may get error, when it does we need to start again
          if not ran:#If this is the first time we access https://meteostat.net/en/ in a specific way of searching
            #Click on reject cookie button
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,"//*[@id='cookieModal']/div/div/div[3]/button[1]"))).click()
            inputElement = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='search']")))
            inputElement.click()#click on search text box
            #Searching
            inputElement.send_keys(province_name_type)
            #Get first result            
            search_box= wait.until(EC.presence_of_element_located((By.XPATH,"//*[@id='app']/div/div[2]/nav/div/div[1]/div")))
            results = search_box.find_elements(By.XPATH,"./child::*")
            if len(results)==0:
              print("Province unsearchable!!!")
              num_unsearchable+=1
              break
            # print(len(first_result))
            new_province_name=unidecode.unidecode(province_name_type).lower().replace(" ", "")
            found_province=False
            for result in results:
              preprocessed_result = unidecode.unidecode(result.text).lower().replace(" ", "")
              if preprocessed_result == new_province_name or preprocessed_result == new_province_name+'city' :
                driver.execute_script("arguments[0].click();", result)
                print("Result clicked!!")
                found_province=True
                break
            if not found_province:
              print("No result matched!!!")
              break
            if(driver.current_url=='https://meteostat.net/en/#google_vignette' or driver.current_url=='https://meteostat.net/en/'):
              print('Ad block! Run from the begining!!!')
              driver.get(search_url) 
              continue
            end_date = date.today()#So the end day would be today
            ran =True
          else:
            end_date = start_date - timedelta(days=1)# If this is not the first time, the end_date is to continue the last start day we searched
          #The search range is 7 days or less
          start_date = end_date - timedelta(days=min(7,remain_days)-1)
          print("From ",start_date,"to ",end_date )
          new_page_url = driver.current_url.split('?')[0]+f'?t={start_date}/{end_date}'
          if 'vn'not in new_page_url: break
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
          print(f"{type(err).__name__} was raised!!!")#print the error
          start_date = hold_date
          continual_error+=1
    if remain_days <=0:
      # success=True #mark that we succeed
      break
  time.sleep(2)
  merge_csv(unidecode.unidecode(province_name).lower().replace(" ", ""))# merge all csv file belonged to the same province after we search

crawl_meteostat_data(province_name,days)

# if os.path.exists(f'{dir_path}/meteostat_dataset_{unidecode.unidecode(province_name).lower().replace(" ", "")}.csv'):
#   with open("Meteostat_searchable_province.txt", "a") as file:
#     file.write(f"'{unidecode.unidecode(province_name).lower().replace(" ", "")}'\n")