# Imports
import pandas as pandas
from tempfile import NamedTemporaryFile
import streamlit as st
import numpy as np
import random as random
import altair as alt
import matplotlib.pyplot as plt
from io import StringIO
from vega_datasets import data
# Header
st.title('Excel Task Automation')
st.markdown("              ")



# global  list_of_reports
def get_report(file,multiple):
  sheet1_file= file
  sheet_payment_df = pandas.read_excel(sheet1_file,sheet_name='paymentsByFilter')
  sheet1_fawry_df = pandas.read_excel(sheet1_file,sheet_name='F')
  sheet1_amazon_df = pandas.read_excel(sheet1_file,sheet_name='A')
  sheet1_gedia_df = pandas.read_excel(sheet1_file,sheet_name='G')
  if (multiple==False):
   return  Execute(sheet_payment_df,sheet1_amazon_df,sheet1_fawry_df,sheet1_gedia_df,file)
  else :
    uniques = set()
    for index , row in sheet1_fawry_df.iterrows():
      if(row['Order Date'] not in uniques):
          uniques.add(row['Order Date'])
    number_of_days = len(uniques)
        # For Payment Sheet 
    for index ,row in sheet_payment_df.iterrows():
      sheet_payment_df['crea eDa e ime'][index]=pandas.to_datetime(sheet_payment_df['crea eDa e ime'][index]).date()
    sheet_payment_df['Date']=sheet_payment_df['crea eDa e ime']

    # For Amazon Sheet 
    for index ,row in sheet1_amazon_df.iterrows():
      sheet1_amazon_df['Date'][index]=pandas.to_datetime(sheet1_amazon_df['Date'][index]).date()


    # For Gedia  Sheet 
    for index ,row in sheet1_gedia_df.iterrows():
      sheet1_gedia_df['Date'][index]=pandas.to_datetime(sheet1_gedia_df['Date'][index]).date()

    # For Fawry Sheet
    for index ,row in sheet1_fawry_df.iterrows():
      sheet1_fawry_df['Order Date'][index]=pandas.to_datetime(sheet1_fawry_df['Order Date'][index]).date()
    sheet1_fawry_df['Date']=sheet1_fawry_df['Order Date']
    def classify(df):
    # Group the DataFrame by date
      grouped = df.groupby(df['Date'])
      # Create a dictionary of DataFrames, where each key represents a date
      dfs = {date: group for date, group in grouped}
      return dfs
    # Get DFs of All sheets
    payment_dict= classify(sheet_payment_df)
    amazon_dict = classify(sheet1_amazon_df)
    gedia_dict = classify(sheet1_gedia_df)
    fawry_dict = classify(sheet1_fawry_df)
    dates= list(payment_dict.keys())

    list_of_reports=[]
    for date in payment_dict.keys():
      list_of_reports.append(Execute(payment_dict[date],amazon_dict[date],fawry_dict[date],gedia_dict[date],file))
    big_report_df = pandas.DataFrame()
    index =0
    for  x in list_of_reports:
      new_row = pandas.Series(dates[index], index=big_report_df.columns)

      big_report_df.append(new_row, ignore_index=True)
      big_report_df = big_report_df.append(x, ignore_index=True)
      index =index+1
    list_of_reports.append(big_report_df)
    return list_of_reports
# File Execution
def Execute(sheet_payment_df,sheet1_amazon_df,sheet1_fawry_df,sheet1_gedia_df,file):
    # reading stuff
    sheet1_file= file
    sheet_payment_df = sheet_payment_df
    sheet1_fawry_df = sheet1_fawry_df
    sheet1_amazon_df = sheet1_amazon_df
    sheet1_gedia_df = sheet1_gedia_df
    sheet_payment_df['Payment_Gateway']={}
    sheet_payment_df['Count']=1
    sheet_payment_df['Comission']={}
    # getting pgw numbers
    def get_pgw_value(totalVal,walletVal): 
        return totalVal-walletVal  
    def get_amazon_commission(value):
        return value * 0.0095 +1.5
    def get_gedia_commission(value):
      return value* 0.01+ 1.5   
    def get_fawry_commission(value):
        x= value*0.0115  *1.14  
        if(x>28.5):
            return 28.5
        else: return x

