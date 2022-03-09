from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import By
from selenium.webdriver.common.keys import Keys

import pandas as pd

start_page = 0
end_page = 0
url = ""
target_file = ""

driver: webdriver.Chrome = None

is_first_page = True

def init() -> None:
    global start_page, end_page, url, target_file, driver

    start_page = int(input("Starting page: "))
    end_page = int(input("Ending page: "))
    url = input("URL (without the page number, just up to the state): ")
    target_file = input("Target file (where to save): ")

    print("Extracting %d pages (%d->%d) from %s" % ((end_page-start_page)+1, start_page, end_page, url))
    driver = webdriver.Chrome(executable_path="./chromedriver")

def visit_page(page_id: int) -> None:
    global url, driver

    full_url = "%s?page=%d" % (url, page_id)
    print("Visiting page %s..." % (full_url, ))
    driver.get(full_url)

    try:
        # try to find the google vignette ad and close it
        ad_root = driver.find_element(By.ID, "ad_position_box")
    except:
        pass

def is_valid_card(card_element) -> tuple:
    try:
        # try to find the required elements
        header = card_element.find_element(By.CLASS_NAME, "card-header")
        body = card_element.find_element(By.CLASS_NAME, "card-body")
        return (header, body)
    except:
        return (None, None)

def find_company_email(company_name_link) -> str:
    return ""
    """ global driver

    # get the link before changing tab
    company_link = company_name_link.get_attribute("href")
    # get the name of the main tab
    current_tab = driver.current_window_handle
    # open a new tab
    driver.execute_script("window.open('');")
    # get the name of the new tab and switch to it
    new_tab = driver.window_handles[1]
    driver.switch_to.window(new_tab)
    # navigate to the link url
    driver.get(company_link)
    

    result: str = ""
    try:
        # the email link is inside the first element of class "card-text"
        first_card_text_element = driver.find_element(By.CLASS_NAME, "card-text")
        # ...on a <a> element
        link_elements = first_card_text_element.find_elements(By.TAG_NAME, "a")

        for link_element in link_elements:
            element_href: str = link_element.get_attribute("href")
            if element_href.startswith("mailto:"):
                # get the link and remove the "mailto:" part
                result = element_href.replace("mailto:", "")
                print("\t->" + result)
                break
    except:
        pass

    # close the new tab and switch back to the main, just to make sure
    driver.close()
    driver.switch_to.window(current_tab)

    return result """

def append(header, body, book) -> None:
    company_name = ""
    company_address = ""
    company_phone = ""
    company_email = ""

    try:
        company_name_link = header.find_element(By.TAG_NAME, "a")
        company_name = company_name_link.text
        company_email = find_company_email(company_name_link)
    except:
        print("Company name not found!")

    try:
        # get the <p> elements where the information is
        information_points = body.find_elements(By.TAG_NAME, "p")

        # iterate through all of them to search for the address and phone number of the company
        # based on the element's <i> child title
        for information_point in information_points:
            title_element = information_point.find_element(By.TAG_NAME, "i")
            information_point_title = title_element.get_attribute("title")
            if information_point_title == "address":
                company_address = information_point.text
                continue
            elif information_point_title == "phone number":
                company_phone = information_point.text
    except:
        print("Could not find information points!")

    
    book.append([company_name, company_phone, company_address, company_email])
    print("\t%s" % (company_name, ))


def append_current_page() -> None:
    global target_file, driver, is_first_page

    # list of "tuples" for the current page
    book = []

    # wait for div of cards to appear and get the elements from it
    card_container = WebDriverWait(driver, 10000).until(EC.presence_of_element_located((By.CLASS_NAME, "card-columns")))

    # get the cards inside of it
    card_elements = card_container.find_elements(By.CLASS_NAME, "card")

    # iterate through all the elements:
    for card_element in card_elements:
        # check if its an ad or something else and return the header and body elements in a tuple
        header, body = is_valid_card(card_element)
        if header != None and body != None:
            # fetch the info and append to the current page info
            append(header, body, book)
    
    # append to current *target_file*
    print("Adding %d entries to the target file %s..." % (len(book), target_file))
    df = pd.DataFrame(book, columns=["Name", "Phone Number", "Address", "Email"])
    df.to_csv(target_file, index=False, mode="a", header=is_first_page)
    is_first_page = False

if __name__ == "__main__":
    init()
    for page_id in range(start_page, end_page + 1):
        visit_page(page_id)
        append_current_page()