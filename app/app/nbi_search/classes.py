import pandas as pd

# verify dataframe column names
class FIPSData:

    def __init__(self, state_fips_df, county_fips_df, place_fips_df):
        self.state_fips_df = state_fips_df
        self.county_fips_df = county_fips_df
        self.place_fips_df = place_fips_df

    def get_state_name(self, state_id):
        if state_id.isdigit():
            self.state_fips = state_id
            state_name = self.state_fips_df['STATE_NAME'][self.state_fips_df['STATE'] == state_id].values
        else:
            state_fips = self.state_fips_df['STATE'][self.state_fips_df['STUSAB'] == state_id].values
            self.state_fips = state_fips[0]
            state_name = self.state_fips_df['STATE_NAME'][self.state_fips_df['STUSAB'] == state_id].values
        return state_name[0]

    def get_state_postal(self, state_id):
        try:
            state_postal = self.state_fips_df['STUSAB'][self.state_fips_df['STATE'] == state_id].values
            self.state_postal = state_postal[0]
            self.state_fips = state_id
        except:
            state_postal = self.state_fips_df['STUSAB'][self.state_fips_df['STATE_NAME'] == state_id].values
            self.state_postal = state_postal[0]
            state_fips = self.state_fips_df['STATE'][self.state_fips_df['STATE_NAME'] == state_id].values
            self.state_fips = state_fips[0]
        return self.state_postal

    def get_state_fips(self, state_id):
        try:
            state_fips = self.state_fips_df['STATE'][self.state_fips_df['STUSAB'] == state_id].values
            self.state_fips = state_fips[0]
        except:
            state_fips = self.state_fips_df['STATE'][self.state_fips_df['STATE_NAME'] == state_id].values
            self.state_fips = state_fips[0]
        return self.state_fips

    def get_county_name(self, county_fips, state_fips=''):
        if state_fips == '':
            state_fips = self.state_fips
        county_name = self.county_fips_df[3][(self.county_fips_df[1] == state_fips)
                                        & (self.county_fips_df[2] == county_fips)].values
        self.county_name = list(county_name)[0]
        return self.county_name

    def get_county_fips(self, county_name, state_fips=''):
        if state_fips == '':
            state_fips = self.state_fips
        self.county_name = county_name
        county_fips = self.county_fips_df[2][(self.county_fips_df[1] == state_fips)
                                        & (self.county_fips_df[3] == county_name)].values
        self.county_fips = list(county_fips)[0]
        return self.county_fips

    def get_place_name(self, place_fips, county_name='', state_fips=''):
        if state_fips == '':
            state_fips = self.state_fips
        if county_name == '':
            county_name = self.county_name
        place_name = self.place_fips_df['PLACENAME'][(self.place_fips_df['STATEFP'] == state_fips)
                                 & (self.place_fips_df['COUNTY'] == county_name)
                                 & (self.place_fips_df['PLACEFP'] == place_fips)].values
        return place_name[0]

    def get_place_fips(self, place_name, county_name='', state_fips=''):
        if state_fips == '':
            state_fips = self.state_fips
        if county_name == '':
            county_name = self.county_name
        place_fips = self.place_fips_df['PLACEFP'][(self.place_fips_df['STATEFP'] == state_fips)
                                 & (self.place_fips_df['COUNTY'] == county_name)
                                 & (self.place_fips_df['PLACENAME'] == place_name)].values
        return place_fips[0]

    def get_counties(self, state_fips=''):
        if state_fips == '':
            state_fips = self.state_fips
        county_names = self.county_fips_df[3][self.county_fips_df[1] == state_fips].values
        return list(county_names)

    def get_places(self, county_name='', state_fips=''):
        if state_fips == '':
            state_fips = self.state_fips
        if county_name == '':
            county_name = self.county_name
        place_names = self.place_fips_df['PLACENAME'][(self.place_fips_df['STATEFP'] == state_fips)
                                                 & (place_fips_df['COUNTY'] == county_name)]
        return list(place_names)


