import scrapy
import sys
import sqlite3
import ConfigParser

class Grappy(scrapy.Spider):
    name = "grappy"

    config = ConfigParser.ConfigParser()
    config.read('config.ini')

    start_urls = [config.get('PAGES', 'LOGIN')]

    #send login form data to login page
    def parse(self, response):
	self.init_db()

        yield scrapy.FormRequest.from_response(
            response,
            formxpath='//form',
            formdata={
                'user[email]': self.config.get('AUTH', 'USERNAME'),         
                'user[password]': self.config.get('AUTH', 'PASSWORD')
            },
            callback=self.after_login
        )

    #check if login was succesful, and proceed with first profile to crawl
    def after_login(self, response):
        if "try again" in response.body:
		self.logger.error("Login error! Make sure the credentials are set in the config.ini file")
            	return
	else:
		self.logger.info('Succesfully logged in, proceed with first profile!')
		baseurl = self.config.get('PAGES', 'START_PROFILE')
		yield response.follow(baseurl, self.action)
    
    #extract data from profile, save it and proceed with next profile
    def action(self, response):
	url = ''
	name = ''
	picture = ''
	details = ''
	dob = ''
	website = ''
	activity = ''
	interests = ''
	favourite = ''
	about = ''

	name = response.css('h1.userProfileName::text').extract()[0].strip()
	picture = response.xpath('//img[@class="profilePictureIcon circularIcon circularIcon--huge circularIcon--border"]/@src').extract()[0]
	url = response.request.url
	titles = response.xpath("//div[@class='infoBoxRowTitle']").extract()
	items = response.xpath("//div[@class='infoBoxRowItem']").extract()

	for i in range(0, len(titles)):
		self.logger.info("key " + titles[i] + " value " + items[i].strip())
		if("Details" in titles[i]):
			details = response.xpath("//div[@class='infoBoxRowItem']")[i].xpath("text()").extract_first().strip().replace("'","`")
		if("Birthday" in titles[i]):
			dob = response.xpath("//div[@class='infoBoxRowItem']")[i].xpath("text()").extract_first().strip().replace("'","`")
		if("Website" in titles[i]):
			website = response.xpath("//div[@class='infoBoxRowItem']")[i].css('a::attr(href)').extract_first().replace("'","`")
		if("Activity" in titles[i]):
			activity = response.xpath("//div[@class='infoBoxRowItem']")[i].xpath("text()").extract_first().strip().replace("'","`")
		if("Interests" in titles[i]):
			interests = response.xpath("//div[@class='infoBoxRowItem']")[i].xpath("text()").extract_first().strip().replace("'","`")
		if("Favorite" in titles[i]):
			favourite = response.xpath("//div[@class='infoBoxRowItem']")[i].xpath("text()").extract_first().strip().replace("'","`")
		if("About" in titles[i]):
			about = response.xpath("//*[contains(@id, 'freeTextContainerdisplay_user')]/text()")[0].extract().replace("'","`")

	
	self.insert(url, name, picture, details, dob, website, activity, interests, favourite, about)
	for href in response.css('div.friendName a::attr(href)'):
            yield response.follow(href, self.action)

    #insert profile information into DB
    def insert(self, url, name, picture, details, dob, website, activity, interests, favourite, about):
	conn = sqlite3.connect(self.config.get('OUTPUT', 'DB'))

	query = "INSERT INTO PROFILE (URL,NAME,PICTURE,DETAILS,DOB, WEBSITE, ACTIVITY, INTERESTS, FAVOURITES, ABOUT) VALUES ('"+url+"','"+name+"','"+picture+"','"+details+"','"+dob+"','"+website+"','"+activity+"','"+interests+"','"+favourite+"','"+about+"')"
	self.logger.info("execute query " + query)
	conn.execute(query)
	conn.commit()
	conn.close()


    #create DB and 'profile' table if nox exist
    def init_db(self):
        conn = sqlite3.connect(self.config.get('OUTPUT', 'DB'))
	self.logger.info("Database created successfully")
	conn.execute('''CREATE TABLE IF NOT EXISTS PROFILE
         (URL		TEXT	NOT NULL,
	 NAME           TEXT,
	 PICTURE	TEXT,
         DETAILS           TEXT,
	 DOB           TEXT,
	 WEBSITE           TEXT,
	 ACTIVITY           TEXT,
	 INTERESTS           TEXT,
	 FAVOURITES           TEXT,
	 ABOUT           TEXT);''')
	self.logger.info("Table created successfully")
	conn.close()
