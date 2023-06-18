import os, json
import pandas as pd
from flask import request

directory = os.getcwd() + '/app/app/nbi_search/data/'
output_filepath = directory + 'nbi_output.xlsx'
year = '2022'

with open(directory + '/nbi_code_dict.json', 'r') as infile:
    nbi_code_dict = json.load(infile)

state_fips_df = pd.read_csv(directory + 'fips/state_fips.txt', sep="|", dtype=str)
county_fips_df = pd.read_csv(directory + 'fips/county_fips.txt', sep=",", dtype=str, header=None)
place_fips_df = pd.read_csv(directory + 'fips/place_fips.txt', sep="|", dtype=str, encoding = "ISO-8859-1")
from app.app.nbi_search.classes import FIPSData


def get_states():
    state_options = [(None, '--select state--')]
    state_options += list(zip(state_fips_df['STUSAB'], state_fips_df['STATE_NAME']))
    remove_list = [
        ('AS', 'American Samoa'),
        ('MP', 'Northern Mariana Islands'),
        ('UM', 'U.S. Minor Outlying Islands')
        ]
    for item in remove_list:
        state_options.remove(item)
    return state_options


def filter_counties(state_postal):
    from app.app.nbi_search.classes import FIPSData
    fips_class = FIPSData(state_fips_df, county_fips_df, place_fips_df)
    fips_class.get_state_fips(state_postal)
    county_names = fips_class.get_counties()
    return county_names


def county_bridges():
    state_postal = request.form['state_postal']
    county_name = request.form['county_name']

    from app.app.nbi_search.classes import FIPSData
    fips_class = FIPSData(state_fips_df, county_fips_df, place_fips_df)
    fips_class.get_state_fips(state_postal)

    from app.app.nbi_search.classes import NBIBridgeSearch
    nbi_class = NBIBridgeSearch(directory, year, state_postal)
    county_fips = fips_class.get_county_fips(county_name)
    county_bridges_df = nbi_class.get_county_bridges(county_fips).copy()
    county_bridges_df['FACILITY_CARRIED_007'] = county_bridges_df['FACILITY_CARRIED_007']\
        .apply(lambda x: str(x).replace("'", ''))
    county_bridges_df['FEATURES_DESC_006A'] = county_bridges_df['FEATURES_DESC_006A']\
        .apply(lambda x: str(x).replace("'", ''))

    bridge_list = county_bridges_df.to_dict('records')
    return bridge_list


def coordinate_bridges():
    search_coordinate = request.form['coordinate']
    nbi_df = pd.read_csv(directory + 'nbi_df.csv', index_col=0)

    from app.app.nbi_search.classes import get_near_bridges
    coordinate_df = get_near_bridges(search_coordinate, nbi_df).to_dict('records')

    return coordinate_df


def search_structure_number():
    structure_number = request.form['structure_number']
    nbi_df = pd.read_csv(directory + 'nbi_df.csv', usecols=['STRUCTURE_NUMBER_008', 'STATE_CODE_001'])
    state_postal = nbi_df[nbi_df['STRUCTURE_NUMBER_008'] == structure_number]['STATE_CODE_001'].values[0]
    bridge_data = return_bridge_properties(state_postal, structure_number)
    return bridge_data


def return_bridge_properties(state_postal, structure_number):

    from app.app.nbi_search.classes import NBIBridgeSearch
    nbi_class = NBIBridgeSearch(directory, year, state_postal)
    bridge_data_df = nbi_class.get_bridge_data(structure_number)
    nbi_class.export_data(output_filepath)
    bridge_data = nbi_class.format_data(nbi_code_dict)

    fips_class = FIPSData(state_fips_df, county_fips_df, place_fips_df)
    bridge_data['STATE_CODE_001'] = fips_class.get_state_name(bridge_data['STATE_CODE_001'])
    bridge_data['COUNTY_CODE_003'] = fips_class.get_county_name(bridge_data['COUNTY_CODE_003'])
    try:
        bridge_data['PLACE_CODE_004'] = fips_class.get_place_name(bridge_data['PLACE_CODE_004'])
    except:
        bridge_data['PLACE_CODE_004'] = 'N/A'

    return bridge_data
