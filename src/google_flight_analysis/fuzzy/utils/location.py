from google_flight_analysis.fuzzy.utils.alias_dict import AliasKeyDict
from typing import Union

LOCATIONS = AliasKeyDict()
LOCATIONS['ChinaEast/华东'] = ["SHA//虹桥机场", "PVG//浦东机场", "nanjing//南京禄口", "hangzhou//萧山机场"]
LOCATIONS['CN/China/中国'] = None




class LocationCls():
    def __init__(self, location: Union[list, str]):
        match location:
            case str():
                self._location = [location]
            case list() if all(isinstance(item, str) for item in location):
                self._location = location
            case _:
                raise TypeError("location must be a list or a string")
    
    @property
    def location(self):
        return self._location




if __name__=='__main__':
    print(LOCATIONS['华东'])
    print(LOCATIONS)
    cls = LocationCls('SHA')
    print(cls.location)