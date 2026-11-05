import streamlit as st
import twstock
import pandas as pd
import datetime

# 設定網頁標題與排版
st.set_page_config(
    page_title="台積電 (2330) 即時與技術分析面板",
    page_icon="📈",
    layout="wide"
)

st.title("🚀 台積電 (2330) 盤中即時與技術分析面板")
st.markdown("本系統使用 `twstock` 套件，即時擷取台積電盤中報價、最佳五檔買價買量，並計算近期 5 日均線走勢。")

# 建立側邊欄資訊
st.sidebar.header("控制面板")
if st.sidebar.button("🔄 重新整理資料", type="primary"):
    st.rerun()

st.sidebar.info("提示：若為台股非交易時間，即時資料將顯示收盤時之最新狀態。")

# 建立主要版面：使用兩個分頁
tab1, tab2 = st.tabs(["📊 即時行情與五檔買進", "📈 近期收盤價與 5 日均線"])

# --- 分頁一：即時行情與五檔買進 ---
with tab1:
    st.subheader("💡 盤中即時報價與委買五檔")
    
    # 取得即時資料
    data = twstock.realtime.get('2330')
    
    if data['success']:
        info = data['info']
        rt = data['realtime']
        
        # 顯示基本指標數據
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("當前成交價", f"{rt['latest_trade_price']} 元", f"{rt['change']} 元")
        col2.metric("開盤價", f"{rt['open']} 元")
        col3.metric("最高價", f"{rt['high']} 元")
        col4.metric("最低價", f"{rt['low']} 元")
        
        st.write(f"**更新時間**：{info['time']} | **累積成交量**：{rt['accumulate_trade_volume']} 張")
        
        st.markdown("---")
        st.markdown("### 📋 最佳五檔買進資訊 (委買)")
        
        # 整理五檔資料為 DataFrame 呈現
        bid_data = []
        for i in range(5):
            bid_data.append({
                "級別": f"買 {i+1}",
                "委買價格 (元)": rt['best_bid_price'][i],
                "委買數量": rt['best_bid_volume'][i]
            })
        
        df_bid = pd.DataFrame(bid_data)
        st.dataframe(df_bid, use_container_width=True, hide_index=True)
        
    else:
        st.error("⚠️ 無法取得即時資訊，請稍後再試。")

# --- 分頁二：近期收盤價與 5 日均線 ---
with tab2:
    st.subheader("📉 近期收盤價與 5 日移動平均線 (MA5)")
    
    with st.spinner('正在計算技術指標並載入歷史資料...'):
        # 建立 Stock 物件並計算均線
        tsmc = twstock.Stock('2330')
        ma_5_list = tsmc.moving_average(tsmc.price, 5)
        
        # 取得最近 30 天資料
        recent_dates = tsmc.date[-30:]
        recent_prices = tsmc.price[-30:]
        recent_ma5 = ma_5_list[-30:]
        
        # 組裝成 DataFrame
        chart_data = []
        for date, price, ma in zip(recent_dates, recent_prices, recent_ma5):
            chart_data.append({
                "日期": date.strftime('%Y-%m-%d'),
                "收盤價": price,
                "5日均線": round(ma, 2) if ma is not None else None
            })
        
        df_history = pd.DataFrame(chart_data)
        
        # 繪製互動式折線圖
        st.line_chart(df_history.set_index("日期")[["收盤價", "5日均線"]])
        
        st.markdown("### 📄 近期歷史數據明細表")
        st.dataframe(df_history, use_container_width=True, hide_index=True)