def create_nbi_filepath(directory, year, state_postal):
    return directory + year + 'del/' + state_postal + year[-2:] + '.txt'

# verify dataframe column names
class NBIBridgeSearch:

    def __init__(self, directory, year, state_postal):
        filepath = create_nbi_filepath(directory, year, state_postal)
        self.state_df = pd.read_csv(filepath, sep=",", dtype=object)
        self.state_df['STRUCTURE_NUMBER_008'] = self.state_df['STRUCTURE_NUMBER_008']\
            .apply(lambda x: str(x).strip())

    def get_county_bridges(self, county_fips):
        self.county_df = self.state_df[self.state_df['COUNTY_CODE_003'] == county_fips]
        return self.county_df

    def get_place_bridges(self, place_fips):
        self.place_df = self.county_df[self.county_df['PLACE_CODE_004'] == place_fips]
        return self.place_df

    def get_bridge_data(self, structure_number):
        self.bridge_data_df = self.state_df[self.state_df['STRUCTURE_NUMBER_008'] == structure_number]
        return self.bridge_data_df

    def export_data(self, output_filepath):
        output_df = self.bridge_data_df
        output_df.to_excel(output_filepath, index=False)

    def format_data(self, code_dict):
        bridge_data = self.bridge_data_df.copy().squeeze()

        def decode(code, code_dict):
            try:
                return code_dict[code]
            except:
                return 'N/A'

        def format_dimension(meter_dimension):
            try:
                meter_to_foot_factor = 3.2808398950131235
                foot_dimension = float(meter_dimension) * meter_to_foot_factor
                return '{0:.2f}'.format(foot_dimension)
            except:
                return 'N/A'

        def format_latitude(latitude_dms):
            try:
                seconds = float(latitude_dms[-4:])/100
                minutes = int(latitude_dms[2:4])
                degrees = int(latitude_dms[0:2])
                return degrees + minutes/60 + seconds/3600
            except:
                return 'N/A'

        def format_longitude(longitude_dms):
            try:
                seconds = float(longitude_dms[-4:])/100
                minutes = int(longitude_dms[3:5])
                degrees = int(longitude_dms[0:3])
                return -1*(degrees + minutes/60 + seconds/3600)
            except:
                return 'N/A'

        def format_tons(metric_tons):
            try:
                metric_to_ton_factor = 1.10231
                tons = float(metric_tons) * metric_to_ton_factor
                return '{0:.1f}'.format(tons)
            except:
                return 'N/A'

        bridge_data['FACILITY_CARRIED_007'] = bridge_data['FACILITY_CARRIED_007'].replace("'", '')
        bridge_data['FEATURES_DESC_006A'] = bridge_data['FEATURES_DESC_006A'].replace("'", '')

        # GENERAL
        bridge_data['OPEN_CLOSED_POSTED_041'] = decode(bridge_data['OPEN_CLOSED_POSTED_041'], code_dict['status_dict'])
        if bridge_data['YEAR_RECONSTRUCTED_106'] == '0':
            bridge_data['YEAR_RECONSTRUCTED_106'] = 'N/A'
        bridge_data['OWNER_022'] = decode(bridge_data['OWNER_022'], code_dict['owner_dict'])
        # LOCATION
        bridge_data['LAT_016'] = format_latitude(bridge_data['LAT_016'])
        bridge_data['LONG_017'] = format_longitude(bridge_data['LONG_017'])
        if bridge_data['STATE_CODE_001'] == '66':
            bridge_data['LONG_017'] = -1 * bridge_data['LONG_017']
        # SERVICE
        bridge_data['SERVICE_ON_042A'] = decode(bridge_data['SERVICE_ON_042A'], code_dict['service_type_dict'])
        bridge_data['FUNCTIONAL_CLASS_026'] = decode(bridge_data['FUNCTIONAL_CLASS_026'], code_dict['functional_classification_dict'])
        bridge_data['ADT_029'] = "{:,}".format(int(bridge_data['ADT_029']))
        # DIMENSIONS
        bridge_data['STRUCTURE_LEN_MT_049'] = format_dimension(bridge_data['STRUCTURE_LEN_MT_049'])
        bridge_data['MAX_SPAN_LEN_MT_048'] = format_dimension(bridge_data['MAX_SPAN_LEN_MT_048'])
        bridge_data['DECK_WIDTH_MT_052'] = format_dimension(bridge_data['DECK_WIDTH_MT_052'])
        bridge_data['ROADWAY_WIDTH_MT_051'] = format_dimension(bridge_data['ROADWAY_WIDTH_MT_051'])
        if bridge_data['VERT_CLR_OVER_MT_053'] == '99.99':
            bridge_data['VERT_CLR_OVER_MT_053'] = '> 325'
        else:
            bridge_data['VERT_CLR_OVER_MT_053'] = format_dimension(float(bridge_data['VERT_CLR_OVER_MT_053']))
        # DESIGN
        bridge_data['STRUCTURE_KIND_043A'] = decode(bridge_data['STRUCTURE_KIND_043A'], code_dict['material_dict'])
        bridge_data['STRUCTURE_TYPE_043B'] = decode(bridge_data['STRUCTURE_TYPE_043B'], code_dict['design_dict'])
        bridge_data['DECK_STRUCTURE_TYPE_107'] = decode(bridge_data['DECK_STRUCTURE_TYPE_107'], code_dict['deck_dict'])
        bridge_data['SURFACE_TYPE_108A'] = decode(bridge_data['SURFACE_TYPE_108A'], code_dict['wearing_surface_dict'])
        bridge_data['DECK_PROTECTION_108C'] = decode(bridge_data['DECK_PROTECTION_108C'], code_dict['deck_protection_dict'])
        bridge_data['DESIGN_LOAD_031'] = decode(bridge_data['DESIGN_LOAD_031'], code_dict['design_load_dict'])
        # LOAD RATING
        bridge_data['OPERATING_RATING_064'] = format_tons(bridge_data['OPERATING_RATING_064'])
        bridge_data['OPR_RATING_METH_063'] = decode(bridge_data['OPR_RATING_METH_063'], code_dict['rating_method_dict'])
        bridge_data['INVENTORY_RATING_066'] = format_tons(bridge_data['INVENTORY_RATING_066'])
        bridge_data['INV_RATING_METH_065'] = decode(bridge_data['INV_RATING_METH_065'], code_dict['rating_method_dict'])

        return bridge_data


