# DataRevive
#### Video Demo:  <https://youtu.be/iOSNwDc26i8>
#### Description:

DataRevive is a Python-based data cleaning pipeline created for my final project in Harvard's CS50P. Dealing with messy, real-world CSV files can be frustrating because they often contain missing values, broken dates, or random text errors that break data analysis tools. I built this tool to automatically load a messy CSV file, fix the most common issues without crashing, and save a clean version ready for analysis.

## Project Structure

I divided the code into three main files to keep the logic organized and easy to test:

- `project.py`: This is the main program file. It handles getting the file path from the user, validating that it exists and is a CSV, running the cleaning process, and finally writing the cleaned data to a new file. I kept the core helper functions here clean so they could be easily tested with pytest.
- `loader.py`: This file only handles reading the CSV using pandas. Getting data loaded right is often the first place programs crash, so this file tests different text encodings (like utf-8 and latin1) and safely handles pandas parsing errors.
- `cleaner.py`: The core logic that cleans the dataframe. Instead of just deleting rows with missing data, it tries to fix them safely. It standardizes column names, removes exact duplicates, fixes incorrect text (like "ERROR" or "UNKNOWN"), and fills in missing numbers with the median and missing text with the mode. It even has a function to dynamically find mathematical relationships between columns (like Quantity * Price = Total) to accurately calculate missing values when possible!
- `test_project.py`: Contains unit tests written for the `pytest` framework to verify that the helper functions in `project.py` work correctly.

## How to Run

You can run the program from your terminal:

```bash
python project.py
```

It will ask you for a file path. If you don't have a messy CSV handy, you can just press `ENTER` and it will run on the default `sample_data.csv` (if you have one in the folder).

It outputs a step-by-step summary of what was cleaned or changed, and then saves a new file with the prefix `revived_` (for example, `revived_sales.csv`) in the same folder you ran the script from.

## Design Choices

1. **Separation of Concerns:**
I kept user input/output in `project.py` and strictly separated the heavy Data Science parsing logic into standalone `cleaner` and `loader` files. This strategic modularity made writing isolated Pytest unit tests significantly more straightforward.

2. **Safe Output Files:**
I meticulously designed `create_output_filename` to construct a completely new filename operating purely within the current working directory, completely bypassing the original file's path structure. This deliberate mechanism guarantees the obviation of sudden `PermissionError` system crashes that frequently emerge when inadvertently attempting to write back to restricted, external, or read-only administrative drives.

3. **No Dropped Rows:**
A paramount priority in DataRevive was uncompromisingly avoiding premature data loss. Rather than applying a destructive `.dropna()` operation, the algorithm attempts intensive imputation or sophisticated mathematical deduction techniques first. Dropping rows remains an absolute last resort that is basically avoided virtually entirely within this pipeline.

4. **Dynamic Column Relationships via Itertools (`itertools.permutations`):**
One of the most mathematically complex yet exceptionally rewarding features of DataRevive is the implementation of the `mathematically_deduce_missing` functionality. Real-world financial, operational, or transaction data will often harbor intrinsic mathematical relationships hidden directly within its structure—for instance, evaluating exact matches for `Unit_Price * Quantity = Total_Sales`, or dealing with scaled weight thresholds. A naive or simple programmatic approach might involve rigidly hard-coding these column names explicitly to target specific datasets securely. However, I elected to take a much more advanced, generalized computational route by intentionally employing Python's `itertools.permutations` to dynamically discover, evaluate, and extract these underlying relationships across absolutely any given external dataset shape.

