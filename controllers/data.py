from istacqgis.controllers.istacpy import istacpy
from istacqgis.controllers import resources
import os
import csv

def writeIndicatorData(self, indicator):
    
    # Variables
    measure_code_list = []
    geographical_code = ""
    geographical_granularity = ""
    geographical_label_en = ""
    geographical_label = ""
    temporal_code = ""
    temporal_granularity = ""
    temporal_label_en = ""
    temporal_label = ""
    calculated_date = ""
    measure_code = ""
    value = ""
    # Measures units
    measure_unit = ""
    measure_unit_multiplier = ""
    measure_unit_symbol = ""
    # Measure as columns
    annual_percentage_rate = ""
    interperiod_percentage_rate = ""
    absolute = "" # Note: absolute = value
    annual_puntual_rate = ""
    interperiod_puntual_rate = ""
    
    # Get path
    file_path = self.plugin_dir + "/data/" + resources.getIndicatorFileName(self, indicator) + ".csv"
    
    
    with open(file_path, 'w', newline='') as csvfile:
        
        indicator_data = istacpy.get_indicators_code_data(indicator)
        indicator_code = istacpy.get_indicators_code(indicator)
        
        if self.measures_as_columns:
            measure_code_list = list(indicator_data["dimension"]["MEASURE"]["representation"]["index"].keys())
            # Convert to lower case
            measure_code_list = [x.lower() for x in measure_code_list]
        
        fieldnames = get_field_names(self, measure_code_list)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        index = 0
        for i in range(indicator_data["dimension"]["GEOGRAPHICAL"]["representation"]["size"]):
            for j in range(indicator_data["dimension"]["TIME"]["representation"]["size"]):
                cont = 0
                max = indicator_data["dimension"]["MEASURE"]["representation"]["size"]
                for k in range(indicator_data["dimension"]["MEASURE"]["representation"]["size"]):
                    
                    # Geographical code
                    geographical_code = list(indicator_data["dimension"]["GEOGRAPHICAL"]["representation"]["index"].keys())[list(indicator_data["dimension"]["GEOGRAPHICAL"]["representation"]["index"].values()).index(i)]
                    # Temporal code
                    temporal_code = list(indicator_data["dimension"]["TIME"]["representation"]["index"].keys())[list(indicator_data["dimension"]["TIME"]["representation"]["index"].values()).index(j)]
                    # Date calculated
                    if self.date:
                        temporal_granularity = resources.detect_date_pattern(temporal_code)
                        calculated_date = resources.calculated_date(temporal_code, temporal_granularity)
                    
                    # Measure code
                    measure_code = list(indicator_data["dimension"]["MEASURE"]["representation"]["index"].keys())[list(indicator_data["dimension"]["MEASURE"]["representation"]["index"].values()).index(k)]
                    # Value
                    if indicator_data["observation"][index] == ".":
                        value = None
                    else:
                        value = indicator_data["observation"][index]
                    
                    # Measures as columns
                    if self.measures_as_columns:
                        # Measures
                        list_tmp = ["annual_percentage_rate", "interperiod_percentage_rate", "absolute", "annual_puntual_rate", "interperiod_puntual_rate"]
                        for measure_variable in measure_code_list:
                            
                            if measure_variable.upper() == measure_code and measure_variable == "annual_percentage_rate":
                                annual_percentage_rate = value
                            elif measure_variable.upper() == measure_code and measure_variable == "interperiod_percentage_rate":
                                interperiod_percentage_rate = value
                            elif measure_variable.upper() == measure_code and measure_variable == "absolute":
                                absolute = value
                            elif measure_variable.upper() == measure_code and measure_variable == "annual_puntual_rate":
                                annual_puntual_rate = value
                            elif measure_variable.upper() == measure_code and measure_variable == "interperiod_puntual_rate":
                                interperiod_puntual_rate = value
                            else:
                                if measure_variable not in list_tmp:
                                    print("Add variable: " + str(measure_variable))

                    # Geographical granularity
                    if self.geographical_and_temporal_columns or self.geographical_and_temporal_labels:
                        for geo in indicator_code["dimension"]["GEOGRAPHICAL"]["representation"]:
                            if geo["code"] == geographical_code:
                                geographical_granularity = geo["granularityCode"]
                                # Geographical label
                                if self.geographical_and_temporal_labels:
                                    geographical_label = geo["title"]["es"]
                                    # All langs
                                    if self.langs:
                                        try:
                                            geographical_label_en = geo["title"]["en"]
                                        except KeyError:
                                            geographical_label_en = None
                    # Temporal granularity
                    if self.geographical_and_temporal_columns or self.geographical_and_temporal_labels:
                        for time in indicator_code["dimension"]["TIME"]["representation"]:
                            if time["code"] == temporal_code:
                                temporal_granularity = time["granularityCode"]
                    
                    # Temporal label
                    if self.geographical_and_temporal_labels:
                        temporal_label = resources.get_date_title(temporal_code, temporal_granularity)
                        if self.langs:
                            temporal_label_en = resources.get_date_title(temporal_code, temporal_granularity, lang = "en")
                    # Unit measures
                    if self.measures_units:
                        for measure in indicator_code["dimension"]["MEASURE"]["representation"]:
                            if measure["code"] == measure_code:
                                try:
                                    measure_unit = measure["quantity"]["unit"]["es"]
                                except KeyError:
                                    measure_unit = None
                                try:
                                    measure_unit_multiplier = measure["quantity"]["unitMultiplier"]["es"]
                                except KeyError:
                                    measure_unit_multiplier = None
                                try:
                                    measure_unit_symbol = measure["quantity"]["unitSymbol"]
                                except KeyError:
                                    measure_unit_symbol = None

                    
                    if self.measures_as_columns:
                        cont += 1
                        if cont == max:
                            # Get content to write in CSV file
                            content = writerowContent(self, measure_code_list, geographical_code, geographical_granularity, geographical_label_en, geographical_label, temporal_code, temporal_granularity, temporal_label_en, temporal_label, calculated_date, measure_code, value, measure_unit, measure_unit_multiplier, measure_unit_symbol, absolute, annual_percentage_rate, interperiod_percentage_rate, annual_puntual_rate, interperiod_puntual_rate)
                            # Write content
                            writer.writerow(content)
                    else:
                        # Get content to write in CSV file
                        content = writerowContent(self, measure_code_list, geographical_code, geographical_granularity, geographical_label_en, geographical_label, temporal_code, temporal_granularity, temporal_label_en, temporal_label, calculated_date, measure_code, value, measure_unit, measure_unit_multiplier, measure_unit_symbol, absolute, annual_percentage_rate, interperiod_percentage_rate, annual_puntual_rate, interperiod_puntual_rate)
                        # Write content
                        writer.writerow(content)
                    index += 1
        
