#!/usr/bin/python3

import json
import requests
import sys

schools = '''Barnes Primary School
Wimbledon Park Primary School
Belleville Primary School
Sheringdale Primary School
Sheen Mount Primary School
Grazebrook Primary School
Coldfall Primary School
Earlsfield Primary School
Merton Park Primary School
Bousfield Primary School
Marshgate Primary School
Brandlehow Primary School
Dulwich Hamlet Junior School
Grove Park Primary School
Honeywell Junior School
Gillespie Primary School
Fielding Primary School
Aldersbrook Primary School
Churchfields Junior School
Wells Primary School
Thomson House School
Courtland School
Deansfield Primary School
Deer Park School
The Vineyard School
Telferscot Primary School
Hackney New Primary School
Dundonald Primary School
Honeywell Infant School
Abacus Belsize Primary School
Brindishe Lee School
East Sheen Primary School
William Patten Primary School
Stewart Fleming Primary School
City of London Primary Academy, Islington
Gordonbrock Primary School
Eliot Bank Primary School
Monkfrith Primary School
Kilmorie Primary School
Ambler Primary School and Children’s Centre
Bounds Green Infant School
Wimbledon Chase Primary School
Henry Cavendish Primary School
Harris Primary Academy East Dulwich
Eversley Primary School
Mossbourne Riverside Academy
Haberdashers’ Aske’s Hatcham Temple Grove Free School
Yardley Primary School
Stillness Infant School
Hadley Wood Primary School
Rosendale Primary School
Goldbeaters Primary School
John Ball Primary School
Charles Dickens Primary School
East Lane Primary School
St Stephen’s Primary School
Brindishe Manor School
Shacklewell Primary School
Sherington Primary School
West London Free School Primary
Langford Primary School
Riverside Primary School
Newport School
Brookland Junior School
Riverley Primary School
Tollgate Primary School
Trinity Primary Academy
Sebright School
Britannia Village Primary School
Montpelier Primary School
Strand-on-the-Green Infant and Nursery School
Burnt Ash Primary School
Churchfields Infants’ School
Curwen Primary School
South Grove Primary School
Brooklands Primary School
Brookland Infant and Nursery School
Highlands Primary School
Northside Primary School
London Fields Primary School
Jubilee Primary School
Ark Conway Primary Academy
Mayflower Primary School
Harris Primary Academy Coleraine Park
Noel Park Primary School
Tooting Primary School
Rockmount Primary School
Greenleaf Primary School
Martin Primary School
Globe Primary School
Redriff Primary School
Elmhurst Primary School
Ark Academy
Nightingale Primary School
One Degree Academy
Millennium Primary School
Singlegate Primary School
Jessop Primary School
Whitings Hill Primary School
Shaftesbury Primary School
Priestmead Primary School and Nursery
Dunraven School
Moss Hall Infant School
Oakhill Primary School
The Hyde School
Rathfern Primary School
Brindishe Green School
Springfield Community Primary School
Southwold Primary School
Lionel Primary School
Holmleigh Primary School
Hallsville Primary School
Bowes Primary School
Bigland Green Primary School
Ark Priory Primary Academy
Harris Primary Academy Merton
Highfield Primary School
Kaizen Primary School
Downderry Primary School
Barnfield Primary School
Fullwood Primary School
Selborne Primary School
Galleywall Primary School
Seven Kings School
Vicar’s Green Primary School
Worcesters Primary School
Crampton Primary
Foxfield Primary School
Manorside Primary School
Wykeham Primary School
David Livingstone Academy
Sir William Burrough Primary School
Virginia Primary School
Harris Academy Chobham
Angel Oak Academy
Pimlico Primary
Davies Lane Primary School
Coppetts Wood Primary School
Phoenix Primary School
Cleves Primary School
Barclay Primary School
Redbridge Primary School
The Pears Family School
The Orion Primary School
Ronald Ross Primary School
Thames View Infants
Chesterton Primary School
Marlborough Primary School
Ark John Keats Academy
Ark Isaac Newton Academy
Mowlem Primary School
Willow Brook Primary School Academy
Christchurch Primary School
Paxton Primary School
Ashmole Primary School
Kingfisher Hall Primary Academy
John Donne Primary School
Culloden Primary - A Paradigm Academy
Glebe Primary School
Kensington Primary Academy
Miles Coverdale Primary School
Shoreditch Park Primary School
Wyvil Primary School and Resource Bases for Speech, Language and Communication Needs, and Autism
John Stainer Community Primary School
Harris Academy Tottenham
Sudbourne Primary School
Perivale Primary School
Old Palace Primary School
Cleveland Road Primary School
Granton Primary School
The Woodside Primary Academy
Reay Primary School
Bygrove Primary School
Brackenbury Primary School
Byron Court Primary School
Tidemill Academy
Mount Stewart Junior School
Blue Gate Fields Junior School
Herbert Morrison Primary School
Monega Primary School
Harris Primary Academy Kent House
Ray Lodge Primary School
Parkhill Infants’ School
Oakington Manor Primary School
Gearies Primary School
Old Ford Primary - A Paradigm Academy
Albemarle Primary School
Albion Primary School
St Paul’s Way Trust School
Clapham Manor Primary School
Kensington Primary School
Colegrave Primary School
Sandringham Primary School
Belmont School
Heronsgate Primary School
Kingsmead Primary School
The Willow Primary School
The Willow Primary School
Manorfield Primary School
Harris Primary Academy Philip Lane
Harris Primary Academy Philip Lane
Brampton Primary School
Woodberry Down Community Primary School
Cyril Jackson Primary School
Cyril Jackson Primary School
Selwyn Primary School
Portway Primary School
Mitchell Brook Primary School
Crowland Primary School
Queensbridge Primary School
Ilderton Primary School
Cardwell Primary School
School 21
Hillbrook School
Surrey Square Primary School
Vauxhall Primary School
Delta Primary School
John Ruskin Primary School and Language Classes
Loxford School
Morningside Primary School
Torridon Primary School
Thomas Buxton Primary School
Sheringham Primary School
Essex Primary School
Brentside Primary School
Ashburnham Community School
Tufnell Park Primary School
Millbank Academy
Henry Fawcett Primary School
Rhyl Community Primary School
'''

def main():
    for school in schools.split('\n'):
        print(school, end='\t')
        url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=' + school + ' London&inputtype=textquery&fields=rating&key=' + sys.argv[1]
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        js = json.loads(response.text)
        print(js)

        if js['status'] != 'OK':
            break

        print(js['candidates'][0]['rating'])


if __name__ == '__main__':
    main()
