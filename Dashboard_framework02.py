#!/usr/bin/env python
# coding: utf-8



import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy import stats

st.set_page_config(page_title="AdventureWorks Dashboard", 
                   page_icon= "\U0001F6B2",
                   initial_sidebar_state="expanded",
                   )

hero = st.container()
topRow = st.container()
midRow = st.container()
chartRow = st.container()
confidenceintervalRow = st.container()
footer = st.container()





df1 = pd.read_csv('https://raw.githubusercontent.com/wilble/Streamlit/main/Data/output.csv')

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
    .description-box {
        width: 100%;
        background-color: #9370DB;
        padding: 10px;
        border-radius: 5px;
        color: #ddd;
        font-size: 24px;
        font-family: serif;
    }  
    </style>
    """,
    unsafe_allow_html=True
)

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
    st.markdown("This visualization gives a quick glance at a few KPI metrics from the AdventureWorks sample SQL Database. You can choose which year to inspect or the business as a whole and also review a single month in the line graph. B2B sales and B2C (Online sales) are broken out and displayed. At the bottom there's a confidence interval regarding B2B-gross margin % and a few impressions from that visualization.")
    
    # The Selectbox
    Sales_Year = df1['SalesYear'].unique()
    line = st.selectbox('',['Total Sales'] + list(Sales_Year))
    if line == 'Total Sales':
        chosen_line = df1
    else:
        chosen_line = df1[df1['SalesYear'] == line]

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

with hero:
    st.markdown("""<div style="position:relative; margin: auto; text-align: center;">
              \U0001F6B2
            </div>""", unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center; position:relative; top:40%;">AdventureWorks Sales</h1>', unsafe_allow_html=True)

with topRow:

    
    total_turnover = chosen_line['SubTotal'].sum()
    total_cogs = chosen_line['COGS'].sum()
    total_gp = chosen_line['Margin'].sum()
   
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

    st.markdown('<div></div>', unsafe_allow_html=True)
    
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

with confidenceintervalRow:
    st.markdown('<div></div>', unsafe_allow_html=True)

    df1['Proportion'] = df1['Margin'] / df1['SubTotal'] * 100

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name= 'B2B Sales', 
        x=['B2B Sales'],
        y=[df1[df1['OnlineOrderFlag'] == False]['Proportion'].mean()],
        error_y=dict(type='data', array=[stats.t.interval(0.95, len(df1[df1['OnlineOrderFlag'] == False]['Proportion']) - 1, loc=df1[df1['OnlineOrderFlag'] == False]['Proportion'].mean(), scale=stats.sem(df1[df1['OnlineOrderFlag'] == False]['Proportion']))[1] - df1[df1['OnlineOrderFlag'] == False]['Proportion'].mean()], width=12),
    width=0.5
    ))

    fig.update_layout(
        title="B2B - Gross margin % with 95% confidence intervals per invoice",
        xaxis_title='',
        yaxis_title='Gross margin %',
        
    )

    st.plotly_chart(fig)

    st.markdown(
        """
        <div class="description-box">
        <p>The graph above is a visualization of the confidence interval regarding B2B sales.<br> Consider that this is the mean margin per invoice/sales order and how that is not aligning with the KPI for our wholesale business,
        this needs to be examined further.<br> Some initial thoughts regarding this is that larger orders at even lower GM% (Deadstock? Volume discounts?) are considerably driving the KPI down.<br> 
        The salesforce of AdventureWorks seem to be incentivized through hitting sales targets for their monthly bonuses and then also a commission in the range of 1-2%. Both of these incentives seem to be based on the Sub Total per invoice.<br>
        If this is true our operating margin for our wholesale business (which is roughly 73% of our total turnover) has a very possible risk of operating at a loss. This is not including any overhead costs, just the incentives given to the salesforce and the GM%. 
        Considering that this part of the business seem to be quite cash demanding with customers ordering from a stocked warehouse it greatly limits our financial maneuverability as well.
        </p>
        </div>
         """, unsafe_allow_html=True
        )
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
            Designed by William Blennow.
        </p>
        """, unsafe_allow_html=True
        )    