# puttin pgw numbers
    for index, row in sheet_payment_df.iterrows():
        pgw = get_pgw_value(sheet_payment_df['totalAmount'][index],sheet_payment_df['walletAmount'][index])
        provider = row['provider']
        
        sheet_payment_df['Payment_Gateway'][index]= pgw
        if(row['provider'] == 'AMAZONPAY'):
            comm = get_amazon_commission(sheet_payment_df['Payment_Gateway'][index])
        if(row['provider']=='GEIDEABANKMASR'):
            comm = get_gedia_commission(sheet_payment_df['Payment_Gateway'][index])
        if(row['provider'] == 'PAYATFAWRY'):
            comm = get_fawry_commission(sheet_payment_df['Payment_Gateway'][index])
        sheet_payment_df['Comission'][index]=comm

    sheet1_2_df = pandas.DataFrame(columns=['  ','Gross Amount', 'Number of Orders', 'Total Comission',' ','Gross Amount (PGW)','Number of Orders(PGW)','Total Comission(PGW)'])
    sheet1_2_df = sheet1_2_df.append([{}]*4, ignore_index=True)
    sheet1_2_df['  '][0]="Amazon Pay"
    sheet1_2_df['  '][1]="Gedia "
    sheet1_2_df['  '][2]="FawryPay "
    sheet1_2_df['  '][3]="Total "
    sheet1_2_df['Total Comission(PGW)'][2]=0

    sheet1_2_df['Gross Amount (PGW)'][2]=sheet1_fawry_df['Net Amount'].sum(skipna=True)
    sheet1_2_df['Number of Orders(PGW)'][2]=sheet1_fawry_df['Count'].sum(skipna=True)
    sheet1_2_df['Total Comission(PGW)'][2]=sheet1_fawry_df['Merchant Commission'].sum(skipna=True)
