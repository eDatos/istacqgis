from istacqgis.controllers import cache
from istacqgis.controllers.istacpy import istacpy
import json

def getGeographicalGranularities(self, indicator=None):
    
    geographical_granularities = []
    url_to_check = "http://www.gobiernodecanarias.org/istac/QGIS/"
    
    if indicator is None:
        # geographical_granularities = ['COUNTIES', 'COUNTRIES', 'DISTRICTS', 'ISLANDS', 'LARGE_COUNTIES', 'MUNICIPALITIES', 'PROVINCES', 'REGIONS', 'SECTIONS']
        # Get granularities from URL (url_to_check)
        geographical_granularities = cache.get_cache_files_from_url(self, url_to_check, remove_extension = True)
        # Convert to list
        geographical_granularities = list(geographical_granularities)
        
    else:
        content = istacpy.get_indicators_code(indicator)
        for granularity in content["dimension"]["GEOGRAPHICAL"]["granularity"]:
            geographical_granularities.append(granularity["code"])
    
    # Sort geographical
    geographical_granularities.sort()
            
    return geographical_granularities

def convert_to_date(variableelement):
    splited_original = variableelement.split("_")
    splited_date_full = splited_original[1]
    splited_date = splited_date_full.split(".")[0]
    year = splited_date[:4]
    month = splited_date[4:-2]
    day = splited_date[-2:]
    
    return {'variableelement': splited_date, 'date': str(year) + "/" + str(month) + "/" + str(day)}

# Only for DISTRICTS and SECTIONS
def get_cb_date_by_variableelement(self, granularity):
    
    variableelement_visited = []
    # Get elements from URL
    element_list = cache.get_cb_dates_from_url(self, granularity)
    for date in element_list:
        element = granularity + "_" + date + ".geojson" 
        date_dict = convert_to_date(element)
        variableelement_visited.append(date_dict)
    
    return variableelement_visited

def get_geojson_data(self, geographical_granularity):
    
    file = self.plugin_dir + "/data/" + geographical_granularity + ".geojson"
    
    with open(file) as f:
        data = json.load(f)

    variable_element_list = []
    for feature in data['features']:
        variable_element_list.append(feature["properties"]["variable_element"])
        
    return variable_element_list
    