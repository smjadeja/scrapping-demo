import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidArgumentException
import requests
import os 
import cv2
import traceback
import time
import re
import csv
from tqdm import tqdm
import random
import argparse



def get_auction_data(driver,store_data_file_name,output_folder):
    """
    Extracts vehicle information and images from the auction website.

    Parameters:
    - driver: Selenium WebDriver instance used to navigate the auction website.
    - store_data_file_name: Store scrape data in this file.
    - output_folder: Save the scraped images and CSV folder path 
    """
    try:
        data = []
        # get aution vehicle data in page 
        vehical_list = driver.find_elements(By.XPATH, "//*[@class='table-row table-row-border']")
        for index, vehical in tqdm(enumerate(vehical_list), total=len(vehical_list), desc="Processing Vehicles"):
            try:
                # Re-fetch the vehicle list to avoid stale references
                vehical_list_updated = driver.find_elements(By.XPATH, "//*[@class='table-row table-row-border']")
                vehical = vehical_list_updated[index]  # Get the current vehicle element
                time.sleep(2)  # Reduced wait time for responsiveness
                driver.execute_script("arguments[0].scrollIntoView(true);", vehical)

                # Find the vehicle name and stock number within the current vehicle element
                vehical_name = vehical.find_element(By.XPATH, ".//h4[@class='heading-7 rtl-disabled']/a")
                
                stock_number = vehical.find_element(By.XPATH, ".//li/span[@class='data-list__value text-truncate' and contains(@title, 'Stock #:')]")
                
                preprocess_folder_name = re.sub(r'[//,/]+', ' ', vehical_name.text)
                image_store_folder_name = f"{preprocess_folder_name.replace(' ', '_')}"
                #create vehical images folder
                vehical_images = 'vehicle_images'
                image_destination = os.path.join(output_folder,vehical_images, image_store_folder_name)

                # Create a folder to store the images
                if not os.path.exists(image_destination):
                    os.makedirs(image_destination)

                # Store the vehicle name and stock number
                data.append({"Vehicle Name": vehical_name.text, "Stock Number": stock_number.text})

                # Click on the vehicle name to open the detail page
                vehical_name.click()

                # Wait for the detail page to load and for the images to appear
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "spacedthumbs1strow")))

                # Find all images in the `spacedthumbs1strow` container
                image_elements = driver.find_elements(By.CSS_SELECTOR, "#spacedthumbs1strow img")

                # Loop through each image and download them
                for idx, img_element in enumerate(image_elements):
                    image_url = img_element.get_attribute('src')
                    image_name = f"{image_store_folder_name}_image_{idx}.jpg"

                    # Download the image and save it locally
                    image_path = os.path.join(image_destination, image_name)
                    img_data = requests.get(image_url).content
                    with open(image_path, 'wb') as img_file:
                        img_file.write(img_data)

                    # Read the saved image using OpenCV
                    image = cv2.imread(image_path)

                    if image is not None:
                        # Crop the bottom part of the image
                        height, width = image.shape[:2]
                        cropped_image = image[0:height - 10, 0:width]

                        # Save the cropped image
                        cv2.imwrite(image_path, cropped_image)
                        print(f"Saved cropped image at: {image_path}")
                    else:
                        print(f"Failed to load image: {image_path}")

                print(f"Downloaded images for {image_store_folder_name}")

                # Use browser's back button to return to the original vehicle list
                driver.back()

                # Wait for the vehicle list to reappear and reload the vehicle list
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@class='table-row table-row-border']")))
            except Exception as e:
                traceback.print_exc()
                print(f"An error occurred for vehicle {index}: {e}")  
        csv_file_path = os.path.join(output_folder,store_data_file_name)
        # Check if the CSV file exists
        if not os.path.exists(csv_file_path):
            # Create the CSV file and write initial data if it does not exist
            with open(csv_file_path, 'w', newline='') as csv_file:
                # Define the field names (header)
                fieldnames = ['Vehicle Name', 'Stock Number']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                
                # Write the header
                writer.writeheader()

         # Saving the data to a CSV file
        with open(csv_file_path, 'a', newline='') as csv_file:
            fieldnames = ['Vehicle Name', 'Stock Number']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writerows(data)  # Write the vehicle data
        print("Data scraping process has been completed.")
    except Exception as e:
        print(f'Error getting auction data:{e} ')

def select_proxy(file_name):
    """
    Select random proxy ip in txt file 

    Parameters:
    - file_name: The name of the text file containing a list of proxy IP addresses.
    """
    # Load proxy IPs from the text file
    with open(file_name, "r") as f:
        proxies = f.readlines()

    # Strip whitespace characters (like newlines)
    proxies = [proxy.strip() for proxy in proxies if proxy.strip()]

    # Select a random proxy IP
    if proxies:
        random_proxy = random.choice(proxies)
        return random_proxy
    else: 
        return None

def main(proxy_file_name,store_data_file_name,output_folder,script_start_with_proxy):
    """
    The entry point of the vehicle auction data scraper.

    Parameters:
    - Proxy_file_name: proxy ip txt file path
    - Store_data_file_name: scrape data stored in this file
    - output_folder: Save the scraped images and CSV folder path
    - script_start_with_proxy: start python scraping scripts with proxy ip 
    """
    try:
        chrome_options = uc.ChromeOptions()
        if script_start_with_proxy:
            # Select a random proxy IP from the provided text file
            proxy_ip = select_proxy(proxy_file_name)
            if proxy_ip:
                chrome_options.add_argument(f"--proxy-server={proxy_ip}")
            else:
                print(f"Please add the proxy IP to the proxy.txt file.")
        driver = uc.Chrome(options = chrome_options)
        driver.get("https://www.iaai.com/branchlocations")
        time.sleep(3)

        # Find the list of auctions in the table body
        auctions_list = driver.find_elements(By.XPATH, '//*[@class="table-body"]')
        driver.implicitly_wait(2)

        if auctions_list:
            # Check if there are any auctions found
            first_auction = auctions_list[0]  # Get the first auction element 

            # Find the clickable calendar element for the first auction
            click_on_first_auction = first_auction.find_element(By.XPATH, "//*[@class='calendar__body']")

            # Scroll to the first auction element to bring it into view
            driver.execute_script("arguments[0].scrollIntoView(true);", click_on_first_auction)
            click_on_first_auction.click()  # Click on the first auction's calendar
            driver.implicitly_wait(4)  # Wait for the page to load

            # Call a function to extract data from the auction page
            get_auction_data(driver,store_data_file_name,output_folder)
        
    except Exception as e:
        # Print out the exact error for debugging
        print(f"Error during scraping:{e}")
    except OSError:
        pass
    except KeyboardInterrupt:
        pass
    except InvalidArgumentException as e:
        print(f"Invalid Argument: {e}")
    finally:
        # Close the browser after operation
        driver.quit()

# Call the main function to execute the script
if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Scraping script parameters.")
    parser.add_argument('--proxy_file', type=str, default="proxy_ip.txt", 
                        help="Path to the proxy IP text file.")
    parser.add_argument('--store_data_file', type=str, default="vehicle_data.csv", 
                        help="Path to the output CSV file for storing data.")
    parser.add_argument('--output_folder', type=str, default="output", 
                        help="Path to the output folder.")
    parser.add_argument('--script_start_with_proxy', type=str, help='Path to the file containing proxy IPs', required=True)
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the main function with parsed arguments
    main(args.proxy_file, args.store_data_file, args.output_folder,args.script_start_with_proxy)