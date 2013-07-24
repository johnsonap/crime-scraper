crime-scraper
=============

Here we have a simple flask application to pull the latest wanted suspects in Bay County, Fla. from the crimestopers web page, seen here:
http://www.pcstips.com/wanteds.aspx

The application uses BeautifulSoup to scrape all the suspects then store them in a MongoDB store on Heroku (or locally if no heroku environment variables are present).

So far as best I can tell the crimestoppers page is updated once per week, some time on Monday. I use Temporize Scheduler to run the <code>/updatelists</code> route which scrapes a fresh copy of the suspects.
