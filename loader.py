import pandas as pd
import numpy as np
import itertools


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize the column names of a DataFrame.

    Strips leading and trailing whitespace, converts to lowercase, and replaces
    spaces with underscores to ensure consistent column naming conventions
    across the dataset.

    Args:
        df (pd.DataFrame): The input pandas DataFrame.

    Returns:
        pd.DataFrame: The DataFrame with standardized column names.
    """
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    return df


def neutralize_bad_text(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace known invalid text patterns and placeholders with NaN values.

    Scans the DataFrame for common artifact placeholder values like 'ERROR',
    'UNKNOWN', and empty spaces, substituting them with numpy NaN to facilitate
    accurate downstream numerical calculations and statistical imputation.

    Args:
        df (pd.DataFrame): The input pandas DataFrame containing raw text.

    Returns:
        pd.DataFrame: The DataFrame with bad textual values neutralized to NaN.
    """
    bad_values = ['ERROR', 'UNKNOWN', 'UNKNOWN ', ' ERROR', 'N/A', 'null', '', ' ']
    return df.replace(bad_values, np.nan)


def mathematically_deduce_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduce missing numerical values through intrinsic mathematical relationships.

    Iterates over all permutations of numerical columns to discover implicit
    mathematical relations (A * B = C). When a computationally strong relationship
    is identified, it systematically fills in missing values across those columns
    utilizing algebraic deduction. Includes robust exception handling to prevent
    division-by-zero or incompatible type-casting crashes.

    Args:
        df (pd.DataFrame): The input pandas DataFrame with potentially missing data.

    Returns:
        pd.DataFrame: The DataFrame with missing values deduced mathematically.
    """
    recovered_count = 0

    # Try to fix columns that look like text but are actually numbers
    for col in df.columns:
        if df[col].dtype == object:
            # test if we can convert it to numbers
            test_numeric = pd.to_numeric(df[col].astype(str).str.strip(), errors='coerce')
            # if more than 50% are valid numbers, update it
            if test_numeric.notna().sum() > len(df) * 0.5:
                df[col] = test_numeric

    actual_num_cols = df.select_dtypes(include=['number']).columns.tolist()

    # Search for columns where A * B = C to calculate missing data
    if len(actual_num_cols) >= 3:
        discovered = False
        # loop through all combinations of 3 numeric columns
        for A, B, C in itertools.permutations(actual_num_cols, 3):
            if discovered:
                break

            valid_rows = df[(df[A].notna()) & (df[B].notna()) & (df[C].notna())]
            if len(valid_rows) < 10:
                continue

            try:
                # If they match mathematically, we can use this rule
                matches = np.isclose(valid_rows[A] * valid_rows[B], valid_rows[C], rtol=1e-2)
                match_rate = matches.sum() / len(valid_rows)

                if match_rate > 0.95:
                    discovered = True
                    print(f"  - Math relationship found: '{A}' * '{B}' = '{C}'")

                    # Fix missing C
                    mask_C = df[C].isna() & df[A].notna() & df[B].notna()
                    df.loc[mask_C, C] = df[A] * df[B]
                    recovered_count += mask_C.sum()

                    # Fix missing A
                    mask_A = df[A].isna() & df[C].notna() & df[B].notna()
                    valid_B = df[B] != 0
                    df.loc[mask_A & valid_B, A] = round(df[C] / df[B], 2)
                    recovered_count += (mask_A & valid_B).sum()

                    # Fix missing B
                    mask_B = df[B].isna() & df[C].notna() & df[A].notna()
                    valid_A = df[A] != 0
                    df.loc[mask_B & valid_A, B] = round(df[C] / df[A], 2)
                    recovered_count += (mask_B & valid_A).sum()
            except (ZeroDivisionError, TypeError) as error_msg:
                # Gracefully handle situations where invalid types or zeros disrupt the algorithm
                print(f"  - Validation skipped for {A}, {B}, {C} due to calculation error: {error_msg}")
                continue

    if recovered_count > 0:
        print(f"  - Calculated {recovered_count} missing values using math.")

    return df


def verify_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and intelligently parse datetime fields.

    Attempts to gracefully convert specified and known date columns into internal
    pandas datetime objects. Out-of-range or deeply malformed date strings are
    coerced efficiently into NaT (Not a Time).

    Args:
        df (pd.DataFrame): The input pandas DataFrame containing unparsed dates.

    Returns:
        pd.DataFrame: The DataFrame with cleanly parsed and structured date columns.
    """
    if 'transaction_date' in df.columns:
        invalid_before = df['transaction_date'].isna().sum()
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        invalid_after = df['transaction_date'].isna().sum()
        invalid_found = invalid_after - invalid_before
        if invalid_found > 0:
            print(f"  - Invalidated {invalid_found} corrupted date formats.")
    return df


def fill_remaining_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Impute any leftover and unresolved missing values systematically.

    Applies precise statistical imputation methods to fill empty dataframe cells
    depending exclusively on the column's respective data type structure:
    - Numeric fields: Imputed fundamentally utilizing the median.
    - Datetime fields: Imputed utilizing the highest occurring mode occurrence.
    - Textual/Categorical fields: Imputed using the prevalent mode string.

    Args:
        df (pd.DataFrame): The DataFrame requiring final missing data replacement.

    Returns:
        pd.DataFrame: The DataFrame completely filled with statistical estimations.
    """
    for col in df.columns:
        missing_count = df[col].isna().sum()
        if missing_count == 0:
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            fill_val = df[col].median()
            if pd.isna(fill_val):
                fill_val = 0
            df[col] = df[col].fillna(fill_val)
            print(f"  - Filled {missing_count} missing values in '{col}' with median: {fill_val:.2f}")
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            md = df[col].mode()
            fill_val = md[0] if not md.empty else pd.Timestamp('2023-01-01')
            df[col] = df[col].fillna(fill_val)
            print(f"  - Filled {missing_count} missing values in '{col}' with mode date.")
        else:
            md = df[col].mode()
            fill_val = md[0] if not md.empty else "Unknown"
            df[col] = df[col].fillna(fill_val)
            print(f"  - Filled {missing_count} missing values in '{col}' with mode: '{fill_val}'")

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Orchestrate the entire high-level data cleaning process iteratively.

    Executes a cohesive sequence of data standardization and correction milestones
    on a given DataFrame. This sequentially encompasses textual neutralization,
    duplicate row removal, implicit mathematical deductions, structural date parsing,
    and systemic fallback imputation, successfully resulting in an optimized
    dataset adequately prepped for complex analysis routines.

    Args:
        df (pd.DataFrame): The original, unstructured pandas DataFrame.

    Returns:
        pd.DataFrame | None: The fully resolved DataFrame, or None if empty/invalid.
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        return None

    print("\n--- STEP 2: Cleaning Data ---")
    clean_df = df.copy()

    clean_df = standardize_columns(clean_df)
    clean_df = neutralize_bad_text(clean_df)

    initial_rows = len(clean_df)
    clean_df = clean_df.drop_duplicates()
    dupes_removed = initial_rows - len(clean_df)
    if dupes_removed > 0:
        print(f"  - Removed {dupes_removed} duplicate rows.")

    clean_df = mathematically_deduce_missing(clean_df)
    clean_df = verify_dates(clean_df)
    clean_df = fill_remaining_missing(clean_df)

    print("--- Data cleaning successfully completed! ---")
    return clean_df