By utilizing the standard library function `itertools.permutations(actual_num_cols, 3)` directly inside the core pipeline, the system can systematically and efficiently iterate through every single possible unique permutation of three numerical columns discovered in the ingested CSV. When a specific permutation configuration is subjected to testing, the conditional testing branch applies rigorous validation boundary metrics—checking to verify if the discovered mathematical multiplication rule truthfully holds its integrity across an overwhelming 95% of row entries before officially recognizing the rule as valid truth. The power of permutations is essential here because algebraic sequence matters: computationally measuring if `A * B = C` yields entirely different inferences than testing if `A * C = B`. While computing extensive permutations definitively scales upwards in overall computational time complexity matching larger arrays of valid numeric columns ($O(n^3)$), typical transactional and financial datasets normally contain only a manageable cluster of core numerical fields, explicitly permitting this robust dynamic search to execute remarkably fast while decisively eliminating any previously required rigid hardcoding limitations. Furthermore, additional robust Exception-handling `try-except` defensive wrappers were implemented thoroughly alongside this block to immediately preempt rogue edge-case data crashes, such as correctly handling random zero vectors raising unexpected `ZeroDivisionError` traps, or mixed strings failing with an abrupt `TypeError`.

5. **Robust Encoding Handling (`loader.py`):**
An equally significant overarching design philosophy surrounding DataRevive involved navigating and resolving corrupted incoming file types alongside varying unrecognized character encodings effortlessly. Many working data analysts routinely encounter the notorious `UnicodeDecodeError` immediately when forcefully attempting to load unstructured or messy CSV files extracted externally from either outdated legacy networking systems or specific regional global machines utilizing alternative code pages. To reliably insulate the end-user entirely from witnessing these cryptic system tracebacks, the `loader.py` module directly adopts a heavily agile iterative fallback procedure.

Initially, loading procedures aggressively default towards utilizing the prevailing, universally recognized standard `utf-8` text encoding scheme. Knowing full well that raw real-world data files routinely arrive sporting localized configurations, the underlying system is programmed to smoothly cascade backwards down a designated fallback chain—methodically evaluating `latin1` and `cp1252` encoding paradigms dynamically if preceding text-reading exceptions trigger in sequence. This sophisticated multi-layered fallback strategy intrinsically hinges upon catching `pandas` specific I/O exceptions smoothly through targeted catching blocks, rather than permitting them to escalate upwards into terminal program-breaking scenarios.

Interpreting standard exception objects proactively successfully thwarts catastrophic runtime failures altogether. Specifically, the ability to safely distinguish between hitting an explicitly empty file triggering an isolated `pd.errors.EmptyDataError`, juxtaposed against receiving a structurally garbled and unreadable layout manifesting a `pd.errors.ParserError`, provides the foundational ability to generate highly specialized and genuinely informative command-line logging messages guiding the user to the problem's source. Constructively combining these heavily specialized diagnostic warnings together with adaptive multi-level encoding discovery equips DataRevive with undeniably excellent operational resilience. Ultimately, by virtually guaranteeing a streamlined, crash-free loading execution, totally regardless of the file's obscure internal structural text representation, this core software reliably establishes an unshakeable and robust procedural foundation dedicated exclusively to superior data preprocessing and systemic analysis. Let's make no mistake, heavy prioritization inherently rested on ensuring absolute execution stability while promoting actionable transparency uniformly across any desktop environment configurations tested.

6. **Interactive User Interface (CLI) Enhancements:**
Command-line interfaces can often feel opaque to end-users without meaningful visual feedback. To elevate the overall user experience and bridge this gap, I designed and incorporated two critical user-facing elements in the main execution file (`project.py`). First, a customized execution layout is immediately rendered using a dynamic ASCII Art Banner (`BANNER`). This establishes a highly professional, branded look for the project right upon startup, setting a distinct tone. Second, to provide absolute data transparency, I introduced the `display_data_preview()` function. This dedicated method intelligently renders direct tabular snapshots of the underlying dataset explicitly twice: once immediately preceding the cleaning lifecycle and once decisively after all transformations have concluded. By utilizing Pandas' `df.head()` under the hood, this transparent design choice instantly instills explicit trust, visibly demonstrating to the user exactly how fragmented records are computationally restored and polished in real-time.
