# OpenStreetMap Data Case Study

### Map Area

#### Northern Colorado, CO United States

* https://www.openstreetmap.org/#map=11/40.5094/-104.9126
* ```geo:40.5094,-104.9126?z=11```

 
I analyzed the selected geo-location because I am from Colorado. Although I did not grow up in Northern Colorado my parents currently reside in this region which is nestled in a cluster of small-to-medium sized cities, triangle between Fort Collins, Greeley and Loveland.

With much growth over the recent years, I thought it would be interesting to analyze how connected the cities are and investigate what kind of problems / improvement suggestions can be made. 


#### Counting the element tags in the file:
```
{'bounds': 1,
 'member': 14280,
 'meta': 1,
 'nd': 521273,
 'node': 452228,
 'note': 1,
 'osm': 1,
 'relation': 633,
 'tag': 183901,
 'way': 48219}
```
#### Finding out formatting scheme of K attribute in tags
 
```{'lower': 123679, 'lower_colon': 57230, 'other': 2992, 'problemchars': 0}```
 
#### Finding unique k (tag attrib['k']) and count
 
 Total number of unique keys ```(tag attrib['k'])``` is 219


After taking a sample from the Northern Colorado area

#### Number of unique users
>993
#### Number of nodes
>1,017,755
#### Number of Ways
>88,531

 ### Problems Encountered in the Map

### Problem encountered  - Postcodes 

We can re-use part of the code in street abbreviation problem and briefly modify it to use it here. Although most of the postcode is correct, there're still a lot of postcode with incorrect 5 digit formats. Like some postcodes have "-" followed by another string of numbers, some postcodes have "CO " attached infront of them, some postcodes are more than 5 digits. All of these cases have been dealt to produce a clean postcode.

The output of the clean postcode is summarised below.

#### Auditing Postal Codes
```
{'80524': {'80524'},
 '80525': {'80525'},
 '80528-8959': {'80528-8959'},
 '80528-9346': {'80528-9346'},
 '80528-9353': {'80528-9353'},
 '80537': {'80537'},
 '80538': {'80538'},
 '80538-8837': {'80538-8837'},
 '80538-9005': {'80538-9005'},
 '80550': {'80550'},
 '80631': {'80631'}}
80525
80631
80538
80538
80537
80524
80528
80528
80528
80538
80550
```
In the above audit of the postcode, SAMPLE_FILE was used and there were no potential errors produced.
However, errors were produced with bigger SAMPLE_FILE and original OSM file which were then corrected.

## Top 10 contributing users

Top 10 contributing users and their contribution:
```
('Mr_Brown', 47,391),
 ('tekim', 33513),
 ('woodpeck_fixbot', 17110),
 ('GPS_dr', 12555),
 ('gpserror', 11880),
 ('dionysis123', 11032),
 ('freaktechnik', 10040),
 ('joelholdsworth', 9390),
 ('champ39', 9073),
 ('MikeM44', 8901)
```

#### Total appearances of the users:
>30,5411

### Top 20 keys in tags with respect to count size
```
('highway', 18702),
 ('building', 6928),
 ('name', 6154),
 ('service', 4133),
 ('county', 3024),
 ('cfcc', 3018),
 ('reviewed', 2637),
 ('name_base', 2483),
 ('access', 2471),
 ('surface', 2275),
 ('source', 2183),
 ('name_type', 2072),
 ('oneway', 2069),
 ('natural', 1916),
 ('barrier', 1522),
 ('power', 1263),
 ('ref', 996),
 ('lanes', 995),
 ('golf', 984),
 ('street', 972)
```
### When was the 1st Contribution made and by whom
1st Contribution to Northern Colorado OSM database was made by user 'DaveHansenTiger' at 03:39 hrs on 2007-09-21

### Top 20 value in tags with respect to count size
```
('service', 9265),
 ('yes', 8493),
 ('residential', 3940),
 ('no', 3362),
 ('A41', 2626),
 ('private', 2167),
 ('parking_aisle', 2093),
 ('house', 1844),
 ('driveway', 1773),
 ('Larimer, CO', 1582),
 ('Weld, CO', 1437),
 ('Bing', 1232),
 ('tree', 1175),
 ('footway', 1162),
 ('turning_circle', 1126),
 ('fence', 1009),
 ('asphalt', 972),
 ('CO', 940),
 ('tower', 796),
 ('1', 693)
```
### Common ammentities
```angular2html
('fast_food', 46),
 ('restaurant', 42),
 ('cafe', 14),
 ('dentist', 13),
 ('post_box', 12),
 ('school', 10),
 ('fuel', 10),
 ('bank', 10),
 ('parking', 8),
 ('bench', 8),
 ('toilets', 7),
 ('charging_station', 7),
 ('shelter', 5),
 ('bicycle_parking', 5),
 ('waste_basket', 4),
 ('drinking_water', 4),
 ('clinic', 4),
 ('fountain', 3),
 ('dojo', 3),
 ('veterinary', 2)
```

### Land usage - "landuse"
```
('grass', 627),
 ('farmland', 84),
 ('residential', 83),
 ('industrial', 39),
 ('farmyard', 20),
 ('reservoir', 15),
 ('commercial', 14),
 ('retail', 13),
 ('recreation_ground', 9),
 ('quarry', 7),
 ('dirt', 3),
 ('basin', 3),
 ('military', 2),
 ('construction', 2),
 ('cemetery', 2),
 ('railway', 1),
 ('meadow', 1),
 ('logistics', 1),
 ('allotments', 1)
```
### File Sizes

```
noco_map.osm.........59.6 MB
nodes_tags.csv...............8 KB
nodes.csv....................2 MB
ways_nodes.csv...............7.6 MB
ways_tags.csv................2.8 MB
ways.csv.....................1.7 MB
```

## Dataset Improvement

Percentage of nodes with footway accessibility information 362 / 6,140 = 0.5.89 which is almost 6%.

Based on the above 2 queries, approximately only 6% of the nodes in the dataset contain foot way accessibility information. That seems like a strikingly low number, even with a large amount of nodes.

### Ideas for additional improvements 

This region is famous for their bicycle culture as indicated in the most common amenities with almost as many bicycle parking than car parking.
```'bicycle_parking', 5``` v.
```'parking', 8```

It would be interesting to investigate bicycle path accessibility, availability, connectedness, etc. against bicycles and other amenities such as footpaths, footways and other elements and rural mix of farm land, city and suburban. 

