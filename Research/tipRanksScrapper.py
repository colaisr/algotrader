from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


TRANDINGSTOCKS = ["AAPL", "FB", "ZG", "MSFT", "NVDA", "TSLA", "BEP", "GOOGL"]


def getStocksData(stocks,path):
    driver = webdriver.Chrome(path)
    stocksRanks={}
    for s in stocks:
        url="https://www.tipranks.com/stocks/"+s+"/stock-analysis"
        driver.get(url)
        selector="#app > div > div > main > div > div > article > div.client-components-stock-research-tabbed-style__contentArea > div > main > div:nth-child(1) > div.client-components-stock-research-smart-score-style__SmartScore > section.client-components-stock-research-smart-score-style__topSection > div.client-components-stock-research-smart-score-style__rank.client-components-stock-research-smart-score-style__rankSmartScoreTab > div.client-components-stock-research-smart-score-style__OctagonContainer > div > svg > text > tspan"

        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))

            )
            rating = element.text
            stocksRanks[s]=rating

        except:
            print(s, "Not found at Tipranks... skipping")
            continue

    driver.quit()
    return stocksRanks

if __name__ == '__main__':
    r=getStocksData(TRANDINGSTOCKS)
    r=3


