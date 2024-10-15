
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import requests
import time
import numpy
import datetime
import os

from openpyxl import load_workbook
from tqdm.notebook import tqdm



def run_query(query):

    """
    Executes a GraphQL query using a POST request to the Tarkov.dev API.

    Args:
        query (str): The GraphQL query to execute.

    Returns:
        dict: The JSON response from the API if the request is successful.

    Raises:
        Exception: If the API request fails, raises an exception with the response status code and query.
    """
    headers = {"Content-Type": "application/json"}
    response = requests.post('https://api.tarkov.dev/graphql', headers=headers, json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))
    


def get_all_item_info():

    """
    Retrieves detailed information about all items from the Tarkov.dev API.

    Returns:
        dict: The JSON response containing item information such as price, dimensions, category, and barter details.
    """
    base_query = """
    query {
    items(lang: ru) {
        id
        name
        normalizedName
        shortName
        width
        height
        avg24hPrice
        lastLowPrice
        changeLast48h
        low24hPrice
        high24hPrice
        lastOfferCount
        changeLast48hPercent
        category {
        name
        }
        buyFor {
        price
        currency
        priceRUB
        source
        }
        sellFor {
        price
        currency
        priceRUB
        source
        }
        bartersFor {
        id
        }
        bartersUsing {
        id
        }
    }
    }    
    """

    results = run_query(base_query)
    return results



def get_historical_prices(id):

    """
    Fetches the historical price data for a specific item over the last 7 days.

    Args:
        id (str): The unique identifier of the item.

    Returns:
        list: A list of dictionaries containing historical prices and timestamps for the item.
    """
        
    base_query = """
    {
    historicalItemPrices(id: "PATTERN", days: 7, lang: ru) {
        price
        priceMin
        timestamp
    }
    }
    """
    query = base_query.replace("PATTERN", id)
    results = run_query(query)
    return results["data"]["historicalItemPrices"]



def get_historical_prices_items(id_list):

    """
    Fetches historical price data for multiple items by their IDs.

    Args:
        id_list (list): List of item IDs to fetch historical price data for.

    Returns:
        dict: A dictionary where each key is an item ID and the value is its corresponding historical price data.
    """

    responses = {}

    for id in tqdm(id_list):
        responses[id] = get_historical_prices(id)
        time.sleep(0.1)
    
    return responses



def restructure_sales_inner(x):
    """
    Restructures sales data by extracting the source and price in RUB.

    Args:
        x (list): A list of sales data dictionaries containing source and price information.

    Returns:
        list: A list of tuples, where each tuple contains the sales source and price in RUB.
    """
      
    data = [(value["source"],value["priceRUB"]) for value in x]
    return data



def plot_historical_price(data_descrip, data_prices, id, file_path):

    """
    Plots a historical price chart for a specific item and saves the chart as an image file.

    Args:
        data_descrip (pd.DataFrame): DataFrame containing item descriptions including names.
        data_prices (dict): Dictionary containing historical prices for items.
        id (str): The item ID to plot.
        file_path (str): Path to save the generated chart image.
    """

    item_name = data_descrip[data_descrip["id"] == id]["name"].values[0]

    print(f"{item_name}  {id}")
    
    df = pd.DataFrame(data_prices[id])
    values = df["timestamp"].values
    values = numpy.array(values, "int64")
    values = values/1000
    df['timestamp'] = values
    df['timestamp'] = df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x))
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df.columns = ["Open", "Low"]
    df['High'] = df['Open']
    df['Close'] = df['Open']
    mpf.plot(df, type='line', mav=24, title=f'Line Chart for {item_name}', ylabel='Price (RUB)', style='charles', savefig=dict(fname=file_path,dpi=100,pad_inches=0.1))



def plot_all_finance(data_descrip, data_prices, directory):

    """
    Plots historical price charts for all items in the data set and saves them in the specified directory.

    Args:
        data_descrip (pd.DataFrame): DataFrame containing item descriptions including names.
        data_prices (dict): Dictionary containing historical prices for items.
        directory (str): Path to save the generated charts.
    """

    os.makedirs(directory, exist_ok=True)
    for key in data_prices.keys():
        item_name = data_descrip[data_descrip["id"] == key]["name"].values[0]
        item_name = item_name.replace('"', " ")
        file_path = f'{item_name}.png'
        file_path = os.path.join(directory, file_path)
        try:
            plot_historical_price(data_descrip=data_descrip, data_prices=data_prices, id=key, file_path=file_path)
        except:
            print("Plotting failed, probably data is missing/does not exist")


