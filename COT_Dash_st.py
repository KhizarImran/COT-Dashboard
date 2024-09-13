import pandas as pd
import cot_reports as cot
import streamlit as st
import plotly.graph_objects as go

# Set the page layout to wide
st.set_page_config(layout="wide")

@st.cache_data
def load_data(year=2024, report_type='legacy_fut'):
    df = cot.cot_year(year=year, cot_report_type=report_type)
    df["As of Date in Form YYYY-MM-DD"] = pd.to_datetime(df["As of Date in Form YYYY-MM-DD"])
    return df

@st.cache_data
def load_instruments():
    with open('financials.txt', 'r') as file:
        return [line.strip() for line in file]

def prepare_data(df, instruments):
    # Filter rows for specified instruments
    filtered_df = df[df["Market and Exchange Names"].isin(instruments)]
    
    # Select relevant columns
    filtered_df = filtered_df[["Market and Exchange Names", "As of Date in Form YYYY-MM-DD", 
                               "Noncommercial Positions-Long (All)", "Noncommercial Positions-Short (All)", 
                               "Change in Noncommercial-Long (All)", "Change in Noncommercial-Short (All)",
                               "% of OI-Noncommercial-Long (All)", "% of OI-Noncommercial-Short (All)",
                               "% of OI-Nonreportable-Long (All)", "% of OI-Nonreportable-Short (All)"]]
    
    # Calculate 'Flip' columns for both Noncommercial and Nonreportable
    filtered_df['Noncommercial Flip'] = filtered_df["% of OI-Noncommercial-Long (All)"] - filtered_df["% of OI-Noncommercial-Short (All)"]
    filtered_df['Nonreportable Flip'] = filtered_df["% of OI-Nonreportable-Long (All)"] - filtered_df["% of OI-Nonreportable-Short (All)"]
    
    # Set index
    filtered_df.set_index("As of Date in Form YYYY-MM-DD", inplace=True) 
    
    return filtered_df

def plot_chart(data, title, y_axis_title):
    fig = go.Figure()
    
    for column in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data[column], mode='lines', name=column))
    
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title=y_axis_title,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_cot_charts(filtered_df, instruments):
    st.header("COT Report Analysis")
    
    # Use the list of instruments for the dropdown
    selected_futures = st.selectbox("Select Futures Instrument", instruments)
    
    # Filter data for the selected futures
    filtered_data = filtered_df[filtered_df["Market and Exchange Names"] == selected_futures]
    
    # Display charts in 2x2 layout
    col1, col2 = st.columns(2)
    
    # First chart: Noncommercial Positions
    with col1:
        plot_chart(
            filtered_data[["% of OI-Noncommercial-Long (All)", "% of OI-Noncommercial-Short (All)"]],
            "Noncommercial Positions - Long vs Short",
            "Percentage of Open Interest"
        )
    
    # Second Chart: Difference in Noncommercial Positions
    with col2:
        plot_chart(
            filtered_data[["Noncommercial Flip"]],
            "Noncommercial Flip (Long - Short)",
            "Difference in Percentage"
        )
    
    # Heading for Non-reportable section
    st.subheader("Non-reportable")
    
    col3, col4 = st.columns(2)
    
    # Third Chart: Non-reportable Positions
    with col3:
        plot_chart(
            filtered_data[["% of OI-Nonreportable-Long (All)", "% of OI-Nonreportable-Short (All)"]],
            "Non-reportable Positions - Long vs Short",
            "Percentage of Open Interest"
        )
    
    # Fourth Chart: Difference in Non-reportable Positions
    with col4:
        plot_chart(
            filtered_data[["Nonreportable Flip"]],
            "Non-reportable Flip (Long - Short)",
            "Difference in Percentage"
        )

def main():
    # Load data
    df = load_data()
    
    # Load instruments from file
    instruments = load_instruments()
    
    # Prepare data
    filtered_df = prepare_data(df, instruments)
    
    # Title
    st.title('COT Report Analysis Dashboard')
    
    # Display COT charts
    display_cot_charts(filtered_df, instruments)

if __name__ == "__main__":
    main()