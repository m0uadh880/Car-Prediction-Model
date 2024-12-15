# Importing necessary libraries for automobile.tn
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


# List to store the scraped data
automobile_data_list = [['Titre', 'Prix', 'Fabricant', 'Carrosserie', 'Energie',
                         'Puissance fiscale', 'Boite', 'Transmission',  
                         'Kilometrage', 'Annee','Age', 'Inserée le'
                           ]]

# List of car manufacturers for identification
manufacturers_list = ['Alfa Romeo', 'Audi', 'BAIC', 'YX', 'BMW', 'BYD', 'Chery', 'Chevrolet', 'Citroën', 'Cupra',
                      'Dacia', 'DFSK', 'Dodge', 'Dongfeng', 'DS', 'Faw', 'Fiat', 'Ford', 'Foton', 'GAC', 'Geely',
                      'Great Wall', 'Haval', 'Honda', 'Hummer', 'Hyundai', 'Infiniti', 'Isuzu', 'Iveco', 'Jaguar',
                      'Jeep', 'KIA', 'Lada', 'Lancia', 'Land Rover', 'Mahindra', 'Maserati', 'Mazda', 'Mercedes-Benz',
                      'MG', 'Mini', 'Mitsubishi', 'Nissan', 'Opel', 'Peugeot', 'Piaggio', 'Porsche', 'Renault', 'Seat',
                      'Skoda', 'Smart', 'Ssangyong', 'Suzuki', 'TATA', 'Toyota', 'Volkswagen', 'Volvo', 'Wallyscar']

# Base URL for automobile listings
base_url = 'https://www.automobile.tn/fr/occasion/'

automobile_pages_urls = [f"{base_url}{i}" for i in range(1, 175)]

# List to store individual car listing URLs
automobile_cars_urls = []


async def get_automobile_urls(url, session, max_retries=3):

    for attempt in range(max_retries):
        try:
            # Fetching HTML content of the page
            async with session.get(url, timeout=30) as response:
                response.raise_for_status()
                html_content = await response.text()

                soup1 = BeautifulSoup(html_content, "html.parser")
                soup2 = BeautifulSoup(soup1.prettify(), 'html.parser')

                articles = soup2.find_all('div', {'data-key': True})
                data_keys = [div['data-key'] for div in articles]

                for data_key in data_keys:
                    article = soup2.find('div', {'data-key': data_key})
                    href = article.find('a', {'class': 'occasion-link-overlay'}).get('href')
                    link = f'https://www.automobile.tn{href}'
                    automobile_cars_urls.append(link)
                automobile_pages_urls.remove(url)

        except asyncio.TimeoutError:
            await asyncio.sleep(2 ** attempt)   

        except aiohttp.ClientError as e:
            await asyncio.sleep(2 ** attempt)   # an exponential delay before retrying
            pass
           
        else :
            # Break the loop if successful
            break
    else:
        pass

