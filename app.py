import streamlit as st
import pandas as pd
import io
import math
import requests
from PIL import Image
import folium
from streamlit_folium import st_folium
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as OpenpyxlImage
from geopy.geocoders import Nominatim
from streamlit_drawable_canvas import st_canvas

# הגדרות עמוד ראשי
st.set_page_config(
    page_title="מערכת פיקוח צמתים - רכבת קלה",
    page_icon="🚦",
    layout="wide"
)

st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E3A8A; text-align: right; margin-bottom: 5px; }
    .sub-title { font-size: 18px; color: #4B5563; text-align: right; margin-bottom: 20px; }
    .stButton>button { width: 100%; background-color: #1E3A8A; color: white; font-weight: bold; }
    .footer { text-align: center; margin-top: 40px; padding: 15px; border-top: 1px solid #E5E7EB; color: #6B7280; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚦 מערכת פיקוח צמתים וכתב כמויות - רכבת קלה</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">תיעוד מהיר בשטח | סקיצת מפה ושרטוט תוואי | אישור הארקה | הפקת דוח Excel</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎨 סקיצת צומת ומפה", 
    "🔢 ספירת ציוד בשטח", 
    "⚡ אישור הארקה ובטיחות",
    "📊 כתב כמויות וחישוב כבלים",
    "📥 הפקת דוח למנכ״ל (Excel)"
])

# ---------------------------------------------------------
# כרטיסייה 1: סקיצת צומת ושרטוט ויזואלי
# ---------------------------------------------------------
with tab1:
    st.subheader("📌 פרטי הפיקוח ומיקום")
    col_a, col_b = st.columns(2)
    with col_a:
        junction_name = st.text_input("שם / מספר הצומת", "אלנבי מנחם בגין תל אביב")
        inspector_name = st.text_input("שם המפקח בשטח", "נתנאל הררי")
        project_phase = st.selectbox("שלב הסדר התנועה", [
            "שלב א' - מצב קיים (לפני שינוי)",
            "שלב ב' - הסדר זמני (כבילה עילית)",
            "שלב ג' - הסדר קבוע (כבילה תחתית / סופי)"
        ])
    with col_b:
        inspection_date = st.date_input("תאריך סיור הפיקוח")
        cabling_mode = st.radio("סוג כבילה מרכזי בתוואי", ["כבילה תחתית (שרוולים/שוקיות באדמה)", "כבילה עילית (זמנית על מתוחים)"])
        general_notes = st.text_area("הערות כלליות/מיקום צומת", "תוואי כבילה מתוכנן מצד מזרח למערב כולל מעבר ארון פיקוד")

    st.divider()
    st.subheader("🗺️ איתור ובחירת נקודת הצומת על גבי המפה")
    st.caption("חפש כתובת או לחץ ישירות על גבי המפה כדי לסמן את הנקודה המדויקת של הצומת:")

    # מיקום ברירת מחדל (תל אביב - אלנבי / מנחם בגין)
    if "map_lat" not in st.session_state:
        st.session_state["map_lat"] = 32.06050
        st.session_state["map_lon"] = 34.77537

    col_map_in1, col_map_in2 = st.columns([3, 1])
    with col_map_in1:
        map_search_query = st.text_input("חיפוש כתובת / צומת:", value=junction_name)
    with col_map_in2:
        if st.button("🔍 חפש כתובת"):
            try:
                geolocator = Nominatim(user_agent="traffic_inspector_app_v3")
                location = geolocator.geocode(map_search_query)
                if location:
                    st.session_state["map_lat"] = location.latitude
                    st.session_state["map_lon"] = location.longitude
                    st.success(f"נמצא: {location.address}")
                else:
                    st.error("הכתובת לא נמצאה, לחץ ידנית על המפה לבחירת מיקום.")
            except Exception as e:
                st.error(f"שגיאת איתור: {e}")

    # הצגת מפה אינטראקטיבית לבחירת נקודה
    m = folium.Map(
        location=[st.session_state["map_lat"], st.session_state["map_lon"]], 
        zoom_start=17,
        tiles="OpenStreetMap"
    )
    folium.Marker(
        [st.session_state["map_lat"], st.session_state["map_lon"]],
        popup="מיקום הצומת הנבחר",
        tooltip="מיקום הצומת"
    ).add_to(m)

    map_data = st_folium(m, height=350, width=800, key="interactive_folium_map")

    # עדכון מיקום לפי לחיצת עכבר על המפה
    if map_data and map_data.get("last_clicked"):
        st.session_state["map_lat"] = map_data["last_clicked"]["lat"]
        st.session_state["map_lon"] = map_data["last_clicked"]["lng"]

    col_btn_fetch, _ = st.columns([2, 2])
    with col_btn_fetch:
        if st.button("🖼️ טען את מפת המיקום הנבחר ללוח השרטוט"):
            with st.spinner("מכין תמונה מתוך המפה..."):
                lat, lon = st.session_state["map_lat"], st.session_state["map_lon"]
                zoom = 17
                
                # חישוב אריח מפה מדויק ותקני באמצעות ספרית math הרשמית
                n = 2.0 ** zoom
                xtile = int((lon + 180.0) / 360.0 * n)
                ytile = int((1.0 - math.log(math.tan(math.radians(lat)) + (1.0 / math.cos(math.radians(lat)))) / math.pi) / 2.0 * n)
                
                tile_url = f"https://tile.openstreetmap.org/{zoom}/{xtile}/{ytile}.png"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                
                try:
                    res = requests.get(tile_url, headers=headers, timeout=5)
                    if res.status_code == 200:
                        st.session_state["fetched_bg_map"] = Image.open(io.BytesIO(res.content)).resize((800, 450))
                        st.success("תמונת המפה נטענה בהצלחה ללוח השרטוט למטה!")
                    else:
                        st.warning("לא ניתן להוריד מפה אוטומטית. ניתן להעלות תמונת מסך/תצלום אוויר בטופס למטה.")
                except Exception as e:
                    st.warning(f"שגיאת תקשורת קלה. מומלץ להעלות תמונה ידנית: {e}")

    st.divider()
    st.subheader("📐 לוח שרטוט וסקיצה הנדסית לצומת")
    st.caption("שרטט את תוואי הכבלים, העמודים והפנסים. השרטוט החזותי שייווצר פה יוטמע כתמונה מלאה בתוך קובץ ה-Excel.")

    col_tool1, col_tool2, col_tool3 = st.columns(3)
    with col_tool1:
        drawing_mode = st.selectbox(
            "כלי שרטוט:",
            ("freedraw", "line", "rect", "circle", "transform"),
            format_func=lambda x: {
                "freedraw": "✏️ ציור חופשי (תוואי כבלים)",
                "line": "📏 קו ישר",
                "rect": "🟦 מלבן / ארון פיקוד",
                "circle": "🟢 עיגול / עמוד / פנס",
                "transform": "🖐️ הזזה ועריכת אלמנטים"
            }.get(x, x)
        )
    with col_tool2:
        stroke_color = st.color_picker("צבע התוואי/האלמנט:", "#FF0000")
    with col_tool3:
        stroke_width = st.slider("עובי הקו:", 1, 15, 3)

    bg_image_file = st.file_uploader("📷 העלה תמונת רקע / תצלום אוויר לצומת (אופציונלי):", type=["png", "jpg", "jpeg"])
    
    bg_img = None
    if bg_image_file:
        bg_img = Image.open(bg_image_file)
    elif "fetched_bg_map" in st.session_state:
        bg_img = st.session_state["fetched_bg_map"]

    # לוח השרטוט הגרפי
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#F3F4F6" if bg_img is None else None,
        background_image=bg_img,
        height=450,
        width=800,
        drawing_mode=drawing_mode,
        key="canvas_junction_sketch",
    )

    if canvas_result.image_data is not None:
        st.session_state["canvas_sketch_image"] = canvas_result.image_data