def restructure_sales_outer(x):

    """
    Restructures the sales data by separating 'buyFor' and 'sellFor' into individual keys and prices.

    Args:
        x (dict): A dictionary containing item data including buy and sell prices.

    Returns:
        dict: The restructured dictionary with individual buy and sell prices keyed by their source.
    """
        
    purchase_data = x["buyFor"]
    purchase_data = restructure_sales_inner(purchase_data)
    sales_data = x["sellFor"]
    sales_data = restructure_sales_inner(sales_data)

    for key, value in purchase_data:

        key = "buy_" + key
        x[key] = value
    
    for key, value in sales_data:

        key = "sell_" + key
        x[key] = value
        
    del x["buyFor"]
    del x["sellFor"]

    return x

def adjust_wb(file_path):

    """
    Adjusts the column widths of an Excel workbook based on the maximum content length in each column.

    Args:
        file_path (str): Path to the Excel workbook to adjust.
    """
    # Load the workbook and select the active worksheet
    wb = load_workbook(file_path)
    ws = wb.active

    # Set column widths based on maximum length of content
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column name

        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass

        adjusted_width = max_length + 2
        ws.column_dimensions[column].width = adjusted_width

    # Save the workbook with adjusted column widths
    wb.save(file_path)

def price_screener(data_descrip, data_prices):

    """
    Screens items based on their price changes over time and generates Excel reports for items to buy and sell.

    Args:
        data_descrip (pd.DataFrame): DataFrame containing item descriptions including names.
        data_prices (dict): Dictionary containing historical prices for items.
    """

    # 29 intervals in a day

    dataset_dict_list = []

    for key in data_prices.keys():


        item_name = data_descrip[data_descrip["id"] == key]["name"].values[0]
        item_name = item_name.replace('"', " ")
        print(f"Working on {item_name}")

        if len(data_prices[key]) < 1:
            print(f"No data for {item_name}")
            continue

        df = pd.DataFrame(data_prices[key])
        values = df["timestamp"].values
        values = numpy.array(values, "int64")
        values = values/1000
        df['timestamp'] = values
        df['timestamp'] = df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x))
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        df.columns = ["Open", "Low"]
        df['High'] = df['Open']
        df['Close'] = df['Open']

        high_prices = df["High"].values
        low_prices = df["Low"].values

        high_avg_7 = numpy.mean(high_prices)
        low_avg_7 = numpy.mean(low_prices)

        last_2_hours_high = numpy.mean(high_prices[-2:])
        last_2_hours_low = numpy.mean(low_prices[-2:])

        change_high = last_2_hours_high - high_avg_7
        change_low = last_2_hours_low - low_avg_7

        change_high_prc = (last_2_hours_high - high_avg_7)/high_avg_7*100
        change_low_prc = (last_2_hours_low - low_avg_7)/low_avg_7*100

        data_item = {}
        data_item["id"] = key
        data_item["name"] = item_name
        data_item["high_avg_7"] = high_avg_7
        data_item["low_avg_7"] = low_avg_7
        data_item["last_2_hours_high"] = last_2_hours_high
        data_item["last_2_hours_low"] = last_2_hours_low
        data_item["change_high"] = change_high
        data_item["change_low"] = change_low
        data_item["change_high_prc"] = change_high_prc
        data_item["change_low_prc"] = change_low_prc

        for key, value in data_item.items():

            if not isinstance(value, str):
                data_item[key] = numpy.round(a=value, decimals=2)


        dataset_dict_list.append(data_item)

    df = pd.DataFrame(dataset_dict_list)
    print(df.shape)
    df_to_buy = df.sort_values("change_low_prc")
    df_to_sell = df.sort_values("change_low_prc", ascending = False)
    df_to_buy = df_to_buy[df_to_buy["change_low"]  < 0]
    df_to_sell = df_to_sell[df_to_sell["change_low"]  > 0]
    df_to_buy.to_excel("items_to_buy.xlsx")
    df_to_sell.to_excel("items_to_sell.xlsx")

    adjust_wb("items_to_buy.xlsx")
    adjust_wb("items_to_sell.xlsx")



