# Importing necessary libraries for tayara.tn
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio 
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd

# Base URL for Tayara car listings
base_url_tayara = "https://www.tayara.tn/ads/c/V%C3%A9hicules/?page="

# Generating URLs for the first 315 pages of listings
tayara_url_list = [f"{base_url_tayara}{i}" for i in range(1,316)]

# List to store individual car listing URLs
tayara_links_to_be_scraped = []

# Data structure to store scraped information
tayara_data = [['titre' , 'prix' ,'gouvernerat et date d''ajout' , 'Kilométrage', 'Couleur du véhicule' 
                , 'Boite' , 'Année' ,'Cylindrée' , 'Marque', 'Modèle', 'Puissance fiscale' , 
                'Type de carrosserie', 'Carburant', 'Number of Pictures', 'Description']]


async def get_hrefs(url, session, max_retries=5):
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') 
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')

    for attempt in range(max_retries):
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)

            wait = WebDriverWait(driver, 10)
            element_one = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#__next > div.flex.flex-col.xl\:flex-row.h-fit.w-full.overflow-x-hidden.mt-\[14rem\].mt-\[14rem\].lg\:mt-\[9rem\] > main > div.mt-3.mx-2.lg\:ml-0.lg\:mr-6.lg\:mt-12.relative.z-10 > div.relative.-z-40 > div:nth-child(2) > div')))
            all_links = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'article')))                 
                    
            for link in all_links:
                url_1 = link.find_element(By.TAG_NAME, 'a').get_attribute('href')
                tayara_links_to_be_scraped.append(url_1)
            driver.quit()
            break
        except Exception as e:  
                await asyncio.sleep(1)


async def scrape_tayara(url, session, max_retries=5):
    """
    Asynchronously scrapes car information from Tayara website.

    Parameters:
    - url (str): The URL of the Tayara page to be scraped.
    - session (aiohttp.ClientSession): An aiohttp client session for making asynchronous HTTP requests.
    - max_retries (int): Maximum number of retry attempts in case of a failure.

    Returns:
    - None: The function prints the scraped car data or an error message.
    """
    for attempt in range(max_retries):
        try:
            car = []
            
            async with session.get(url) as response:
                response.raise_for_status()
                html_content = await response.text()
                
                soup1 = BeautifulSoup(html_content, "html.parser")
                soup2 = BeautifulSoup(soup1.prettify(), 'html.parser')
                
                title = soup2.find('h1', {'class': 'text-gray-700 font-bold text-2xl font-arabic'}).text.strip()
                car.append(title)
                
                price = soup2.select_one('#__next > div.flex.flex-col.xl\:flex-row.h-fit.w-full.overflow-x-hidden.mt-\[14rem\].mt-\[14rem\].lg\:mt-\[9rem\] > main > div.grid.grid-cols-12.gap-x-2.mt-6.pr-0 > div > div:nth-child(2) > div.mt-4 > data').get('value')
               
                car.append(price)

                place_and_date_added = soup2.find('div', {'class', 'flex justify-between items-center mt-5 mb-8'}).find('div', {'class': 'flex items-center space-x-2 mb-1'}).find('span').text.replace('\n', '').strip()

                
                car.append(place_and_date_added)
                
                data = {x.find('span', {'class': 'text-gray-600/80 text-2xs md:text-xs lg:text-xs font-medium'}).text.strip(): x.find('span', {'class': 'text-gray-700/80 text-xs md:text-sm lg:text-sm font-semibold'}).text.strip() for x in [x.find('div', {'class': 'px-4 py-2 bg-gray-100/70 flex items-center rounded-md border border-gray-300/80'}).find('span', {'class': 'flex flex-col py-1'}) for x in soup2.find('ul', {'class': 'grid gap-3 grid-cols-12'}).find_all('li', {'class': 'col-span-6 lg:col-span-3'})]}

                for i,j in data.items():
                    if i in tayara_data[0]:
                        car.insert( tayara_data[0].index(i),j)
                tayara_data.append(car)  


                try :
                    
                    nbr_pictures = soup2.select_one('#__next > div.flex.flex-col.xl\:flex-row.h-fit.w-full.overflow-x-hidden.mt-\[14rem\].mt-\[14rem\].lg\:mt-\[9rem\] > aside > div.grow.overflow-y-hidden > div > div.flex.flex-row.content-start.gap-2.flex-wrap.my-2.mx-auto')
                    nbr_pictures = len(nbr_pictures.find_all('a'))
                    car.append(nbr_pictures)
                except Exception as e:
                    
                    car.append(0) 

                try :

                    description = soup2.select_one('#__next > div.flex.flex-col.xl\:flex-row.h-fit.w-full.overflow-x-hidden.mt-\[14rem\].mt-\[14rem\].lg\:mt-\[9rem\] > main > div.grid.grid-cols-12.gap-x-2.mt-6.pr-0 > div > div:nth-child(4) > p').text
                    car.append(description)

                except Exception as e:
                    
                    car.append('')      
                break

        except Exception as e:
            pass
    else:
        pass


async def main():

    """ 
    Asynchronous main function to orchestrate the fetching and parsing of car listing URLs.

    """
    async with aiohttp.ClientSession() as session:
        tasks = [get_hrefs(url, session) for url in tayara_url_list]
        await asyncio.gather(*tasks)

    async with aiohttp.ClientSession() as session:
        tasks = [scrape_tayara(url, session) for url in tayara_links_to_be_scraped]
        await asyncio.gather(*tasks)

    tayara_df = pd.DataFrame(tayara_data[1:], columns=tayara_data[0])
    file_path = "###########"
    tayara_df.to_csv(file_path, index=False)

if __name__ == '__main__':
    main()
