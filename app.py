import streamlit as st
import pandas as pd
import io
from PIL import Image
import folium
from streamlit_folium import st_folium
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# הגדרות עמוד ראשי
st.set_page_config(
    page_title="מערכת פיקוח צמתים - רכבת קלה",
    page_icon="🚦",
    layout="wide"
)

# עיצוב מותאם אישית בכותרת
st.markdown("""
    <style>
    .main-title {
        font-size: 32px;
        font-weight: bold;
        color: #1E3A8A;
        text-align: right;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 18px;
        color: #4B5563;
        text-align: right;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚦 מערכת פיקוח צמתים וכתב כמויות - רכבת קלה</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">תיעוד מהיר בשטח | בדיקות הארקה | סקיצת מפה | הפקת דוח Excel לעריכה</div>', unsafe_allow_html=True)

# כרטיסיות ראשיות באפליקציה
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 פרטי צומת ומפה", 
    "🔢 ספירת ציוד בשטח (לפני/אחרי)", 
    "⚡ אישור הארקה ובטיחות",
    "📊 כתב כמויות וחישוב כבלים",
    "📥 הפקת דוח למנכ״ל (Excel)"
])

# ---------------------------------------------------------
# כרטיסייה 1: פרטי צומת ומפה
# ---------------------------------------------------------
with tab1:
    st.subheader("📌 פרטי הפיקוח והמיקום")
    col_a, col_b = st.columns(2)
    with col_a:
        junction_name = st.text_input("שם / מספר הצומת", "צומת 102 - אלנבי / מנחם בגין")
        inspector_name = st.text_input("שם המפקח בשטח", "נתנאל הררי")
        project_phase = st.selectbox("שלב הסדר התנועה", [
            "שלב א' - מצב קיים (לפני שינוי)",
            "שלב ב' - הסדר זמני (כבילה עילית)",
            "שלב ג' - הסדר קבוע (כבילה תחתית / סופי)"
        ])
    with col_b:
        inspection_date = st.date_input("תאריך סיור הפיקוח")
        cabling_mode = st.radio("סוג כבילה מרכזי בתוואי", ["כבילה תחתית (שרוולים/שוקיות באדמה)", "כבילה עילית (זמנית על מתוחים)"])
        general_notes = st.text_area("הערות כלליות/מיקום צומת", "נתיב השתלבות מזרח כולל בלינקר מזהיר לפני הסדר תנועה")

    st.divider()
    st.subheader("🗺️ איתור הצומת על גבי מפת גוגל / מפת לוויין")
    st.info("לחץ על המפה כדי לסמן את מיקום ארון הפיקוד / מרכז הצומת:")

    m = folium.Map(location=[32.0636, 34.7735], zoom_start=16)
    folium.TileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google', name='Google Satellite').add_to(m)
    
    map_data = st_folium(m, height=350, width="100%")
    
    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lng = map_data["last_clicked"]["lng"]
        st.success(f"📍 קואורדינטות נבחרו: {lat:.5f}, {lng:.5f}")

# ---------------------------------------------------------
# כרטיסייה 2: ספירת ציוד בשטח (פשוט ומהיר למפקח)
# ---------------------------------------------------------
with tab2:
    st.subheader("🔢 תיעוד ציוד בצומת (קליק פשוט להוספה)")
    st.caption("הזן את הכמויות שהיו במצב הקיים ('לפני') ואת הכמויות המתוכננות/קיימות ('אחרי'):")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🏛️ עמודים ותשתיות")
        poles_metal_before = st.number_input("עמודי מתכת (לפני)", min_value=0, value=4)
        poles_metal_after = st.number_input("עמודי מתכת (אחרי)", min_value=0, value=6)
        
        poles_concrete_before = st.number_input("עמודי בטון (לפני)", min_value=0, value=2)
        poles_concrete_after = st.number_input("עמודי בטון (אחרי)", min_value=0, value=0)

    with col2:
        st.markdown("### 🚥 פנסי תנועה לרכב והולכי רגל")
        car_lights_before = st.number_input("פנסי רכב - 3 צבעים (לפני)", min_value=0, value=6)
        car_lights_after = st.number_input("פנסי רכב - 3 צבעים (אחרי)", min_value=0, value=8)

        ped_lights_before = st.number_input("פנסי הולכי רגל (לפני)", min_value=0, value=4)
        ped_lights_after = st.number_input("פנסי הולכי רגל (אחרי)", min_value=0, value=6)

    with col3:
        st.markdown("### 🚲 בלינקרים, אופניים ונתיבי השתלבות")
        blinkers_before = st.number_input("בלינקרים / מהבהבים (לפני)", min_value=0, value=1)
        blinkers_after = st.number_input("בלינקרים / מהבהבים (אחרי)", min_value=0, value=3)

        bike_lights_before = st.number_input("פנסי אופניים (לפני)", min_value=0, value=0)
        bike_lights_after = st.number_input("פנסי אופניים (אחרי)", min_value=0, value=2)

# ---------------------------------------------------------
# כרטיסייה 3: אישור הארקה ובטיחות
# ---------------------------------------------------------
with tab3:
    st.subheader("⚡ צ'קליסט אישור הארקה ובטיחות בצומת (חובה)")
    st.warning("ללא אישור הארקה תקין, הדוח יסומן כ'לא מאושר בטיחותית'.")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        g_poles = st.checkbox("✅ בוצעה בדיקת חיבור הארקה לכל עמודי הצומת", value=True)
        g_cabinet = st.checkbox("✅ הארקת ארון פיקוד מרכזי מחוברת ותקינה", value=True)
        g_continuity = st.checkbox("✅ בוצעה בדיקת רציפות הארקה (Continuity Test)", value=True)
        g_value = st.number_input("ערך הארקה שנמדד (אוהם Ω) - אופציונלי", min_value=0.0, value=1.2, step=0.1)

    with col_g2:
        st.markdown("📷 **צילום חובה של חיבור הארקה מהשטח:**")
        grounding_img = st.file_uploader("העלה צילום פתח עמוד / פס הארקה בארון", type=["jpg", "png", "jpeg"])
        if grounding_img:
            image = Image.open(grounding_img)
            st.image(image, caption="תמונת הארקה שצולמה בשטח", width=300)

    is_grounding_approved = g_poles and g_cabinet and g_continuity
    if is_grounding_approved:
        st.success("🛡️ סטטוס בטיחות: הארקת הצומת מאושרת ותקינה!")
    else:
        st.error("❌ אזהרה: טרם הושלמו כל בדיקות ההארקה הנדרשות!")

# ---------------------------------------------------------
# כרטיסייה 4: כתב כמויות וחישוב כבלים אוטומטי
# ---------------------------------------------------------
with tab4:
    st.subheader("📊 כתב כמויות הנדסי אוטומטי (לפני vs אחרי)")

    boq_data = [
        {"תיאור הרכיב": "עמודי מתכת (זרוע/ישר)", "לפני": poles_metal_before, "אחרי": poles_metal_after},
        {"תיאור הרכיב": "עמודי בטון", "לפני": poles_concrete_before, "אחרי": poles_concrete_after},
        {"תיאור הרכיב": "פנסי תנועה לרכב (3 צבעים)", "לפני": car_lights_before, "אחרי": car_lights_after},
        {"תיאור הרכיב": "פנסי הולכי רגל", "לפני": ped_lights_before, "אחרי": ped_lights_after},
        {"תיאור הרכיב": "בלינקרים / מהבהבי אזהרה", "לפני": blinkers_before, "אחרי": blinkers_after},
        {"תיאור הרכיב": "פנסי אופניים", "לפני": bike_lights_before, "אחרי": bike_lights_after},
    ]

    df_boq = pd.DataFrame(boq_data)
    df_boq["שינוי (דלתא Δ)"] = df_boq["אחרי"] - df_boq["לפני"]

    st.dataframe(df_boq, use_container_width=True)

    st.divider()
    st.subheader("🔌 חישוב מטראז' כבלים מנותח מאחורי הקלעים")
    st.caption("החישוב כולל: מרחק אופקי ממוצע (25מ') + עלייה אנכית בגובה העמוד (4מ') + רזרבות חיבורים בארון ובבסיס (3מ'):")

    added_car_lights = max(0, car_lights_after - car_lights_before)
    added_ped_lights = max(0, ped_lights_after - ped_lights_before)
    added_blinkers = max(0, blinkers_after - blinkers_before)

    cable_heavy = (added_car_lights * 32) + (added_blinkers * 20)
    cable_light = added_ped_lights * 22
    cable_ground = (poles_metal_after * 6) + 15

    m1, m2, m3 = st.columns(3)
    m1.metric("כבל פיקוד רמזורים כבד (16-24 גידים)", f"{cable_heavy} מטר", delta=f"+{cable_heavy} מ'")
    m2.metric("כבל פיקוד הולכי רגל/שילוט (10 גידים)", f"{cable_light} מטר", delta=f"+{cable_light} מ'")
    m3.metric("כבל הארקה תקני (עמודים + ארון)", f"{cable_ground} מטר", delta=f"+{cable_ground} מ'")

# ---------------------------------------------------------
# כרטיסייה 5: הפקת דוח מעוצב למנכ"ל (Excel פתוח לעריכה)
# ---------------------------------------------------------
with tab5:
    st.subheader("📥 הפקת קובץ Excel מקיף ומעוצב ברמה הנדסית")
    st.info("קובץ ה-Excel מיוצר עם נוסחאות עבודה פתוחות, כך שהמנכ״ל או מנהל הפרויקט יוכלו לערוך כמויות ומחירים מאוחר יותר במידת הצורך.")

    def generate_excel_report():
        output = io.BytesIO()
        wb = openpyxl.Workbook()
        
        ws1 = wb.active
        ws1.title = "כתב כמויות וסיכום"
        ws1.views.sheetView[0].rightToLeft = True

        ws1.merge_cells("A1:E1")
        title_cell = ws1["A1"]
        title_cell.value = f"דוח פיקוח וכתב כמויות - {junction_name}"
        title_cell.font = Font(name="Arial", size=16, bold=True, color="FFFFFF")
        title_cell.fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        title_cell.alignment = Alignment(horizontal="center", vertical="center")

        ws1["A3"] = "שם המפקח:"
        ws1["B3"] = inspector_name
        ws1["A4"] = "תאריך סיור:"
        ws1["B4"] = str(inspection_date)
        ws1["A5"] = "שלב הסדר תנועה:"
        ws1["B5"] = project_phase
        ws1["A6"] = "סטטוס הארקה:"
        ws1["B6"] = "מאושר ותקין" if is_grounding_approved else "לא אושר"

        headers = ["תיאור הרכיב / ציוד", "כמות לפני (מצב קיים)", "כמות אחרי (מתוכנן)", "שינוי (דלתא Δ)", "הערות פיקוח"]
        ws1.append([])
        ws1.append(headers)

        header_fill = PatternFill(start_color="3B82F6", end_color="3B82F6", fill_type="solid")
        header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")

        for col_num in range(1, 6):
            cell = ws1.cell(row=8, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        for r_idx, row in df_boq.iterrows():
            row_num = 9 + r_idx
            ws1.cell(row=row_num, column=1, value=row["תיאור הרכיב"])
            ws1.cell(row=row_num, column=2, value=row["לפני"])
            ws1.cell(row=row_num, column=3, value=row["אחרי"])
            ws1.cell(row=row_num, column=4, value=f"=C{row_num}-B{row_num}")
            ws1.cell(row=row_num, column=5, value="")

        ws1.append([])
        ws1.append(["אומדן כבלים מחושב", "מטראז' (מטר)", "סוג כבל", "סוג התקנה"])
        cb_row = ws1.max_row
        for col_num in range(1, 5):
            ws1.cell(row=cb_row, column=col_num).font = Font(bold=True)
            ws1.cell(row=cb_row, column=col_num).fill = PatternFill(start_color="E5E7EB", fill_type="solid")

        ws1.append(["כבל פיקוד רמזורים כבד", cable_heavy, "16-24 גידים", cabling_mode])
        ws1.append(["כבל פיקוד הולכי רגל", cable_light, "10 גידים", cabling_mode])
        ws1.append(["כבל הארקה תקני", cable_ground, "1x16 צהוב-ירוק", "תחתי/עמודים"])

        for col in ws1.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws1.column_dimensions[col_letter].width = max(max_len + 3, 15)

        wb.save(output)
        return output.getvalue()

    excel_file = generate_excel_report()
    st.download_button(
        label="📊 הורד דוח Excel הנדסי פתוח לעריכה עבור המנכ״ל",
        data=excel_file,
        file_name=f"Junction_Report_{junction_name.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