# ---------------------------------------------------------
# כרטיסייה 2: ספירת ציוד בשטח
# ---------------------------------------------------------
with tab2:
    st.subheader("🔢 תיעוד ציוד בצומת")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🏛️ עמודים ותשתיות")
        poles_metal_before = st.number_input("עמודי מתכת (לפני)", min_value=0, value=4)
        poles_metal_after = st.number_input("עמודי מתכת (אחרי)", min_value=0, value=6)
        poles_concrete_before = st.number_input("עמודי בטון (לפני)", min_value=0, value=2)
        poles_concrete_after = st.number_input("עמודי בטון (אחרי)", min_value=0, value=0)

    with col2:
        st.markdown("### 🚥 פנסי תנועה")
        car_lights_before = st.number_input("פנסי רכב (לפני)", min_value=0, value=6)
        car_lights_after = st.number_input("פנסי רכב (אחרי)", min_value=0, value=8)
        ped_lights_before = st.number_input("פנסי הולכי רגל (לפני)", min_value=0, value=4)
        ped_lights_after = st.number_input("פנסי הולכי רגל (אחרי)", min_value=0, value=6)

    with col3:
        st.markdown("### 🚲 בלינקרים ואופניים")
        blinkers_before = st.number_input("בלינקרים / מהבהבים (לפני)", min_value=0, value=1)
        blinkers_after = st.number_input("בלינקרים / מהבהבים (אחרי)", min_value=0, value=3)
        bike_lights_before = st.number_input("פנסי אופניים (לפני)", min_value=0, value=0)
        bike_lights_after = st.number_input("פנסי אופניים (אחרי)", min_value=0, value=2)

