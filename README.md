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
