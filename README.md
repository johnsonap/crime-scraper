crime-scraper
=============

Here we have a simple flask application to pull the latest wanted suspects in Bay County, Fla. from the crimestopers web page, seen here:
http://www.pcstips.com/wanteds.aspx

The application uses <a href="http://www.crummy.com/software/BeautifulSoup/">BeautifulSoup</a> to scrape all the suspects from the crimestoppers page, then stores them in a MongoDB store on Heroku (or locally if no heroku environment variables are present).

So far as best I can tell the crimestoppers page is updated once per week, some time on Monday. I use the Temporize Scheduler add-on to run the <code>/updatelists</code> route which scrapes a fresh copy of the suspects.

We also have the index page which provides a nice little front end for displaying them, and also a raw json feed endpoint for possible future outside use. 
