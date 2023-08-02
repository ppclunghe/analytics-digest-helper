import pandas as pd


def process_tvl(df: pd.DataFrame) -> str:
    # Select the row corresponding to 'Total'
    total_row = df[df["chain"] == "Total"]

    # Extract the 'TVL' and 'TVL change, %' from the total row
    total_tvl = total_row["TVL"].values[0]
    total_tvl_change = total_row["TVL change, %"].values[0] * 100

    # Format the total TVL and total TVL change into strings
    total_tvl_str = f"${total_tvl / 1e9:.2f}b"
    total_tvl_change_str = f"{total_tvl_change:.2f}%"

    # Select the rows corresponding to 'Ethereum' and 'Polygon'
    eth_row = df[df["chain"] == "Ethereum"]
    polygon_row = df[df["chain"] == "Polygon"]

    # Extract the 'Token price change, %' from the Ethereum and Polygon rows
    eth_price_change = float(eth_row["Token price change, %"].values[0]) * 100
    polygon_price_change = float(polygon_row["Token price change, %"].values[0]) * 100

    # Format the Ethereum and Polygon price changes into strings
    eth_price_change_str = f"{eth_price_change:.2f}%"
    polygon_price_change_str = f"{polygon_price_change:.2f}%"

    # Combine everything into a result string
    result_string = (
        f"TVL: {total_tvl_str}\n"
        f"TVL Percentage Change: {total_tvl_change_str}\n"
        f"Ethereum Token Price Change: {eth_price_change_str}\n"
        f"Polygon Token Price Change: {polygon_price_change_str}"
    )

    return result_string


def process_netDepositGrowthLeaders(df: pd.DataFrame) -> str:
    # Calculate rank by net deposit growth
    df = df.sort_values("eth_deposits_growth", ascending=False)
    df["rank"] = range(1, len(df) + 1)

    # Find Lido's stats
    lido_stats = df[df["name"] == "Lido"]

    # If Lido is not in the list, return None for both values
    if lido_stats.empty:
        return ""

    lido_net_deposit_growth = round(lido_stats.iloc[0]["eth_deposits_growth"], 2)
    lido_rank = lido_stats.iloc[0]["rank"]

    return f"Lido had net deposit growth of {lido_net_deposit_growth} ETH. ETH Growth Leaderboard rank: {lido_rank}"


def process_stETHApr(df: pd.DataFrame) -> str:
    # Get the most recent 7d moving average
    recent_7d_ma = df["stakingAPR_ma_7"].values[0]

    # Convert the value to percentage and format it with 2 decimal places
    recent_7d_ma_percentage = "{:.2%}".format(recent_7d_ma)

    # Format the result into a string
    result_string = f"7d MA: {recent_7d_ma_percentage}"

    return result_string


def process_stEthToEth(df: pd.DataFrame) -> str:
    # Get the most recent weight_avg_price
    recent_avg_price = df["weight_avg_price"].values[0]

    # Format the result into a string with 6 decimal places
    result_string = f"stETH/ETH price: {recent_avg_price:.6f}"

    return result_string


def process_dexLiquidityReserves(df: pd.DataFrame) -> str:
    # Select the row corresponding to 'total'
    total_row = df[df["token"] == "total"]

    # Extract the 'end value' and 'period_change' from this row
    end_value = total_row["end value"].values[0]
    period_change = total_row["period_change"].values[0]

    # Format the end value into a string in billions with 2 decimal places
    end_value_str = f"${end_value / 1e9:.2f}b"

    # Format the period change into a string as a percentage with 2 decimal places
    period_change_str = f"{period_change * 100:.2f}%"

    # Combine these into a result string
    result_string = f"Total End Value: {end_value_str}\nPeriod Change: {period_change_str}"

    return result_string


