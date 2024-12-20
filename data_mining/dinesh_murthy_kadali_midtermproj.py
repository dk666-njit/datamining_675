# -*- coding: utf-8 -*-
"""dinesh_murthy_kadali_midtermproj.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1tety-3_Z9xAiIKSQddi7qasy1CE7_vww
"""

# Import necessary libraries
import pandas as pd
from itertools import combinations
from mlxtend.frequent_patterns import apriori, association_rules, fpgrowth
from mlxtend.preprocessing import TransactionEncoder
import time

# Define file paths for the datasets (use raw strings to avoid escape sequence issues)
dataset_paths = {
    "Amazon": r"/content/amazon.csv",
    "BestBuy": r"/content/bestbuy.csv",
    "KMart": r"/content/kmart.csv",
    "Nike": r"/content/nike.csv"
}

# Load transactions from CSV files
def read_transactions(file_path):
    data_frame = pd.read_csv(file_path)
    transactions = data_frame['Items'].apply(lambda x: x.split(', ')).tolist()
    return transactions

# Brute Force Method for generating frequent itemsets
def find_frequent_itemsets(transactions, min_support):
    item_frequency = {}
    for transaction in transactions:
        for item in transaction:
            item_frequency[item] = item_frequency.get(item, 0) + 1

    frequent_items = {1: {item: count for item, count in item_frequency.items() if count / len(transactions) >= min_support}}

    k = 2
    while True:
        previous_itemsets = list(frequent_items[k - 1].keys())
        candidate_itemsets = list(combinations(previous_itemsets, k))
        item_frequency = {}
        for transaction in transactions:
            transaction_set = set(transaction)
            for itemset in candidate_itemsets:
                if set(itemset).issubset(transaction_set):
                    item_frequency[itemset] = item_frequency.get(itemset, 0) + 1

        frequent_items[k] = {itemset: count for itemset, count in item_frequency.items() if count / len(transactions) >= min_support}
        if not frequent_items[k]:
            del frequent_items[k]
            break
        k += 1
    return frequent_items

# Apriori Algorithm
def run_apriori_algorithm(transactions, min_support, min_confidence):
    encoder = TransactionEncoder()
    transformed_data = encoder.fit(transactions).transform(transactions)
    dataframe = pd.DataFrame(transformed_data, columns=encoder.columns_)

    frequent_itemsets = apriori(dataframe, min_support=min_support, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)

    return frequent_itemsets, rules

# FP-Growth Algorithm
def run_fpgrowth_algorithm(transactions, min_support, min_confidence):
    encoder = TransactionEncoder()
    transformed_data = encoder.fit(transactions).transform(transactions)
    dataframe = pd.DataFrame(transformed_data, columns=encoder.columns_)

    frequent_itemsets = fpgrowth(dataframe, min_support=min_support, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)

    return frequent_itemsets, rules

# Timing function for comparison
def get_execution_time(algorithm_function, *args):
    start = time.time()
    result = algorithm_function(*args)
    end = time.time()
    return result, end - start

# Main program loop
while True:
    # Prompt user to select a database or exit
    print("\nAvailable databases:")
    for i, name in enumerate(dataset_paths.keys(), 1):
        print(f"{i}. {name}")
    print("0. Exit")

    selected_option = int(input("Enter the number corresponding to the database you'd like to choose (or 0 to exit): "))

    # Exit the loop if the user chooses 0
    if selected_option == 0:
        print("Exiting the program.")
        break

    # Get the selected database name
    selected_dataset = list(dataset_paths.keys())[selected_option - 1]

    # Load the selected transactions
    transaction_data = read_transactions(dataset_paths[selected_dataset])
    print(f"Loaded {len(transaction_data)} transactions from {selected_dataset}.")

    # Prompt user for support and confidence thresholds
    min_support = float(input("Enter support threshold in % (e.g., 10 for 10%): ")) / 100
    min_confidence = float(input("Enter confidence threshold in % (e.g., 20 for 20%): ")) / 100

    print(f"\nProcessing {selected_dataset} with support {min_support * 100}% and confidence {min_confidence * 100}%...")

    # Brute Force
    bf_results, bf_time = get_execution_time(find_frequent_itemsets, transaction_data, min_support)
    print(f"\nBrute Force Frequent Itemsets:\n{bf_results}")
    print(f"Brute Force Time: {bf_time:.4f}s")

    # Apriori
    apriori_results, apriori_time = get_execution_time(run_apriori_algorithm, transaction_data, min_support, min_confidence)
    print(f"\nApriori Frequent Itemsets:\n{apriori_results[0]}")
    print(f"Apriori Rules:\n{apriori_results[1]}")
    print(f"Apriori Time: {apriori_time:.4f}s")

    # FP-Growth
    fp_results, fp_time = get_execution_time(run_fpgrowth_algorithm, transaction_data, min_support, min_confidence)
    print(f"\nFP-Growth Frequent Itemsets:\n{fp_results[0]}")
    print(f"FP-Growth Rules:\n{fp_results[1]}")
    print(f"FP-Growth Time: {fp_time:.4f}s")

    # Ask if the user wants to run another analysis
    continue_choice = input("\nDo you want to analyze another dataset? (yes/no): ").strip().lower()
    if continue_choice != 'yes':
        print("Exiting the program.")
        break