import streamlit as st
import pandas as pd

pd.options.display.max_columns = None
pd.options.display.max_rows = None


#從google sheet 讀取資料，並產生所有持股的字典
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQL4Pg0pLF4gg23UHyC4COsat3NOyfFYbnZoenJD6JX-hith6CKZWlEdM_qZrfogYVOqF0XGrcZmVHp/pub?output=xlsx"
@st.cache
def get_list(name):
    df = pd.read_excel(url,sheet_name = name,header=None)
    return list(df[0])
youren_owings = get_list("youren")
pty_owings = get_list("pty")
cyc_owings = get_list("cyc")

owings = dict(youren = youren_owings, pty = pty_owings, cyc = cyc_owings) 




#從hisotck 獲取資料
website_path = "https://histock.tw/stock/gift.aspx"
@st.cache
def histock_info(attr):
    valid_stocks = pd.read_html(website_path,attrs = {'id': attr})[0]
    #最新公佈的id為CPHB1_gvToday，未過最後買進的id為CPHB1_gv，已過最後買進的的id為CPHB1_gvOld
    sub_stocks = valid_stocks[["代號", "名稱","股價","股東會紀念品"]]
    new =sub_stocks.set_index("代號")
    new["股東會紀念品"] = new["股東會紀念品"].str.replace("參考圖", "") #將最後的參考圖字樣去除
    return new


#從histock抓取要比對的股號清單
info_detail = histock_info("CPHB1_gvOld")
check_list = info_detail.index.values


#產生持有情形的字典
own_situation = {}

for q in check_list:
    result_list = []
    for p,li in owings.items():
        if q in li:
            result_list.append(1)
        else:
            result_list.append(0)
    own_situation[q] = result_list
            

# 顯示結果
df = pd.DataFrame.from_dict(own_situation, orient='index',columns=['youren', 'pty', 'cyc'])

st.write("資料如下")
df2 = pd.concat([info_detail, df], axis=1) # axis=0 as default


#st.table(df2)
st.dataframe(df2)

 # Same as st.write(df)