def get_field_names(self, measure_code_list):

    # Generating all checked combinations options ...
    if self.measures_as_columns:
        # 0 0 0 0 0
        fieldnames = [
            'geographical_code',
            'temporal_code', 
            #'measure_code', 
            'value'
        ]
        # 1 0 0 0 0 (MEASURES AS COLUMNS)
        if "absolute" in measure_code_list and "annual_percentage_rate" not in measure_code_list and "interperiod_percentage_rate" not in measure_code_list and "annual_puntual_rate" not in measure_code_list and "interperiod_puntual_rate" not in measure_code_list:
            # 0 0 0 0 0
            fieldnames = [
                'geographical_code',
                'temporal_code', 
                #'measure_code',
                'value'
            ]
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    #'measure_code',
                    'value',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value'
                ]
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value'
                ]
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value'
                ]
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value'
                ]
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value'
                ]
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value'
                ]
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0 
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value'
                ]
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value'
                ]
            # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value'
                ]
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value'
                ]
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value'
                ]
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
        # 1 0 0 0 1 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" not in measure_code_list and "interperiod_percentage_rate" not in measure_code_list and "annual_puntual_rate" not in measure_code_list and "interperiod_puntual_rate" in measure_code_list:
            # 0 0 0 0 0
            fieldnames = [
                'geographical_code',
                'temporal_code', 
                #'measure_code', 
                'value',
                'interperiod_puntual_rate'
            ]
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate'
                ]
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate'
                ]
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate'
                ]
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate'
                ]
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate'
                ]
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate'
                ]
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0 
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate'
                ]
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate'
                ]
            # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate'
                ]
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate'
                ]
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate'
                ]
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            
        # 1 0 0 1 0 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" not in measure_code_list and "interperiod_percentage_rate" not in measure_code_list and "annual_puntual_rate" in measure_code_list and "interperiod_puntual_rate" not in measure_code_list:
            # 0 0 0 0 0
            fieldnames = [
                'geographical_code',
                'temporal_code', 
                #'measure_code', 
                'value',
                'annual_puntual_rate'
            ]
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate'
                ]
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate'
                ]
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate'
                ]
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate'
                ]
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate'
                ]
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate'
                ]
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0 
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate'
                ]
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate'
                ]
            # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate'
                ]
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate'
                ]
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate'
                ]
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
        # 1 0 0 1 1 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" not in measure_code_list and "interperiod_percentage_rate" not in measure_code_list and "annual_puntual_rate" in measure_code_list and "interperiod_puntual_rate" in measure_code_list:
            # 0 0 0 0 0
            fieldnames = [
                'geographical_code',
                'temporal_code', 
                #'measure_code', 
                'value',
                'annual_puntual_rate',
                'interperiod_puntual_rate'
            ]
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol',
                ]
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0 
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
        # 1 0 1 0 0 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" not in measure_code_list and "interperiod_percentage_rate" in measure_code_list and "annual_puntual_rate" not in measure_code_list and "interperiod_puntual_rate" not in measure_code_list:
            # 0 0 0 0 0
            fieldnames = [
                'geographical_code',
                'temporal_code', 
                #'measure_code', 
                'value',
                'interperiod_percentage_rate'
            ]
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate'
                ]
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate'
                ]
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate'
                ]
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate'
                ]
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate'
                ]
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate'
                ]
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0 
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate'
                ]
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate'
                ]
            # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate'
                ]
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate'
                ]
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate'
                ]
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
        # 1 0 1 0 1 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" not in measure_code_list and "interperiod_percentage_rate" in measure_code_list and "annual_puntual_rate" not in measure_code_list and "interperiod_puntual_rate" in measure_code_list:
            # 0 0 0 0 0
            fieldnames = [
                'geographical_code',
                'temporal_code', 
                #'measure_code', 
                'value',
                'interperiod_percentage_rate',
                'interperiod_puntual_rate'
            ]
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0 
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
        # 1 0 1 1 0 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" not in measure_code_list and "interperiod_percentage_rate" in measure_code_list and "annual_puntual_rate" in measure_code_list and "interperiod_puntual_rate" not in measure_code_list:
            # 0 0 0 0 0
            fieldnames = [
                'geographical_code',
                'temporal_code', 
                #'measure_code', 
                'value',
                'interperiod_percentage_rate',
                'annual_puntual_rate'
            ]
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0 
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
        # 1 0 1 1 1 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" not in measure_code_list and "interperiod_percentage_rate" in measure_code_list and "annual_puntual_rate" in measure_code_list and "interperiod_puntual_rate" in measure_code_list:
            # 0 0 0 0 0
            fieldnames = [
                'geographical_code',
                'temporal_code', 
                #'measure_code', 
                'value',
                'interperiod_percentage_rate',
                'annual_puntual_rate',
                'interperiod_puntual_rate'
            ]
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0 
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
        # 1 1 0 0 0 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" in measure_code_list and "interperiod_percentage_rate" not in measure_code_list and "annual_puntual_rate" not in measure_code_list and "interperiod_puntual_rate" not in measure_code_list:
            # 0 0 0 0 0
            fieldnames = [
                'geographical_code',
                'temporal_code', 
                #'measure_code', 
                'value',
                'annual_percentage_rate'
            ]
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate'
                ]
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate'
                ]
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate'
                ]
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate'
                ]
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate'
                ]
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate'
                ]
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0 
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate'
                ]
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate'
                ]
            # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate'
                ]
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate'
                ]
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate'
                ]
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
        # 1 1 0 0 1 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" in measure_code_list and "interperiod_percentage_rate" not in measure_code_list and "annual_puntual_rate" not in measure_code_list and "interperiod_puntual_rate" in measure_code_list:
            # 0 0 0 0 0
            fieldnames = [
                'geographical_code',
                'temporal_code', 
                #'measure_code', 
                'value',
                'annual_percentage_rate',
                'interperiod_puntual_rate'
            ]
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0 
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
        # 1 1 0 1 0 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" in measure_code_list and "interperiod_percentage_rate" not in measure_code_list and "annual_puntual_rate" in measure_code_list and "interperiod_puntual_rate" not in measure_code_list:
            # 0 0 0 0 0
            fieldnames = [
                'geographical_code',
                'temporal_code', 
                #'measure_code', 
                'value',
                'annual_percentage_rate',
                'annual_puntual_rate'
            ]
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0 
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
        # 1 1 0 1 1 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" in measure_code_list and "interperiod_percentage_rate" not in measure_code_list and "annual_puntual_rate" in measure_code_list and "interperiod_puntual_rate" in measure_code_list:
            # 0 0 0 0 0
            fieldnames = [
                'geographical_code',
                'temporal_code', 
                #'measure_code', 
                'value',
                'annual_percentage_rate',
                'annual_puntual_rate',
                'interperiod_puntual_rate'
            ]
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0 
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
        # 1 1 1 0 0 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" in measure_code_list and "interperiod_percentage_rate" in measure_code_list and "annual_puntual_rate" not in measure_code_list and "interperiod_puntual_rate" not in measure_code_list:
            # 0 0 0 0 0
            fieldnames = [
                'geographical_code',
                'temporal_code', 
                #'measure_code', 
                'value',
                'annual_percentage_rate',
                'interperiod_percentage_rate'
            ]
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate'
                ]
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate'
                ]
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate'
                ]
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate'
                ]
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate'
                ]
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate'
                ]
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0 
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate'
                ]
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate'
                ]
            # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate'
                ]
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate'
                ]
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate'
                ]
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
        # 1 1 1 0 1 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" in measure_code_list and "interperiod_percentage_rate" in measure_code_list and "annual_puntual_rate" not in measure_code_list and "interperiod_puntual_rate" in measure_code_list:
            # 0 0 0 0 0
            fieldnames = [
                'geographical_code',
                'temporal_code', 
                #'measure_code', 
                'value',
                'annual_percentage_rate',
                'interperiod_percentage_rate',
                'interperiod_puntual_rate'
            ]
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0 
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
        # 1 1 1 1 0 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" in measure_code_list and "interperiod_percentage_rate" in measure_code_list and "annual_puntual_rate" in measure_code_list and "interperiod_puntual_rate" not in measure_code_list:
            # 0 0 0 0 0
            fieldnames = [
                'geographical_code',
                'temporal_code', 
                #'measure_code', 
                'value',
                'annual_percentage_rate',
                'interperiod_percentage_rate',
                'annual_puntual_rate'
            ]
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0 
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate'
                ]
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
        # 1 1 1 1 1 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" in measure_code_list and "interperiod_percentage_rate" in measure_code_list and "annual_puntual_rate" in measure_code_list and "interperiod_puntual_rate" in measure_code_list:
            # 0 0 0 0 0
            fieldnames = [
                'geographical_code',
                'temporal_code', 
                #'measure_code', 
                'value',
                'annual_percentage_rate',
                'interperiod_percentage_rate',
                'annual_puntual_rate',
                'interperiod_puntual_rate'
            ]
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'temporal_code',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0 
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'temporal_code',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'temporal_code',
                    'temporal_granularity',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate'
                ]
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                fieldnames = [
                    'geographical_code',
                    'geographical_granularity',
                    'geographical_label',
                    'geographical_label_en',
                    'temporal_code',
                    'temporal_granularity',
                    'temporal_label',
                    'temporal_label_en',
                    'date',
                    #'measure_code',
                    'value',
                    'annual_percentage_rate',
                    'interperiod_percentage_rate',
                    'annual_puntual_rate',
                    'interperiod_puntual_rate',
                    'measure_unit',
                    'measure_unit_multiplier',
                    'measure_unit_symbol'
                ]
    else:
        # 0 0 0 0 0
        fieldnames = [
            'geographical_code',
            'temporal_code', 
            'measure_code', 
            'value'
        ]
        # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
        # 0 0 0 1 0
        if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
            fieldnames = [
                'geographical_code',
                'temporal_code',
                'measure_code',
                'value',
                'measure_unit',
                'measure_unit_multiplier',
                'measure_unit_symbol'
            ]
        # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
        # 0 0 1 0 0
        elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_label',
                'temporal_code',
                'temporal_label',
                'measure_code',
                'value'
            ]
        # 0 0 1 0 1
        elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_label',
                'geographical_label_en',
                'temporal_code',
                'temporal_label',
                'temporal_label_en',
                'measure_code',
                'value'
            ]
        # 0 0 1 1 0
        elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_label',
                'temporal_code',
                'temporal_label',
                'measure_code',
                'value',
                'measure_unit',
                'measure_unit_multiplier',
                'measure_unit_symbol'
            ]
        # 0 0 1 1 1
        elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_label',
                'geographical_label_en',
                'temporal_code',
                'temporal_label',
                'temporal_label_en',
                'measure_code',
                'value',
                'measure_unit',
                'measure_unit_multiplier',
                'measure_unit_symbol'
            ]
        # 0 1 0 0 0
        elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_granularity',
                'temporal_code',
                'temporal_granularity',
                'measure_code',
                'value'
            ]
        # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
        # 0 1 0 1 0
        elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_granularity',
                'temporal_code',
                'temporal_granularity',
                'measure_code',
                'value',
                'measure_unit',
                'measure_unit_multiplier',
                'measure_unit_symbol'
            ]
        # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
        # 0 1 1 0 0
        elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_granularity',
                'geographical_label',
                'temporal_code',
                'temporal_granularity',
                'temporal_label',
                'measure_code',
                'value'
            ]
        # 0 1 1 0 1
        elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_granularity',
                'geographical_label',
                'geographical_label_en',
                'temporal_code',
                'temporal_granularity',
                'temporal_label',
                'temporal_label_en',
                'measure_code',
                'value'
            ]
        # 0 1 1 1 0
        elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_granularity',
                'geographical_label',
                'temporal_code',
                'temporal_granularity',
                'temporal_label',
                'measure_code',
                'value',
                'measure_unit',
                'measure_unit_multiplier',
                'measure_unit_symbol'
            ]
        # 0 1 1 1 1
        elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_granularity',
                'geographical_label',
                'geographical_label_en',
                'temporal_code',
                'temporal_granularity',
                'temporal_label',
                'temporal_label_en',
                'measure_code',
                'value',
                'measure_unit',
                'measure_unit_multiplier',
                'measure_unit_symbol'
            ]
        # 1 0 0 0 0
        elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
            fieldnames = [
                'geographical_code',
                'temporal_code',
                'date',
                'measure_code',
                'value'
            ]
        # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
        # 1 0 0 1 0
        elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
            fieldnames = [
                'geographical_code',
                'temporal_code',
                'date',
                'measure_code',
                'value',
                'measure_unit',
                'measure_unit_multiplier',
                'measure_unit_symbol'
            ]
        # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
        # 1 0 1 0 0 
        elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_label',
                'temporal_code',
                'temporal_label',
                'date',
                'measure_code',
                'value'
            ]
        # 1 0 1 0 1
        elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_label',
                'geographical_label_en',
                'temporal_code',
                'temporal_label',
                'temporal_label_en',
                'date',
                'measure_code',
                'value'
            ]
        # 1 0 1 1 0
        elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_label',
                'temporal_code',
                'temporal_label',
                'date',
                'measure_code',
                'value',
                'measure_unit',
                'measure_unit_multiplier',
                'measure_unit_symbol'
            ]
        # 1 0 1 1 1
        elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_label',
                'geographical_label_en',
                'temporal_code',
                'temporal_label',
                'temporal_label_en',
                'date',
                'measure_code',
                'value',
                'measure_unit',
                'measure_unit_multiplier',
                'measure_unit_symbol'
            ]
        # 1 1 0 0 0
        elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_granularity',
                'temporal_code',
                'temporal_granularity',
                'date',
                'measure_code',
                'value'
            ]
        # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
        # 1 1 0 1 0
        elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_granularity',
                'temporal_code',
                'temporal_granularity',
                'date',
                'measure_code',
                'value',
                'measure_unit',
                'measure_unit_multiplier',
                'measure_unit_symbol'
            ]
        # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
        # 1 1 1 0 0
        elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_granularity',
                'geographical_label',
                'temporal_code',
                'temporal_granularity',
                'temporal_label',
                'date',
                'measure_code',
                'value'
            ]
        # 1 1 1 0 1
        elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_granularity',
                'geographical_label',
                'geographical_label_en',
                'temporal_code',
                'temporal_granularity',
                'temporal_label',
                'temporal_label_en',
                'date',
                'measure_code',
                'value'
            ]
        # 1 1 1 1 1
        elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
            fieldnames = [
                'geographical_code',
                'geographical_granularity',
                'geographical_label',
                'geographical_label_en',
                'temporal_code',
                'temporal_granularity',
                'temporal_label',
                'temporal_label_en',
                'date',
                'measure_code',
                'value',
                'measure_unit',
                'measure_unit_multiplier',
                'measure_unit_symbol'
            ]
         
    return fieldnames
    

