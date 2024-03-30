import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

class StockData:
    
    def __init__(self, stock_exchange=None, stock_ID=None, file_no=None):
        """Init function for receiveng input and creating variables"""

        self.stock_exchange = stock_exchange
        self.stock_ID = stock_ID
        self.file_no = file_no
            
        self.paths = []
        self.dataframes = []
        self.samples = []
        self.outliers = []

        self.errors = []

    def get_paths_in_dir(self, dir_path):
        """List all files in a directory."""

        files = []
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            for root, _, filenames in os.walk(dir_path):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
        return files
    
    def get_paths(self, base_folder, dir=None, file=None, file_no=None):
        """Get all the file paths based on the three input parameters"""

        if not isinstance(base_folder, str):
            raise TypeError("Internal server error") # Base folder problems
        base_folder = os.path.abspath(base_folder)

        if not os.path.exists(base_folder):
            raise FileNotFoundError("Internal server error") # Base folder problems
        

        if file_no is not None and (not isinstance(file_no, int) or file_no <= 0):
            try:
                file_no_int = int(file_no)
            except ValueError:
                raise ValueError("Invalid file number! Please enter a valid integer.")
        
        if dir is None and file is None and file_no is None:
            # Case: No parameters provided
            files = []
            for root, _, filenames in os.walk(base_folder):
                for filename in filenames:
                    files.append(os.path.join(root, filename))

        elif dir is not None and file_no is None:
            # Case: Only dir provided or Both dir and file provided
            if not isinstance(dir, str):
                raise TypeError("Invalid stock exchange name! Please check your input.")
            dir_path = os.path.join(base_folder, dir)
            if file is None:
                files = self.get_paths_in_dir(dir_path)
            else:
                if not isinstance(file, str):
                    raise TypeError("Invalid stock id! Please check your input.")
                file = file + ".csv"
                file_path = os.path.join(dir_path, file)
                if os.path.isfile(file_path):
                    files = [file_path]
                else:
                    files = []

        elif file is not None and file_no is None or file is not None and file_no is not None:
            # Case: Only file provided
            if not isinstance(file, str):
                raise TypeError("Invalid stock id! Please check your input.")
            file = file + ".csv"
            files = []
            for root, _, filenames in os.walk(base_folder):
                for filename in filenames:
                    if filename == file:
                        files.append(os.path.join(root, filename))

        elif dir is None and file_no is not None:
            # Case: Only file_no provided
            files = []
            for root, _, filenames in os.walk(base_folder):
                for filename in filenames[:file_no]:
                    files.append(os.path.join(root, filename))

        elif dir is not None and file_no is not None:
            # Case: Both dir and file_no provided
            if not isinstance(dir, str):
                raise TypeError("Invalid stock exchange name! Please check your input.")
            dir_path = os.path.join(base_folder, dir)
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                files = []
                for root, _, filenames in os.walk(dir_path):
                    for filename in filenames[:file_no]:
                        files.append(os.path.join(root, filename))
            else:
                files = []

        if not files:
            raise FileNotFoundError("Stock/s not found or unknown error! Please check your input. A list of available stocks can be found at /api/stocks")
        return files
    
    def get_files(self, file_paths):
        """Load the files into pandas dataframes and add them to the dataframes list"""

        for file_path in file_paths:
            try:
                # Attempt to load the file into a DataFrame
                df = pd.read_csv(file_path, header=None, names=['stock', 'date', 'value'])  # You can adjust this according to your file format
                self.dataframes.append(df)
            except FileNotFoundError:
                self.errors.append(f"Stock data not found!")
                return False
            except pd.errors.EmptyDataError:
                self.errors.append(f"Stock data is empty!")
                return False
            except pd.errors.ParserError:
                self.errors.append(f"Stock data not in csv format!")
                return False
            except Exception as e:
                self.errors.append(f"Internal server error!")
                return False

        return True
    
    def load_data(self):
        """Function that is called in order to process input parameters, find file paths and load the files into pandas dataframes"""
        try:
            self.paths = self.get_paths("./stock_price_data_files", self.stock_exchange, self.stock_ID, self.file_no)
        except (FileNotFoundError, ValueError, TypeError) as e:
            self.errors.append(str(e))
            return False
        
        if self.get_files(self.paths):
            return True
        else:
            return False
        
    def generate_samples(self):
        """ Function that generates random samples (30 datapoints)"""
        for df in self.dataframes:
            random_timestamp_index = np.random.randint(0, len(df) - 29)  # Ensure at least 30 rows left after the selected index
            # Get the next 30 data points
            selected_data = df.iloc[random_timestamp_index:random_timestamp_index + 30]  # Assuming 'Value' is the column name for the data points
            self.samples.append(selected_data)

    def find_outliers(self):
        """Function that finds the outliers in all the samples and saves them into the outliers list"""
        for df in self.samples:
            
            # Calculate Mean
            mean = round(np.mean(df['value']), 6)

            #Calculate standard deviation
            std_dev = round(np.std(df['value']), 6)

            # Calculate upper and lower limits
            upper_limit = round(mean + 2 * std_dev, 6)
            lower_limit = round(mean - 2 * std_dev, 6)

            # Identify outliers
            outliers = df[(df['value'] > upper_limit) | (df['value'] < lower_limit)]

            outliers_df = pd.DataFrame({
                'Stock_ID': outliers['stock'],
                'Timestamp': outliers['date'],
                'Value': outliers['value'],
                'Mean': mean,
                'Standard_Deviation': std_dev,
                'Upper_Limit': upper_limit,
                'Lower_Limit': lower_limit,
                'Value_Mean_Difference': round(outliers['value'] - mean, 6),
                'Percent_Deviation': abs(((outliers[outliers['value'] > upper_limit]['value'] - upper_limit) / upper_limit * 100)._append((outliers[outliers['value'] < lower_limit]['value'] - lower_limit) / lower_limit * 100))
            })
            self.outliers.append(outliers_df)

    def save_outliers_to_files(self):
        # Generate timestamp for directory name
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Create directory name
        directory_name = f"./oultier_files/request_{timestamp}"

        for index, path in enumerate(self.paths):
            if len(self.outliers[index]) > 0:
                parts = path.split('/')
                stock_exchange = parts[-2]
                stock_id = os.path.splitext(parts[-1])[0]
                # print(f"{stock_exchange}, {stock_id}")

                try:
                    # Attempt to create the directory if it doesn't exist
                    if not os.path.exists(directory_name):
                        os.makedirs(directory_name)
                    else:
                        print(f"Directory '{directory_name}' already exists. Skipping creation.")
                except Exception as e:
                    print(f"An error occurred while creating directory '{directory_name}': {e}")

                exchange_dir = os.path.join(directory_name, stock_exchange)

                try:
                    # Attempt to create the exchange directory if it doesn't exist
                    if not os.path.exists(exchange_dir):
                        os.makedirs(exchange_dir)
                    else:
                        print(f"Directory '{exchange_dir}' already exists. Skipping creation.")
                except Exception as e:
                    print(f"An error occurred while creating directory '{exchange_dir}': {e}")

                try:
                    # Save dataframe as CSV inside exchange directory
                    self.outliers[index].to_csv(os.path.join(exchange_dir, f"{stock_id}.csv"), index=False)
                    print("Dataframe saved successfully.")
                except Exception as e:
                    print(f"An error occurred while reading CSV file or saving dataframe: {e}")

                print("Process completed.")

    def get_outliers_dict(self):
        json_output = {}
        for index, path in enumerate(self.paths):
            if len(self.outliers[index]) > 0:
                parts = path.split('/')
                stock_exchange = parts[-2]
                stock_id = os.path.splitext(parts[-1])[0]

                if stock_exchange not in json_output:
                    json_output[stock_exchange] = {}

                json_output[stock_exchange][stock_id] = json.loads(self.outliers[index].to_json(orient='records'))

        return json_output

