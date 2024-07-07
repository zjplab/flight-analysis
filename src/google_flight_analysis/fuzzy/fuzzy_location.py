from google_flight_analysis.fuzzy.utils.location import LOCATIONS
import pandas as pd

class FuzzyLocationScrape():
    '''
    This class is used to generate a list of Scrape objects based on a list of locations
    '''
    def __init__(self, *args):
        self._locations = None
        self._data = pd.DataFrame()
        self._url = None
        self._type = None
        self.generated_scrape_objs = None
        self._parse_args(*args)
