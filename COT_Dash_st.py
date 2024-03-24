import pandas as pd
import cot_reports as cot
import streamlit as st 

@st.cache_data
def load_data(year=2024, report_type='legacy_fut'):
    df = cot.cot_year(year=year, cot_report_type=report_type)
    df["As of Date in Form YYYY-MM-DD"] = pd.to_datetime(df["As of Date in Form YYYY-MM-DD"])
    return df

def prepare_data(df):
    filtered_df = df[["Market and Exchange Names", "As of Date in Form YYYY-MM-DD", 
                      "Noncommercial Positions-Long (All)", "Noncommercial Positions-Short (All)", 
                      "Change in Noncommercial-Long (All)", "Change in Noncommercial-Short (All)",
                      "% of OI-Noncommercial-Long (All)", "% of OI-Noncommercial-Short (All)" ]]
    filtered_df['Flip'] = filtered_df["% of OI-Noncommercial-Long (All)"] - filtered_df["% of OI-Noncommercial-Short (All)"]
    filtered_df.set_index("As of Date in Form YYYY-MM-DD", inplace=True) 
    return filtered_df

def plot_chart(data, title):
    st.line_chart(data, use_container_width=True)
    st.text(title)

def main():
    # Load data
    df = load_data()
    
    # Prepare data
    filtered_df = prepare_data(df)
    
    # Get unique futures instruments
    futures_list_display = ["NASDAQ MINI - CHICAGO MERCANTILE EXCHANGE", 
                            "E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE",
                            "RUSSELL E-MINI - CHICAGO MERCANTILE EXCHANGE",
                            "BITCOIN - CHICAGO MERCANTILE EXCHANGE",
                            "VIX FUTURES - CBOE FUTURES EXCHANGE"]
    
    # Title
    st.title('COT Report Dashboard')
    
    # First chart
    selected_futures = st.selectbox("Select Futures Instrument", futures_list_display)
    filtered_data = filtered_df[filtered_df["Market and Exchange Names"] == selected_futures]
    plot_chart(filtered_data[["% of OI-Noncommercial-Long (All)", "% of OI-Noncommercial-Short (All)"]],
               "Noncommercial Positions")
    
    # Second Chart
    plot_chart(filtered_data["Flip"], "Difference in Noncommercial Positions i.e 'Flip'")

if __name__ == "__main__":
    main()
