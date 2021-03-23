# import asyncio
# import time
#
# from requests_html import HTMLSession, AsyncHTMLSession
#
# TRANDINGSTOCKS = ["AAPL", "FB", "ZG", "MSFT", "NVDA", "TSLA", "BEP", "GOOGL"]
# stocksRanks={}
#
#
#
#
# def get_tiprank_ratings_to_Stocks(stocks):
#     """
#
#     :param stocks: list of stocks to track
#     :return: stock-rank dictionary
#     """
#
#
#     try:
#         # asyncio.run(get_all_stocks_ratings(TRANDINGSTOCKS))
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         loop.run_until_complete(get_all_stocks_ratings(TRANDINGSTOCKS))
#         global stocksRanks
#         while len(stocksRanks)==0:
#             time.sleep(1)
#         return stocksRanks
#     except (Exception, KeyboardInterrupt) as e:
#         print('ERROR', str(e))
#
#
#
#
#
# async def get_stock_rank(s):
#     url = "https://www.tipranks.com/stocks/" + s + "/stock-analysis"
#     print("Getting info for "+s)
#     session = AsyncHTMLSession()
#
#     r = await session.get(url)
#     await r.html.arender()
#
#     mark =r.html.find('svg', first=True)
#     score = mark.full_text
#     print('Got score of: ' + score + ' for ' + s)
#     await session.close()
#     return s,score
#
#
# async def get_all_stocks_ratings(stocks):
#     t0 = time.time()
#
#
#     coroutines = [get_stock_rank(url) for url in stocks]
#     results = await asyncio.gather(*coroutines)
#     # completed, pending = await asyncio.wait(coroutines)
#     for s,r in results:
#         global stocksStatistics
#         stocksRanks[s] = r
#
#     t1 = time.time()
#     print(f"{t1-t0} seconds to download {len(stocks)} ratings.")
#
# if __name__ == '__main__':
#     try:
#         dict=get_tiprank_ratings_to_Stocks(TRANDINGSTOCKS)
#         m=2
#     except (Exception, KeyboardInterrupt) as e:
#         print('ERROR', str(e))
