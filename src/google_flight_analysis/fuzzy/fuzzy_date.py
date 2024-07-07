from datetime import datetime
from typing import Any
import pandas as pd
from google_flight_analysis.scrape import Scrape, ScrapeObjects, date_format
from google_flight_analysis.fuzzy.utils.date_process import DateParser
import concurrent
from concurrent.futures import ThreadPoolExecutor
class FuzzyDateScrape():
    '''
    The differenee here is that in the ending of each date, we can a +n and or -n 
    to indicate that we want to search for flights n days before or after the date
    '''
    def __init__(self, *args):
        self._origin = None
        self._dest = None
        self._date = None
        self._data = pd.DataFrame()
        self._url = None
        self._type = None
        self.generated_scrape_objs = None
        self._parse_args(*args)
    
    def _parse_args(self, *args):
        '''
			args Format

			one-way:
				org, dest, date

			round-trip:
				org, dest, dateleave, datereturn

			chain-trip:
				org, dest, date, org, dest, date, org, dest, date ...

			perfect-chain:
				org, date, org, date, org, date, org, date, ..., dest
				implied condition: dest of prev city = origin of next city
		'''
    	# one way
        if len(args) == 3:
            assert len(args[0]) == 3 and isinstance(args[0], str), "Issue with arg 0, see docs"
            assert len(args[1]) == 3 and isinstance(args[1], str), "Issue with arg 1, see docs"
            assert isinstance(args[2], str), "Issue with arg 2, see docs"

            self._origin, self._dest, self._date = [args[0]], [args[1]], [args[2]]

            assert len(self._origin) == len(self._dest) == len(self._date), "Issue with array lengths, talk to dev"
            combinations = DateParser._parse_date(self._date[0])
            self.generated_scrape_objs = [Scrape(self._origin[0], self._dest[0], date.strftime("%Y-%m-%d")) for date in combinations]
            
        # round-trip
        elif len(args) == 4:
            assert len(args[0]) == 3 and isinstance(args[0], str), "Issue with arg 0, see docs"
            assert len(args[1]) == 3 and isinstance(args[1], str), "Issue with arg 1, see docs"
            assert isinstance(args[2], str), "Issue with arg 2, see docs"
            assert isinstance(args[3], str), "Issue with arg 3, see docs"

            self._origin, self._dest, self._date = [args[0], args[1]], [args[1], args[0]], args[2:]
            assert len(self._origin) == len(self._dest) == len(self._date), "Issue with array lengths, talk to dev"
            self._type = 'round-trip'
            combinations = DateParser.generate_date_combinations(self._date)
            self.generated_scrape_objs = [Scrape(args[0], args[1], date_list[0].strftime("%Y-%m-%d"), date_list[1].strftime("%Y-%m-%d")) for date_list in combinations if date_list[0] < date_list[1]]

        # chain-trip, chain is component of 3s, check that last one is an actual date to not confuse w perfect
        elif len(args) >= 3 and len(args) % 3 == 0 and len(args[-1]) == 10 and type(args[-1]) == str:
            self._origin, self._dest, self._date = [], [], []

            for i in range(0, len(args), 3):
                assert len(args[i]) == 3 and type(args[i]) == str, "Issue with arg {}, see docs".format(i)
                assert len(args[i + 1]) == 3 and type(args[i+1]) == str, "Issue with arg {}, see docs".format(i+1)
                assert len(args[i + 2]) == 10 and type(args[i + 2]) == str, "Issue with arg {}, see docs".format(i+2)
                
                if i > 0:
                    assert datetime.strptime(self._date[-1], date_format) < datetime.strptime(args[i + 2], date_format), "Dates are not in order ({d1} > {d2}). Make sure to provide them in increasing order in YYYY-MM-DD format.".format(d1 = self._date[-1], d2 = args[i+2])

                self._origin += [args[i]]
                self._dest += [args[i + 1]]
                self._date += [args[i + 2]]

            assert len(self._origin) == len(self._dest) == len(self._date), "Issue with array lengths, talk to dev"
            self._url = self._make_url()
            self._type = 'chain-trip'


        # perfect-chain
        elif len(args) >= 4 and len(args) % 2 == 1 and len(args[-1]) == 3 and type(args[-1]) == str:
            assert len(args[0]) == 3 and type(args[0]) == str, "Issue with arg 0, see docs"
            assert len(args[1]) == 10 and type(args[1]) == str, "Issue with arg 1, see docs"

            self._origin, self._dest, self._date = [args[0]], [], [args[1]]

            for i in range(2, len(args)-1, 2):
                assert len(args[i]) == 3 and type(args[i]) == str, "Issue with arg {}, see docs".format(i)
                assert len(args[i + 1]) == 10 and type(args[i + 1]) == str, "Issue with arg {}, see docs".format(i+1)
                assert datetime.strptime(self._date[-1], date_format) < datetime.strptime(args[i + 1], date_format), "Dates are not in order ({d1} > {d2}). Make sure to provide them in increasing order in YYYY-MM-DD format.".format(d1 = self._date[-1], d2 = args[i+1])

                self._origin += [args[i]]
                self._dest += [args[i]]
                self._date += [args[i+1]]

            assert len(args[-1]) == 3 and type(args[-1]) == str, "Issue with last arg, see docs"
            self._dest += [args[-1]]

            assert len(self._origin) == len(self._dest) == len(self._date), "Issue with array lengths, talk to dev"
            self._url = self._make_url()
            self._type = 'perfect-chain'

        else:
            raise NotImplementedError()

    def search_and_merge(self, file_name="output.xlsx"):
        data_frame = []
        for scrape_obj in self.generated_scrape_objs:
            ScrapeObjects(scrape_obj)
            data_frame.append(scrape_obj.data)
        merged_df = pd.concat(data_frame)
        merged_df.to_excel(file_name)
        return merged_df



    def search_and_merge_multithread(self, file_name="output.xlsx"):
        def scrape_and_collect_data(scrape_obj):
            ScrapeObjects(scrape_obj)
            return scrape_obj.data

        with ThreadPoolExecutor() as executor:
            # Submit all scraping tasks to the executor and store futures in a list
            futures = [executor.submit(scrape_and_collect_data, scrape_obj) for scrape_obj in self.generated_scrape_objs]
            # Collect results based on the order of submission
            data_frame = [future.result() for future in futures]

        merged_df = pd.concat(data_frame)
        merged_df.to_excel(file_name)
        return merged_df
# test
if __name__=='__main__':
    # print("Testing One Way:")
    # test = FuzzyDateScrape('AMS', 'PVG', '2024-09-27+5-2')
    # test.search_and_merge_multithread()
    
    print("\nTesting Round Trip:")
    test2 = FuzzyDateScrape('AMS', 'PVG', '2024-09-27+5-2', '2024-10-01+10-2')
    test2.search_and_merge_multithread()