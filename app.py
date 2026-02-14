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
# [디자인] CSS 스타일 (간격 및 여백 최적화)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* 폰트 설정 (Noto Sans KR) */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
        color: #333333;
    }

    /* 포인트 컬러 설정 */
    :root {
        --primary-color: #1a237e; /* 딥 네이비 */
        --accent-color: #3949ab;  /* 밝은 네이비 */
        --bg-gray: #f5f7fa;
    }

    /* 헤더 스타일 (간격 조정됨) */
    h1 {
        color: var(--primary-color) !important;
        font-weight: 700 !important;
        font-size: 34px !important;
        border-bottom: 2px solid #eee;
        padding-bottom: 15px;
        margin-bottom: 20px; /* 제목 아래 여백 대폭 추가 */
    }
    
    /* 1. 제목 텍스트 설정 */
    h3 {
        position: relative !important; /* 바 위치 기준점 */
        color: #444 !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
        
        /* 기존 border-left 삭제하고 아래로 대체 */
        border: none !important; 
        
        /* ★ [여백 조절] 파란 바와 글자 사이의 거리 */
        padding-left: 12px !important; 
        
        line-height: 1.4 !important;
    }

    /* 2. 파란색 바(Bar) 새로 그리기 - 길이/두께 조절 가능 */
    h3::before {
        content: "";
        position: absolute;
        left: 0;
        top: 46%; /* 글자 높이의 중앙에 배치 */
        transform: translateY(-50%); /* 정확한 수직 중앙 정렬 */
        
        /* ★ [파란 바 조절] 여기서 숫자만 바꾸세요 */
        width: 5px;        /* 두께 */
        height: 24px;      /* 길이 (높이) */
        
        background-color: var(--accent-color); /* 색상 (위에서 설정한 파란색) */
        border-radius: 0px; /* 모서리를 살짝 둥글게 */
    }

    /* 입력 필드 스타일 */
    .stTextInput > div > div > input, .stNumberInput > div > div > input {
        background-color: #fff;
        border-radius: 6px;
        border: 1px solid #ddd;
        padding: 10px; /* 입력창 내부 여백 */
    }

    /* 결과 카드 스타일 */
    .result-card {
        background-color: var(--primary-color);
        color: white;
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .result-card h2 {
        color: #e0e0e0 !important;
        margin: 0;
        font-size: 16px;
        font-weight: 400;
    }
    .result-card h1 {
        color: white !important;
        margin: 15px 0 0 0;
        font-size: 42px !important; /* 숫자 크기 키움 */
        border: none;
        padding: 0;
    }

    /* 버튼 스타일 */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 50px; /* 버튼 높이 키움 */
        font-weight: 600;
        border: none;
        background-color: #f0f2f5;
        color: #333;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #e0e0e0;
        transform: translateY(-1px);
    }
    
    /* 저장하기 버튼 (Primary) */
    div.stButton > button[kind="primary"] {
        background-color: var(--primary-color);
        color: white;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: var(--accent-color);
        box-shadow: 0 4px 10px rgba(26, 35, 126, 0.2);
    }

    /* 데이터프레임 헤더 스타일 */
    th {
        background-color: #f8f9fa !important;
        color: #555 !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #ddd !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# [기능] 엑셀 변환 함수
# ---------------------------------------------------------
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='원가계산서')
        workbook = writer.book
        worksheet = writer.sheets['원가계산서']
        header_fmt = workbook.add_format({'bold': True, 'fg_color': '#e9ecef', 'border': 1, 'align': 'center', 'vcenter': True})
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_fmt)
            worksheet.set_column(col_num, col_num, 15)
    return output.getvalue()

# ---------------------------------------------------------
# [메인] 앱 실행
# ---------------------------------------------------------
def main():
    # 사이드바
    with st.sidebar:
        st.header("저장된 프로젝트")
        if 'scraps' not in st.session_state:
            st.session_state.scraps = []
        
        if len(st.session_state.scraps) > 0:
            st.caption(f"총 {len(st.session_state.scraps)}건 저장됨")
            scrap_df = pd.DataFrame(st.session_state.scraps)
            st.dataframe(
                scrap_df[['상품명', '순이익', '마진율']], 
                hide_index=True,
                use_container_width=True
            )
            st.download_button(
                label="전체 내역 엑셀 다운로드",
                data=to_excel(scrap_df),
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
    st.title("모자 원가 관리 시스템")

    # 5:5 레이아웃 분할
    col_input, col_result = st.columns(2, gap="large")

    # =========================================================
    # [왼쪽] 데이터 입력
    # =========================================================
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
        
        # 합계 표시
        st.info(f"자재비 {int(material_sum):,}원 + 공임비 {int(labor_sum):,}원 = 제조원가 {int(total_cog):,}원")

    # =========================================================
    # [오른쪽] 분석 결과
    # =========================================================
    with col_result:
        st.subheader("가격 및 수익 분석")
        
        target_price = st.number_input("판매 희망가 (KRW)", value=49000, step=1000)
        
        # -----------------------------------------------------
        # [추가된 기능] 배수(Multiplier) 자동 계산 및 표시
        # -----------------------------------------------------
        if total_cog > 0:
            multiplier = target_price / total_cog
        else:
            multiplier = 0
            
        # 조그만 글씨(caption)로 배수 표시
        st.caption(f"원가({int(total_cog):,}원) 대비 **{multiplier:.1f}배수** 책정됨")
        # -----------------------------------------------------

        rc1, rc2 = st.columns(2)
        with rc1:
            channel = st.selectbox("판매 채널", ["자사몰 (3.5%)", "무신사 (30%)", "스마트스토어 (6%)", "백화점 (35%)", "기타"])
        with rc2:
            vat_on = st.toggle("VAT(10%) 포함", value=True)

        # 수수료 로직
        fees_map = {"자사몰 (3.5%)": 0.035, "무신사 (30%)": 0.30, "스마트스토어 (6%)": 0.06, "백화점 (35%)": 0.35, "기타": 0.0}
        fee_rate = fees_map[channel]
        
        if vat_on:
            vat = target_price - (target_price / 1.1)
        else:
            vat = target_price * 0.1
        
        fee = target_price * fee_rate
        profit = target_price - total_cog - fee - vat
        margin = (profit / target_price) * 100 if target_price > 0 else 0

        # 여백 추가
        st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

        # 결과 카드
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
        st.dataframe(
            breakdown_df.style.format({"금액": "{:,.0f}원"}), 
            hide_index=True, 
            use_container_width=True
        )

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
            st.toast("저장이 완료되었습니다.", icon=None)
            time.sleep(0.5)
            st.rerun()

if __name__ == "__main__":
    main()