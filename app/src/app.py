from flask import Flask, jsonify, request
from StockData import StockData


app = Flask(__name__)

@app.route('/get/outliers')
def get_outliers():
    stock_exchange = request.args.get('stock_exchange')
    stock_id = request.args.get('stock_id')
    file_no = request.args.get('file_no')

    print(f"{stock_exchange} - {stock_id} - {file_no}")

    sd = StockData(stock_exchange=stock_exchange, stock_ID=stock_id, file_no=file_no)

    print(f"{stock_exchange} - {stock_id} - {file_no}")

    if sd.load_data():
        sd.generate_samples()
        sd.find_outliers()
        sd.save_outliers_to_files()
        return jsonify({"status": "success", "outliers": sd.get_outliers_dict()})
    else:
        return jsonify({"status": "failed", "errors": sd.errors})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)