# ---------------------------------------------------------
# כרטיסייה 3: אישור הארקה
# ---------------------------------------------------------
with tab3:
    st.subheader("⚡ צ'קליסט אישור הארקה ובטיחות")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        g_poles = st.checkbox("✅ בוצעה בדיקת חיבור הארקה לכל עמודי הצומת", value=True)
        g_cabinet = st.checkbox("✅ הארקת ארון פיקוד מרכזי מחוברת ותקינה", value=True)
        g_continuity = st.checkbox("✅ בוצעה בדיקת רציפות הארקה (Continuity Test)", value=True)
        g_value = st.number_input("ערך הארקה שנמדד (אוהם Ω)", min_value=0.0, value=1.2, step=0.1)

    with col_g2:
        grounding_img = st.file_uploader("📷 צילום פתח עמוד / פס הארקה", type=["jpg", "png", "jpeg"])
        if grounding_img:
            image = Image.open(grounding_img)
            st.image(image, caption="תמונת הארקה מהשטח", width=300)

    is_grounding_approved = g_poles and g_cabinet and g_continuity
    if is_grounding_approved:
        st.success("🛡️ סטטוס בטיחות: הארקת הצומת מאושרת ותקינה!")
    else:
        st.error("❌ אזהרה: טרם הושלמו כל בדיקות ההארקה הנדרשות!")

# ---------------------------------------------------------
# כרטיסייה 4: כתב כמויות
# ---------------------------------------------------------
with tab4:
    st.subheader("📊 כתב כמויות הנדסי (לפני vs אחרי)")
    boq_data = [
        {"תיאור הרכיב": "עמודי מתכת (זרוע/ישר)", "לפני": poles_metal_before, "אחרי": poles_metal_after},
        {"תיאור הרכיב": "עמודי בטון", "לפני": poles_concrete_before, "אחרי": poles_concrete_after},
        {"תיאור הרכיב": "פנסי תנועה לרכב", "לפני": car_lights_before, "אחרי": car_lights_after},
        {"תיאור הרכיב": "פנסי הולכי רגל", "לפני": ped_lights_before, "אחרי": ped_lights_after},
        {"תיאור הרכיב": "בלינקרים / מהבהבים", "לפני": blinkers_before, "אחרי": blinkers_after},
        {"תיאור הרכיב": "פנסי אופניים", "לפני": bike_lights_before, "אחרי": bike_lights_after},
    ]
    df_boq = pd.DataFrame(boq_data)
    df_boq["שינוי (דלתא Δ)"] = df_boq["אחרי"] - df_boq["לפני"]
    st.dataframe(df_boq, use_container_width=True)

    added_car_lights = max(0, car_lights_after - car_lights_before)
    added_ped_lights = max(0, ped_lights_after - ped_lights_before)
    added_blinkers = max(0, blinkers_after - blinkers_before)

    cable_heavy = (added_car_lights * 32) + (added_blinkers * 20)
    cable_light = added_ped_lights * 22
    cable_ground = (poles_metal_after * 6) + 15

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("כבל פיקוד רמזורים כבד", f"{cable_heavy} מטר")
    m2.metric("כבל פיקוד הולכי רגל", f"{cable_light} מטר")
    m3.metric("כבל הארקה תקני", f"{cable_ground} מטר")