async def scrape_automobile(url, session, max_retries=5):

    for attempt in range(max_retries):
        car = []
        try:
            async with session.get(url, timeout=30) as response:
                if response.status != 200:
                    print(f"Error: Status {response.status} for {url}")
                    continue
                response.raise_for_status()
                html_content = await response.text()
                # Parsing HTML content
                soup1 = BeautifulSoup(html_content, "html.parser")
                soup2 = BeautifulSoup(soup1.prettify(), 'html.parser')

                try:
                    title = soup2.select_one('#content_container > div.occasion-details-v2 > h1').text.strip()
                    title = ' '.join(title.split())
                    car.append(title)
                except Exception as e:
                    car.append("") 

                try:
                    price = str(soup2.select_one('#content_container > div.occasion-details-v2 > div:nth-child(5) > div.col-md-4 > div > div:nth-child(1) > div.price-box > div').text[:-18].strip()).replace(' ','')
                    car.append(price)
                except Exception as e:
                    car.append("") 
                
                try:
                    manufacturer = next((manuf for manuf in manufacturers_list if manuf.lower() in title.lower()), 'Other')
                    car.append(manufacturer)
                except Exception as e:
                    car.append("")           

                try:
                    carroserie = soup2.select_one('#content_container > div.occasion-details-v2 > div:nth-child(5) > div.col-md-4 > div > div:nth-child(1) > div.main-specs > ul > li:nth-child(7) > span.spec-value').text.strip()
                    car.append(carroserie)
                except Exception as e:
                    car.append("")
                              
                try:
                    energie = soup2.select_one('#content_container > div.occasion-details-v2 > div:nth-child(5) > div.col-md-4 > div > div:nth-child(1) > div.main-specs > ul > li:nth-child(3) > span.spec-value').text.strip()
                    car.append(energie)
                except Exception as e:
                    car.append("")
                
                try:
                    Puissance_fiscale = soup2.select_one('#content_container > div.occasion-details-v2 > div:nth-child(5) > div.col-md-4 > div > div:nth-child(1) > div.main-specs > ul > li:nth-child(5) > span.spec-value').text.replace('cv','').strip()
                    car.append(Puissance_fiscale)
                except Exception as e:
                    car.append("")
                
                try:
                    Boite = soup2.select_one('#content_container > div.occasion-details-v2 > div:nth-child(5) > div.col-md-4 > div > div:nth-child(1) > div.main-specs > ul > li:nth-child(4) > span.spec-value').text.strip()
                    car.append(Boite)
                except Exception as e:
                    car.append("")         
                
                try:
                    transmission = soup2.select_one('#content_container > div.occasion-details-v2 > div:nth-child(5) > div.col-md-4 > div > div:nth-child(1) > div.main-specs > ul > li:nth-child(6) > span.spec-value').text.strip()
                    car.append(transmission)
                except Exception as e:
                    car.append("")
                
                try:
                    kilo = soup2.select_one('#content_container > div.occasion-details-v2 > div:nth-child(5) > div.col-md-4 > div > div:nth-child(1) > div.main-specs > ul > li:nth-child(1) > span.spec-value').text.replace('km','').strip().replace(' ','')
                    car.append(kilo)
                except Exception as e:
                    car.append("")
                               
                try:
                    annee = soup2.select_one('#content_container > div.occasion-details-v2 > div:nth-child(5) > div.col-md-4 > div > div:nth-child(1) > div.main-specs > ul > li:nth-child(2) > span.spec-value').text.strip().split('.')[1]
                    car.append(annee)
                except Exception as e:
                    car.append("")
                
                try:
                    age = datetime.now().year -  int(annee)
                    car.append(age)
                except Exception as e:
                    car.append("")
                
                try:
                    Inserée = soup2.select_one('#content_container > div.occasion-details-v2 > div:nth-child(5) > div.col-md-4 > div > div:nth-child(1) > div.main-specs > ul > li:nth-child(8) > span.spec-value').text.strip()
                    car.append(Inserée)
                except Exception as e:
                    car.append("")
                

                automobile_data_list.append(car)
                break
        except Exception as e:
            await asyncio.sleep(5)
            pass     
    else:
        print(f"Failed to scrape {url} after {max_retries} attempts. index {automobile_cars_urls.index(url)}")


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [get_automobile_urls(url, session) for url in automobile_pages_urls]
        await asyncio.gather(*tasks)


    
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_automobile(url, session) for url in automobile_cars_urls]
        await asyncio.gather(*tasks)

    automobile_df = pd.DataFrame(automobile_data_list[1:], columns=automobile_data_list[0])

    automobile_df['Model'] = automobile_df.apply(lambda row: row['Titre'].replace(row['Fabricant'], '').strip(), axis=1)
    

    file_path = "./initial_datasets/automobile_data.csv"
    automobile_df.to_csv(file_path, index=False)

if __name__ == '__main__':
    asyncio.run(main())