####### Trader resells #######

def get_all_trader_stuff():

    """
    Retrieves all trader offers from Tarkov.dev API, including items, prices, and trader levels.

    Returns:
        dict: The JSON response containing trader offers, item details, and task unlock requirements.
    """
        
    base_query = """
    {
    traders(lang: ru) {
    id
    name
    cashOffers {
        item {
        id
        name
        basePrice
        low24hPrice
        avg24hPrice
        lastLowPrice
        lastOfferCount
        category {
        name
        }
        sellFor {
            price
            currency
            priceRUB
            source
        }
        }
        minTraderLevel
        price
        currency
        priceRUB
        buyLimit
        taskUnlock {
        id
        name
        }
    }
    }
    } 
    """

    results = run_query(base_query)
    return results["data"]["traders"]

def compute_comission(row, use_current_price = True):

    """
    Computes the commission for an item based on its base price and selling price.

    Args:
        row (pd.Series): A row of trader item data containing base price, selling price, and trader limits.
        use_current_price (bool, optional): Whether to use the current market price for commission calculation.
                                            Defaults to True.

    Returns:
        tuple: A tuple containing the commission for one item and the commission for the full trader limit.

    Note: Commission formula may change in different game versions. See here for more accurate formula if needs update: https://escapefromtarkov.fandom.com/wiki/Trading
    """

    if row["avg24hPrice"] is None:
        return (None, None)

    Q_min = 1
    Q_limit = row["buyLimit"]
    row_base_price = row["basePrice"]
    row_price_to_sell = row["lastLowPrice"]
    row_avg_price = row["avg24hPrice"]

    Ti = 0.03
    Tr = 0.03

    v0 = row_base_price

    if use_current_price:
        vr = row_price_to_sell
    else:
        vr = row_avg_price

    Po = numpy.log10(v0/vr)
    if (vr<v0):
        Po = Po**1.08

    Pr = numpy.log10(vr/v0)
    if (vr>=v0):
        Pr = Pr**1.08

    comission_1 = v0 * Ti * 4**Po * Q_min + vr * Tr * 4**Pr * Q_min
    comission_limit = v0 * Ti * 4**Po * Q_limit + vr * Tr * 4**Pr * Q_limit

    return (comission_1, comission_limit)

def get_task_name(x):

    """
    Retrieves the task name from a task dictionary.

    Args:
        x (dict): A dictionary containing task information.

    Returns:
        str: The name of the task if it exists, otherwise None.
    """
        
    try:
        return x["name"]
    except:
        pass

def compute_profit(row, use_current_price=True):

    """
    Computes the profit for buying and reselling an item based on current or average prices.

    Args:
        row (pd.Series): A row of trader item data containing prices and commissions.
        use_current_price (bool, optional): Whether to use the current market price for profit calculation.
                                            Defaults to True.

    Returns:
        tuple: A tuple containing profit for one item, profit for the full trader limit, and the percentage profit.
    """

    if row["avg24hPrice"] is None:
        return (None, None, None)
    
    if row["price"] is None:
        return (None, None, None)

    if row["price"] == 0:
        return (None, None, None)
    
    if use_current_price:
    
        profit_1 = row["lastLowPrice"] - row["com_1"] - row["priceRUB"]
        profit_full = row["lastLowPrice"]*row["buyLimit"] - row["com_full"] - row["priceRUB"]*row["buyLimit"]
        profit_1_perc = profit_1/row["price"] * 100
    
    else:
        profit_1 = row["avg24hPrice"] - row["com_1"] - row["priceRUB"]
        profit_full = row["avg24hPrice"]*row["buyLimit"] - row["com_full"] - row["priceRUB"]*row["buyLimit"]
        profit_1_perc = profit_1/row["price"] * 100

    return (profit_1, profit_full,profit_1_perc)