# ---------------------------------------------------------
# כרטיסייה 5: הפקת דוח Excel עם סקיצה ויזואלית מובנית
# ---------------------------------------------------------
with tab5:
    st.subheader("📥 הפקת דוח Excel למנכ״ל")
    
    def generate_excel_report():
        output = io.BytesIO()
        wb = openpyxl.Workbook()
        
        # ------------------- גיליון 1: כתב כמויות -------------------
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

        headers = ["תיאור הרכיב / ציוד", "כמות לפני", "כמות אחרי", "שינוי (דלתא Δ)", "הערות"]
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

        # הוספת חישובי כבלים ל-Excel
        cable_start_row = 17
        ws1.cell(row=cable_start_row, column=1, value="סיכום כבלים מתוכנן").font = Font(bold=True, size=12)
        ws1.cell(row=cable_start_row+1, column=1, value="כבל פיקוד רמזורים כבד")
        ws1.cell(row=cable_start_row+1, column=2, value=f"{cable_heavy} מטר")
        ws1.cell(row=cable_start_row+2, column=1, value="כבל פיקוד הולכי רגל")
        ws1.cell(row=cable_start_row+2, column=2, value=f"{cable_light} מטר")
        ws1.cell(row=cable_start_row+3, column=1, value="כבל הארקה תקני")
        ws1.cell(row=cable_start_row+3, column=2, value=f"{cable_ground} מטר")

        # ------------------- גיליון 2: סקיצה הנדסית ויזואלית -------------------
        ws2 = wb.create_sheet(title="סקיצת תוואי ומיקומים")
        ws2.views.sheetView[0].rightToLeft = True

        ws2.merge_cells("A1:G1")
        title_cell2 = ws2["A1"]
        title_cell2.value = f"תרשים סקיצת צומת ותוואי שטח - {junction_name}"
        title_cell2.font = Font(name="Arial", size=14, bold=True, color="FFFFFF")
        title_cell2.fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        title_cell2.alignment = Alignment(horizontal="center", vertical="center")

        # הזרקת תמונת הסקיצה הויזואלית לגיליון Excel
        if "canvas_sketch_image" in st.session_state and st.session_state["canvas_sketch_image"] is not None:
            img_data = st.session_state["canvas_sketch_image"]
            img = Image.fromarray(img_data.astype('uint8'), 'RGBA')
            
            # המרת התמונה ל-RGB לצורך שמירה ב-Excel
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            
            img_byte_arr = io.BytesIO()
            bg.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            excel_img = OpenpyxlImage(img_byte_arr)
            excel_img.width = 650
            excel_img.height = 360
            ws2.add_image(excel_img, "B3")
        else:
            ws2.cell(row=4, column=2, value="לא בוצע שרטוט ויזואלי על גבי הלוח.").font = Font(bold=True, color="FF0000")

        wb.save(output)
        return output.getvalue()

    excel_file = generate_excel_report()
    st.download_button(
        label="📊 הורד דוח Excel הנדסי (כולל תרשים סקיצה חזותי)",
        data=excel_file,
        file_name=f"Junction_Report_{junction_name.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ---------------------------------------------------------
# פוטר זכויות יוצרים
# ---------------------------------------------------------
st.markdown(
    '<div class="footer">© כל הזכויות שמורות לנתנאל הררי | 📞 0545520445</div>',
    unsafe_allow_html=True
)
