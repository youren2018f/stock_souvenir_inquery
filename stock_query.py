import streamlit as st
import pandas as pd

###################################################
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
####################################################



#5/2修改一下
import pandas as pd
website_path = "https://histock.tw/stock/gift.aspx"
valid_stocks = pd.read_html(website_path,attrs = {'id': 'CPHB1_gvToday'})[0]
#最新公佈的id為CPHB1_gvToday，未過最後買進的id為CPHB1_gv，已過最後買進的的id為CPHB1_gvOld



pd.options.display.max_columns = None
pd.options.display.max_rows = None

sub_stocks = valid_stocks[["代號", "名稱","股價","股東會紀念品"]]

new =sub_stocks.set_index("代號")
new["股東會紀念品"] = new["股東會紀念品"].str.replace("參考圖", "") #將最後的參考圖字樣去除


check_list = []
for i in range(len(sub_stocks)) :
    check_list.append(sub_stocks.loc[i, "代號"])









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
            

df = pd.DataFrame.from_dict(own_situation, orient='index',columns=['youren', 'pty', 're', 'cyc'])

df2 = pd.concat([new, df], axis=1) # axis=0 as default
df2 = df2.round()

st.dataframe(df2)

 # Same as st.write(df)






