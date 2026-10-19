# My Python Capstone project
🇰🇪 Analysis of Food Prices in Kenya: A Study of Maize and Bean Prices Across Markets

📌 Project Overview

This project analyzes maize and bean prices across different markets in Kenya using real-world food price data from the Food and Agriculture Organization (FAO).

The aim is to understand how food prices change over time, how prices vary between markets, and whether monthly price patterns can be identified.

The analysis is presented through an interactive dashboard built with Python, Plotly, and Streamlit.

❗ Problem Statement

Food prices can change over time and differ from one market to another. These changes affect household budgets, traders, and communities.

This project uses data analysis and visualization to explore historical maize and bean prices in Kenya, helping people understand price trends and differences across markets.

🎯 Project Objectives

* Analyze maize and bean price trends over time.
* Compare average food prices across markets.
* Investigate monthly patterns in maize and bean prices.
* Examine missing values in the dataset.
* Build an interactive dashboard for exploring food price information.

📊 Dataset

The dataset was obtained from the Food and Agriculture Organization (FAO).

Dataset file: KEN_RTFP_mkt_2007_2026-10-05.csv

The original dataset contains 55,692 rows and 46 columns, covering 234 markets.

This project focuses on two commodities:

* 🌽 Maize: maize_fao
* 🫘 Beans: beans

The dataset includes dates, market names, administrative regions, and food price information.

Missing price observations are considered during analysis and are not treated as zero prices.

🛠️ Tools and Technologies

* Python — Programming and data analysis.
* Pandas — Data cleaning, filtering, and manipulation.
* Plotly — Interactive data visualizations.
* Streamlit — Building the interactive dashboard.
* Jupyter Notebook — Exploratory data analysis.
* Visual Studio Code — Development environment.
* Git and GitHub — Version control and project sharing.

📈 Dashboard Features

1. Overview

Displays summary statistics, including available records, markets covered, and average maize and bean prices.

2. Price Trends

Visualizes how maize and bean prices change over time.

3. Market Comparisons

Compares average recorded maize and bean prices across different markets.

4. Seasonal Analysis

Examines monthly average prices to identify possible recurring patterns.

5. Data Explorer

Allows users to explore filtered records, inspect missing values, and download filtered data where supported.

🔍 Research Questions

1. How have maize and bean prices changed over time?
2. How do average maize and bean prices differ across markets?
3. Which months have relatively higher or lower average prices?
4. How can data visualization make food price information easier to understand?

⚙️ Methodology

The project follows these steps:

1. Load the dataset using Pandas.
2. Inspect the data structure and identify missing values.
3. Prepare the date and price columns for analysis.
4. Select the maize and bean price variables.
5. Calculate summary statistics and group prices by year, market, and month.
6. Create charts using Plotly.
7. Build an interactive dashboard using Streamlit.
8. Interpret the findings and consider data limitations.

🌍 Expected Impact

The project can help:

* Households understand historical food price patterns when planning budgets.
* Traders compare recorded prices across markets.
* Students and researchers explore real-world data analysis.
* Community planners identify price patterns that may require further investigation.

The analysis describes historical patterns. It does not automatically predict future prices or establish the causes of price changes.

📁 Project Structure

Kenya-food-prices/
│
├── app.py
├── food_prices_analysis.ipynb
├── KEN_RTFP_mkt_2007_2026-10-05.csv
├── README.md



🚀 How to Run the Project

Prerequisites

Install Python and ensure the project files are available on your computer.

1. Install the required libraries

python -m pip install pandas plotly streamlit jupyter

2. Open the project folder

Open the Kenya-food-prices folder in Visual Studio Code.

3. Run the Streamlit dashboard

python -m streamlit run app.py

Streamlit will provide a local URL that you can open in your browser.

Ensure the CSV dataset is available at the location expected by app.py.

⚠️ Limitations

* Some maize and bean price observations are missing.
* The analysis is limited to the available data and selected commodities.
* Market averages may hide differences between individual dates or observations.
* Monthly patterns do not necessarily prove seasonal causes.
* The project does not independently establish why prices rise or fall.

🔮 Future Improvements

* Add reliable county-level geographical analysis.
* Explore relationships between food prices and other economic factors.
* Improve data quality checks and missing-value analysis.
* Add more food commodities.
* Investigate methods for forecasting future prices.

👩‍💻 Author

Gloria Ngina

📜 Data Source

WORLD BANK— Food Price Data.

This project is intended for educational and analytical purposes.

⸻

⭐ Using Python and data visualization to better understand food price patterns in Kenya.
