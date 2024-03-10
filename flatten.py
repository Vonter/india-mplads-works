import csv
import logging
import os
import pandas as pd
import re

from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("flatten.log"),
        logging.StreamHandler()
    ]
)

# Get list of XLS files
def get_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.xls')]

# Parse tables in XLS file
def parse_tables(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        tables = soup.find_all('table')
        dataframe = []
        for table in tables:
            df = pd.read_html(str(table))[0] # Convert table to DataFrame
            dataframe.append(df)
        return dataframe

# Process list of XLS files
def process_files(files):
    # Initialize DataFrame
    combinedDataframe = pd.DataFrame()

    # Iterate over XLS files
    for file in files:
        logging.info("Processing {}".format(file))

        # Parse tables in XLS file
        tables = parse_tables(os.path.join("./raw", file))
        # Create DataFrame from table
        dataframe = pd.concat(tables, ignore_index=True)

        # Concatenate DataFrame if it contains data
        if dataframe.iloc[0, 0] == "No Data Found":
            logging.info("No data found in {}, skipping".format(file))
        else:
            combinedDataframe = pd.concat([dataframe, combinedDataframe], ignore_index = True)

    # Remove duplicate rows
    combinedDataframe = combinedDataframe.drop_duplicates()

    return combinedDataframe

# Format columns of DataFrame
def format_dataframe(dataframe):
    dataframe['CONSTITUENCY'] = dataframe['CONSTITUENCY'].astype(str).fillna('')
    dataframe['HOUSE'] = dataframe.apply(lambda row: "Rajya Sabha" if "Rajya Sabha" in row['CONSTITUENCY'] else "Lok Sabha", axis=1)
    dataframe['MP NAME'] = dataframe['MP NAME'].str.replace(r'\(\d+.*\)', '', regex=True)
    dataframe["RECOMMENDED DATE"] = pd.to_datetime(dataframe["RECOMMENDED DATE"], format="%d %b %Y")
    dataframe = dataframe.drop("S.No.", axis = 1)
    dataframe = dataframe.sort_values(by='RECOMMENDED DATE', ascending=False)

    return dataframe

# Save DataFrame as CSV
def save_dataframe(dataframe, file_path):
    dataframe.to_csv(file_path, index=False, sep=";", quoting=csv.QUOTE_ALL)

# Flatten XLS to CSV
def flatten():
    # Get list of XLS files
    files = get_files("./raw")
    # Process list of XLS files
    dataframe = process_files(files)
    # Format columns of DataFrame
    dataframe = format_dataframe(dataframe)
    # Save DataFrame as CSV
    save_dataframe(dataframe, os.path.join("./csv", "MPLADS.csv"))

if __name__ == "__main__":
    flatten()
