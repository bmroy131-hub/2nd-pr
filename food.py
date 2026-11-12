import streamlit as st
import pandas as pd


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Online Food Delivery Dashboard",
    page_icon="🍔",
    layout="wide"
)

st.title("🍔 Online Food Delivery Analysis Dashboard")
st.markdown(
    "Business Performance | Customer Behaviour | Delivery Analysis"
)

st.divider()


# =====================================================
# 2. LOAD DATASET
# =====================================================

file_path = r"C:\Users\Admin\Downloads\ONINE_FOOD_DELIVERY_ANALYSIS (1).csv"

try:
    df = pd.read_csv(file_path)
    st.success("Dataset loaded successfully!")

except FileNotFoundError:
    st.warning("CSV file was not found at the given location.")

    uploaded_file = st.file_uploader(
        "Upload your Online Food Delivery CSV file",
        type=["csv"]
    )

    if uploaded_file is None:
        st.stop()

    df = pd.read_csv(uploaded_file)
    st.success("Uploaded dataset loaded successfully!")


# =====================================================
# 3. CHECK DATASET COLUMNS
# =====================================================

required_columns = [
    "Order_ID",
    "Customer_ID",
    "Customer_Age",
    "Customer_Gender",
    "City",
    "Area",
    "Restaurant_ID",
    "Restaurant_Name",
    "Cuisine_Type",
    "Order_Date",
    "Order_Time",
    "Delivery_Time_Min",
    "Distance_km",
    "Order_Value",
    "Discount_Applied",
    "Final_Amount",
    "Payment_Mode",
    "Order_Status",
    "Cancellation_Reason",
    "Delivery_Partner_ID",
    "Delivery_Rating",
    "Restaurant_Rating",
    "Order_Day",
    "Peak_Hour",
    "Profit_Margin"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error("The following columns are missing from your CSV:")
    st.write(missing_columns)
    st.stop()


# =====================================================
# 4. DATA PREPROCESSING
# =====================================================

# Convert Order_Date into datetime format
df["Order_Date"] = pd.to_datetime(
    df["Order_Date"],
    errors="coerce"
)

# Standardize text columns
text_columns = [
    "City",
    "Cuisine_Type",
    "Payment_Mode",
    "Order_Status",
    "Customer_Gender",
    "Cancellation_Reason"
]

for column in text_columns:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
    )

# Standardize order status
df["Order_Status"] = df["Order_Status"].str.title()

# Convert numerical columns into numeric format
numeric_columns = [
    "Customer_Age",
    "Delivery_Time_Min",
    "Distance_km",
    "Order_Value",
    "Discount_Applied",
    "Final_Amount",
    "Delivery_Rating",
    "Restaurant_Rating",
    "Profit_Margin"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# =====================================================
# 5. SIDEBAR FILTERS
# =====================================================

st.sidebar.title("🔎 Dashboard Filters")

# City filter
city_options = sorted(
    df["City"].dropna().unique().tolist()
)

selected_cities = st.sidebar.multiselect(
    "Select City",
    options=city_options,
    default=city_options
)

# Cuisine filter
cuisine_options = sorted(
    df["Cuisine_Type"].dropna().unique().tolist()
)

selected_cuisines = st.sidebar.multiselect(
    "Select Cuisine",
    options=cuisine_options,
    default=cuisine_options
)

# Order status filter
status_options = sorted(
    df["Order_Status"].dropna().unique().tolist()
)

selected_status = st.sidebar.multiselect(
    "Select Order Status",
    options=status_options,
    default=status_options
)

# Date filter
valid_dates = df["Order_Date"].dropna()

selected_dates = None

if not valid_dates.empty:

    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    selected_dates = st.sidebar.date_input(
        "Select Order Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )


# =====================================================
# 6. APPLY FILTERS
# =====================================================

filtered_df = df[
    df["City"].isin(selected_cities)
    & df["Cuisine_Type"].isin(selected_cuisines)
    & df["Order_Status"].isin(selected_status)
].copy()

# Apply date filter only when a start and end date are selected
if (
    isinstance(selected_dates, (tuple, list))
    and len(selected_dates) == 2
):

    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        filtered_df["Order_Date"].dt.date.between(
            start_date,
            end_date
        )
    ]


# =====================================================
# 7. KEY PERFORMANCE INDICATORS (KPIs)
# =====================================================

st.header("📊 Key Performance Indicators")

total_orders = filtered_df["Order_ID"].nunique()

# Delivered orders
delivered_df = filtered_df[
    filtered_df["Order_Status"] == "Delivered"
].copy()

# Cancelled orders
cancelled_df = filtered_df[
    filtered_df["Order_Status"] == "Cancelled"
].copy()

delivered_orders = delivered_df["Order_ID"].nunique()
cancelled_orders = cancelled_df["Order_ID"].nunique()

# Revenue from delivered orders
total_revenue = delivered_df["Final_Amount"].sum()

# Average order value
average_order_value = (
    total_revenue / delivered_orders
    if delivered_orders > 0
    else 0
)

# Average delivery time
average_delivery_time = delivered_df[
    "Delivery_Time_Min"
].mean()

# Cancellation percentage
cancellation_rate = (
    cancelled_orders / total_orders * 100
    if total_orders > 0
    else 0
)

# Average delivery rating
average_delivery_rating = delivered_df[
    "Delivery_Rating"
].mean()

# Average profit margin
average_profit_margin = delivered_df[
    "Profit_Margin"
].mean()


# Display first row of KPI cards
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Orders",
    f"{total_orders:,}"
)

