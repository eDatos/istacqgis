from istacqgis.controllers import resources
import re # regular expressions
import urllib.request
import os # os path
import glob
import csv

def get_all_files_in_directory(self, extension="*.geojson"):
    
    path = self.plugin_dir + "/data/" + extension
    files = glob.glob(path)
    
    names = [os.path.basename(x) for x in files]
    return names
    
def get_cb_dates_from_file_path(self, option):
    
    list = []
    files = get_all_files_in_directory(self)
    
    for file in files:
        if option == "DISTRICTS":
            if bool(re.match(r"^DISTRICTS*", file)):
                list.append(file)
        elif option == "SECTIONS":
            if bool(re.match(r"^SECTIONS*", file)):
                list.append(file)
    
    return list

def get_file_size(self, filename, extension):
    path = self.plugin_dir + "/data/" + filename + "." + extension
    try:
        file_size = os.path.getsize(path)
    except FileNotFoundError:
        print("ERROR: File not found: " + path)
        file_size = 0
    return file_size

def get_temporal_code_from_csv(self, indicator):
    
    # Get path
    file_path = self.plugin_dir + "/data/" + resources.getIndicatorFileName(self, indicator) + ".csv"
    min = 0
    max = 9999
    cont = 0
    
    with open(file_path, 'r' ) as f:
        reader = csv.DictReader(f)
        for row in reader:
            
            temporal_code = row['temporal_code']
            temporal_granularity = resources.detect_date_pattern(temporal_code)
            calculated_date = resources.calculated_date(temporal_code, temporal_granularity)
            
            if cont == 0:
                min = calculated_date
                max = min
                cont += 1
            else:
                if calculated_date > max:
                    max = calculated_date
                if calculated_date < min:
                    min = calculated_date
    
    return {'max': max, 'min': min}

# Check if plugin /data folder is empty
def cache_is_empty(self):
    
    files = get_all_files_in_directory(self)
    if len(files) == 0:
        return True
    else:
        return False

# Get all files names from an URL 
def get_cache_files_from_url(self, url):
    
    links = []

    try:
        # Connect to a URL
        website = urllib.request.urlopen(url)
        # Read html code
        html = website.read().decode('utf-8')
        # Use re.findall to get all the links
        links = re.findall(r'[\w\.-]+geojson+', html)
        
    except urllib.error.HTTPError as err:

        if err.code == 404:
           print("HTTP Error 404: URL (" + url + ") not found")
        else:
           raise
        print("Please, contact us at consultas.istac@gobiernodecanarias.org")
    
    return set(links)

def download_file_from_url(self, url, file):
    
    # Get path
    file_path = self.plugin_dir + "/data/" + file
    
    # Download file
    try:
        urllib.request.urlretrieve(url+file, filename=file_path, reporthook=None, data=None)
    except urllib.error.HTTPError:
        print("Warning: Not file " + file + " found at " + url)
        print("Please, contact us at consultas.istac@gobiernodecanarias.org")
            