# getting gedia numbers
    sheet1_gedia_df['Comission'] = {}
    actual_geida_com =0
    actual_geida_count=0
    actual_geida_amount_sum = 0

    for index,row in sheet1_gedia_df.iterrows():
        if( row['Status'] != 'Failed'):
            sheet1_gedia_df['Comission'][index]= row['Gross Amount']-row['Net Amount']
            actual_geida_com = sheet1_gedia_df['Comission'][index]+actual_geida_com
            actual_geida_count=actual_geida_count+1
            actual_geida_amount_sum=actual_geida_amount_sum+sheet1_gedia_df['Gross Amount'][index]
    print('x')
    sheet1_2_df['Gross Amount (PGW)'][1]=actual_geida_amount_sum
    sheet1_2_df['Number of Orders(PGW)'][1]=actual_geida_count
    sheet1_2_df['Total Comission(PGW)'][1]=actual_geida_com

    def get_amazon_num(value):
        return float(value)* 0.0095 +1.5

    sheet1_amazon_df['Count'] = 1
    sheet1_amazon_df['Comission']={}
    for index, row in sheet1_amazon_df.iterrows():
        sheet1_amazon_df['Comission'][index]= get_amazon_num(float(row['Amount']))
    sum=0
    for index , row in sheet1_amazon_df.iterrows():
        sum=sum+float(row['Amount'])


    sheet1_2_df['Gross Amount (PGW)'][0]=sum
    sheet1_2_df['Number of Orders(PGW)'][0]=sheet1_amazon_df['Count'].sum()
    sheet1_2_df['Total Comission(PGW)'][0]=sheet1_amazon_df['Comission'].sum()
    
    sheet1_2_df['Gross Amount (PGW)'][3] = sheet1_2_df['Gross Amount (PGW)'][2]+sheet1_2_df['Gross Amount (PGW)'][0]+sheet1_2_df['Gross Amount (PGW)'][1]
    sheet1_2_df['Number of Orders(PGW)'][3] = sheet1_2_df['Number of Orders(PGW)'][2]+sheet1_2_df['Number of Orders(PGW)'][1]+sheet1_2_df['Number of Orders(PGW)'][0]
    sheet1_2_df['Total Comission(PGW)'][3] = sheet1_2_df['Total Comission(PGW)'][2]+sheet1_2_df['Total Comission(PGW)'][1]+sheet1_2_df['Total Comission(PGW)'][0]


    def get_sums():
        amazon_sum=0
        amazon_order_count=0
        amazon_commission=0
        gedia_sum=0
        gedia_order_count=0
        gedia_comission = 0
        fawry_sum_sum=0
        fawry_order_count=0
        fawry_comission=0
        list_of_vendors=[]
        for index , row in sheet_payment_df.iterrows():
            if(row['provider'] == 'AMAZONPAY'):
                amazon_order_count=amazon_order_count+1
                amazon_sum = amazon_sum+row['Payment_Gateway']
                amazon_commission = amazon_commission+ row['Comission']
            if(row['provider'] == 'GEIDEABANKMASR'):
                gedia_order_count=gedia_order_count+1
                gedia_sum = gedia_sum+row['Payment_Gateway']
                gedia_comission= gedia_comission+row['Comission']
            if(row['provider'] == 'PAYATFAWRY'):
                fawry_order_count=fawry_order_count+1
                fawry_sum_sum = fawry_sum_sum+row['Payment_Gateway']
                fawry_comission = fawry_comission + row['Comission']
        list_of_vendors.append(amazon_sum)
        list_of_vendors.append(amazon_order_count)
        list_of_vendors.append(amazon_commission)
        list_of_vendors.append(gedia_sum)
        list_of_vendors.append(gedia_order_count)
        list_of_vendors.append(gedia_comission)
        list_of_vendors.append(fawry_sum_sum)
        list_of_vendors.append(fawry_order_count)
        list_of_vendors.append(fawry_comission)
        return list_of_vendors
    
    list_of_sums = get_sums()
    sheet1_2_df['Gross Amount'][0] = list_of_sums[0]
    sheet1_2_df['Number of Orders'][0] = list_of_sums[1]
    sheet1_2_df['Total Comission'][0] = list_of_sums[2]
    sheet1_2_df['Gross Amount'][1] = list_of_sums[3]
    sheet1_2_df['Number of Orders'][1] = list_of_sums[4]
    sheet1_2_df['Total Comission'][1] = list_of_sums[5]
    sheet1_2_df['Gross Amount'][2] = list_of_sums[6]
    sheet1_2_df['Number of Orders'][2] = list_of_sums[7]
    sheet1_2_df['Total Comission'][2] = list_of_sums[8]

    sheet1_2_df['Gross Amount'][3] = list_of_sums[0]+list_of_sums[3]+list_of_sums[6]
    sheet1_2_df['Number of Orders'][3] = list_of_sums[1]+list_of_sums[4]+list_of_sums[7]
    sheet1_2_df['Total Comission'][3] = list_of_sums[2]+list_of_sums[5]+list_of_sums[8]



    return sheet1_2_df

file_df= 0
# button_pressed=False
# File Uploading
uploaded_file = st.file_uploader("Choose a file", type="xlsx")
if uploaded_file is not None:
            path_in = uploaded_file.name
            print(uploaded_file.name)
# Execute file on Button Click
csv = "None"
multiple = st.checkbox("Multiple")