def process_totalStEthinDeFi(df: pd.DataFrame) -> str:
    def format_row(row):
        # Format the row's data into a nice string.
        title = row["title"].capitalize()
        start_amount = row["start_amount"]
        end_amount = row["end_amount"]
        period_change = row["period_change"] * 100  # Convert to percentage

        # Format amounts with commas as thousand separators and two decimal places.
        formatted_start_amount = "{:,.2f}".format(start_amount)
        formatted_end_amount = "{:,.2f}".format(end_amount)
        formatted_period_change = "{:.2f}%".format(period_change)

        # Check if the change is negative (a decrease).
        if period_change < 0:
            # If it's a decrease, remove the negative sign from the change and say "decreased by".
            formatted_string = f"{title} decreased by {formatted_period_change[1:]}, ending at {formatted_end_amount}"
        else:
            # If it's not a decrease, say "increased by".
            formatted_string = f"{title} increased by {formatted_period_change}, ending at {formatted_end_amount}"

        return formatted_string

    # Apply the function to each row in the df, creating a list of formatted strings.
    formatted_strings = df.apply(format_row, axis=1).tolist()
    return "\n".join(formatted_strings)


def process_stEthOnL2(df: pd.DataFrame) -> str:
    # Select the row corresponding to 'total'
    total_row = df[df["bridge"] == "total"]

    # Extract the 'end_amount' and 'period_change' from the total row
    total_end_amount = total_row["end_amount"].values[0]
    total_period_change = total_row["period_change"].values[0]

    # Format the total end amount and total period change into strings
    total_end_amount_str = f"{total_end_amount:.0f} wstETH"
    total_period_change_str = f"{total_period_change:.2f}%"

    # Initialize an empty string to store the individual bridge data
    bridge_data_str = ""

    # Loop over the rows of the DataFrame
    for i, row in df.iterrows():
        # Skip the total row
        if row["bridge"] == "total":
            continue

        # Extract the 'bridge', 'end_amount' and 'period_change' for each row
        bridge = row["bridge"]
        end_amount = row["end_amount"]
        period_change = row["period_change"]

        # Format the end amount and period change into strings
        end_amount_str = f"{end_amount:.0f} wstETH"
        period_change_str = f"{period_change:.2f}%"

        # Append this bridge's data to the bridge data string
        bridge_data_str += f"{bridge}: {end_amount_str} (7d: {period_change_str})\n"

    # Combine the total and bridge data into a result string
    result_string = f"The amount of wstETH on L2 grew by {total_period_change_str}, hitting {total_end_amount_str}:\n\n{bridge_data_str}"

    return result_string


def process_bridgeChange(df):
    # Get the period changes for each bridge type
    total_change = round(df.loc[df["bridge"] == "total", "period_change"].values[0], 2)
    arbitrum_change = round(df.loc[df["bridge"] == "Arbitrum Bridges", "period_change"].values[0], 2)
    optimism_change = round(df.loc[df["bridge"] == "Optimism Bridges", "period_change"].values[0], 2)
    polygon_change = round(df.loc[df["bridge"] == "Polygon Bridges", "period_change"].values[0], 2)

    # Format and return the message
    return (
        f"Total period change: {total_change}. "
        f"Arbitrum Bridge Change: {arbitrum_change}. "
        f"Optimism Bridge Change: {optimism_change}. "
        f"Polygon Bridge Change: {polygon_change}"
    )


# Define a dictionary mapping the DataFrame names to their respective processing functions
process_functions = {
    "tvl": process_tvl,
    "netDepositGrowthLeaders": process_netDepositGrowthLeaders,
    "stETHApr": process_stETHApr,
    "stEthToEth": process_stEthToEth,
    "dexLiquidityReserves": process_dexLiquidityReserves,
    "bridgeChange": process_bridgeChange,
    "totalStEthinDeFi": process_totalStEthinDeFi,
}


def process_dune(dune_results: dict[str, pd.DataFrame]) -> dict[str, str]:
    res = {}

    for df_name, df in dune_results.items():
        process_func = process_functions.get(df_name)
        if process_func is not None:
            s = process_func(df)
            res[df_name] = s

    return res