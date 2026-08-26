import streamlit as st
import pandas as pd
import io
import math
from PIL import Image, ImageDraw, ImageFont
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as OpenpyxlImage
from streamlit_drawable_canvas import st_canvas

# ---------------------------------------------------------
# הגדרות עמוד ועיצוב Streamlit
# ---------------------------------------------------------
st.set_page_config(
    page_title="מערכת פיקוח תשתיות צמתים ורמזורים",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Rubik', sans-serif;
    direction: rtl;
}
.main-header {
    background: linear-gradient(135deg, #0f2b48 0%, #1e4d7b 100%);
    color: white;
    padding: 24px 30px;
    border-radius: 12px;
    box-shadow: 0 8px 20px rgba(15, 43, 72, 0.15);
    margin-bottom: 25px;
    border-right: 8px solid #00a887;
}
.main-header h1 { font-size: 26px; font-weight: 700; margin: 0; color: #ffffff; }
.main-header p { font-size: 14px; margin-top: 6px; margin-bottom: 0; color: #d0e1f9; }
.stButton>button {
    width: 100%;
    background: linear-gradient(90deg, #0f2b48 0%, #1e4d7b 100%);
    color: white;
    font-weight: 700;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #1e4d7b 0%, #00a887 100%);
}
.legend-chip {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 16px;
    color: white;
    font-size: 13px;
    font-weight: 600;
    margin-inline-end: 8px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
<h1>🚦 מערכת פיקוח הנדסית, בקרה וסקיצת צמתים</h1>
<p>ניהול כמויות, תכנון סקיצה דינמית (צומת X / T / רק"ל) והפקת דוחות נפרדים (אקסל / תמונה)</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# בנק האלמנטים המורחב (כולל רק"ל ומעברי חצייה)
# ---------------------------------------------------------
ELEMENT_BANK = {
    "pole_metal":    {"label": "עמוד מתכת",        "emoji": "🗼", "color": "#7f8c8d"},
    "pole_concrete": {"label": "עמוד בטון",         "emoji": "🧱", "color": "#8d6e63"},
    "car_light":     {"label": "פנס רכב (רגיל)",     "emoji": "🚦", "color": "#e74c3c"},
    "lrt_light":     {"label": "רמזור רק''ל (רכבת)", "emoji": "🚋", "color": "#9b59b6"},
    "ped_light":     {"label": "פנס הולכי רגל",     "emoji": "🚶", "color": "#3498db"},
    "blinker":       {"label": "בלינקר / מהבהב",    "emoji": "🔶", "color": "#f39c12"},
    "crosswalk":     {"label": "מעבר חצייה",        "emoji": "🦓", "color": "#ffffff"},
    "cabinet":       {"label": "ארון פיקוד/בקר",    "emoji": "🗄️", "color": "#2c3e50"},
}

# ---------------------------------------------------------
# מחולל רקע צומת (PIL)
# ---------------------------------------------------------
def create_junction_background(j_type="4_way", include_lrt=True):
    width, height = 900, 500
    img = Image.new("RGB", (width, height), "#1e272c")
    draw = ImageDraw.Draw(img)
    
    # כביש ראשי
    road_color = "#34495e"
    line_color = "#ffffff"
    
    if j_type == "4_way":
        draw.rectangle([350, 0, 550, 500], fill=road_color) # אנכי
        draw.rectangle([0, 175, 900, 325], fill=road_color) # אופקי
        
        # מעברי חצייה
        for y in range(185, 315, 18):
            draw.line([(320, y), (345, y)], fill=line_color, width=4)
            draw.line([(555, y), (580, y)], fill=line_color, width=4)
        for x in range(360, 540, 18):
            draw.line([(x, 145), (x, 170)], fill=line_color, width=4)
            draw.line([(x, 330), (x, 355)], fill=line_color, width=4)
            
    else: # T-Junction
        draw.rectangle([0, 175, 900, 325], fill=road_color) # אופקי
        draw.rectangle([350, 175, 550, 500], fill=road_color) # אנכי למטה
        
        for y in range(185, 315, 18):
            draw.line([(320, y), (345, y)], fill=line_color, width=4)
            draw.line([(555, y), (580, y)], fill=line_color, width=4)
        for x in range(360, 540, 18):
            draw.line([(x, 330), (x, 355)], fill=line_color, width=4)

    # פסי רק"ל (רכבת קלה) במרכז הכביש במידה ונבחר
    if include_lrt:
        rail_color = "#f1c40f"
        # קווי מסילה אופקיים
        draw.line([(0, 245), (900, 245)], fill=rail_color, width=3)
        draw.line([(0, 255), (900, 255)], fill=rail_color, width=3)
        # אדני מסילה
        for x in range(0, 900, 15):
            draw.line([(x, 242), (x, 258)], fill="#e67e22", width=2)
            
    return img

# ---------------------------------------------------------
# כרטיסיות ראשיות
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🎨 סקיצת תוואי ושרטוט צומת",
    "🔢 כתב כמויות ואומדן כבלים",
    "📥 הפקת דוחות (אקסל / סקיצה)"
])

# ---------------------------------------------------------
# טאב 1: סקיצה ושרטוט
# ---------------------------------------------------------
with tab1:
    st.subheader("⚙️ הגדרות הצומת והרקע")
    c1, c2, c3 = st.columns(3)
    with c1:
        junction_name = st.text_input("שם הצומת / הפרויקט", "צומת אלנבי - מנחם בגין")
        inspector_name = st.text_input("שם המפקח", "נתנאל הררי")
    with c2:
        j_type_choice = st.selectbox("סוג הצומת", ["צומת 4 כיוונים (X)", "צומת 3 כיוונים (T)"])
        j_code = "4_way" if "4" in j_type_choice else "3_way"
    with c3:
        has_lrt = st.checkbox("הוסף תוואי מסילת רק''ל (רכבת קלה)", value=True)
        inspection_date = st.date_input("תאריך פיקוח")

    bg_img = create_junction_background(j_code, has_lrt)
    st.session_state["bg_img"] = bg_img

    st.divider()
    st.subheader("🖌️ סרגל כלים וסקיצה")
    
    # הצגת מקרא
    legend_html = "".join([
        f'<span class="legend-chip" style="background:{v["color"]}; color:{"#000" if v["color"]=="#ffffff" else "#fff"}">{v["emoji"]} {v["label"]}</span>'
        for v in ELEMENT_BANK.values()
    ])
    st.markdown(legend_html, unsafe_allow_html=True)

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        draw_mode = st.selectbox("מצב כלי עבודה:", [
            "🖐️ הזזה ועריכת אלמנטים (transform)",
            "➕ הוספת נקודה / אלמנט (point)",
            "✏️ ציור חופשי (freedraw)",
            "📏 קו ישר / תוואי כבל (line)",
            "🟦 מלבן / ארון פיקוד (rect)"
        ])
        mode_key = draw_mode.split("(")[1].replace(")", "").strip()
        
    with col_m2:
        if mode_key == "point":
            selected_elem = st.selectbox("בחר אלמנט להצבה:", list(ELEMENT_BANK.keys()), 
                                         format_func=lambda k: f"{ELEMENT_BANK[k]['emoji']} {ELEMENT_BANK[k]['label']}")
            color_to_use = ELEMENT_BANK[selected_elem]["color"]
            stroke_width = st.slider("גודל רכיב:", 6, 25, 12)
        else:
            color_to_use = st.color_picker("צבע הקו/האלמנט:", "#00A887")
            stroke_width = st.slider("עובי הקו:", 1, 12, 4)
            
    with col_m3:
        st.write("")
        st.write("")
        if st.button("🗑️ נקה סקיצה מאפס"):
            st.session_state["reset_key"] = st.session_state.get("reset_key", 0) + 1

    # השרטוט עצמו - ללא background_image_url
    canvas_result = st_canvas(
        fill_color="rgba(0, 168, 135, 0.3)",
        stroke_width=stroke_width,
        stroke_color=color_to_use,
        background_image=bg_img,
        height=500,
        width=900,
        drawing_mode=mode_key,
        point_display_radius=stroke_width if mode_key == "point" else 3,
        key=f"canvas_{st.session_state.get('reset_key', 0)}"
    )

    if canvas_result.image_data is not None:
        st.session_state["canvas_data"] = canvas_result.image_data
        st.session_state["canvas_json"] = canvas_result.json_data

# ---------------------------------------------------------
# טאב 2: כתב כמויות ותחשיבים
# ---------------------------------------------------------
with tab2:
    st.subheader("🔢 כתב כמויות - ציוד צומת ותשתיות")
    st.caption("הזן את הכמויות המתוכננות עבור הציוד בצומת:")

    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        st.markdown("##### 🗼 עמודים ותשתיות")
        n_poles_metal = st.number_input("עמודי מתכת", min_value=0, value=6)
        n_poles_conc = st.number_input("עמודי בטון", min_value=0, value=0)
        n_cabinets = st.number_input("ארונות פיקוד/בקר", min_value=0, value=1)
        
    with col_q2:
        st.markdown("##### 🚦 רמזורים ופנסים")
        n_car_lights = st.number_input("פנסי רכב (רגיל)", min_value=0, value=8)
        n_lrt_lights = st.number_input("רמזורי רק''ל (רכבת)", min_value=0, value=4)
        n_ped_lights = st.number_input("פנסי הולכי רגל", min_value=0, value=6)
        
    with col_q3:
        st.markdown("##### 🔶 בלינקרים ומעברים")
        n_blinkers = st.number_input("בלינקרים / מהבהבים", min_value=0, value=2)
        n_crosswalks = st.number_input("מעברי חצייה", min_value=0, value=4)

    # חישוב אומדן כבלי חשמל ופיקוד
    st.divider()
    st.subheader("🔌 אומדן כמויות כבלים מתוכנן (מטרים)")
    
    cable_heavy = (n_car_lights * 30) + (n_lrt_lights * 40) + (n_blinkers * 15)
    cable_ped = n_ped_lights * 20
    cable_ground = (n_poles_metal * 8) + 25

    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("כבל פיקוד רמזורים/רק''ל (NYCWY / NYY)", f"{cable_heavy} מ'")
    mc2.metric("כבל פיקוד הולכי רגל", f"{cable_ped} מ'")
    mc3.metric("כבל הארקה תקני", f"{cable_ground} מ'")

# ---------------------------------------------------------
# טאב 3: הפקת דוחות נפרדים
# ---------------------------------------------------------
with tab3:
    st.subheader("📥 ייצוא והפקת דוחות")
    st.write("תוכל להפיק בנפרד את קובץ האקסל המלא של כתב הכמויות, או להוריד את תמונת הסקיצה המלאה של הצומת.")
    
    col_exp1, col_exp2 = st.columns(2)

    # --- ייצוא 1: דוח אקסל ---
    with col_exp1:
        st.markdown("#### 📊 דוח כתב כמויות באקסל (Excel)")
        st.write("כולל ניתוח כמויות, אומדן כבלים ופרטי פרויקט בפורמט RTL מעוצב.")

        def generate_excel():
            output = io.BytesIO()
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "כתב כמויות"
            ws.views.sheetView[0].rightToLeft = True

            # עיצובים
            font_title = Font(name="Arial", size=16, bold=True, color="FFFFFF")
            font_header = Font(name="Arial", size=11, bold=True, color="FFFFFF")
            font_bold = Font(name="Arial", size=10, bold=True)
            fill_primary = PatternFill(start_color="0F2B48", fill_type="solid")
            fill_secondary = PatternFill(start_color="1E4D7B", fill_type="solid")
            thin_border = Border(left=Side(style='thin', color='CBD5E1'),
                                 right=Side(style='thin', color='CBD5E1'),
                                 top=Side(style='thin', color='CBD5E1'),
                                 bottom=Side(style='thin', color='CBD5E1'))

            # כותרת
            ws.merge_cells("A1:E1")
            ws["A1"] = f"כתב כמויות הנדסי - {junction_name}"
            ws["A1"].font = font_title
            ws["A1"].fill = fill_primary
            ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[1].height = 35

            # פרטים
            ws["A3"] = "מפקח אחראי:"
            ws["B3"] = inspector_name
            ws["D3"] = "תאריך:"
            ws["E3"] = str(inspection_date)
            ws["A3"].font = font_bold
            ws["D3"].font = font_bold

            # טבלת כמויות ציוד
            headers = ["תיאור הרכיב", "סוג / קטגוריה", "כמות מתוכננת", "יחידת מידה", "הערות"]
            ws.row_dimensions[5].height = 25
            for col_num, h in enumerate(headers, 1):
                cell = ws.cell(row=5, column=col_num, value=h)
                cell.font = font_header
                cell.fill = fill_secondary
                cell.alignment = Alignment(horizontal="center", vertical="center")

            items = [
                ("עמוד מתכת", "תשתיות", n_poles_metal, "יח'"),
                ("עמוד בטון", "תשתיות", n_poles_conc, "יח'"),
                ("ארון פיקוד/בקר", "תשתיות", n_cabinets, "יח'"),
                ("פנס רכב (רגיל)", "רמזורים", n_car_lights, "יח'"),
                ("רמזור רק''ל (רכבת)", "רמזורים", n_lrt_lights, "יח'"),
                ("פנס הולכי רגל", "רמזורים", n_ped_lights, "יח'"),
                ("בלינקר / מהבהב", "איתות", n_blinkers, "יח'"),
                ("מעבר חצייה", "סימון", n_crosswalks, "יח'"),
                ("כבל פיקוד רמזורים/רק''ל", "כבלים", cable_heavy, "מטר"),
                ("כבל פיקוד הולכי רגל", "כבלים", cable_ped, "מטר"),
                ("כבל הארקה תקני", "כבלים", cable_ground, "מטר"),
            ]

            for row_idx, item in enumerate(items, 6):
                ws.cell(row=row_idx, column=1, value=item[0])
                ws.cell(row=row_idx, column=2, value=item[1])
                ws.cell(row=row_idx, column=3, value=item[2])
                ws.cell(row=row_idx, column=4, value=item[3])
                for c in range(1, 6):
                    ws.cell(row=row_idx, column=c).border = thin_border

            # התאמת רוחב עמודות
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

            wb.save(output)
            return output.getvalue()

        st.download_button(
            label="📥 ההורד דוח כתב כמויות (Excel)",
            data=generate_excel(),
            file_name=f"BOQ_{junction_name.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # --- ייצוא 2: דוח סקיצה בתמונה ---
    with col_exp2:
        st.markdown("#### 🖼️ ייצוא תמונת סקיצת הצומת")
        st.write("הורדת התרשים המשולב (הורקע + האלמנטים ששורטטו) כקובץ תמונה PNG ברזולוציה מלאה.")

        def get_combined_sketch():
            base_bg = st.session_state.get("bg_img", create_junction_background()).copy().convert("RGBA")
            
            if "canvas_data" in st.session_state and st.session_state["canvas_data"] is not None:
                sketch_arr = st.session_state["canvas_data"]
                sketch_img = Image.fromarray(sketch_arr.astype('uint8'), 'RGBA')
                base_bg.paste(sketch_img, (0, 0), sketch_img)
                
            output = io.BytesIO()
            base_bg.convert("RGB").save(output, format="PNG")
            return output.getvalue()

        st.download_button(
            label="🖼️ הורד תמונת סקיצה (PNG)",
            data=get_combined_sketch(),
            file_name=f"Sketch_{junction_name.replace(' ', '_')}.png",
            mime="image/png"
        )
