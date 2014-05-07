# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
from geopy import geocoders

#import requests
import time
import urllib2
import re
import sys

def main():

#sudo easy_install geopy
#sudo easy_install BeautifulSoup

	if len(sys.argv) < 2:
		print "Usage: py usnews_ranking_extractor.py <total-pages>"
		sys.exit(0)

	global g
	global kml

	g = geocoders.GoogleV3()
	
	kml = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
  <name>US Colleges</name>
  <description><![CDATA[]]></description>
  <Style id="style1">
    <IconStyle>
      <Icon>
        <href>http://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href>
      </Icon>
      <hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>
    </IconStyle>
  </Style>
	'''

	url_base = "http://colleges.usnews.rankingsandreviews.com/best-colleges/rankings/national-liberal-arts-colleges/page+"
	total = int(sys.argv[1])
	i = 1
	while i <= total:
		i += 1
		getCollegeFromWebPage(getWebPageContent(url_base+str(i)))

	kml += '''
	</Document>
</kml>
	'''

	saveToKML(kml)


def getWebPageContent(url):
	html_page = urllib2.urlopen(url).read()
	return BeautifulSoup(html_page)

def getCollegeFromWebPage(content):
	k = 0
	for school in content.findAll("div",attrs={"class":["school-description school-description-first school-description-odd","school-description school-description-odd","school-description school-description-even", "school-description school-description-last school-description-odd"]}):
		k += 1
		rank = school.find("span", attrs={"rel":".cluetipcontent"}).text
		name = school.find("a", attrs={"class":"school-name"}).text
		link = "http://colleges.usnews.rankingsandreviews.com"+school.find("a", attrs={"class":"school-name"}).get("href")
		print k
		time.sleep(2)
		addr_latitude,addr_longitude = getCoordinatesFromAddress(getAddressFromWebPage(link))
		assembleKML(name, str(addr_latitude), str(addr_longitude))


def getAddressFromWebPage(link):
		address_lines = getWebPageContent(link).find("dl",attrs={"class":"stat address"})
		address = ""
		k = 0
		for address_line in address_lines.findAll("dt"):
			address += address_line.text + ("," if k<1 else "")
			k += 1
		return address

def getCoordinatesFromAddress(address):
	# lat, lang = gmaps.address_to_latlng(address)
	place,(latitude,longitude) = g.geocode(address,exactly_one=True)

	print "%s: %.5f, %.5f" % (place, latitude, longitude)  
	return (latitude, longitude)
	
def assembleKML(name, coord_lat, coord_long):
	global kml

	kml += '''<Placemark>
    <name>'''
	kml += name
	kml += '''</name>
    <styleUrl>#style1</styleUrl>
    <Point>
      <coordinates>'''
	kml += coord_long + "," + coord_lat + "</coordinates>"
	kml += '''
    </Point>
  </Placemark>
		'''


def saveToKML(finalstring):
	f = open("usenews_ranking_college.kml",'w')
	f.write(finalstring.encode('utf-8'))


if __name__ == '__main__':

	g = None
	kml = None
	main()