def get_near_bridges(search_coordinate, nbi_df, search_radius=0.5):

    from math import radians, cos, sin, asin, sqrt

    def haversine(coord_1, coord_2):
        """
        Calculate the great circle distance in kilometers between two points
        on the earth (specified in decimal degrees)
        """
        lat_1 = coord_1[0]
        lon_1 = coord_1[1]
        lat_2 = coord_2[0]
        lon_2 = coord_2[1]

        # convert decimal degrees to radians
        lat_1, lon_1, lat_2, lon_2,  = map(radians, [lat_1, lon_1, lat_2, lon_2])

        # haversine formula
        d_lat = lat_2 - lat_1
        d_lon = lon_2 - lon_1
        a = sin(d_lat/2)**2 + cos(lat_1) * cos(lat_2) * sin(d_lon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
        return c * r

    latitude = float(search_coordinate.split(',')[0].strip())
    longitude = float(search_coordinate.split(',')[1].strip())
    search_coordinate = [latitude, longitude]

    tolerance = search_radius / 111 # Distance per degree latitude. Divide by 69 for miles.
    low_lat = search_coordinate[0] - tolerance
    high_lat = search_coordinate[0] + tolerance

    search_df = nbi_df.copy()[(nbi_df['LAT_016'] >= low_lat) & (nbi_df['LAT_016'] <= high_lat)]
    search_df['DISTANCE'] = search_df.apply(lambda x: haversine(search_coordinate, [x['LAT_016'], x['LONG_017']]), axis=1)
    near_bridge_df = search_df[search_df['DISTANCE'] <= search_radius].sort_values('DISTANCE')

    return near_bridge_df
