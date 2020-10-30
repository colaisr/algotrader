from requests_html import HTMLSession

TRANDINGSTOCKS = ["AAPL", "FB", "ZG", "MSFT", "NVDA", "TSLA", "BEP", "GOOGL"]


def get_tiprank_ratings_to_Stocks(stocks):
    """

    :param stocks: list of stocks to track
    :param path: path to webDriver
    :return: stock-rank dictionary
    """
    stocksRanks={}
    for s in stocks:
        print('Getting tiprank for : '+s)
        url="https://www.tipranks.com/stocks/"+s+"/stock-analysis"
        try:

            session = HTMLSession()

            r = session.get(url)
            r.html.render()

            mark = r.html.find('svg', first=True)
            score = mark.full_text
            stocksRanks[s]=score
            print('Got score of: '+score+' for '+s)

        except Exception as e:
            if hasattr(e, 'message'):
                print("Error in getting info for "+s+": " + str(e.message))
            else:
                print("Error in getting info for "+s+": " + str(e))

            continue

    return stocksRanks

if __name__ == '__main__':
    r=get_tiprank_ratings_to_Stocks(TRANDINGSTOCKS)
    r=3