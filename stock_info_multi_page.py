
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
import pandas as pd
import io 


#從google sheet 讀取資料，並產生所有持股的字典
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0BwiihF-lw2kZo63LNIe8W11dKZfeaI8dciE3trlcnusbi7WAVxgXklDRaPQRpmvnrNrvYpnH6seb/pub?output=xlsx"
@st.cache
def get_list(name):
    df = pd.read_excel(url,sheet_name = name,header=None)
    return list(df[0])
youren_owings = get_list("youren")
pty_owings = get_list("pty")
re_owings = get_list("re")
cyc_owings = get_list("cyc")

owings = dict(youren = youren_owings, pty = pty_owings, re = re_owings, cyc = cyc_owings) 





with st.sidebar:
    choose = option_menu("App Gallery", ["庫存查詢",  "histock資料比對", "Python e-Course"],
                         icons=['search',  'kanban', 'book'],
                         menu_icon="app-indicator", default_index=0,
                         styles={
        "container": {"padding": "5!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "25px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#02ab21"},
    }
    )


if choose == "庫存查詢":
    if st.button('庫存有變動，請按此按鈕'):
     st.legacy_caching.clear_cache()
    #page1
    text_input  = st.text_input('請輸入股號，多個股號以空白間隔')
    query = text_input.split()

    #query = input("輸入股號\n").split() #
    query = list(map(int, query))

    #產生比對結果的字典
    own_situation = {}

    for q in query:
        result_list = []
        for p,li in owings.items():
            if q in li:
                result_list.append(1)
            else:
                result_list.append(0)
        own_situation[q] = result_list

    if text_input:
        df = pd.DataFrame.from_dict(own_situation, orient='index',columns=['youren', 'pty', 're', 'cyc'])
        df
   
        

elif choose == "histock資料比對":
    #從hisotck 獲取資料
    
    website_path = "https://histock.tw/stock/gift.aspx"
    @st.experimental_singleton
    def histock_info(attr):
        valid_stocks = pd.read_html(website_path,attrs = {'id': attr})[0]
        #最新公佈的id為CPHB1_gvToday，未過最後買進的id為CPHB1_gv，已過最後買進的的id為CPHB1_gvOld
        sub_stocks = valid_stocks[["代號", "名稱","股價","股東會紀念品"]]
        new =sub_stocks.set_index("代號")
        new["股東會紀念品"] = new["股東會紀念品"].str.replace("參考圖", "") #將最後的參考圖字樣去除
        return new


    #從histock抓取要比對的股號清單

    #最新公告
    try:
        info_detail_new = histock_info("CPHB1_gvToday")
        check_list_new = info_detail_new.index.values
    except:
        pass
    #最後買進日未到期
    try:
        info_detail_now = histock_info("CPHB1_gv")
        check_list_now = info_detail_now.index.values
    except:
        pass
    #最後買進日已到期
    try:
        info_detail_old = histock_info("CPHB1_gvOld")
        check_list_old = info_detail_old.index.values
    except:
        pass
    # if st.button('從histock下載最新資料，請按此按鈕'):
    #     st.experimental_singleton.clear()

    option = st.selectbox(
     '請選擇表格',
     ('最新公告', '最後買進日未到期', '最後買進日已到期'))
    #產生持有情形的字典
    if option == '最新公告':
        try:
            
            own_situation = {}

            for q in check_list_new:
                result_list = []
                for p,li in owings.items():
                    if q in li:
                        result_list.append(1)
                    else:
                        result_list.append(0)
                own_situation[q] = result_list
                        

            # 顯示結果
            df = pd.DataFrame.from_dict(own_situation, orient='index',columns=['youren', 'pty', 're', 'cyc'])


            df_outer = info_detail_new.join(df, how='outer')
            # #test for 
            # st.write("資料如下")
            # df2 = pd.concat([info_detail, df], axis=1) # axis=0 as default
            

            #st.table(df2)
            st.table(df_outer)
        except:
            st.write("沒有最新公告")
    if option == '最後買進日未到期':
        try:

            own_situation = {}

            for q in check_list_now:
                result_list = []
                for p,li in owings.items():
                    if q in li:
                        result_list.append(1)
                    else:
                        result_list.append(0)
                own_situation[q] = result_list
                        

            # 顯示結果
            df = pd.DataFrame.from_dict(own_situation, orient='index',columns=['youren', 'pty', 're', 'cyc'])


            df_outer = info_detail_now.join(df, how='outer')
            st.table(df_outer)
        except:
            st.write("沒有最後買進日未到期的資料")
        # #test for 
        # st.write("資料如下")
        # df2 = pd.concat([info_detail, df], axis=1) # axis=0 as default
        

        #st.table(df2)
        
    if option == '最後買進日已到期':
        try:

            own_situation = {}

            for q in check_list_old:
                result_list = []
                for p,li in owings.items():
                    if q in li:
                        result_list.append(1)
                    else:
                        result_list.append(0)
                own_situation[q] = result_list
                        

            # 顯示結果
            df = pd.DataFrame.from_dict(own_situation, orient='index',columns=['youren', 'pty', 're', 'cyc'])


            df_outer = info_detail_old.join(df, how='outer')
            # #test for 
            # st.write("資料如下")
            # df2 = pd.concat([info_detail, df], axis=1) # axis=0 as default
            

            #st.table(df2)
            st.table(df_outer)
        except:
            st.write("沒有最後買進日已到期的資料")



    # Same as st.write(df)


elif choose == "Python e-Course":
    pass #page3
