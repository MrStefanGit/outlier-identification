# outlier-identification

## Description

A python application inside a Docker container that expodes an API and can identify outliers in time-series data. It uses generated stock data stored in csv files.

### Outlier detection method

First step in outlier detection is to extract a sample of 30 data points starting from a random timestamp inside the files. The files are determined by the input parameters stock_exhange, stock_id, file_no.

After the sample data is selected the outliers are identified by comparing all the values with a computed threshhold, any values lower or higher than the treshold are considered outliers.

The threshold is calculated with the following formula:

```python
upper_limit = mean + 2 * standard_deviation
lower_limit = mean - 2 * standard_deviation
```

Where mean is the computed mean of the values from the selected data and standard_deviation is the standard deviation computed from the selected data.

After the outliers are identified they are saved in the output directory in a csv file. One csv file for each stock_id, grouped in folders for each stock_exhange.

## Folder structure

```yaml
docker-compose.yml # docker-compose file that runs the application
app:
    Dockerfile # Image definition for the docker container
    requirements.txt # Python dependencies for the application
    src:
        StockData.py # Python class that handles all data related functions
        app.py # Python file that handles API requests
        stock_price_data_files: # Directory that contains the stock data files
            STOCK_EXCHANGE:
                STOCK_ID.csv
outlier_files_output: # Output folder for storing outliers in csv files
    request_timestamp: # Folder for specific request
        STOCK_EXCHANGE:
            STOCK_ID.csv
```

## API endpoints

The app exposes an api having the following endponts:

| ENDPOINT | PATH | DESCRIPTION | PARAMETERS |
| :------: | :--: | :---------: | :--------: |
|GET_OULIERS_FROM_STOCK_DATA|/get/outliers|Returns a json object for the stocks selected trough the input parameters|stock_exhange, stock_id, file_no|

## Running the application

### Docker

Just run `docker-compose up -d --build` and it should create a container running the application. By default the application will run on port 8080, but you can change that in the docker-compose.yaml file

## Using the application

In order to use the application you need to send requests to the application:

```bash
curl 'http://localhost:8080/get/outliers'
```

You can use the input parameters in order to select the data you want to be processed and he output is received as a json in the response of the request, or in the outlier_files_output folder as csv files

### Inputs

#### Stock exhange

Will process all the files from the specified stock exchange.

POSSIBLE VALUES:
- LSE
- NASDAQ
- NYSE

```bash
curl 'http://localhost:8080/get/outliers?stock_exchange=LSE'
```

#### Stock ID

Will process only the file of the specified stock ID

POSSIBLE VALUES:
- LSE
    - FLTR
    - GSK
- NASDAQ
    - TSLA
- NYSE
    - ASH
    - NMR

```bash
curl 'http://localhost:8080/get/outliers?stock_id=TSLA'
curl 'http://localhost:8080/get/outliers?stock_exchange=LSE&stock_id=FLTR'
```

#### File number

Will process only a certain number of stocks from the specified stock exchange
```bash
curl 'http://localhost:8080/get/outliers?file_no=1'
curl 'http://localhost:8080/get/outliers?stock_exchange=LSE&file_no=1'
```

