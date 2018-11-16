from istacqgis.controllers import resources

class istacpy:
    
    def get_subjects():
        # Build URL
        api = "indicators"
        path = "subjects"
    
        # Get content
        url = resources.get_url(api, path)
        content = resources.get_content(url)
    
        return content
    
    def get_indicators_code(indicatorcode):
        # URL params
        api = "indicators"
        path = "indicators"
    
        # Get URL
        url = resources.get_url(api, path, resource=indicatorcode)
    
        # Get content
        content = resources.get_content(url)
    
        return content

    def get_indicators(q="", order="", limit=25, offset=0, fields="", representation=""):
        # URL params
        api = "indicators"
        path = "indicators"
    
        # Parse order
        if order is not None:
            order = resources.parse_param(order)
    
        # Parse fields
        if fields is not None:
            fields = resources.parse_param(fields)
    
        # Parse representation
        if representation is not None:
            representation = resources.parse_param(representation)
    
        # Get indicators using query (q) parameter
        if q is not None:
            q = resources.parse_param(q)
            params = "&order=" + order + "&limit=" + str(limit) + "&offset=" + str(
                offset) + "&fields=" + fields + "&representation=" + representation
            path = path + "?q=" + q + params
        else:
            params = "?order=" + order + "&limit=" + str(limit) + "&offset=" + str(
                offset) + "&fields=" + fields + "&representation=" + representation
            path = path + params
    
        # Get URL
        url = resources.get_url(api, path)
    
        # Get content
        content = resources.get_content(url)
    
        return content
    
    def get_indicators_code_data(indicatorcode, representation="", granularity="", fields=""):
        # Parse representation
        if representation is not None:
            representation = resources.parse_param(representation)
    
        # Parse granularity
        if granularity is not None:
            granularity = resources.parse_param(granularity)
    
        # Parse fields
        if fields is not None:
            fields = resources.parse_param(fields)
    
        # Build URL
        api = "indicators"
        path = "indicators"
        resource = indicatorcode + "/data" + "?representation=" + representation + "&granularity=" + granularity + \
                   "&fields=" + fields
        url = resources.get_url(api, path, resource=resource)
    
        # Get content
        content = resources.get_content(url)
    
        return content
    
    def get_codelists_agency_resource_version_codes(agencyid, resourceid, version, limit=25, offset=0, query="", orderby="",
                                                    openness="", order="", fields=""):
        # Parse query
        if query is not None:
            query = resources.parse_param(query)
    
        # Parse orderby
        if orderby is not None:
            orderby = resources.parse_param(orderby)
    
        # Parse fields
        if fields is not None:
            fields = resources.parse_param(fields)
    
        # Build URL
        api = "structural-resources"
        path = "codelists"
        resource = agencyid + "/" + resourceid + "/" + version + "/codes" + ".json"
        params = "?limit=" + str(limit) + "&offset=" + str(offset) + "&query=" + query + "&orderby=" + orderby + \
                 "&openness=" + openness + "&order=" + order + "&fields=" + fields
        resource = resource + params
        url = resources.get_url(api, path, resource)
    
        # Get content
        content = resources.get_content(url)
    
        return content

    def get_codelists(limit=25, offset=0, query="", orderby=""):
        # Parse query
        if query is not None:
            query = resources.parse_param(query)
    
        # Parse orderby
        if orderby is not None:
            orderby = resources.parse_param(orderby)
    
        # Build URL
        api = "structural-resources"
        path = "codelists" + ".json"
        params = "?limit=" + str(limit) + "&offset=" + str(offset) + "&query=" + query + "&orderby=" + orderby
        path = path + params
        url = resources.get_url(api, path)
    
        # Get content
        content = resources.get_content(url)
    
        return content
    
    def get_geographic_granularity_name(self, geographical):
        
        geographical_title_es = ""
        
         # Build URL
        api = "indicators"
        path = "geographicGranularities"
        url = resources.get_url(api, path)
        
        # Get content
        content = resources.get_content(url)
        for geo in content['items']:
            if geo['code'] == geographical:
                geographical_title_es = geo['title']['es']
        
        
        return geographical_title_es
