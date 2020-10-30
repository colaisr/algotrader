from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


TRANDINGSTOCKS = ["AAPL", "FB", "ZG", "MSFT", "NVDA", "TSLA", "BEP", "GOOGL"]


def get_tiprank_ratings_to_Stocks(stocks, path):
    """

    :param stocks: list of stocks to track
    :param path: path to webDriver
    :return: stock-rank dictionary
    """
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

    driver = webdriver.Chrome(path)
    stocksRanks={}
    for s in stocks:
        url="https://www.tipranks.com/stocks/"+s+"/stock-analysis"
        driver.get(url)
        selector="#app > div > div > main > div > div > article > div.client-components-stock-research-tabbed-style__contentArea > div > main > div:nth-child(1) > div.client-components-stock-research-smart-score-style__SmartScore > section.client-components-stock-research-smart-score-style__topSection > div.client-components-stock-research-smart-score-style__rank.client-components-stock-research-smart-score-style__rankSmartScoreTab > div.client-components-stock-research-smart-score-style__OctagonContainer > div > svg > text > tspan"

        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))

            )
            rating = element.text
            stocksRanks[s]=rating

        except Exception as e:

            print(s, "Not found at Tipranks... skipping")
            continue

    driver.quit()
    return stocksRanks

if __name__ == '__main__':
    r=get_tiprank_ratings_to_Stocks(TRANDINGSTOCKS,"/Users/colakamornik/Desktop/algotrader/Research/chromedriverM")
    r=3


