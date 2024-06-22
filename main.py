from playwright.sync_api import sync_playwright
from openpyxl.workbook import Workbook
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse

@dataclass
class Business:
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None

    latitude: float = None
    longitude: float = None

@dataclass
class BusinessList:
    business_list : list[Business] = field(default_factory=list)


    def dataframe(self):
        return pd.json_normalize((asdict(business) for business in self.business_list), sep = ',')
    
    
    def save_to_excel(self, filename):
      
        self.dataframe().to_excel(f"{filename}.xlsx", index=False)

    def save_to_csv(self, filename):
        self.dataframe().to_csv(f"{filename}.csv", index=False)

def extract_coordinates_from_url(url: str) -> tuple[float,float]:
    """helper function to extract coordinates from url"""
    
    coordinates = url.split('/@')[-1].split('/')[0]
    # return latitude, longitude
    return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])



def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto('https://www.google.com/maps', timeout = 6000)
        page.wait_for_timeout(5000)

        page.locator('//input[@id="searchboxinput"]').fill(search_for)
        page.wait_for_timeout(30000)

        page.keyboard.press('Enter')
        page.wait_for_timeout(50000)

        listings = page.locator('//a[@class="hfpxzc"]').all()
        print(len(listings))


        business_list = BusinessList()

        for listing in listings:
            listing.click()

            namepath = '//h1[@class="DUwDvf lfPIob"]'
            addresspath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
            websitepath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
            phonepath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
            
            business = Business()
            if page.locator(namepath).count() > 0:
                business.name = page.locator(namepath).all()[0].inner_text()
            else:
                business.name = "Blank_"

            if page.locator(addresspath).count() > 0:
                business.address = page.locator(addresspath).all()[0].inner_text()
            else:
                business.address = "Blank_"

            if page.locator(websitepath).count() > 0:
                business.website = page.locator(websitepath).all()[0].inner_text()
            else:
                business.website = "Blank_"
                
            if page.locator(phonepath).count() > 0:
                business.phone_number = page.locator(phonepath).all()[0].inner_text()
            else:
                business.phone_number = "Blank_"
            



            business.latitude, business.longitude = extract_coordinates_from_url(page.url)
  
            # print('-----------------------------------------')
            # print(business.name)
            # print(business.address)
            # print(business.website)
            # print(business.phone_number)
            # print(business.latitude)
            # print(business.longitude)
            # print(business.address)
            # print('-----------------------------------------')

            business_list.business_list.append(business)
            business_list.save_to_csv('google_maps_data')
            business_list.save_to_excel('google_maps_data')
       

        browser.close()

if __name__  == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--search', type=str)
    parser.add_argument('-l', '--location', type=str)
    args = parser.parse_args()

    if args.location and args.search:
        search_for = f'{args.search} {args.location}'
    else:
        search_for = 'dentist new york'
    
    main()