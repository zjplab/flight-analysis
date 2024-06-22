import sys
import os

# Assuming this script is in the root of your project and `src` is also in the root
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')

# Add `src` to the sys.path
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Now you can import your modules
from google_flight_analysis.scrape import *


result = Scrape('AMS', 'PVG', '2024-09-27', '2024-10-01') # obtain our scrape object, represents out query
result.type # This is in a round-trip format
result.origin # ['JFK', 'IST']
result.dest # ['IST', 'JFK']
result.date # ['2023-07-20', '2023-08-20']


ScrapeObjects(result) # runs selenium through ChromeDriver, modifies results in-place
result.data.to_csv('test.csv') # save results to a csv
print(result.data) # get queried representation of result