def Generating_Tabs(all_reports):
    # Generate the tab labels
    tab_labels = [f"Tab {i+1}" for i in range(len(all_reports)-1)]
    # Generate the tab content
    def generate_tab_content(i):
        # ///////////////////////////////////////////////
        if(button_pressed):
                st.dataframe(file_df)
        # Cache the dataframe so it's only loaded once
                @st.cache_data
                def load_data():
                
                    return pandas.DataFrame(
                        {
                            "Gateways": ["Fawry","Amazon","GEIDEA"],
                            "Total Amount": [file_df['Gross Amount'][2],file_df['Gross Amount'][0],file_df['Gross Amount'][1]],
                            "Amount": [file_df['Gross Amount (PGW)'][2],file_df['Gross Amount'][0],file_df['Gross Amount'][1]],

                        }
                    )
                # st.checkbox("Use container width", value=False, key="use_container_width")
                df = load_data()
                ########################  THE AMOUNT  ###########################
                st.header('The Amount')
                # Set the figure size and background color
                fig, ax = plt.subplots(figsize=(12, 4))
                fig.patch.set_facecolor('none')
                # Set the positions of the bars on the x-axis
                x = range(len(df))
                # Set the width of each bar
                width = 0.35
                # Plot the bars for "Amount"
                ax.bar(x, df["Amount"], width, label="Amount")
                # Plot the bars for "Total Amount"
                ax.bar([i + width for i in x], df["Total Amount"], width, label="Total Amount")
                # Set the x-axis labels
                ax.set_xticks([i + width/2 for i in x])
                ax.set_xticklabels(df["Gateways"])
                # Set the y-axis label
                ax.set_ylabel("Amount")
                # Set the chart title
                ax.set_title("Grouped Bar Chart")
                # Add a legend
                ax.legend()
                # Set the background color to transparent
                ax.set_facecolor('none')
                # Set the color of the axis labels, title, and legend to white
                ax.spines['bottom'].set_color('white')
                ax.spines['left'].set_color('white')
                ax.spines['top'].set_color('white')
                ax.spines['right'].set_color('white')
                ax.yaxis.label.set_color('white')
                ax.xaxis.label.set_color('white')
                ax.title.set_color('white')
                ax.legend().get_texts()[0].set_color("white")
                ax.legend().get_texts()[1].set_color("white")
                ax.tick_params(axis='x', colors='white')
                ax.tick_params(axis='y', colors='white')
                #Show the chart
                st.pyplot(plt)
        # ///////////////////////////////////////////////
    # Create the tabs
    tabs = st.tabs(tab_labels)
    # Display the content for each tab
    for i, tab in enumerate(tabs):
        generate_tab_content(i)

if st.button('Execute'):
    # GET MULTIPLE FLAG FROM CHECKBOX
        multiple = True 
        all_reports=get_report(uploaded_file, multiple)
        file_df = get_report(uploaded_file, multiple)[len(get_report(uploaded_file,multiple))-1]
        button_pressed=True
        st.write(" File Executed Succesfully")
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')
        
        if isinstance(file_df, pandas.DataFrame):
            csv_data = file_df.to_csv(index=False).encode('utf-8')
        st.download_button(
       "Press to Download",
       csv_data,
       "Report.csv",
       "text/csv",
       key='download-csv'
    )
        Generating_Tabs(all_reports) 

