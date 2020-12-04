import re
import json
from PyQt5.QtCore import QUrl, QEventLoop
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

# Build API URL
def get_url(api, path, resource=None):
    url_root = "https://datos.canarias.es/api/estadisticas/" + api + "/v1.0/"
    if resource is None:
        url = url_root + path
    else:
        url = url_root + path + "/" + resource

    return url


# Example: parse_param("GEOGRAPHICAL[MUNICIPALITIES]")
def parse_param(param):
    param = param.strip()  # Remove white spaces (trim)
    param = param.replace("[", "%5B")  # Replace [ for %5B
    param = param.replace("]", "%5D")  # Replace ] for %5D
    param = param.replace(",", "%2C")  # Replace , for %2C
    param = param.replace("|", "%7C")  # Replace | for %7C
    param = param.replace("+", "%2B")  # Replace + for %2B
    param = param.replace("\"", "%22")  # Replace \" for %22
    param = param.replace(" ", "%20")  # Replace space for %20

    return param

def errorCatcher( msg, tag, level ):
    print("Error: " + msg) 


def get_content(url, is_json = True):
    
    content_requests = ""
    
    # Get content
    networkAccessManager = QNetworkAccessManager()
    req = QNetworkRequest(QUrl(url))
    
    # Set JSON headers
    if is_json:
        headers = {'Content-Type': 'application/json;charset=UTF-8', 'Access-Control-Allow-Origin': '*'}
        req.setHeader(QNetworkRequest.ContentTypeHeader, headers)
        
    reply = networkAccessManager.get(req)
    event = QEventLoop()
    reply.finished.connect(event.quit)
    event.exec()
    
    # Capture errors
    er = reply.error()
    if er == QNetworkReply.NoError:
        bytes_string = reply.readAll()
        if is_json:
            content_requests = json.loads(str(bytes_string, 'utf-8'))
        else:
            content_requests = bytes_string.data().decode('utf8')

    return content_requests

# Calculated date
def detect_date_pattern(date):
    
    granularity = ""
    if bool(re.match(r"^[0-9][0-9][0-9][0-9]$", date)):
        granularity = "YEARLY"
    elif bool(re.match(r"^[0-9][0-9][0-9][0-9]M[0-9][0-9]$", date)):
        granularity = "MONTHLY"
    elif bool(re.match(r"^[0-9][0-9][0-9][0-9]Q[0-9]$", date)):
        granularity = "QUARTERLY"
    elif bool(re.match(r"^[0-9][0-9][0-9][0-9]H[0-9][0-9]$", date)):
        granularity = "BIYEARLY"
    elif bool(re.match(r"^[0-9][0-9][0-9][0-9]W[0-9][0-9]$", date)):
        granularity = "WEEKLY"
    else:
        granularity = None
        
    return granularity

def calculated_date(temporal_code, temporal_granularity):

    if temporal_granularity == "YEARLY":
        date_tmp = "01/01/" + temporal_code
    elif temporal_granularity == "MONTHLY":
        splited_date = temporal_code.split("M")
        splited_year = splited_date[0]
        splited_month = splited_date[1]
        date_tmp = "01/" + splited_month + "/" + splited_year
    elif temporal_granularity == "QUARTERLY":
        splited_date = temporal_code.split("Q")
        splited_year = splited_date[0]
        splited_month = int(splited_date[1]) * 3
        if splited_month < 10:
            splited_month = "0" + str(splited_month)
        date_tmp = "01/" + str(splited_month) + "/" + splited_year
    else:
        date_tmp = None

    return date_tmp

# Temporal label
def get_date_title_month(month, lang = "es"):
    if month == "01":
        if lang == "es":
            return "Enero"
        elif lang == "en":
            return "January"
    elif month == "02":
        if lang == "es":
            return "Febrero"
        elif lang == "en":
            return "February"
    elif month == "03":
        if lang == "es":
            return "Marzo"
        elif lang == "en":
            return "March"
    elif month == "04":
        if lang == "es":
            return "Abril"
        elif lang == "en":
            return "April"
    elif month == "05":
        if lang == "es":
            return "Mayo"
        elif lang == "en":
            return "May"
    elif month == "06":
        if lang == "es":
            return "Junio"
        elif lang == "en":
            return "June"
    elif month == "07":
        if lang == "es":
            return "Julio"
        elif lang == "en":
            return "July"
    elif month == "08":
        if lang == "es":
            return "Agosto"
        elif lang == "en":
            return "August"
    elif month == "09":
        if lang == "es":
            return "Septiembre"
        elif lang == "en":
            return "September"
    elif month == "10":
        if lang == "es":
            return "Octubre"
        elif lang == "en":
            return "October"
    elif month == "11":
        if lang == "es":
            return "Noviembre"
        elif lang == "en":
            return "November"
    elif month == "12":
        if lang == "es":
            return "Diciembre"
        elif lang == "en":
            return "December"
    else:
        return None


def get_date_title_quarterly(quarterly, lang="es"):
    if quarterly == 1:
        if lang == "es":
            return "Primer trimestre"
        elif lang == "en":
            return "First quarter"
    elif quarterly == 2:
        if lang == "es":
            return "Segundo trimestre"
        elif lang == "en":
            return "Second quarter"
    elif quarterly == 3:
        if lang == "es":
            return "Tercer trimestre"
        elif lang == "en":
            return "Third quarter"
    elif quarterly == 4:
        if lang == "es":
            return "Cuatro trimestre"
        elif lang == "en":
            return "Fourth quarter"
    else:
        return None


def get_date_title(temporal_code, temporal_granularity, lang="es"):
    date_title_es = ""
    if temporal_code is not None and temporal_granularity is not None:
        if temporal_granularity == "YEARLY":
            date_title_es = temporal_code
        elif temporal_granularity == "MONTHLY":
            splited_date = temporal_code.split("M")
            splited_year = splited_date[0]
            splited_month = splited_date[1]
            month_title_es = get_date_title_month(splited_month, lang)
            date_title_es = splited_year + " " + month_title_es
        elif temporal_granularity == "QUARTERLY":
            splited_date = temporal_code.split("Q")
            splited_year = splited_date[0]
            splited_month = int(splited_date[1]) * 3
            splited_quarterly = splited_date[1]
            if splited_month < 10:
                splited_month = "0" + str(splited_month)
            date_title_es = splited_year + " " + get_date_title_quarterly(int(splited_quarterly), lang)
        else:
            date_title_es = None
    else:
        date_title_es = None

    return date_title_es

def getIndicatorFileName(self, indicator):
    
    cb_list = []
    # Add indicator
    cb_list.append(indicator)
    # Add checkbox options
    if self.measures_as_columns:
        cb_list.append("MEASURES-AS-COLUMNS")
    if self.date:
        cb_list.append("DATE")
    if self.geographical_and_temporal_columns:
        cb_list.append("GEO-AND-TIME-COLUMNS")
    if self.geographical_and_temporal_labels:
        cb_list.append("GEO-AND-TIME-LABELS")
    if self.measures_units:
        cb_list.append("MEASURES-UNITS")
    if self.langs:
        cb_list.append("LANGS")
        
    name = '_'.join(cb_list)
    return name