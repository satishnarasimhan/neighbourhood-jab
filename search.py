# -*- coding: utf-8 -*-
"""
Created on Sat May 15 12:39:53 2021

@author: Satish Narasimhan
"""

#Import Libraries
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import yagmail

def getDaysList(td):
    dates = []
    today = datetime.now()
    
    for n in range(0, td):
        dates.append(
            (today + relativedelta(days=n)).strftime('%d-%m-%Y'))
    return dates   

def getKeysByValue(dictOfElements, valueToFind):
    listOfKeys = list()
    listOfItems = dictOfElements.items()
    for item  in listOfItems:
        if item[1] == valueToFind:
            listOfKeys.append(item[0])
    return  listOfKeys


def extract_element_from_json(obj, path):
    '''
    Credit to Brett Mullins - https://bcmullins.github.io/parsing-json-python/
    Extracts an element from a nested dictionary or
    a list of nested dictionaries along a specified path.
    If the input is a dictionary, a list is returned.
    If the input is a list of dictionary, a list of lists is returned.
    obj - list or dict - input dictionary or list of dictionaries
    path - list - list of strings that form the path to the desired element
    '''
    def extract(obj, path, ind, arr):
        '''
            Extracts an element from a nested dictionary
            along a specified path and returns a list.
            obj - dict - input dictionary
            path - list - list of strings that form the JSON path
            ind - int - starting index
            arr - list - output list
        '''
        key = path[ind]
        if ind + 1 < len(path):
            if isinstance(obj, dict):
                if key in obj.keys():
                    extract(obj.get(key), path, ind + 1, arr)
                else:
                    arr.append(None)
            elif isinstance(obj, list):
                if not obj:
                    arr.append(None)
                else:
                    for item in obj:
                        extract(item, path, ind, arr)
            else:
                arr.append(None)
        if ind + 1 == len(path):
            if isinstance(obj, list):
                if not obj:
                    arr.append(None)
                else:
                    for item in obj:
                        arr.append(item.get(key, None))
            elif isinstance(obj, dict):
                arr.append(obj.get(key, None))
            else:
                arr.append(None)
        return arr
    if isinstance(obj, dict):
        return extract(obj, path, 0, [])
    elif isinstance(obj, list):
        outer_arr = []
        for item in obj:
            outer_arr.append(extract(item, path, 0, []))
        return outer_arr


# Mailing List - From
send_email = 'N'

to ='<<Email id for SMTP configuration>>'

# Area / Location of Subscribers
loc_mapping = {
    "North BLR":[ "560001", "560003", "560005", "560012","560020", "560024",        "560032","560052","560054","560064", "560010", "560094"]
    }

# Mailing List - Subscribers
mailing_list = {
    "emailid1": 'North BLR',
    "emailid2" : 'Central BLR' ,
    "emailid3" : 'South BLR',
    }

# Enter the location you would like to search for
loc = 'North BLR'
# Capturing all relevant recipients for the location
recipients = getKeysByValue(mailing_list, loc)
print("Mail recipients: ")
print(recipients)

pin_code = loc_mapping[loc]
 
print("Pincodes to be searched :")
print(pin_code)
#pin_code = list(set(pin_code.values()))


day = datetime.now()
today = day.strftime("%d-%m-%Y")
day = today #"16-06-2021"

dfObj = pd.DataFrame(columns=['Pincode','Facility','Date','Slots','Min. Age', "Vaccine"])

print("Empty DataFrame:" ,dfObj, sep = '\n' )


for pin in pin_code:
    
    url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={pin}&date={day}"

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

    # If you need continuous polling, uncomment the with clause below
# with requests.session() as session:
    session = requests.session()
    response = session.get(url, headers=headers)
    response = response.json()
    #print (response)
           
    dic = response
            #for i in dic:
            #    print("{}\t{}".format(i,dic[i]))
            
    facility = extract_element_from_json(dic, ["centers","name"])
    address = extract_element_from_json(dic, ["centers","address"])
    session_date = extract_element_from_json(dic, ["centers","sessions","date"])
    avl_slots = extract_element_from_json(dic,["centers","sessions","available_capacity"])
    min_age = extract_element_from_json(dic,["centers","sessions","min_age_limit"])
    time_slot = extract_element_from_json(dic, ["centers","sessions","slots"])
    vaccine = extract_element_from_json(dic, ["centers","sessions","vaccine"])
    dose1_slot = extract_element_from_json(dic, ["centers","sessions","available_capacity_dose1"])
    dose2_slot = extract_element_from_json(dic, ["centers","sessions","available_capacity_dose2"])
    
                   
    # print("Checking for Pincode: "+ pin) 
       
    print(facility)
    s = list(set(session_date))
    print("Checking schedule for the following dates:")
    print(s)
    
    for n in range (len(facility)):
        print ("Facility: "+str(facility[n]))
        for i in range(len(s)):
            print ("Session Date: "+str(session_date[i]))
            if ((dose2_slot[i] != 0) and (str(dose1_slot[i]) != "None") and (min_age[i] != 18) and vaccine[i] != "Covaxin"):
            #if ((dose1_slot[i] != 0) and (str(dose2_slot[i]) != "None") and (min_age[i] != 18)):
                print("Slots available !!")
                send_email = 'Y'
                
                dfObj = dfObj.append(
                    {'Pincode': pin,'Facility': str(facility[n]),'Date':str(session_date[i]),'Slots':str(dose1_slot[i]), 'Min. Age': str(min_age[i]), 'Vaccine':str(vaccine[i])},ignore_index = True)
                
                dose1_slot[i] = 0 # To reset the value
                
            else:                                                       
                print("No slots available")
                print("-----------------") 
                        
                
# Email alert
if (send_email == 'Y'):
    
    uname = to
    
    subject = "Vaccination Slots available for : " + str(loc)
    contents = dfObj #.to_html(index=False)
   
    print (subject)
    print (contents)
       
    yagmail.SMTP(uname).send(to, subject, contents, bcc = recipients)
    print('Email sent successfully . . .')

                