# def generate_tab_content(i):
    #     if(button_pressed):
    #         st.dataframe(file_df)
    # # Cache the dataframe so it's only loaded once
    #         @st.cache_data
    #         def load_data():
             
    #             return pandas.DataFrame(
    #                 {
    #                     "Gateways": ["Fawry","Amazon","GEIDEA"],
    #                     "Total Amount": [file_df['Gross Amount'][2],file_df['Gross Amount'][0],file_df['Gross Amount'][1]],
    #                     "Amount": [file_df['Gross Amount (PGW)'][2],file_df['Gross Amount'][0],file_df['Gross Amount'][1]],

    #                 }
    #             )
    #         # st.checkbox("Use container width", value=False, key="use_container_width")
    #         df = load_data()
    #         ########################  THE AMOUNT  ###########################
    #         st.header('The Amount')
    #         # Set the figure size and background color
    #         fig, ax = plt.subplots(figsize=(12, 4))
    #         fig.patch.set_facecolor('none')
    #         # Set the positions of the bars on the x-axis
    #         x = range(len(df))
    #         # Set the width of each bar
    #         width = 0.35
    #         # Plot the bars for "Amount"
    #         ax.bar(x, df["Amount"], width, label="Amount")
    #         # Plot the bars for "Total Amount"
    #         ax.bar([i + width for i in x], df["Total Amount"], width, label="Total Amount")
    #         # Set the x-axis labels
    #         ax.set_xticks([i + width/2 for i in x])
    #         ax.set_xticklabels(df["Gateways"])
    #         # Set the y-axis label
    #         ax.set_ylabel("Amount")
    #         # Set the chart title
    #         ax.set_title("Grouped Bar Chart")
    #         # Add a legend
    #         ax.legend()
    #         # Set the background color to transparent
    #         ax.set_facecolor('none')
    #         # Set the color of the axis labels, title, and legend to white
    #         ax.spines['bottom'].set_color('white')
    #         ax.spines['left'].set_color('white')
    #         ax.spines['top'].set_color('white')
    #         ax.spines['right'].set_color('white')
    #         ax.yaxis.label.set_color('white')
    #         ax.xaxis.label.set_color('white')
    #         ax.title.set_color('white')
    #         ax.legend().get_texts()[0].set_color("white")
    #         ax.legend().get_texts()[1].set_color("white")
    #         ax.tick_params(axis='x', colors='white')
    #         ax.tick_params(axis='y', colors='white')
    #         #Show the chart
    #         st.pyplot(plt)
            ########################  NUMBER OF ORDERS  ###########################
            # st.header('Number Of Orders')
            # fig, ax = plt.subplots(figsize=(12, 4))
            # fig.patch.set_facecolor('none')
            # x = range(len(df))
            # width = 0.35
            # ax.bar(x, df["Amount"], width, label="Amount")
            # ax.bar([i + width for i in x], df["Total Amount"], width, label="Total Amount")
            # ax.set_xticks([i + width/2 for i in x])
            # ax.set_xticklabels(df["Gateways"])
            # ax.set_ylabel("Amount")
            # ax.set_title("Grouped Bar Chart")
            # ax.legend()
            # ax.set_facecolor('none')
            # ax.spines['bottom'].set_color('white')
            # ax.spines['left'].set_color('white')
            # ax.spines['top'].set_color('white')
            # ax.spines['right'].set_color('white')
            # ax.yaxis.label.set_color('white')
            # ax.xaxis.label.set_color('white')
            # ax.title.set_color('white')
            # ax.legend().get_texts()[0].set_color("white")
            # ax.legend().get_texts()[1].set_color("white")
            # ax.tick_params(axis='x', colors='white')
            # ax.tick_params(axis='y', colors='white')
            # st.pyplot(plt)

            # ########################  TOTAL COMMISSION  ###########################
            # st.header('Sum Of Commissions')
            # fig, ax = plt.subplots(figsize=(12, 4))
            # fig.patch.set_facecolor('none')
            # x = range(len(df))
            # width = 0.35
            # ax.bar(x, df["Amount"], width, label="Amount")
            # ax.bar([i + width for i in x], df["Total Amount"], width, label="Total Amount")
            # ax.set_xticks([i + width/2 for i in x])
            # ax.set_xticklabels(df["Gateways"])
            # ax.set_ylabel("Amount")
            # ax.set_title("Grouped Bar Chart")
            # ax.legend()
            # ax.set_facecolor('none')
            # ax.spines['bottom'].set_color('white')
            # ax.spines['left'].set_color('white')
            # ax.spines['top'].set_color('white')
            # ax.spines['right'].set_color('white')
            # ax.yaxis.label.set_color('white')
            # ax.xaxis.label.set_color('white')
            # ax.title.set_color('white')
            # ax.legend().get_texts()[0].set_color("white")
            # ax.legend().get_texts()[1].set_color("white")
            # ax.tick_params(axis='x', colors='white')
            # ax.tick_params(axis='y', colors='white')
            # st.pyplot(plt)


