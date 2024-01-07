#!/usr/bin/env python
# coding: utf-8

# In[1]:
pip install plotly.graph_objects

import streamlit as st
import pandas as pd
import plotly.graph_objects as go


from sqlalchemy import create_engine


# In[2]:


engine = create_engine('mssql://DESKTOP-1PS8E8C/AdventureWorks2022?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
connection = engine.connect()


# In[3]:


# Write about the why and not the how (the how is in the code)
query_1 = """
SELECT
    SOD.SalesOrderID,
    SOH.[Status],
    SOH.ShipDate,
    FORMAT(SOH.ShipDate, 'yyyy-MM') AS SalesMonthYear,
	SOH.OnlineOrderFlag,
	SOH.SalesPersonID,
    SOH.TerritoryID,
	ST.[Group],
	SOH.TotalDue,
    SOH.SubTotal,
    SUM(SOD.OrderQty * ISNULL(PCH.StandardCost, P.StandardCost)) AS COGS,
    SUM(SOD.LineTotal) - SUM(SOD.OrderQty * ISNULL(PCH.StandardCost, P.StandardCost)) AS Margin,
    YEAR(SOH.ShipDate) AS SalesYear,
    MONTH(SOH.ShipDate) AS SalesMonth
FROM Sales.SalesOrderHeader AS SOH
INNER JOIN Sales.SalesOrderDetail AS SOD ON SOH.SalesOrderID = SOD.SalesOrderID
INNER JOIN Production.Product AS P ON p.ProductID = SOD.ProductID
LEFT JOIN Sales.SalesTerritory AS ST on st.TerritoryID = SOH.TerritoryID
LEFT JOIN Production.ProductCostHistory AS PCH on PCH.ProductID = P.ProductID and (PCH.StartDate <= SOH.ShipDate and ISNULL(PCH.enddate,'9999-12-31') > SOH.shipdate)
WHERE SOH.[Status] = 5
GROUP BY SOD.SalesOrderID, SOH.[Status], SOH.ShipDate, SOH.OnlineOrderFlag, SOH.SalesPersonID, SOH.TotalDue, SOH.SubTotal, YEAR(SOH.ShipDate), MONTH(SOH.ShipDate), SOH.TerritoryID, ST.[Group]
ORDER BY SalesYear;
"""
pd.read_sql(query_1, con=connection)


# In[ ]:


st.set_page_config(page_title="AdventureWorks Dashboard", 
                   page_icon="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Map-circle-blue.svg/1024px-Map-circle-blue.svg.png",
                   initial_sidebar_state="expanded",
                   )

hero = st.container()
topRow = st.container()
midRow = st.container()
chartRow = st.container()
footer = st.container()


# In[4]:


df1 = pd.read_sql(query_1, con=connection)


# In[ ]:


# CSS styles
# Custom styling for top and down
st.markdown(
    """
    <style>
    .top-stats {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 12px 0 40px 0;
        width: 100%;
        height: 40px;
    }
    .subheader {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .stat {
        flex: 1; 

        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        background-color: #111;

        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    .stat p {
        padding-top: 8px;
    }
    .stat p {
        color: #bbb;
        font-size: 12px;
    }
    .stat span {
        color: #ddd;
        font-size: 24px;
        font-family: serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# In[ ]:


# Sidebar
with st.sidebar:
    st.markdown(f'''
        <style>
        section[data-testid="stSidebar"] {{
                width: 500px;
                background-color: #000b1a;
                }}
        section[data-testid="stSidebar"] h1 {{
                color: #e3eefc;
                }}
        section[data-testid="stSidebar"] p {{
                color: #ddd;
                text-align: left;
                }}
        section[data-testid="stSidebar"] svg {{
                fill: #ddd;
                }}
        </style>
    ''',unsafe_allow_html=True)
    st.title("AdventureWorks")
    st.markdown("This visualization gives a quick glance at a few KPI metrics from the AdventureWorks sample SQL Database. You can choose which year to inspect or the business as a whole and also divide it into B2B sales or B2C (Online sales).")
    
    # The Selectbox
    Sales_Year = df1['SalesYear'].unique()
    line = st.selectbox('',['Total Sales'] + list(Sales_Year))
    if line == 'Total Sales':
        chosen_line = df1
    else:
        chosen_line = df1[df1['SalesYear'] == line]

    # Customizing the select box
    st.markdown(f'''
    <style>
        .stSelectbox div div {{
                background-color: #fafafa;
                color: #333;
        }}
        .stSelectbox div div:hover {{
                cursor: pointer
        }}
        .stSelectbox div div .option {{
                background-color: red;
                color: #111;
        }}
        .stSelectbox div div svg {{
                fill: black;
        }}
    </style>
    ''', unsafe_allow_html=True)


# In[ ]:


# The Hero Section
with hero:
    # the logo
    st.markdown("""<div style="position:relative; margin: auto; text-align: center;">
              <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Map-circle-blue.svg/1024px-Map-circle-blue.svg.png" width=56>
            </div>""", unsafe_allow_html=True)

    # the header
    st.markdown('<h1 style="text-align:center; position:relative; top:40%;">AdventureWorks Sales</h1>', unsafe_allow_html=True)


# In[ ]:


# The Rows
with topRow:

    # Calculate the total number of invoices
    total_turnover = chosen_line['SubTotal'].sum()

    # Calculate the average rating and number of ratings
    total_cogs = chosen_line['COGS'].sum()

    # Find the most active time for invoices
    total_gp = chosen_line['Margin'].sum()
    # the result is 2:14 PM so I'll type it by hand for now.
    st.markdown(
        """
        <div class="subheader">Top Stats</div>
        <div class="top-stats">
            <div class="stat">
                <p>Turnover<br><span>%.2f$M</span></p>
            </div>
            <div class="stat">
                <p>COGS<br><span>%.2f$M</span></p>
            </div>
            <div class="stat">
                <p>Gross Profit<br><span>%.2f$M</span></p>
            </div>
        </div>
        """ % (total_turnover / 1e6, total_cogs / 1e6, total_gp / 1e6),
        unsafe_allow_html=True
    )
    
with midRow:
    # Calculate the total income, costs, and profit
    grossmargin_pct = chosen_line['Margin'].sum() / chosen_line['SubTotal'].sum()
    b2b_turnover = chosen_line[chosen_line['OnlineOrderFlag'] == False]['SubTotal'].sum()
    b2c_turnover = chosen_line[chosen_line['OnlineOrderFlag'] == True]['SubTotal'].sum()
    b2b_gm = chosen_line[chosen_line['OnlineOrderFlag'] == False]['Margin'].sum() / chosen_line[chosen_line['OnlineOrderFlag'] == False]['SubTotal'].sum()
    b2c_gm = chosen_line[chosen_line['OnlineOrderFlag'] == True]['Margin'].sum() / chosen_line[chosen_line['OnlineOrderFlag'] == True]['SubTotal'].sum()
    st.markdown(
        """
        <div class="top-stats">
            <div class="stat" style="background-color: #3E4095;">
                <p>Gross Margin<br><span>%.1f%%</span></p>
            </div>
            <div class="stat" style="background-color: #9370DB;">
                <p>B2B Turnover<br><span>%.2f$M</span></p>
                <p>B2B Gross Margin<br><span>%.1f%%</span></p>
            </div>
            <div class="stat" style="background-color: #7E83D1;">
                <p>B2C Turnover<br><span>%.2f$M</span></p>
                <p>B2C Gross Margin<br><span>%.1f%%</span></p>
            </div>
        </div>
        """ % (grossmargin_pct * 100, b2b_turnover / 1e6, b2b_gm * 100, b2c_turnover / 1e6, b2c_gm * 100),
        unsafe_allow_html=True
    )



with chartRow:
    # Filter for the month
    #df1['Order_date'] = pd.to_datetime(superSales['Order_date'])
    #mar_data = (superSales['Order_date'].dt.month == 3)
    #lineQuantity = chosen_line[(mar_data)]

    # Quantity for each day
    #quantity_per_day = lineQuantity.groupby('Order_date')['Quantity'].sum().reset_index()

    # some space
    st.markdown('<div></div>', unsafe_allow_html=True)
    
    # Create a line chart for Quantity over the last month using Plotly
    fig_linechart = go.Figure()
  
    fig_linechart.add_trace(go.Scatter(x=sorted(chosen_line['SalesMonthYear'].unique()), y=chosen_line.groupby('SalesMonthYear')['SubTotal'].sum()
                         , name='Turnover',
                         line = dict(color='royalblue', width=4), mode='lines+markers', marker=dict(size=10)))
    fig_linechart.add_trace(go.Scatter(x=sorted(chosen_line['SalesMonthYear'].unique()), y=chosen_line.groupby('SalesMonthYear')['COGS'].sum()
                         , name='COGS',
                         line = dict(color='green', width=4, dash='dot'), mode='lines+markers', marker=dict(size=10)))
    fig_linechart.add_trace(go.Scatter(x=sorted(chosen_line['SalesMonthYear'].unique()), y=chosen_line.groupby('SalesMonthYear')['Margin'].sum()
                         , name='Gross Profit',
                         line=dict(color='orange', width=4, dash='dot'), mode='lines+markers', marker=dict(size=10)))
    fig_linechart.update_layout(title='Financial drivers', xaxis_title='Month', yaxis_title='',
        margin_r=100,
    )

    
    st.plotly_chart(fig_linechart)


with footer:
    st.markdown("---")
    st.markdown(
        """
        <style>
            p {
                font-size: 16px;
                text-align: center;
            }
            a {
                text-decoration: none;
                color: #00a;
                font-weight: 600;
            }
        </style>
        <p>
            &copy; Designed by William Blennow.
        </p>
        """, unsafe_allow_html=True
        )    


# In[ ]:




