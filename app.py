import streamlit as st
import pandas as pd
from io import BytesIO
import datetime
import time

# ---------------------------------------------------------
# [설정] 페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="SWORD 원가 관리 시스템",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# [중요] 세션 상태 초기화
# ---------------------------------------------------------
if 'scraps' not in st.session_state:
    st.session_state.scraps = []

# ---------------------------------------------------------
# [디자인] CSS 스타일
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
        color: #333333;
    }
    :root {
        --primary-color: #1a237e;
        --accent-color: #3949ab;
        --bg-gray: #f5f7fa;
    }
    h1 {
        color: var(--primary-color) !important;
        font-weight: 700 !important;
        font-size: 34px !important;
        border-bottom: 2px solid #eee;
        padding-bottom: 15px;
        margin-bottom: 20px;
    }
    h3 {
        position: relative !important;
        color: #444 !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
        border: none !important; 
        padding-left: 12px !important; 
        line-height: 1.4 !important;
    }
    h3::before {
        content: "";
        position: absolute;
        left: 0;
        top: 46%;
        transform: translateY(-50%);
        width: 5px;
        height: 24px;
        background-color: var(--accent-color);
    }
    .stTextInput > div > div > input, .stNumberInput > div > div > input {
        background-color: #fff;
        border-radius: 6px;
        border: 1px solid #ddd;
        padding: 10px;
    }
    .result-card {
        background-color: var(--primary-color);
        color: white;
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .result-card h2 { color: #e0e0e0 !important; margin: 0; font-size: 16px; font-weight: 400; }
    .result-card h1 { color: white !important; margin: 15px 0 0 0; font-size: 42px !important; border: none; padding: 0; }
    
    div.stButton > button {
        width: 100%; border-radius: 8px; height: 50px; font-weight: 600; border: none; background-color: #f0f2f5; color: #333; transition: all 0.2s;
    }
    div.stButton > button:hover { background-color: #e0e0e0; transform: translateY(-1px); }
    div.stButton > button[kind="primary"] { background-color: var(--primary-color); color: white; }
    div.stButton > button[kind="primary"]:hover { background-color: var(--accent-color); box-shadow: 0 4px 10px rgba(26, 35, 126, 0.2); }
    th { background-color: #f8f9fa !important; color: #555 !important; font-weight: 600 !important; border-bottom: 2px solid #ddd !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# [기능] 엑셀 변환 함수 (수정됨: vcenter -> valign)
# ---------------------------------------------------------
def to_excel(df):
    try:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            # ★ 여기가 수정되었습니다! (vcenter -> valign)
            header_fmt = workbook.add_format({
                'bold': True, 
                'fg_color': '#e9ecef', 
                'border': 1, 
                'align': 'center', 
                'valign': 'vcenter' 
            })
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_fmt)
                worksheet.set_column(col_num, col_num, 15)
                
        return output.getvalue()
        
    except Exception as e:
        st.error(f"🚨 엑셀 변환 중 에러: {e}")
        return None

# ---------------------------------------------------------
# [메인] 앱 실행
# ---------------------------------------------------------
def main():
    # 사이드바
    with st.sidebar:
        st.header("저장된 프로젝트")
        
        # 저장된 데이터가 있는지 확인
        if len(st.session_state.scraps) > 0:
            st.caption(f"총 {len(st.session_state.scraps)}건 저장됨")
            scrap_df = pd.DataFrame(st.session_state.scraps)
            
            # 리스트 표시
            st.dataframe(
                scrap_df[['상품명', '순이익', '마진율']], 
                hide_index=True,
                use_container_width=True
            )
            
            # 엑셀 다운로드
            excel_data = to_excel(scrap_df)
            
            if excel_data:
                st.download_button(
                    label="전체 내역 엑셀 다운로드",
                    data=excel_data,
                    file_name=f"Costing_Report_{datetime.date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )

            if st.button("목록 초기화"):
                st.session_state.scraps = []
                st.rerun()
        else:
            st.info("계산 결과가 이곳에 저장됩니다.")
            
    # 메인 타이틀
    st.title("SWORD 원가 관리 시스템")

    col_input, col_result = st.columns(2, gap="large")

    # [왼쪽] 데이터 입력
    with col_input:
        st.subheader("기본 정보")
        c1, c2 = st.columns(2)
        with c1:
            product_name = st.text_input("상품명", value="2026 SS 시그니처 볼캡")
        with c2:
            produce_qty = st.number_input("생산 수량 (MOQ)", min_value=1, value=100, step=50)

        st.subheader("원자재 정보 (BOM)")
        if 'materials' not in st.session_state:
            st.session_state.materials = pd.DataFrame(
                [
                    {"자재명": "겉감 (Main Fabric)", "단가": 4500, "소요량": 0.3},
                    {"자재명": "챙심 (Brim)", "단가": 500, "소요량": 1.0},
                    {"자재명": "땀받이 (Sweatband)", "단가": 800, "소요량": 1.0},
                    {"자재명": "탑버튼 & 아일렛", "단가": 150, "소요량": 1.0},
                    {"자재명": "메인 라벨", "단가": 120, "소요량": 1.0},
                    {"자재명": "케어 라벨", "단가": 80, "소요량": 1.0},
                    {"자재명": "폴리백 & 박스", "단가": 500, "소요량": 1.0},
                ]
            )
        
        edited_materials = st.data_editor(
            st.session_state.materials,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "자재명": st.column_config.TextColumn("자재명", width="medium"),
                "단가": st.column_config.NumberColumn("단가(원)", format="%d"),
                "소요량": st.column_config.NumberColumn("소요량", format="%.2f")
            }
        )
        material_sum = (edited_materials["단가"] * edited_materials["소요량"]).sum()

        st.subheader("공임 및 고정비")
        lc1, lc2 = st.columns(2)
        with lc1:
            sewing = st.number_input("봉제 공임", value=6000, step=100)
            embroidery = st.number_input("자수/나염", value=1500, step=100)
        with lc2:
            finish = st.number_input("마감/포장", value=500, step=100)
            logistics = st.number_input("물류/기타", value=300, step=100)
        
        fixed_cost = st.number_input("패턴/샘플 개발비 (전체)", value=300000, step=10000)
        fixed_per_unit = fixed_cost / produce_qty
        
        labor_sum = sewing + embroidery + finish + logistics + fixed_per_unit
        total_cog = material_sum + labor_sum
        st.info(f"자재비 {int(material_sum):,}원 + 공임비 {int(labor_sum):,}원 = 제조원가 {int(total_cog):,}원")

    # [오른쪽] 분석 결과
    with col_result:
        st.subheader("가격 및 수익 분석")
        
        target_price = st.number_input("판매 희망가 (KRW)", value=49000, step=1000)
        
        # [배수 계산]
        if total_cog > 0:
            multiplier = target_price / total_cog
        else:
            multiplier = 0
        st.caption(f"📊 원가({int(total_cog):,}원) 대비 **{multiplier:.1f}배수** 책정됨")

        rc1, rc2 = st.columns(2)
        with rc1:
            channel = st.selectbox("판매 채널", ["자사몰 (3.5%)", "무신사 (30%)", "스마트스토어 (6%)", "백화점 (35%)", "기타"])
        with rc2:
            vat_on = st.toggle("VAT(10%) 포함", value=True)

        fees_map = {"자사몰 (3.5%)": 0.035, "무신사 (30%)": 0.30, "스마트스토어 (6%)": 0.06, "백화점 (35%)": 0.35, "기타": 0.0}
        fee_rate = fees_map[channel]
        
        if vat_on:
            vat = target_price - (target_price / 1.1)
        else:
            vat = target_price * 0.1
        
        fee = target_price * fee_rate
        profit = target_price - total_cog - fee - vat
        margin = (profit / target_price) * 100 if target_price > 0 else 0

        st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-card">
            <h2>예상 순이익 (Net Profit)</h2>
            <h1>{int(profit):,}원</h1>
            <p style="margin-top:15px; font-size:18px; opacity:0.9; font-weight:500;">마진율 {margin:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

        st.write("상세 비용 구조")
        breakdown_df = pd.DataFrame([
            {"구분": "판매가", "금액": target_price, "비고": "100%"},
            {"구분": "(-) 제조원가", "금액": -total_cog, "비고": f"{(total_cog/target_price)*100:.1f}%"},
            {"구분": "(-) 수수료", "금액": -fee, "비고": f"{fee_rate*100}%"},
            {"구분": "(-) 부가세", "금액": -vat, "비고": "10%"},
            {"구분": "(=) 순이익", "금액": profit, "비고": f"{margin:.1f}%"},
        ])
        st.dataframe(breakdown_df.style.format({"금액": "{:,.0f}원"}), hide_index=True, use_container_width=True)

        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

        if st.button("현재 결과 리스트에 저장", type="primary"):
            scrap_item = {
                "상품명": product_name,
                "생산수량": produce_qty,
                "채널": channel,
                "판매가": int(target_price),
                "제조원가": int(total_cog),
                "수수료": int(fee),
                "부가세": int(vat),
                "순이익": int(profit),
                "마진율": f"{margin:.1f}%",
                "저장일시": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.scraps.append(scrap_item)
            st.toast("✅ 저장되었습니다!", icon=None)
            time.sleep(0.5)
            st.rerun()

if __name__ == "__main__":
    main()