def compute_minimal_profitable_price(row):

    """
    Computes the minimum selling price required to make a profit after considering commissions and costs.

    Args:
        row (pd.Series): A row of trader item data containing base prices, buying costs, and commission rates.

    Returns:
        float: The minimum price required to make a profit, or None if the profit cannot be achieved.
    """

    if row["avg24hPrice"] is None:
        return (None, None)
    row_base_price = row["basePrice"]
    purchase_price = row["priceRUB"]
    Q_min = 1

    price_ranges = numpy.arange(row_base_price, row_base_price*15, step=25)

    def compute_profit_per_price(x):

        vr = x
        Ti = 0.03
        Tr = 0.03

        v0 = row_base_price
        Po = numpy.log10(v0/vr)

        if (vr<v0):
            Po = Po**1.08

        Pr = numpy.log10(vr/v0)
        if (vr>=v0):
            Pr = Pr**1.08
        comission_1 = v0 * Ti * 4**Po * Q_min + vr * Tr * 4**Pr * Q_min

        if comission_1 < 0:
            comission_1 = 0

        profit_1 = x - comission_1 - purchase_price
        return profit_1

    vectorized_function = numpy.vectorize(compute_profit_per_price)

    try:
        results = vectorized_function(price_ranges)
        positive_values_indices = numpy.where(results > 0)[0]
        minimal_positive_index = positive_values_indices[numpy.argmin(results[positive_values_indices])]
        indexed_value = price_ranges[minimal_positive_index]
        
        return indexed_value
    
    except:
        return None

def get_profitable_resells(trader_offers_list, directory, use_current_price = True):

    """
    Analyzes trader resell opportunities and generates Excel reports for each trader's profitable items.
    Ref is not supported at the moment as his pricing is GPs.

    Args:
        trader_offers_list (list): List of trader offers with item details and prices.
        directory (str): Path to save the generated Excel reports.
        use_current_price (bool, optional): Whether to use current prices for resell profit calculations.
                                            Defaults to True.
    """

    os.makedirs(directory, exist_ok=True)

    for trader in trader_offers_list:

        if trader["name"] in ["Скупщик","Смотритель","Водитель БТР","Реф"]:
            continue

        trader_co = trader["cashOffers"]

        for x in trader_co:
            sell_for = x["item"]["sellFor"]
            data = [(value["source"],value["priceRUB"]) for value in sell_for]
            for key, value in data:
                key = "sell_" + key
                x["item"][key] = value

        trader_co_df = pd.DataFrame(trader_co)
        trader_item_df = pd.DataFrame(list(trader_co_df["item"].values))
        trader_full_df = pd.concat([trader_item_df, trader_co_df], axis=1)
        trader_full_df['taskUnlock'] = trader_full_df['taskUnlock'].apply(get_task_name)
        trader_full_df = trader_full_df.drop(columns=['sellFor', 'item', "sell_fence", "sell_peacekeeper", 
                                                      "sell_mechanic", "sell_prapor", "sell_skier", "sell_ref", "sell_ragman", "sell_jaeger"],  errors='ignore')
        trader_full_df['category'] = trader_full_df['category'].apply(lambda x: x["name"])
        
        def compute_comission_wrapper(x, use_current_price = use_current_price):
            return compute_comission(x, use_current_price = use_current_price)
        
        def compute_profit_wrapper(x, use_current_price = use_current_price):
            return compute_profit(x, use_current_price = use_current_price)
        
        comission_results = trader_full_df.apply(compute_comission_wrapper, axis=1)
        trader_full_df["com_1"] = [x[0] for x in comission_results]
        trader_full_df["com_full"] = [x[1] for x in comission_results]

        profit_results = trader_full_df.apply(compute_profit_wrapper, axis=1)
        trader_full_df["prof_1"] = [x[0] for x in profit_results]
        trader_full_df["prof_full"] = [x[1] for x in profit_results]
        trader_full_df["profit_1_perc"] = [x[2] for x in profit_results]
        trader_full_df["min_profit_price"] = trader_full_df.apply(compute_minimal_profitable_price, axis=1)

        trader_full_df = trader_full_df.round(2)
        trader_full_df = trader_full_df.groupby(['category', "minTraderLevel"], group_keys=False).apply(lambda x: x.sort_values('prof_1', ascending=False))
        trader_full_df["trader_name"] = trader["name"]
        trader_full_df["trader_id"] = trader["id"]

        save_path = trader["name"] + "___trades.xlsx"

        save_path = os.path.join(directory, save_path)

        trader_full_df.to_excel(save_path)
        adjust_wb(save_path)