col2.metric(
    "Delivered Orders",
    f"{delivered_orders:,}"
)

col3.metric(
    "Total Revenue",
    f"₹{total_revenue:,.2f}"
)

col4.metric(
    "Cancellation Rate",
    f"{cancellation_rate:.2f}%"
)


# Display second row of KPI cards
col5, col6, col7, col8 = st.columns(4)

col5.metric(
    "Average Order Value",
    f"₹{average_order_value:,.2f}"
)

col6.metric(
    "Average Delivery Time",
    f"{average_delivery_time:.1f} min"
    if pd.notna(average_delivery_time)
    else "N/A"
)

col7.metric(
    "Average Delivery Rating",
    f"{average_delivery_rating:.2f}/5"
    if pd.notna(average_delivery_rating)
    else "N/A"
)

col8.metric(
    "Average Profit Margin",
    f"{average_profit_margin:.2f}"
    if pd.notna(average_profit_margin)
    else "N/A"
)


# =====================================================
# 8. CITY-WISE ORDER ANALYSIS
# =====================================================

st.divider()
st.header("🏙️ City-wise Order Analysis")

city_orders = (
    filtered_df
    .groupby("City")["Order_ID"]
    .nunique()
    .reset_index(name="Total Orders")
    .sort_values("Total Orders", ascending=False)
)

if not city_orders.empty:
    st.bar_chart(
        city_orders,
        x="City",
        y="Total Orders"
    )
else:
    st.info("No city data available for the selected filters.")


# =====================================================
# 9. CUISINE-WISE ORDER ANALYSIS
# =====================================================

st.divider()
st.header("🍕 Cuisine-wise Order Analysis")

cuisine_orders = (
    filtered_df
    .groupby("Cuisine_Type")["Order_ID"]
    .nunique()
    .reset_index(name="Total Orders")
    .sort_values("Total Orders", ascending=False)
)

if not cuisine_orders.empty:
    st.bar_chart(
        cuisine_orders,
        x="Cuisine_Type",
        y="Total Orders"
    )
else:
    st.info("No cuisine data available for the selected filters.")


# =====================================================
# 10. DAILY ORDER TRENDS
# =====================================================

st.divider()
st.header("📅 Daily Order Trends")

daily_orders = (
    filtered_df
    .dropna(subset=["Order_Date"])
    .groupby("Order_Date")["Order_ID"]
    .nunique()
    .reset_index(name="Total Orders")
    .sort_values("Order_Date")
)

