import pandas as pd
import json
import os
import ast

class OutputHandler:

    @staticmethod
    def create_excel_file(json_obj, output_file="output.xlsx"):

        json_dict = OutputHandler.adjust_json_dict(json_obj)

        pd.DataFrame(json_dict).to_excel(output_file, engine="xlsxwriter")

    @staticmethod
    def adjust_json_dict_old(json_obj):

        if isinstance(json_obj, str):
            json_obj = json.loads(json_obj)

        # print("Adjusting json object")
        dict_list = []
        for key, value in json_obj.items():
            for instance in json_obj[key]['Instances']:
                new_dictionary = {}
                new_dictionary["File name"] = key
                new_dictionary['Title'] = json_obj[key]['Title']
                new_dictionary['Search Terms'] = ', '.join(json_obj[key]['Search terms'])
                new_dictionary['Page Number'] = instance['Page number']
                new_dictionary['Reference'] = instance['Reference']
                dict_list.append(new_dictionary)

        return dict_list

    @staticmethod
    def adjust_json_dict(info_list):

        if isinstance(info_list, str):
            json_obj = ast.literal_eval(info_list)
        else:
            json_obj = info_list

        print("Adjusting json object")
        dict_list = []
        for instance in json_obj:
            new_dictionary = {}
            new_dictionary['Land Use Document type'] = instance[0]
            new_dictionary['Title'] = instance[1]
            new_dictionary['Section #'] = instance[4]
            new_dictionary['Section Title'] = instance[5]
            new_dictionary['Search Terms'] = instance[6]
            new_dictionary['Page Number'] = instance[3]
            new_dictionary['Link'] = f"{instance[2]}#page={instance[3]}"
            new_dictionary['Reference'] = instance[7]
            new_dictionary['Proposed amendement'] = "In Development"
            new_dictionary['Rationale'] = "In Development"
            dict_list.append(new_dictionary)

        return dict_list


# if __name__ == "__main__":
#     test_data = ""
#     # with open('Untitled_2.txt') as test_file:
#     #     test_data = test_file.read()
#     test_data = [['Zoning district', 'Guidelines: Great Northern Way CD-1 Guidelines', 'https://guidelines.vancouver.ca/CD-1/G001.pdf', 5, 'section number', 'section name', 'parking', '2.4 Sustainability  \n(a) Design for Green Mobility through transit -oriented design, emphasis on non- automotive \ntransportati on, appropriate parking standards for cars and bikes, and enhanced \nopportunities for public bike share, car -share and electric vehicles.  \n(b) Create opportunities for sustainable green energy through integration of all new buildings, where feasible, with the SEFC Neighbourhood Energy Utility. '], ['Zoning district', 'Guidelines: Great Northern Way CD-1 Guidelines', 'https://guidelines.vancouver.ca/CD-1/G001.pdf', 6, 'section number', 'section name', 'parking', ' \n3.2 Setbacks  \n(a) Provide a 3- m (10 -ft.) setback along Great Northern Way, west of Carolina St.  \n(b) Provide a 9- m (30 -ft) setback along Great Norther n Way, east of Carolina St, noting that \nthis may be reduced to 3- m (10 -ft) where conditions permit. \n(c) Provide a 15- m (50 -ft.) landscape setback along the westerly and easterly most property \nlines of the CD -1 boundary to be reserved for the commemoration of China and Brewery \nCreeks.  \n(d) Building setbacks from property lines need to be provided and will be analyzed on a site \nby site basis.  Solar performance and other design criteria such as the effect on adjacent \nopen spaces; adjacent building design and use; any other concerns of a similar nature to \nthe foregoing will need to be taken into account.  \n(e) Parking or loading access is not to be located at or above grade in the landscape setbacks.  '], ['Zoning district', 'Guidelines: Great Northern Way CD-1 Guidelines', 'https://guidelines.vancouver.ca/CD-1/G001.pdf', 7, 'section number', 'section name', 'parking', '4.1 Parking Facilities  \n(a) All off -street parking should be located on the site it serves, unless otherwise approved \nby the Director of Planning in consultation with the General Manager of Engineering. \nSome interim surface parking may  be permitted, subject to landscaped setbacks and \nacceptable access points as determined by the Director of Planning in consultation with the General Manager of Engineering Services.  \n(b) No parking or maneuvering is permitted in landscape setbacks. '], ['Zoning district', 'Guidelines: Great Northern Way CD-1 Guidelines', 'https://guidelines.vancouver.ca/CD-1/G001.pdf', 7, 'section number', 'section name', 'parking', '4.3 Parking and Loading Access  \n(a) Where possible, access to parking and loading areas should be fr om the lane. If located \nalong the street, parking and loading should be combined into one entrance and its width should minimize interruption to the streetwall.  \n(b) Shared parking and loading entrances are encouraged for abutting properties.  \n(c) Where load ing access is taken from the street, trucks must not back in from (or onto) the \nstreet and all maneuvering must be done on site.  \n(d) No insulation, piping or mechanical equipment is to be visible from the street unless dealt \nwith in an architectural manner . '], ['Zoning district', 'Guidelines: Great Northern Way CD-1 Guidelines', 'https://guidelines.vancouver.ca/CD-1/G001.pdf', 10, 'section number', 'section name', 'parking', '(b) Proposed Access Road  – A new local road is proposed into the site off Great Northern \nWay at Carolina Street, which will terminate at a cul -de-sac bulb. The new road will be a \nlocal street with provision for on- street parking where appropri ate. The road should have \nlandscaped boulevards, street trees and sidewalks and be designed to prioritize pedestrian \nmovements. Traffic calming devices such as curb bulges should be incorporated into the \ndesign.  ']]
#
#     print(type(test_data))
#     print(test_data)
#     OutputHandler.create_excel_file(test_data)