def writerowContent(self, measure_code_list, geographical_code, geographical_granularity, geographical_label_en, geographical_label, temporal_code, temporal_granularity, temporal_label_en, temporal_label, calculated_date, measure_code, value, measure_unit, measure_unit_multiplier, measure_unit_symbol, absolute, annual_percentage_rate, interperiod_percentage_rate, annual_puntual_rate, interperiod_puntual_rate):
    
    # Generating all checked combinations options ...
    if self.measures_as_columns:
        # 0 0 0 0 0
        writecontent = {
            'geographical_code': geographical_code, 
            'temporal_code': temporal_code,
            'measure_code': measure_code,
            'value': absolute
        }
        # 1 0 0 0 0 (MEASURES AS COLUMNS)
        if "absolute" in measure_code_list and "annual_percentage_rate" not in measure_code_list and "interperiod_percentage_rate" not in measure_code_list and "annual_puntual_rate" not in measure_code_list and "interperiod_puntual_rate" not in measure_code_list:
            # 0 0 0 0 0
            writecontent = {
                'geographical_code': geographical_code, 
                'temporal_code': temporal_code,
                #'measure_code': measure_code,
                'value': absolute
            }
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute
                }
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute
                }
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
             # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute
                }
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute
                }
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute
                }
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
               writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute
                }
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute
                }
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute
                }
             # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute
                }
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0 
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute
                }
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute
                }
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
        # 1 0 0 0 1 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" not in measure_code_list and "interperiod_percentage_rate" not in measure_code_list and "annual_puntual_rate" not in measure_code_list and "interperiod_puntual_rate" in measure_code_list:
            # 0 0 0 0 0
            writecontent = {
                'geographical_code': geographical_code, 
                'temporal_code': temporal_code,
                #'measure_code': measure_code,
                'value': absolute,
                'interperiod_puntual_rate': interperiod_puntual_rate
            }
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
             # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
               writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
             # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0 
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
        # 1 0 0 1 0 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" not in measure_code_list and "interperiod_percentage_rate" not in measure_code_list and "annual_puntual_rate" in measure_code_list and "interperiod_puntual_rate" not in measure_code_list:
            # 0 0 0 0 0
            writecontent = {
                'geographical_code': geographical_code, 
                'temporal_code': temporal_code,
                #'measure_code': measure_code,
                'value': absolute,
                'annual_puntual_rate': annual_puntual_rate
            }
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
             # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
               writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate
                }
             # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0 
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
        # 1 0 0 1 1 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" not in measure_code_list and "interperiod_percentage_rate" not in measure_code_list and "annual_puntual_rate" in measure_code_list and "interperiod_puntual_rate" in measure_code_list:
            # 0 0 0 0 0
            writecontent = {
                'geographical_code': geographical_code, 
                'temporal_code': temporal_code,
                #'measure_code': measure_code,
                'value': absolute,
                'annual_puntual_rate': annual_puntual_rate,
                'interperiod_puntual_rate': interperiod_puntual_rate
            }
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
             # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
               writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
             # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0 
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
        # 1 0 1 0 0 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" not in measure_code_list and "interperiod_percentage_rate" in measure_code_list and "annual_puntual_rate" not in measure_code_list and "interperiod_puntual_rate" not in measure_code_list:
            # 0 0 0 0 0
            writecontent = {
                'geographical_code': geographical_code, 
                'temporal_code': temporal_code,
                #'measure_code': measure_code,
                'value': absolute,
                'interperiod_percentage_rate': interperiod_percentage_rate
            }
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
             # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
               writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
             # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0 
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
        # 1 0 1 0 1 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" not in measure_code_list and "interperiod_percentage_rate" in measure_code_list and "annual_puntual_rate" not in measure_code_list and "interperiod_puntual_rate" in measure_code_list:
            # 0 0 0 0 0
            writecontent = {
                'geographical_code': geographical_code, 
                'temporal_code': temporal_code,
                #'measure_code': measure_code,
                'value': absolute,
                'interperiod_percentage_rate': interperiod_percentage_rate,
                'interperiod_puntual_rate': interperiod_puntual_rate
            }
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
             # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
               writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
             # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0 
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
        # 1 0 1 1 0 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" not in measure_code_list and "interperiod_percentage_rate" in measure_code_list and "annual_puntual_rate" in measure_code_list and "interperiod_puntual_rate" not in measure_code_list:
            # 0 0 0 0 0
            writecontent = {
                'geographical_code': geographical_code, 
                'temporal_code': temporal_code,
                #'measure_code': measure_code,
                'value': absolute,
                'interperiod_percentage_rate': interperiod_percentage_rate,
                'annual_puntual_rate': annual_puntual_rate
            }
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
             # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
               writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
             # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0 
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
        # 1 0 1 1 1 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" not in measure_code_list and "interperiod_percentage_rate" in measure_code_list and "annual_puntual_rate" in measure_code_list and "interperiod_puntual_rate" in measure_code_list:
            # 0 0 0 0 0
            writecontent = {
                'geographical_code': geographical_code, 
                'temporal_code': temporal_code,
                #'measure_code': measure_code,
                'value': absolute,
                'interperiod_percentage_rate': interperiod_percentage_rate,
                'annual_puntual_rate': annual_puntual_rate,
                'interperiod_puntual_rate': interperiod_puntual_rate
            }
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
             # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
               writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
             # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0 
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
        # 1 1 0 0 0 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" in measure_code_list and "interperiod_percentage_rate" not in measure_code_list and "annual_puntual_rate" not in measure_code_list and "interperiod_puntual_rate" not in measure_code_list:
            # 0 0 0 0 0
            writecontent = {
                'geographical_code': geographical_code, 
                'temporal_code': temporal_code,
                #'measure_code': measure_code,
                'value': absolute,
                'annual_percentage_rate': annual_percentage_rate
            }
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate
                }
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate
                }
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
             # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate
                }
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate
                }
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate
                }
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
               writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate
                }
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate
                }
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate
                }
             # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate
                }
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0 
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate
                }
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate
                }
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
        # 1 1 0 0 1 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" in measure_code_list and "interperiod_percentage_rate" not in measure_code_list and "annual_puntual_rate" not in measure_code_list and "interperiod_puntual_rate" in measure_code_list:
            # 0 0 0 0 0
            writecontent = {
                'geographical_code': geographical_code, 
                'temporal_code': temporal_code,
                #'measure_code': measure_code,
                'value': absolute,
                'annual_percentage_rate': annual_percentage_rate,
                'interperiod_puntual_rate': interperiod_puntual_rate
            }
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
             # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
               writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
             # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0 
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
        # 1 1 0 1 0 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" in measure_code_list and "interperiod_percentage_rate" not in measure_code_list and "annual_puntual_rate" in measure_code_list and "interperiod_puntual_rate" not in measure_code_list:
            # 0 0 0 0 0
            writecontent = {
                'geographical_code': geographical_code, 
                'temporal_code': temporal_code,
                #'measure_code': measure_code,
                'value': absolute,
                'annual_percentage_rate': annual_percentage_rate,
                'annual_puntual_rate': annual_puntual_rate
            }
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
             # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
               writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
             # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0 
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
        # 1 1 0 1 1 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" in measure_code_list and "interperiod_percentage_rate" not in measure_code_list and "annual_puntual_rate" in measure_code_list and "interperiod_puntual_rate" in measure_code_list:
            # 0 0 0 0 0
            writecontent = {
                'geographical_code': geographical_code, 
                'temporal_code': temporal_code,
                #'measure_code': measure_code,
                'value': absolute,
                'annual_percentage_rate': annual_percentage_rate,
                'annual_puntual_rate': annual_puntual_rate,
                'interperiod_puntual_rate': interperiod_puntual_rate
            }
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
             # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
               writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
             # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0 
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
        # 1 1 1 0 0 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" in measure_code_list and "interperiod_percentage_rate" in measure_code_list and "annual_puntual_rate" not in measure_code_list and "interperiod_puntual_rate" not in measure_code_list:
            # 0 0 0 0 0
            writecontent = {
                'geographical_code': geographical_code, 
                'temporal_code': temporal_code,
                #'measure_code': measure_code,
                'value': absolute,
                'annual_percentage_rate': annual_percentage_rate,
                'interperiod_percentage_rate': interperiod_percentage_rate
            }
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
             # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
               writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
             # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0 
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate
                }
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
        # 1 1 1 0 1 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" in measure_code_list and "interperiod_percentage_rate" in measure_code_list and "annual_puntual_rate" not in measure_code_list and "interperiod_puntual_rate" in measure_code_list:
            # 0 0 0 0 0
            writecontent = {
                'geographical_code': geographical_code, 
                'temporal_code': temporal_code,
                #'measure_code': measure_code,
                'value': absolute,
                'annual_percentage_rate': annual_percentage_rate,
                'interperiod_percentage_rate': interperiod_percentage_rate,
                'interperiod_puntual_rate': interperiod_puntual_rate
            }
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
             # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
               writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
             # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0 
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
        # 1 1 1 1 0 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" in measure_code_list and "interperiod_percentage_rate" in measure_code_list and "annual_puntual_rate" in measure_code_list and "interperiod_puntual_rate" not in measure_code_list:
            # 0 0 0 0 0
            writecontent = {
                'geographical_code': geographical_code, 
                'temporal_code': temporal_code,
                #'measure_code': measure_code,
                'value': absolute,
                'annual_percentage_rate': annual_percentage_rate,
                'interperiod_percentage_rate': interperiod_percentage_rate,
                'annual_puntual_rate': annual_puntual_rate
            }
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
             # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
               writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
             # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0 
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate
                }
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
        # 1 1 1 1 1 (MEASURES AS COLUMNS)
        elif "absolute" in measure_code_list and "annual_percentage_rate" in measure_code_list and "interperiod_percentage_rate" in measure_code_list and "annual_puntual_rate" in measure_code_list and "interperiod_puntual_rate" in measure_code_list:
            # 0 0 0 0 0
            writecontent = {
                'geographical_code': geographical_code, 
                'temporal_code': temporal_code,
                #'measure_code': measure_code,
                'value': absolute,
                'annual_percentage_rate': annual_percentage_rate,
                'interperiod_percentage_rate': interperiod_percentage_rate,
                'annual_puntual_rate': annual_puntual_rate,
                'interperiod_puntual_rate': interperiod_puntual_rate
            }
            # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
            # 0 0 0 1 0
            if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 0 1 0 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 0 1 0 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 0 1 1 0
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
             # 0 0 1 1 1
            elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 0 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 0 1 0
            elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 0 1 1 0 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 1 0 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 0 1 1 1 0
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
               writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 0 1 1 1 1
            elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 0 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 0 1 0
            elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'temporal_code': temporal_code,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 0 1 0 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 0 1 0 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
             # 1 0 1 1 0
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 0 1 1 1
            elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 0 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 0 1 0
            elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }
            # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
            # 1 1 1 0 0 
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 1 0 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate
                }
            # 1 1 1 1 1
            elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
                writecontent = {
                    'geographical_code': geographical_code,
                    'geographical_granularity': geographical_granularity,
                    'geographical_label': geographical_label,
                    'geographical_label_en': geographical_label_en,
                    'temporal_code': temporal_code,
                    'temporal_granularity': temporal_granularity,
                    'temporal_label': temporal_label,
                    'temporal_label_en': temporal_label_en,
                    'date': calculated_date,
                    #'measure_code': measure_code,
                    'value': absolute,
                    'annual_percentage_rate': annual_percentage_rate,
                    'interperiod_percentage_rate': interperiod_percentage_rate,
                    'annual_puntual_rate': annual_puntual_rate,
                    'interperiod_puntual_rate': interperiod_puntual_rate,
                    'measure_unit': measure_unit,
                    'measure_unit_multiplier': measure_unit_multiplier,
                    'measure_unit_symbol': measure_unit_symbol
                }

    else:    
        # 0 0 0 0 0
        writecontent = {
            'geographical_code': geographical_code, 
            'temporal_code': temporal_code,
            'measure_code': measure_code,
            'value': value
        }
        # 0 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activa cuando X X 1 X X)
        # 0 0 0 1 0
        if not self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'temporal_code': temporal_code,
                'measure_code': measure_code,
                'value': value,
                'measure_unit': measure_unit,
                'measure_unit_multiplier': measure_unit_multiplier,
                'measure_unit_symbol': measure_unit_symbol
            }
        # 0 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
        # 0 0 1 0 0
        elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_label': geographical_label,
                'temporal_code': temporal_code,
                'temporal_label': temporal_label,
                'measure_code': measure_code,
                'value': value
            }
        # 0 0 1 0 1
        elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_label': geographical_label,
                'geographical_label_en': geographical_label_en,
                'temporal_code': temporal_code,
                'temporal_label': temporal_label,
                'temporal_label_en': temporal_label_en,
                'measure_code': measure_code,
                'value': value
            }
        # 0 0 1 1 0
        elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_label': geographical_label,
                'temporal_code': temporal_code,
                'temporal_label': temporal_label,
                'measure_code': measure_code,
                'value': value,
                'measure_unit': measure_unit,
                'measure_unit_multiplier': measure_unit_multiplier,
                'measure_unit_symbol': measure_unit_symbol
            }
         # 0 0 1 1 1
        elif not self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_label': geographical_label,
                'geographical_label_en': geographical_label_en,
                'temporal_code': temporal_code,
                'temporal_label': temporal_label,
                'temporal_label_en': temporal_label_en,
                'measure_code': measure_code,
                'value': value,
                'measure_unit': measure_unit,
                'measure_unit_multiplier': measure_unit_multiplier,
                'measure_unit_symbol': measure_unit_symbol
            }
        # 0 1 0 0 0
        elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_granularity': geographical_granularity,
                'temporal_code': temporal_code,
                'temporal_granularity': temporal_granularity,
                'measure_code': measure_code,
                'value': value
            }
        # 0 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
        # 0 1 0 1 0
        elif not self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_granularity': geographical_granularity,
                'temporal_code': temporal_code,
                'temporal_granularity': temporal_granularity,
                'measure_code': measure_code,
                'value': value,
                'measure_unit': measure_unit,
                'measure_unit_multiplier': measure_unit_multiplier,
                'measure_unit_symbol': measure_unit_symbol
            }
        # 0 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
        # 0 1 1 0 0
        elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_granularity': geographical_granularity,
                'geographical_label': geographical_label,
                'temporal_code': temporal_code,
                'temporal_granularity': temporal_granularity,
                'temporal_label': temporal_label,
                'measure_code': measure_code,
                'value': value
            }
        # 0 1 1 0 1
        elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_granularity': geographical_granularity,
                'geographical_label': geographical_label,
                'geographical_label_en': geographical_label_en,
                'temporal_code': temporal_code,
                'temporal_granularity': temporal_granularity,
                'temporal_label': temporal_label,
                'temporal_label_en': temporal_label_en,
                'measure_code': measure_code,
                'value': value
            }
        # 0 1 1 1 0
        elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
           writecontent = {
                'geographical_code': geographical_code,
                'geographical_granularity': geographical_granularity,
                'geographical_label': geographical_label,
                'temporal_code': temporal_code,
                'temporal_granularity': temporal_granularity,
                'temporal_label': temporal_label,
                'measure_code': measure_code,
                'value': value,
                'measure_unit': measure_unit,
                'measure_unit_multiplier': measure_unit_multiplier,
                'measure_unit_symbol': measure_unit_symbol
            }
        # 0 1 1 1 1
        elif not self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_granularity': geographical_granularity,
                'geographical_label': geographical_label,
                'geographical_label_en': geographical_label_en,
                'temporal_code': temporal_code,
                'temporal_granularity': temporal_granularity,
                'temporal_label': temporal_label,
                'temporal_label_en': temporal_label_en,
                'measure_code': measure_code,
                'value': value,
                'measure_unit': measure_unit,
                'measure_unit_multiplier': measure_unit_multiplier,
                'measure_unit_symbol': measure_unit_symbol
            }
        # 1 0 0 0 0
        elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs :
            writecontent = {
                'geographical_code': geographical_code,
                'temporal_code': temporal_code,
                'date': calculated_date,
                'measure_code': measure_code,
                'value': value
            }
        # 1 0 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
        # 1 0 0 1 0
        elif self.date and not self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'temporal_code': temporal_code,
                'date': calculated_date,
                'measure_code': measure_code,
                'value': value,
                'measure_unit': measure_unit,
                'measure_unit_multiplier': measure_unit_multiplier,
                'measure_unit_symbol': measure_unit_symbol
            }
        # 1 0 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
        # 1 0 1 0 0
        elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_label': geographical_label,
                'temporal_code': temporal_code,
                'temporal_label': temporal_label,
                'date': calculated_date,
                'measure_code': measure_code,
                'value': value
            }
        # 1 0 1 0 1
        elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_label': geographical_label,
                'geographical_label_en': geographical_label_en,
                'temporal_code': temporal_code,
                'temporal_label': temporal_label,
                'temporal_label_en': temporal_label_en,
                'date': calculated_date,
                'measure_code': measure_code,
                'value': value
            }
         # 1 0 1 1 0
        elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and not self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_label': geographical_label,
                'temporal_code': temporal_code,
                'temporal_label': temporal_label,
                'date': calculated_date,
                'measure_code': measure_code,
                'value': value,
                'measure_unit': measure_unit,
                'measure_unit_multiplier': measure_unit_multiplier,
                'measure_unit_symbol': measure_unit_symbol
            }
        # 1 0 1 1 1
        elif self.date and not self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_label': geographical_label,
                'geographical_label_en': geographical_label_en,
                'temporal_code': temporal_code,
                'temporal_label': temporal_label,
                'temporal_label_en': temporal_label_en,
                'date': calculated_date,
                'measure_code': measure_code,
                'value': value,
                'measure_unit': measure_unit,
                'measure_unit_multiplier': measure_unit_multiplier,
                'measure_unit_symbol': measure_unit_symbol
            }
        # 1 1 0 0 0
        elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_granularity': geographical_granularity,
                'temporal_code': temporal_code,
                'temporal_granularity': temporal_granularity,
                'date': calculated_date,
                'measure_code': measure_code,
                'value': value
            }
        # 1 1 0 0 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
        # 1 1 0 1 0
        elif self.date and self.geographical_and_temporal_columns and not self.geographical_and_temporal_labels and self.measures_units and not self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_granularity': geographical_granularity,
                'temporal_code': temporal_code,
                'temporal_granularity': temporal_granularity,
                'date': calculated_date,
                'measure_code': measure_code,
                'value': value,
                'measure_unit': measure_unit,
                'measure_unit_multiplier': measure_unit_multiplier,
                'measure_unit_symbol': measure_unit_symbol
            }
        # 1 1 0 1 1 (esta opción nunca ocurre, todos los idimas sólo se activan cuando X X 1 X X)
        # 1 1 1 0 0 
        elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and not self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_granularity': geographical_granularity,
                'geographical_label': geographical_label,
                'temporal_code': temporal_code,
                'temporal_granularity': temporal_granularity,
                'temporal_label': temporal_label,
                'date': calculated_date,
                'measure_code': measure_code,
                'value': value
            }
        # 1 1 1 0 1
        elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and not self.measures_units and self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_granularity': geographical_granularity,
                'geographical_label': geographical_label,
                'geographical_label_en': geographical_label_en,
                'temporal_code': temporal_code,
                'temporal_granularity': temporal_granularity,
                'temporal_label': temporal_label,
                'temporal_label_en': temporal_label_en,
                'date': calculated_date,
                'measure_code': measure_code,
                'value': value
            }
        # 1 1 1 1 1
        elif self.date and self.geographical_and_temporal_columns and self.geographical_and_temporal_labels and self.measures_units and self.langs:
            writecontent = {
                'geographical_code': geographical_code,
                'geographical_granularity': geographical_granularity,
                'geographical_label': geographical_label,
                'geographical_label_en': geographical_label_en,
                'temporal_code': temporal_code,
                'temporal_granularity': temporal_granularity,
                'temporal_label': temporal_label,
                'temporal_label_en': temporal_label_en,
                'date': calculated_date,
                'measure_code': measure_code,
                'value': value,
                'measure_unit': measure_unit,
                'measure_unit_multiplier': measure_unit_multiplier,
                'measure_unit_symbol': measure_unit_symbol
            }

    return writecontent
                    