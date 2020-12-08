#import dependencies
from splinter import Browser
from bs4 import BeautifulSoup as soup


import pandas as pd
import datetime as dt

# set the executable path and initialize the chrome browser in splinter
executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
browser = Browser('chrome', **executable_path)

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)

    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "mars_hemi": mars_hemis(browser),
        #"weather": mars_weather(browser)
    }
    # Stop webdriver and return data
    browser.quit()
    return data       


def mars_news(browser):

    # Scrape Mars News
    # visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # set 1 sec delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

# Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # find and click the full image button
    full_image_elem = browser.find_by_id('full_image')[0]
    full_image_elem.click()

    # find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url


def mars_facts():

    try:
        # Visit Mars facts url 
        facts_url = 'https://space-facts.com/mars/'

        # Use Panda's `read_html` to parse the url
        mars_facts = pd.read_html(facts_url)

        # Find the mars facts DataFrame in the list of DataFrames as assign it to `mars_df`
        mars_df = mars_facts[0]

        # Assign the columns `['Description', 'Value']`
        mars_df.columns = ['Description','Value']

        # Set the index to the `Description` column without row indexing
        mars_df.set_index('Description', inplace=True)

        # Save html code to folder Assets
        returnthis = mars_df.to_html()

        return returnthis

    except BaseException:
        return None   

def mars_hemis(browser):
    # Visit the mars nasa news site
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    mars_soup = soup(html, 'html.parser')
    first_page = mars_soup.find("div", class_='collapsible results')
    sec_page = first_page.find_all('a')

    for item in sec_page[::2]:
        link = item.get('href')
    
        # click on hemisphere link
        item_url = f'https://astrogeology.usgs.gov{link}'
    
        # navigate to full resolution image page
        browser.visit(item_url)
    
        # parse the page html
        html = browser.html
        mars_soup = soup(html, 'html.parser')
    
        # retrieve full resolution image url string and title for each hemi ima
        img_url_rel = mars_soup.select_one('img.wide-image').get("src")
        title = mars_soup.select_one('h2.title').text
  
        # Use the base URL to create an absolute URL
        img_url = f'https://astrogeology.usgs.gov{img_url_rel}'
        hemisphere_image_urls.append({"img_url" :img_url, "title" : title})

    # 4. Print the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())