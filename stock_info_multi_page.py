import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html
import pandas as pd
import io
import requests
from bs4 import BeautifulSoup

#從google sheet 讀取資料，並產生所有持股的字典
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQL4Pg0pLF4gg23UHyC4COsat3NOyfFYbnZoenJD6JX-hith6CKZWlEdM_qZrfogYVOqF0XGrcZmVHp/pub?output=xlsx"

@st.cache_data
def get_list(name):
    df = pd.read_excel(url,sheet_name = name,header=None)
    return list(df[0])

youren_owings = get_list("youren")
pty_owings = get_list("pty")
cyc_owings = get_list("cyc")

owings = dict(youren = youren_owings, pty = pty_owings, cyc = cyc_owings) 

with st.sidebar:
    choose = option_menu("App Gallery", ["庫存查詢",  "histock資料比對qq", "RachlMei Excel"],
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
        df = pd.DataFrame.from_dict(own_situation, orient='index',columns=['youren', 'pty', 'cyc'])
        df

elif choose == "histock資料比對qq":
    #從hisotck 獲取資料
    
    website_path = "https://histock.tw/stock/gift.aspx"
    
    @st.cache_resource
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
            df = pd.DataFrame.from_dict(own_situation, orient='index',columns=['youren', 'pty', 'cyc'])

            df_outer = info_detail_new.join(df, how='outer')
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
            df = pd.DataFrame.from_dict(own_situation, orient='index',columns=['youren', 'pty', 'cyc'])

            df_outer = info_detail_now.join(df, how='outer')
            st.table(df_outer)
        except:
            st.write("沒有最後買進日未到期的資料")
    
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
            df = pd.DataFrame.from_dict(own_situation, orient='index',columns=['youren', 'pty', 'cyc'])

            df_outer = info_detail_old.join(df, how='outer')
            st.table(df_outer)
        except:
            st.write("沒有最後買進日已到期的資料")

elif choose == "RachlMei Excel":
# 設定網址與 headers（模擬瀏覽器）
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTG7Rb_wjFaHq1Z_ExcEN5EMZPR4-iFvdr5xKvVH-hJORNx6WhCZoijIFYuDGXkKIKqf4WjcBhQ_TYR/pub"
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 若有錯誤會拋出例外

        # 解析 HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # 定位到目標 div
        div = soup.find("div", id="964277633")
        if not div:
            print("找不到 id 為 964277633 的 div")
            exit()

        # 在該 div 內尋找 tbody
        tbody = div.find("tbody")
        if not tbody:
            print("在目標 div 中找不到 tbody")
            exit()

        # 取得 tbody 中的所有 tr
        rows = tbody.find_all("tr")
        start_index = None
        end_index = None

        # 遍歷所有 tr，尋找包含 "A區" 與 "B區" 的列
        for i, row in enumerate(rows):
            # 將此 tr 內所有 td 的文字合併起來
            cell_text = " ".join(td.get_text(strip=True) for td in row.find_all("td"))
            
            # 找到包含 "A區" 的列，並設定下一列為開始列
            if "A區" in cell_text and start_index is None:
                if i + 1 < len(rows):
                    start_index = i + 1
                else:
                    print("A區所在列已是最後一列，無法取得下一列")
                    exit()
            
            # 找到包含 "B區" 的列，作為結束列（包含在內），然後終止搜尋
            if "B區" in cell_text:
                end_index = i
                break

        if start_index is None:
            print("未找到包含 'A區' 的列")
            exit()

        if end_index is None:
            print("未找到包含 'B區' 的列")
            exit()

        # 取出範圍內的 tr（包含結束列）
        target_rows = rows[start_index : end_index + 1]
        table_data = []

        for row in target_rows:
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
            # 確保此列資料足夠長（至少要有15個 cell）
            if len(cells) >= 15:
                # 只取出索引 0, 1, 2, 14 的元素
                filtered = [cells[0], cells[1], cells[2], cells[14]]
                table_data.append(filtered)
            else:
                print("該列資料不足，跳過:", cells)

        # 定義欄位名稱
        columns = ["代號", "名稱", "股東會紀念品", "去年資料"]

        # 建立 DataFrame
        df_excel = pd.DataFrame(table_data, columns=columns)
        df_excel = df_excel.iloc[:-1]        
        df_excel =df_excel.set_index("代號")
        df_excel.index = df_excel.index.astype(int)
        
        check_list_excel = [int(x) for x in df_excel.index.values]
        try:
            own_situation = {}

            for q in check_list_excel:
                result_list = []
                for p,li in owings.items():
                    if q in li:
                        result_list.append(1)
                    else:
                        result_list.append(0)
                own_situation[q] = result_list

            # 顯示結果
            df = pd.DataFrame.from_dict(own_situation, orient='index',columns=['youren', 'pty', 'cyc'])

            df_outer = df_excel.join(df, how='outer')
            st.table(df_outer)
        except:
            st.write("沒有excel的資料")    
