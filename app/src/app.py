from StockData import StockData

stock_exchange = "LSE"
stock_id = "GSK"
file_no = 1

# sd = StockData()
# sd = StockData(file_no=file_no)
# sd = StockData(stock_exchange=stock_exchange)
# sd = StockData(stock_ID=stock_id)
# sd = StockData(stock_exchange=stock_exchange, stock_ID=stock_id)
# sd = StockData(stock_exchange=stock_exchange, file_no=file_no)
# sd = StockData(stock_ID=stock_id, file_no=file_no)
sd = StockData(stock_exchange=stock_exchange, stock_ID=stock_id, file_no=file_no)
print(sd.paths)
if sd.load_data():
    print(f"LENGTH: {len(sd.paths)}, PATHS: {sd.paths}")
    sd.generate_samples()
    print(sd.samples)
    sd.find_outliers()
    print(sd.outliers)
else:
    print(sd.errors)