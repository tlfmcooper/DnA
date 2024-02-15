import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Optional, Tuple
import re

def read_excel_tabs(file_path):
    
    """
    This function reads all the tabs of an excel file into a dictionary of dataframes.

    Parameters:
    file_path (str): The path of the excel file.

    Returns:
    list: A list of dataframes, where each dataframe represents the data in a specific sheet.

    """

    return [*pd.read_excel(file_path, sheet_name=None).values()]

def split_df_columns(df: pd.DataFrame, col_name: str, new_names: list) -> pd.DataFrame:
    """
    This function takes a dataframe and a column name as input, and splits the values in the specified column into multiple columns, using the specified separator. The new columns are given the specified names.

    Parameters:
    df (pd.DataFrame): The input dataframe.
    col_name (str): The name of the column to be split.
    new_names (list): A list of new column names, in the same order as the split columns.

    Returns:
    pd.DataFrame: The input dataframe with the specified column split into multiple columns.

    """
    loc_0 = df.columns.get_loc(col_name)
    codes_split = df[col_name].str.split(pat=",", expand=True).add_prefix(f"{col_name}_")
    df = pd.concat([df.iloc[:, :loc_0], codes_split, df.iloc[:, loc_0:]], axis=1)
    df = df.drop(columns=[col_name])

    renaming_cols = [col for col in df.columns if col.startswith(f"{col_name}_")]
    renaming_dict = dict(zip(renaming_cols, new_names))
    df.rename(columns=renaming_dict, inplace=True)

    return df





def identify_columns_wrong_dtype(df: pd.DataFrame, target_col: str) -> set:
    """
    This function identifies the columns in a dataframe that have the wrong data type.
    It returns a set of the columns that have strings as values and are not all digits.

    Parameters:
        df (pd.DataFrame): The dataframe to check.
        target_col (str): The name of the column to check.

    Returns:
        set: A set of the columns that have the wrong data type.

    """
    # Check that the target column exists in the dataframe
    if target_col not in df.columns:
        raise ValueError(f"The target column '{target_col}' does not exist in the dataframe.")

    # Filter the dataframe to only include the target column and strings
    df_str = df[df[target_col].apply(lambda x: isinstance(x, str) and not x.isdigit())]

    # Get a set of all the values in the target column that are not all digits
    wrong_chars = set(df_str[target_col].values.tolist())

    # Get a set of all the strings in the target column that are not all digits
    non_digit_strings = {item for item in wrong_chars if re.search(r"\D+", item)}

    # Return the non-digit strings
    return non_digit_strings
    
import pandas as pd
import numpy as np

def sanitize_df_columns(df: pd.DataFrame, target_col: str, date_col: str = "FL_DATE", format: str = "mixed", parse_dates: bool = True) -> pd.DataFrame:
    """
    This function takes a dataframe and cleans the specified columns.

    Parameters:
    df (pd.DataFrame): The input dataframe.
    target_col (str): The name of the column to be cleaned.
    date_col (str): The name of the date column. (default: "FL_DATE")
    format (str): The format of the date column. (default: "mixed")
    parse_dates (bool): A boolean value indicating whether to parse the date column. (default: True)

    Returns:
    pd.DataFrame: The input dataframe with the specified columns cleaned.

    """
    if parse_dates and df[date_col].dtype != np.dtype('datetime64[ns]'):
        df[date_col] = pd.to_datetime(df[date_col], format=format)

    print(f"Sanitizing {target_col}...")
    
    strings_to_replace = identify_columns_wrong_dtype(df, target_col)

    df[target_col] = df[target_col].astype(str).replace({string: np.nan for string in strings_to_replace})
    df[target_col] = df[target_col].astype(float)

    # To reduce the memory footprint of the Object data type
    for column, dtype in df.dtypes.items():
        if dtype == np.dtype('O'):
            df[column] = df[column].astype('str')
    print(f"Sanitizing {target_col} done.")

    return df
    
    

