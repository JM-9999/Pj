import streamlit as st
import pandas as pd
from datetime import datetime
import os



# 데이터 안전성
if not os.path.exists("inventory.csv"):
    df = pd.DataFrame(columns=["상품명", "수량", "온도"])
    df.to_csv("inventory.csv", index=False)
else:
    df = pd.read_csv("inventory.csv")

if not os.path.exists("logs.csv"):
    log_df = pd.DataFrame(columns=["시간", "내용"])
    log_df.to_csv("logs.csv", index=False)



# 상품별 온도 이상치
temp_limit = {
    "우유": 4,
    "고기": 4,
    "아이스크림": -15,
    "샐러드": 5,
    "냉동치킨": -18,
    "백신": 2,
    "동결혈장": -18
}



# 페이지 제목
st.title("콜드체인 제품 재고 관리 시스템")



# 1. 현재 재고
st.subheader("현재 재고")
st.dataframe(df)



# 2&3 입출고 (가로 배치)
col1, col2 = st.columns(2)



# 2. 출고 처리 (왼쪽)
with col1:

    st.subheader("출고 처리")

    product = st.selectbox("상품 선택", df["상품명"], key="outbound")
    quantity = st.number_input("출고 수량", min_value=1, value=1, key="out_qty")

    if st.button("출고하기"):

        idx = df[df["상품명"] == product].index[0]
        current_stock = df.loc[idx, "수량"]

        log_df = pd.read_csv("logs.csv")

        if current_stock < quantity:
            st.warning("재고가 부족합니다.")

            fail_log = {
                "시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "내용": f"{product} 출고 실패 (재고 부족)"
            }

            log_df = pd.concat([log_df, pd.DataFrame([fail_log])], ignore_index=True)

        else:
            df.loc[idx, "수량"] -= quantity
            df.to_csv("inventory.csv", index=False)

            st.success(f"{product} {quantity}개 출고 완료")

            new_log = {
                "시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "내용": f"{product} {quantity}개 출고"
            }

            log_df = pd.concat([log_df, pd.DataFrame([new_log])], ignore_index=True)

            st.rerun()

        log_df.to_csv("logs.csv", index=False)



# 3. 입고 처리 (오른쪽)
with col2:

    st.subheader("입고 처리")

    in_product = st.selectbox("입고 상품 선택", df["상품명"], key="inbound")
    in_quantity = st.number_input("입고 수량", min_value=1, value=1, key="in_qty")

    if st.button("입고하기"):

        idx = df[df["상품명"] == in_product].index[0]

        df.loc[idx, "수량"] += in_quantity
        df.to_csv("inventory.csv", index=False)

        st.success(f"{in_product} {in_quantity}개 입고 완료")

        log_df = pd.read_csv("logs.csv")

        new_log = {
            "시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "내용": f"{in_product} {in_quantity}개 입고"
        }

        log_df = pd.concat([log_df, pd.DataFrame([new_log])], ignore_index=True)
        log_df.to_csv("logs.csv", index=False)

        st.rerun()



# 4. 온도 이상 감지 (업그레이드 버전)
st.subheader("온도 이상 감지")

warning_found = False

for i, row in df.iterrows():

    limit = temp_limit.get(row["상품명"], 10)

    if row["온도"] > limit:
        st.error(
            f"{row['상품명']} 온도 이상 감지! "
            f"현재: {row['온도']}℃ / 기준: {limit}℃"
        )
        warning_found = True

if not warning_found:
    st.success("모든 상품 온도 정상")



# 5. 작업 로그
st.subheader("작업 로그")

log_df = pd.read_csv("logs.csv")
st.dataframe(log_df)