if not daily_orders.empty:
    st.line_chart(
        daily_orders,
        x="Order_Date",
        y="Total Orders"
    )
else:
    st.info("No date data available for the selected filters.")


# =====================================================
# 11. PAYMENT MODE ANALYSIS
# =====================================================

st.divider()
st.header("💳 Payment Mode Analysis")

payment_data = (
    filtered_df
    .groupby("Payment_Mode")["Order_ID"]
    .nunique()
    .reset_index(name="Total Orders")
    .sort_values("Total Orders", ascending=False)
)

if not payment_data.empty:
    st.bar_chart(
        payment_data,
        x="Payment_Mode",
        y="Total Orders"
    )
else:
    st.info("No payment data available.")


# =====================================================
# 12. ORDER STATUS ANALYSIS
# =====================================================

st.divider()
st.header("📦 Order Status Analysis")

status_data = (
    filtered_df
    .groupby("Order_Status")["Order_ID"]
    .nunique()
    .reset_index(name="Total Orders")
    .sort_values("Total Orders", ascending=False)
)

if not status_data.empty:
    st.bar_chart(
        status_data,
        x="Order_Status",
        y="Total Orders"
    )
else:
    st.info("No order status data available.")


# =====================================================
# 13. CANCELLATION REASON ANALYSIS
# =====================================================

st.divider()
st.header("❌ Cancellation Reason Analysis")

cancellation_data = (
    cancelled_df["Cancellation_Reason"]
    .fillna("Not specified")
    .value_counts()
    .reset_index()
)

cancellation_data.columns = [
    "Cancellation Reason",
    "Count"
]

if not cancellation_data.empty:

    st.bar_chart(
        cancellation_data,
        x="Cancellation Reason",
        y="Count",
        horizontal=True
    )

else:
    st.info("No cancelled orders in the selected filters.")


# =====================================================
# 14. DELIVERY DISTANCE VS DELIVERY TIME
# =====================================================

st.divider()
st.header("🚴 Delivery Performance Analysis")

delivery_data = filtered_df.dropna(
    subset=[
        "Distance_km",
        "Delivery_Time_Min"
    ]
)

if not delivery_data.empty:

    st.scatter_chart(
        delivery_data,
        x="Distance_km",
        y="Delivery_Time_Min",
        color="Order_Status"
    )

else:
    st.info("No delivery data available for this chart.")


# =====================================================
# 15. REVENUE BY CITY
# =====================================================

st.divider()
st.header("💰 Revenue Analysis")

revenue_city = (
    delivered_df
    .groupby("City")["Final_Amount"]
    .sum()
    .reset_index(name="Revenue")
    .sort_values("Revenue", ascending=False)
)

if not revenue_city.empty:

    st.bar_chart(
        revenue_city,
        x="City",
        y="Revenue"
    )

else:
    st.info("No revenue data available for the selected filters.")


# =====================================================
# 16. CUSTOMER GENDER ANALYSIS
# =====================================================

st.divider()
st.header("👥 Customer Analysis")

gender_data = (
    filtered_df
    .groupby("Customer_Gender")["Customer_ID"]
    .nunique()
    .reset_index(name="Total Customers")
    .sort_values("Total Customers", ascending=False)
)

if not gender_data.empty:

    st.bar_chart(
        gender_data,
        x="Customer_Gender",
        y="Total Customers"
    )

else:
    st.info("No customer gender data available.")


# =====================================================
# 17. FILTERED DATASET
# =====================================================

st.divider()
st.header("📋 Filtered Dataset")

st.write(
    "Total records after applying filters:",
    len(filtered_df)
)

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=350
)


# =====================================================
# 18. DOWNLOAD FILTERED DATASET
# =====================================================

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Dataset",
    data=csv_data,
    file_name="filtered_food_delivery_data.csv",
    mime="text/csv"
)


# =====================================================
# 19. FOOTER
# =====================================================

st.divider()

st.markdown(
    "### Online Food Delivery Analysis Dashboard"
)

st.caption(
    "Developed using Python, Pandas and Streamlit"
)