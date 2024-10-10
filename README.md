Here's a basic and clear README file based on your provided instructions:


Vehicle Auction Data Scraper

This Python script automates the process of scraping vehicle data and images from an auction website. It extracts vehicle information such as the vehicle name, stock number, and downloads associated images. It also supports proxy usage for web scraping.


Features
- Automatically extract vehicle data (e.g., name and stock number) from auction listings.
- Download and store vehicle images in an organized folder structure.
- Save vehicle data to a CSV file.
- Support for random proxy usage for web scraping.


Setup Instructions

1. Create Virtual Environment: Set up a Python virtual environment to isolate dependencies.
   
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   

2. Install Dependencies: Install the necessary Python packages.
   pip install -r requirements.txt

3. Configure File Paths: 
   - In the `scraping.py` file, configure the paths for:
     - `proxy_file_name`: Path to the proxy IP text file.
     - `store_data_file_name`: Path to store the output CSV file containing vehicle data.
   
4. Create Proxy IP Text File:  
   Create a text file for proxy IPs. Example (`proxy_ip.txt`):
   
   123.45.67.89:8080
   987.65.43.21:3128



Usage

Run the script using the following command:

python scraping.py --proxy_file proxy_ip.txt --store_data_file vehicle_data.csv --output_folder output --script_start_with_proxy False


Arguments

1. proxy_file: (Required) Path to the text file containing proxy IPs.
   - Example: `proxy_ip.txt`
2. store_data_file: (Required) Path to the CSV file where scraped vehicle data will be stored.
   - Example: `vehicle_data.csv`
3. output_folder: (Required) Path to the output folder where vehicle images will be saved.
   - Example: `output/`
4. script_start_with_proxy: (Optional) Boolean flag (`True` or `False`) indicating whether the script should start with a proxy.
   - Set to `True` if you want the script to use proxies from the specified file.


Proxy Setup
- Create a file containing proxy IPs in the following format:
  
  IP:PORT
  
- Example:
  
  192.168.1.1:8080
  10.0.0.2:3128
  
- Pass the path to this proxy file using the `--proxy_file` argument.
- Set `--script_start_with_proxy` to `True` if you want to use proxies during scraping.

Note: Running the script with a proxy may slow down the process due to the additional network routing.


## Example Command

python scraping.py --proxy_file proxy_ip.txt --store_data_file vehicle_data.csv --output_folder output --script_start_with_proxy True