def format_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function applies formatting to numeric columns in a dataframe.

    Parameters:
    df (pd.DataFrame): The input dataframe.

    Returns:
    pd.DataFrame: The input dataframe with formatted numeric columns.

    """
    # Apply formatting logic directly within applymap()
    formatted_df = df.map(lambda x: '{:,.0f}'.format(x) if isinstance(x, (int, float)) else x)

    return formatted_df


def flights_stats(df, group_keys=['ORIGIN_IATA_CODE', 'DEST_IATA_CODE'], aggregate_cols=["OP_CARRIER_FL_NUM"], new_aggreg_name="number_of_flights", count=True, top_n=10):
    # Create a grouping object
    grouper = df.groupby(group_keys)[aggregate_cols]
    
    # Group flights by route and count the number of flights
    if count:
        routes = grouper.count().reset_index()
    else: 
        routes =  grouper.sum().reset_index()
    
    if len(aggregate_cols)==1:
        routes.rename(columns={aggregate_cols[0]: new_aggreg_name}, inplace=True)

    # Create a copy of the DataFrame with swapped origin and destination
    swapped_routes = routes.copy()
    swapped_routes.rename(columns={group_keys[0]: group_keys[1], group_keys[1]: group_keys[0]}, inplace=True)

    # Concatenate the original and swapped DataFrames
    return_routes = pd.concat([routes, swapped_routes], ignore_index=True)

    # Group by the route (combination of origin and destination)
    grouped_routes = return_routes.groupby(group_keys)

    # Calculate total number of flights for each route
    return_flights = grouped_routes[new_aggreg_name].sum().reset_index()

    # Drop duplicates from the return flights because we have the same value for route A-B and B-A
    return_flights = return_flights.drop_duplicates(subset=[new_aggreg_name])
    
    top = return_flights.nlargest(top_n, new_aggreg_name)

    return top







def plot_graphs(df: pd.DataFrame,
                     df_col: str = 'number_of_flights',
                     index_name: Optional[str] = 'ORIGIN_IATA_CODE',
                     x_label: Optional[str] = None,
                     y_label: Optional[str] = None,
                     title: Optional[str] = None,
                     figsize: Tuple[int, int] = (16, 8),
                     rotation: int = 45,
                     alpha: float = 0.7) -> None:
    """
    Plot the top flights from the given DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing flight data.
    df_col (str): Name of the column containing the total number of flights. Default is 'number_of_flights'.
    index_name (str, optional): Name of the index. Default is None.
    x_label (str, optional): Label for the x-axis. Default is None.
    y_label (str, optional): Label for the y-axis. Default is None.
    title (str, optional): Plot title. Default is None.
    figsize (tuple, optional): Figure size. Default is (16, 8).
    rotation (int, optional): Rotation angle for x-axis labels. Default is 45.
    alpha (float, optional): Transparency of gridlines. Default is 0.7.

    Returns:
    None
    """
    fig, ax = plt.subplots(figsize=figsize)
    df_copy = df.copy()
    if index_name:
        df_copy.set_index(index_name, inplace=True)
        df_plot = df_copy[df_col]
    else:df_plot =df
    colors = plt.cm.YlOrRd(df_plot.rank() / len(df_plot))
    
    
    df_plot.plot(kind="bar", color=colors, use_index=True)  # Use a diverging colormap
    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)
    if title:
        ax.set_title(title)
    
    #ax.set_xticks(ticks=df_plot.index, labels=df_plot.index,rotation=rotation)  # Rotate x-axis labels for readability
    ax.grid(axis="y", linestyle="--", alpha=alpha)  # Add gridlines for better readability
    fig.tight_layout()  # Adjust spacing for aesthetics

    # Add annotations
    for i, v in enumerate(df_plot):
        ax.text(i, v + 1.0, f"{v:,.2f} ", ha="center", va="bottom", fontsize=8)

    return fig, ax




