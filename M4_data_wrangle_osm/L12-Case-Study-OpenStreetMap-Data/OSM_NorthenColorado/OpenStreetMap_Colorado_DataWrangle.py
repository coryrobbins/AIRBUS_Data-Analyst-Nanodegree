#!/usr/bin/env python
# coding: utf-8

# # Colorado OpenStreetMap Data Wrangling with SQL

# # Map Area
# 
# Northern Colorado, Colorado
# 
# 

# # Downloading OSM XML file and taking a sample out of it

# In[1]:


# OSM XML file and taking a sample out of it
#! pip install cerberus

import xml.etree.ElementTree as ET
import pprint
from collections import defaultdict
import re
import csv
import codecs
import cerberus
#import schema
import sqlite3


PATH = "/Users/coryrobbins/Downloads/noco_map.osm"

OSM_FILE = PATH
SAMPLE_FILE = "sample.osm"
k = 40


# # Getting the elements with tags - nodes and way

# In[2]:


# Getting the elements with tags - nodes and way

def get_element(filename, tags=('node', 'way', 'relation')):
    context = iter(ET.iterparse(filename, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


# # Taking sample from OSM_FILE

# In[3]:




# Taking sample from OSM_FILE

with open(SAMPLE_FILE, 'w') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

# Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(str(ET.tostring(element, encoding='UTF-8')))

    output.write('</osm>')
    output.close()
    


# # Auditing :

# # Counting the element tags in the file

# In[4]:


# Counting the element tags in the file

def count_tags(filename):
    tree=ET.iterparse(filename)
    tags={}
    for event,elem in tree:
        if elem.tag not in tags.keys():
            tags[elem.tag]=1
        else:
            tags[elem.tag] = tags[elem.tag]+1
    return tags    
    
with open(OSM_FILE,'rb') as f:
    tags=count_tags(OSM_FILE)
    pprint.pprint(tags)
f.close()


# # Finding out formatting scheme of K attribute in tags

# In[5]:


# Finding out formatting scheme of K attribute in tags

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        if lower.search(element.attrib['k']):
            keys['lower'] += 1
        elif lower_colon.search(element.attrib['k']):
            keys['lower_colon'] += 1
        elif problemchars.search(element.attrib['k']):
            keys['problemchars'] = keys['problemchars'] + 1
        else:    
            keys['other'] += 1  
#            print element.attrib['k']
#            print element.attrib['v']
    return keys


def process_keys_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

with open(OSM_FILE,'rb') as f:
    keys = process_keys_map(OSM_FILE)
    pprint.pprint(keys)
f.close()    


# # Finding unique k (tag attrib['k']) and count

# In[6]:


# Finding unique k (tag attrib['k']) and count

def unique_keys(filename):
    distinct_keys=[]
    count=1

    EL=get_element(filename, tags=('node', 'way', 'relation'))
    for element in EL:
        if element.tag=='node' or element.tag=='way':
            for tag in element.iter('tag'):
                if tag.attrib['k'] not in distinct_keys:
                    distinct_keys.append(tag.attrib['k'])
                    count+=1
    distinct_keys.sort()
    print("Total number of unique keys (tag attrib['k'])is {}".format(count))
    
#    return distinct_keys
      
    pprint.pprint(distinct_keys)
    
                
unique_keys(SAMPLE_FILE)  # Using Sample file as input to audit the addr:street key

    


# # Finding values(tag attrib['v]) for unique k (tag attrib['k]) and making observation about the data

# In[7]:


#Finding values(tag attrib['v]) for unique k (tag attrib['k]) and making observation about the data

def values_for_unique_keys(filename):

        '''
        # Manually provide the item_name value from the list of distinct_keys to calculate 
        # the values for the corresponding unique key value. We would initialize the key 
        # variable with one value at a time and without iterating so that we could have an idea
        # of what sort of values are there for corresponding key value. Also, we would not iterate
        # as it would a long amount of time to calculate the values for all the corresponding unique
        # key value
        '''
        
        key='addr:street'
        values=[]
        EL=get_element(filename, tags=('node', 'way', 'relation'))
        for element in EL:
            for tag in element.iter('tag'):
                if tag.attrib['k']==key:
                    values.append(tag.attrib['v'])
            element.clear()
        print(key)
        pprint.pprint(values)

        '''
        Using Sample file as input to audit the addr:street key
        '''
values_for_unique_keys(SAMPLE_FILE)  # Using Sample file as input to audit the addr:street key


                    


# # Getting users and count

# In[8]:


# Getting users and count

def get_user(element):
    return element.get('user')


def process_users_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if element.get('user'):
            users.add(get_user(element))
        element.clear()    
    return users


with open(OSM_FILE,'rb') as f:
    users = process_users_map(OSM_FILE)

print(len(users))
#pprint.pprint(users)
f.close()


# # Problem encountered**  - 1

# 1) Street address abbreviation - The main problem we encountered in this dataset come from the street name abbreviation inconsistency. In this following code, we build the regex matching the last element in the string, where usually the street type is based. Then we come up with a list of mapping that need not to be cleaned. See Auditing Street Names. 
# 
# audit_street_type function search the input string for the regex. If there is a match and it is not within the "expected" list, add the match as a key and add the string to the set.
# 
# is_street_name function looks at the attribute k if k="addre:street"
# 
# audit function will return the list that match previous two functions. After that, we can do a pretty print the output of the audit. With the list of all the abbreviated street types we can understand and fill-up our "mapping" dictionary as a preparation to convert these street name into proper form.
# 
# function update_name is the last step of the process, which take the old street name and update them with a better street name.

# # Auditing Street Names

# In[9]:


# Auditing Street Names

'''
We create a regex for the street names and store it in street_type_re. 
Furthermore we create a default dictionary that will include sets of different street names.
Then, we will audit the datafile and look for street names that have an ending that is different to
the values in the expected list.

'''



street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons","Freeway","Circle","Strand","Sterling","Way","Highway",
            "Terrace","South","East","West","North"]

# THIS VARIABLE CONTAINS THE CORRECTIONS
mapping = {
            " St ": " Street ",
            " St.": " Street ",
            " Rd.": " Road ",
            " Rd ": " Road ",
            " Rd": " Road ",
            " Ave ": " Avenue ", 
            " Ave.": " Avenue ",
            " Av ": " Avenue ", 
            " Dr ": " Drive ",
            " Dr.": " Drive",
            " Blvd ": " Boulevard ",
            " Blvd": " Boulevard",
            " Blvd.": " Boulevard",
            " Ct ": " Centre ",
            " Ctr": " Centre",
            " Pl ": " Place ",
            " Ln ": " Lane ",
            " Cir ": " Circle ",
            " Wy": " Way ",
            " S ": " South ",
            " E ": " East ",
            " W ": " West ",
            " N ": "North"
}

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(filename):
    f = open(filename, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(filename, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
            elem.clear()        
    f.close()
    return street_types


def update_name(name, mapping):
    for key,value in mapping.items():
        if key in name:
            return name.replace(key,value)
    return name        
'''
Using the SAMPLE_FILE as an input to audit the street name
'''


st_types = audit(SAMPLE_FILE)

#pprint.pprint(dict(st_types))
for st_type, ways in st_types.items():
    for name in ways:
        better_name = update_name(name, mapping)
        print(name, "=>", better_name)


# In the above audit of the street name, SAMPLE_FILE was used and there were no potential errors produced.However, errors were produced with bigger SAMPLE_FILE and original OSM file which were then corrected.

# # Improving Street Names - Cleaning up and Fixing the Street Names during shape_element function

# In[10]:


# Cleaning up and Fixing the Street Names

'''
Now we are going to do some data cleaning to enhance the data quality of the street names.
We have identified sets of street name endings that have been expected. Through a a mapping dictionary we 
indicate the desired changes. We do this for the street name endings (mapping).
'''




street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons","Freeway","Circle","Strand","Sterling","Way","Highway",
            "Terrace","South","East","West","North"]

# UPDATE THIS VARIABLE
mapping = {
            " St ": " Street ",
            " St.": " Street ",
            " Rd.": " Road ",
            " Rd ": " Road ",
            " Rd": " Road ",
            " Ave ": " Avenue ", 
            " Ave.": " Avenue ",
            " Av ": " Avenue ", 
            " Dr ": " Drive ",
            " Dr.": " Drive",
            " Blvd ": " Boulevard ",
            " Blvd": " Boulevard",
            " Blvd.": " Boulevard",
            " Ct ": " Centre ",
            " Ctr": " Centre",
            " Pl ": " Place ",
            " Ln ": " Lane ",
            " Cir ": " Circle ",
            " Wy": " Way ",
            " S ": " South ",
            " E ": " East ",
            " W ": " West ",
            " N ": "North"
}


'''
The update name function implements the change. If a street name has the defined string which is defined in the mapping
dictionary, then the change is made as defined.
'''

'''
Below 2 functions would be used during shape_element function execution to formatt the street name

'''

def update_street_name(name, mapping):
    for key,value in mapping.items():
        if key in name:
            return name.replace(key,value)
    return name        

def audit_street_name_tag(element): 
    street_name=element.get('v')
    m = street_type_re.search(street_name)
    if m:
        better_street_name=update_street_name(street_name,mapping)
        return better_street_name
    return street_name
              


# # Problem encountered**  - 2

# 2) Postcodes - We can re-use part of the code in street abbreviation problem and briefly modify it to use it here. Although most of the postcode is correct, there're still a lot of  postcode with incorrect 5 digit formats. Like some postcodes have "-" followed by another string of numbers, some postcodes have "CO " attached infront of them, some postcodes are more than 5 digits. All of these cases have been dealt to produce a clean postcode.
# 
# The output of the clean postcode is summarised below. 

# # Auditing Postal Codes  

# In[11]:


# Auditing Postal Codes

'''
In this Section we are going to audit postal 
codes to check for potential errors. 
This is a very similar process compared to
to our cleaning street name strategy

'''

zip_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

zip_types = defaultdict(set)

expected_zip = {}

def audit_zip_codes(zip_types, zip_name, regex, expected_zip):
    m = regex.search(zip_name)
    if m:
        zip_type = m.group()
        if zip_type not in expected_zip:
             zip_types[zip_type].add(zip_name)

def is_zip_name(elem):
    return (elem.attrib['k'] == "addr:postcode")


def audit(filename, regex):
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "way" or elem.tag == "node":
            for tag in elem.iter("tag"):
                if is_zip_name(tag):
                    audit_zip_codes(zip_types, tag.attrib['v'], regex, expected_zip)
    pprint.pprint(dict(zip_types))


'''
Using the SAMPLE_FILE as an input to audit the postcodes
'''   
    
audit(SAMPLE_FILE, zip_type_re)


for zip_type, ways in zip_types.items(): 
        for name in ways:
            if "-" in name:
                name = name.split("-")[0].strip()
            if "CO " in name:
                name = name.split("CO ")[1].strip('CO ')
            elif len(str(name))>5:
                name=name[0:5]
            elif name.isdigit()==False:
                print('OK')
            print(name)  



 
                
        


# In the above audit of the postcode, SAMPLE_FILE was used and there were no potential errors produced.However, errors were produced with bigger SAMPLE_FILE and original OSM file which were then corrected.

# # Cleaning and Fixing Postal Codes during the shape_element function

# In[12]:


'''
We want to have all postal codes in the standard 5 digit display. This means we have to change the postal codes 
that have more than 5 digits, the ones that beginn with "CO" and any other ones that differ from the the plain 5
digit display.
'''


'''
Below 2 functions would be used during shape_element function execution to formatt the postcode
'''


def update_postcode(name): 
    if "-" in name:
        name = name.split("-")[0].strip()
    elif "CO" in name:
        name = name.split("CO ")[1].strip('CO ')
    elif len(str(name))>5:
        name=name[0:5]
    elif name.isdigit()==False:
         name=00000
    return name



def audit_postcode_tag(element,regex=re.compile(r'\b\S+\.?$', re.IGNORECASE)):
    post_code=element.get('v')
    m = regex.search(post_code)
    if m:
        better_postcode=update_postcode(post_code)
        return better_postcode
    return post_code
        


# # Preparing for Database - SQL

# In[13]:


'''
Note: The schema is stored in a .py file in order to take advantage of the
int() and float() type coercion functions. Otherwise it could easily stored as
as JSON or another serialized format.
'''

schema = {
   'node': {
       'type': 'dict',
       'schema': {
           'id': {'required': True, 'type': 'integer', 'coerce': int},
           'lat': {'required': True, 'type': 'float', 'coerce': float},
           'lon': {'required': True, 'type': 'float', 'coerce': float},
           'user': {'required': True, 'type': 'string'},
           'uid': {'required': True, 'type': 'integer', 'coerce': int},
           'version': {'required': True, 'type': 'string'},
           'changeset': {'required': True, 'type': 'integer', 'coerce': int},
           'timestamp': {'required': True, 'type': 'string'}
       }
   },
   'node_tags': {
       'type': 'list',
       'schema': {
           'type': 'dict',
           'schema': {
               'id': {'required': True, 'type': 'integer', 'coerce': int},
               'key': {'required': True, 'type': 'string'},
               'value': {'required': True, 'type': 'string'},
               'type': {'required': True, 'type': 'string'}
           }
       }
   },
   'way': {
       'type': 'dict',
       'schema': {
           'id': {'required': True, 'type': 'integer', 'coerce': int},
           'user': {'required': True, 'type': 'string'},
           'uid': {'required': True, 'type': 'integer', 'coerce': int},
           'version': {'required': True, 'type': 'string'},
           'changeset': {'required': True, 'type': 'integer', 'coerce': int},
           'timestamp': {'required': True, 'type': 'string'}
       }
   },
   'way_nodes': {
       'type': 'list',
       'schema': {
           'type': 'dict',
           'schema': {
               'id': {'required': True, 'type': 'integer', 'coerce': int},
               'node_id': {'required': True, 'type': 'integer', 'coerce': int},
               'position': {'required': True, 'type': 'integer', 'coerce': int}
           }
       }
   },
   'way_tags': {
       'type': 'list',
       'schema': {
           'type': 'dict',
           'schema': {
               'id': {'required': True, 'type': 'integer', 'coerce': int},
               'key': {'required': True, 'type': 'string'},
               'value': {'required': True, 'type': 'string'},
               'type': {'required': True, 'type': 'string'}
           }
       }
   }
}


# # Defining CSV Files and their respective columns

# In[14]:


NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


SCHEMA = schema


NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


# # Shaping up the element

# In[15]:


"""Clean and shape node or way XML element to Python dict"""

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                 problem_chars=PROBLEMCHARS, default_tag_type='regular'):
   
   
   node_attribs = {}
   way_attribs = {}
   way_nodes = []
   tags = [] # Handle secondary tags the same way for both node and way elements
            

  

   if element.tag=='node':
       for field in node_attr_fields:
           node_attribs[field]=element.get(field)
                
       if element.find('tag') is None:
           pass
#           print 'No Tags'
          
       elif element.find('tag') is not None:
           tag_attrib={}
           node_tag_fields=NODE_TAGS_FIELDS
           for tag in element.iter('tag'):
               if PROBLEMCHARS.search(tag.attrib['k']):
                   pass
               elif LOWER_COLON.search(tag.attrib['k']):
                   tag_attrib[node_tag_fields[0]]=element.get('id')
                   tag_attrib[node_tag_fields[1]]=tag.get('k')[(tag.get('k').find(':')+1):]
                   if tag.attrib['k']== "addr:street":
                       tag_attrib[node_tag_fields[2]]=audit_street_name_tag(tag)
                   elif tag.attrib['k']== "addr:postcode":
                       tag_attrib[node_tag_fields[2]]=audit_postcode_tag(tag)       
                   else:
                       tag_attrib[node_tag_fields[2]]=tag.get('v')
                   tag_attrib[node_tag_fields[3]]=tag.get('k').split(':')[0]
                   tags.append(tag_attrib.copy())
               
               else:
                   tag_attrib[node_tag_fields[0]]=element.get('id')
                   tag_attrib[node_tag_fields[1]]=tag.get('k')
                   if tag.attrib['k']== "addr:street":
                       tag_attrib[node_tag_fields[2]]=audit_street_name_tag(tag)
                   elif tag.attrib['k']== "addr:postcode":
                       tag_attrib[node_tag_fields[2]]=audit_postcode_tag(tag)    
                   else:    
                       tag_attrib[node_tag_fields[2]]=tag.get('v')
                   tag_attrib[node_tag_fields[3]]=default_tag_type
                   tags.append(tag_attrib.copy())
           
#        pprint.pprint( {'node':node_attribs,'node_tags':tags})  
       
               
   elif element.tag=='way':
       for field in way_attr_fields:
           way_attribs[field]=element.get(field)
   
       way_node_attrib={}
       way_node_fields=WAY_NODES_FIELDS
       for nd in element.findall('nd'):
           way_node_attrib[way_node_fields[0]]=element.get('id')
           way_node_attrib[way_node_fields[1]]=nd.get('ref')
           way_node_attrib[way_node_fields[2]]=element.findall('nd').index(nd)
           way_nodes.append(way_node_attrib.copy())
#       pprint.pprint({'way':way_attribs,'way_nodes':way_nodes})
       
       
       
       
       if element.find('tag') is None:
           pass
#           print 'No Tags'
          
       elif element.find('tag') is not None:
           way_tag_attrib={}
           way_tag_fields=WAY_TAGS_FIELDS
           for tag in element.iter('tag'):
               if PROBLEMCHARS.search(tag.attrib['k']):
                   pass
               elif LOWER_COLON.search(tag.attrib['k']):
                   way_tag_attrib[way_tag_fields[0]]=element.get('id')
                   way_tag_attrib[way_tag_fields[1]]=tag.get('k')[(tag.get('k').find(':')+1):]
                   if tag.attrib['k']== "addr:street":
                       way_tag_attrib[way_tag_fields[2]]=audit_street_name_tag(tag)
                   elif tag.attrib['k']== "addr:postcode":
                       way_tag_attrib[way_tag_fields[2]]=audit_postcode_tag(tag)    
                   else:
                       way_tag_attrib[way_tag_fields[2]]=tag.get('v')
                   way_tag_attrib[way_tag_fields[3]]=tag.get('k').split(':')[0]
                   tags.append(way_tag_attrib.copy())
                   
               else:
                   way_tag_attrib[way_tag_fields[0]]=element.get('id')
                   way_tag_attrib[way_tag_fields[1]]=tag.get('k')
                   if tag.attrib['k']== "addr:street":
                       way_tag_attrib[way_tag_fields[2]]=audit_street_name_tag(tag) 
                   elif tag.attrib['k']== "addr:postcode":
                       way_tag_attrib[way_tag_fields[2]]=audit_postcode_tag(tag)    
                   else:   
                       way_tag_attrib[way_tag_fields[2]]=tag.get('v')
                   way_tag_attrib[way_tag_fields[3]]=default_tag_type
                   tags.append(way_tag_attrib.copy())
#        pprint.pprint({'way':way_attribs,'way_tags':tags})
#        pprint.pprint({'way':way_attribs,'way_nodes':way_nodes,'way_tags':tags})
       
   

   
   if element.tag == 'node':
       return {'node': node_attribs, 'node_tags': tags}
   elif element.tag == 'way':
       return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
 



    


# # Helper function - Validating the element

# In[16]:


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


# # Helper function - UnicodeDictWriter

# In[17]:


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow(row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# # Writing CSV Files

# In[18]:


def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


# # Loading the data into CSV file from OSM File

# In[19]:


process_map(OSM_FILE, validate=True)


# # Creating and Connecting to SQL database 

# In[20]:


db = sqlite3.connect("northern-colorado")  # Connect to the database
                                
c = db.cursor() # Get a cursor object


# # Creating nodes table

# In[21]:


# creating nodes table in database northernColorado and inserting values into table nodes

query="DROP TABLE IF EXISTS nodes;" # Dropping the table if it already exists
c.execute(query);
db.commit()
query = "CREATE TABLE nodes (id INTEGER PRIMARY KEY NOT NULL,lat REAL,lon REAL,user TEXT,uid INTEGER,version INTEGER,changeset INTEGER,timestamp TEXT);"
c.execute(query)
db.commit()

# Read in the csv file as a dictionary, format the data as a list of tuples:

with open('nodes.csv','rt') as f: 
    dr = csv.DictReader(f)
    to_db = [(i['id'],i['lat'],i['lon'],i['user'],i['uid'],i['version'],i['changeset'],i['timestamp']) for i in dr]
    
# insert the formatted data

c.executemany("INSERT INTO nodes (id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?,?,?,?,?,?,?,?);", to_db)
db.commit()
f.close()


# # Creating nodes_tags table

# In[22]:


# creating nodes_tags table in database northern colorado and inserting values into table nodes_tags

query="DROP TABLE IF EXISTS nodes_tags;"  # Dropping the table if it already exists
c.execute(query);
db.commit()
query = "CREATE TABLE nodes_tags (id INTEGER,key TEXT,value TEXT,type TEXT,FOREIGN KEY (id) REFERENCES nodes(id));"
c.execute(query)
db.commit()

# Read in the csv file as a dictionary, format the data as a list of tuples:

with open('nodes_tags.csv','rt') as f: 
    dr = csv.DictReader(f)
    to_db = [(i['id'],i['key'],i['value'],i['type']) for i in dr]

# insert the formatted data

c.executemany("INSERT INTO nodes_tags (id, key, value, type) VALUES (?,?,?,?);", to_db)
db.commit()
f.close()


# # Creating ways table

# In[23]:


# creating ways table in database northern colorado and inserting values into table ways

query="DROP TABLE IF EXISTS ways;"   # Dropping the table if it already exists
c.execute(query);
db.commit()
query = "CREATE TABLE ways(id INTEGER PRIMARY KEY NOT NULL,user TEXT,uid INTEGER,version TEXT,changeset INTEGER,timestamp TEXT);"
c.execute(query)
db.commit()

# Read in the csv file as a dictionary, format the data as a list of tuples:

with open('ways.csv','rt') as f: 
    dr = csv.DictReader(f)
    to_db = [(i['id'],i['user'],i['uid'],i['version'],i['changeset'],i['timestamp']) for i in dr]

# insert the formatted data        
    
c.executemany("INSERT INTO ways (id, user, uid, version, changeset, timestamp) VALUES (?,?,?,?,?,?);", to_db)
db.commit()
f.close()


# # Creating ways_nodes table

# In[24]:


# creating ways_nodes table in database northern_colorado and inserting values into table ways_nodes

query="DROP TABLE IF EXISTS ways_nodes;"  # Dropping the table if it already exists
c.execute(query);
db.commit()
query = "CREATE TABLE ways_nodes (id INTEGER NOT NULL,node_id INTEGER NOT NULL,position INTEGER NOT NULL,FOREIGN KEY (id) REFERENCES ways(id),FOREIGN KEY (node_id) REFERENCES nodes(id));"
c.execute(query)
db.commit()

# Read in the csv file as a dictionary, format the data as a list of tuples:

with open('ways_nodes.csv','rt') as f: 
    dr = csv.DictReader(f)
    to_db = [(i['id'],i['node_id'],i['position']) for i in dr]

    
# insert the formatted data 
    
c.executemany("INSERT INTO ways_nodes (id, node_id, position) VALUES (?,?,?);", to_db)
db.commit()
f.close()



# # Creating ways_tags table

# In[25]:


# creating ways_tags table in database northen colorado and inserting values into table ways_nodes

query="DROP TABLE IF EXISTS ways_tags;"   # Dropping the table if it already exists
c.execute(query);
db.commit()
query = "CREATE TABLE ways_tags (id INTEGER NOT NULL,key TEXT NOT NULL,value TEXT NOT NULL,type TEXT,FOREIGN KEY (id) REFERENCES ways(id));"
c.execute(query)
db.commit()


# Read in the csv file as a dictionary, format the data as a list of tuples:

with open('ways_tags.csv','rt') as f: 
    dr = csv.DictReader(f)
    to_db = [(i['id'],i['key'],i['value'],i['type']) for i in dr]

# insert the formatted data 

c.executemany("INSERT INTO ways_tags (id, key, value, type) VALUES (?,?,?,?);", to_db)
db.commit()
f.close()


# # Overview of The Data

# This section contains basic statistics about the Northern Colorado OpenStreetMap dataset and the SQL queries used to gather them.

# # File sizes - 

# northerncolorado.osm,
# northern-colorado.db,
# nodes.csv,
# nodes_tags.csv,
# ways.csv,
# ways_nodes.csv,
# ways_tags.csv

# # Number of unique users

# In[26]:


query = "SELECT COUNT(DISTINCT(e.uid))FROM (SELECT uid FROM Nodes UNION ALL SELECT uid FROM Ways) as e;"
c.execute(query)
rows=c.fetchall()

pprint.pprint(rows)


# Number of Unique Users is 993.

# # Number of nodes

# In[27]:


query = "SELECT count(DISTINCT(id)) FROM nodes;"
c.execute(query)
rows=c.fetchall()

pprint.pprint(rows)


# Number of Nodes is  1017755.

# # Number of Ways

# In[28]:


query = "SELECT count(DISTINCT(id)) FROM ways;"
c.execute(query)
rows=c.fetchall()

pprint.pprint(rows)


# Number of ways are 88531.

# # Number of chosen type of nodes

# In[30]:


# number of chosen type of nodes

query = "SELECT type , count(*) as num FROM nodes_tags group by type order by num desc;"
c.execute(query)
rows=c.fetchall()

pprint.pprint(rows)


# In[31]:


# number of chosen type of nodes, like cafes, shops etc.

query = "SELECT value, count(*) FROM (select key,value from nodes_tags UNION ALL select key,value from ways_tags) as e where value like '%cafe%';"
c.execute(query)
rows=c.fetchall()

pprint.pprint(rows)


print('\n')

query = "SELECT value, count(*)  FROM (select key,value from nodes_tags UNION ALL select key,value from ways_tags) as e where value like 'shop%';"
c.execute(query)
rows=c.fetchall()

pprint.pprint(rows)


# # Top 10 contributing users

# In[41]:


#Top 10 contributing users

query = "select e.user, count(*) as num from (select user from nodes UNION ALL select user from ways) as e group by user order by num desc limit 10;"
c.execute(query)
rows=c.fetchall()
print('Top 10 contributing users and their contribution:\n')
pprint.pprint(rows)



#Total users
print('\n')
print('Total appearances of the users:\n')
query = "select count(e.user) from (select user from nodes UNION ALL select user from ways) as e;"
c.execute(query)
rows=c.fetchall()

pprint.pprint(rows)


# # Top 20 keys in tags with respect to count size

# In[42]:


#Top 20 keys in tags with respect to count size

query = "select e.key , count(*) as num from (select key from nodes_tags UNION ALL select key from ways_tags) as e group by e.key order by num desc limit 20;"
c.execute(query)
rows=c.fetchall()

pprint.pprint(rows)


# From the above query, it is observed that tags with K value 'Source' occured maximum time.

# # Top 20 value in tags with respect to count size

# In[43]:


#Top 20 value in tags with respect to count size

query = "select e.value, count(e.value) as num from (select value from nodes_tags UNION ALL select value from ways_tags) as e group by value order by num desc limit 20;"
c.execute(query)
rows=c.fetchall()

pprint.pprint(rows)


# From the above query, it is observed that tags with v value 'US' occured maximum time.

# # when was the 1st Contribution made and by whom

# In[44]:


query = "select e.user, e.timestamp as num from (select user,timestamp from nodes UNION ALL select user,timestamp from ways) as e order by num limit 1;"
c.execute(query)
rows=c.fetchall()

pprint.pprint(rows)


# 1st Contribution to Northern Colorado OSM database was made by user 'DaveHansenTiger' at 03:39 hrs on 2007-09-21

# # List of keys where type is addr

# In[45]:


query="select DISTINCT(key) from nodes_tags where type='addr';"
c.execute(query)
rows=c.fetchall()

pprint.pprint(rows)


# # Common ammenities

# In[46]:


query="select value, count(*) as num from nodes_tags where key='amenity' group by value order by num desc limit 20;"
c.execute(query)
rows=c.fetchall()

pprint.pprint(rows)


# # Land usage - "landuse"

# In[47]:


query="select value, count(*) as num from (select key,value from nodes_tags UNION ALL select key,value from ways_tags) as e  where key='landuse' group by value order by num desc;"
c.execute(query)
rows=c.fetchall()

pprint.pprint(rows)


# # Dataset Improvement

# # Percentage of footways accessible nodes

# In[48]:


query="select count(*) from (select key,value from nodes_tags UNION ALL select key,value from ways_tags) as e  where key like '%footway%';"
c.execute(query)
rows=c.fetchall()

pprint.pprint(rows)


# # Number of nodes

# In[40]:


query="select count(DISTINCT(id)) from  nodes_tags;"
c.execute(query)
rows=c.fetchall()

pprint.pprint(rows)


# # Percentage of nodes with footway accessibility information

# 76/310 = 0.245 which is almost 25.
# 
# Based on the above 2 queries, approximately 25% of the nodes in the dataset contain foot way accessibility information. That seems like a strikingly low number, even with a large amount of nodes. 

# # Ideas for additional improvements 

# It would be interesting to see the bike path accessability for this region. Given the region is a mix of rural and urban, improvments can be made to find which footways and bikeways are connected. 

# # Anticipated problems in implementing the improvement

# 1) One difficulty would be dealing with the lack of data or inconsistencies between different data sources as the region is quire rural and is a cluster of small cities, nodes already in the OpenStreetMap dataset, though this could be overcome with careful string handling and a human verifying inputted data.
# 
# 2) Amount of effort to engineer all these processes and the cost of creating, auditing & maintaining these initiatives could be so overwhelm and may require a dedicated team responsible for all these projects.

# # Conclusion

# The Northern Colorado OpenStreetMap dataset is too small. When I audit the data, much of the data doens't exist. Considering there are many contributors, there are number of gaps in this dataset. I'd recommend a srtuctured input form so everyone can input the same data format to reduce this error or we can create a more robust script to clean the data on a regular basis.While it is clear that the data is not 100% clean, I believe it was sufficiently cleaned for the purposes of this project.A detailed investigation could also be done to identify which users created the features with incorrect or mismatched values in order to potentially identify additional documents for closer scrutiny or to predict what types of users are more prone to producing errors.This dataset shows the need for a standardized data schema, as well as the difficulty of having many different data sources and having information which needs to be constantly updated.
