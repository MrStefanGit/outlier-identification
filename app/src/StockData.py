import pandas as pd
import os

class StockData:
    
    def __init__(self, stock_exchange=None, stock_ID=None, file_no=None):
        """Init function for receiveng input and creating variables"""

        self.stock_exchange = stock_exchange
        self.stock_ID = stock_ID
        self.file_no = file_no
            
        self.paths = []
        self.dataframes = []

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
            raise ValueError("Invalid file number! Please check your input.")
        
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
                self.errors.append(f"File '{file_path}' not found.")
                return False
            except pd.errors.EmptyDataError:
                self.errors.append(f"File '{file_path}' is empty.")
                return False
            except pd.errors.ParserError:
                self.errors.append(f"Error parsing file '{file_path}'.")
                return False
            except Exception as e:
                self.errors.append(f"An error occurred while loading file '{file_path}': {e}")
                return False

        return True
    
    def load_data(self):
        try:
            self.paths = self.get_paths("./stock_price_data_files", self.stock_exchange, self.stock_ID, self.file_no)
        except (FileNotFoundError, ValueError, TypeError) as e:
            self.errors.append(str(e))
            return False
        
        if self.get_files(self.paths):
            return True
        else:
            return False