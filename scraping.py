#!/usr/bin/env python
# coding: utf-8

from email.errors import HeaderMissingRequiredValue
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt
import time

def scrape_all():
    #initiate headless driver for deployment 
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now(), 
      "hemisphere_img_urls": hemisphere_info()}
    print(data)
    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    print(f'visiting{url}')
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Set up the HTML Parser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

# Featured Images 
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    print(f'visiting{url}')
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

# Mars Facts 
def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    
    except BaseException:
        return None

    #Assigning columns to the data frame
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)
    table = df.to_html(classes='table table-striped')
    print(table)
    #convert dataframe to html format, add boostrap
    return table

# CHALLENGE CODE
# Hemisphere data

def init_browser():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser('chrome', **executable_path, headless=True)

def hemisphere_info():
    browser= init_browser()
    url = 'https://marshemispheres.com/'
    print(f'visiting{url}')
    browser.visit(url)
    hemisphere_image_urls= []

    time.sleep(1)

    for i in range(4):
        links = browser.find_by_css("a.product-item img")[i].click()

        html=browser.html
        bs = soup(html, "html.parser")

        title= bs.find('h2', class_= 'title').get_text()
        print(title)
        img_url= bs.find('a', text= 'Sample').get('href')
        full_url = url + img_url
        print(full_url)

        hemispheres = {'title':title, "img_url": full_url}
        hemisphere_image_urls.append(hemispheres)
        browser.back()

    print(hemisphere_image_urls)
    
    browser.quit()
    
    return hemisphere_image_urls


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())