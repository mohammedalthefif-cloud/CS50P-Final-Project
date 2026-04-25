"""
loader.py

This module handles reading the dataset from a CSV file. It explicitly manages
common problems like missing files or unreadable formats so the program doesn't
crash abruptly.
"""

import pandas as pd


def load_data(file_path: str) -> pd.DataFrame | None:
    """
    Reads a CSV file intelligently, trying different encodings if necessary.
    Returns None if an error occurs during parsing or loading.
    """
    print("\n--- STEP 1: Loading Data ---")

    # We will try standard utf-8 first, but if it's a very dirty file
    # it might be encoded differently (like Windows-1252/latin1).
    encodings_to_try = ['utf-8', 'latin1', 'cp1252']
    df = None

    for enc in encodings_to_try:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            if enc != 'utf-8':
                print(f"[NOTICE] Data required '{enc}' encoding to be read correctly.")
            break # Successfully read
        except UnicodeDecodeError:
            continue # Try the next encoding
        except pd.errors.EmptyDataError:
            print(f"Error: The file '{file_path}' is completely empty.")
            return None
        except pd.errors.ParserError:
            print(f"Error: The file '{file_path}' could not be parsed as a valid CSV.")
            return None
        except Exception as e:
            print(f"Error: An unexpected problem occurred: {e}")
            return None

    if df is None:
        print(f"Error: Failed to read '{file_path}' with any standard text encoding.")
        return None

    # Check if the DataFrame has no actual rows
    if df.empty:
        print(f"Error: '{file_path}' loaded properly, but it contains no rows.")
        return None

    # Give the user a quick summary of what was loaded
    memory_usage_kb = df.memory_usage(deep=True).sum() / 1024
    print(f"Success! Securely extracted {df.shape[0]} rows and {df.shape[1]} columns.")
    print(f"Memory footprint: {memory_usage_kb:.2f} KB")

    return df
