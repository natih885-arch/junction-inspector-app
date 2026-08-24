import streamlit as st
import pandas as pd
import io
import requests
from PIL import Image
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.drawing.image import Image as OpenpyxlImage
from geopy.geocoders import Nominatim
from streamlit_drawable_canvas import st_canvas

# הגדרות עמוד
st.set_page_config(
    page_title="מערכת פיקוח צמתים - רכבת קלה",
    page_icon="🚦",
    layout="wide"
)

st.title("🚦 מערכת פיקוח צמתים - תצלום אוויר ושרטוט תוואי")

tab1, tab2, tab3 = st.tabs([
    "🗺️ מפה ושרטוט תוואי צומת", 
    "🔢 כתב כמויות וכבלים",
    "📥 הפקת דוח Excel למנכ״ל"
])

# ---------------------------------------------------------
# כרטיסייה 1: מאתר מיקום + תצלום אוויר + לוח שרטוט
# ---------------------------------------------------------
with tab1:
    st.subheader("📌 איתור צומת וטעינת תצלום אוויר")
    
    col_input1, col_input2 = st.columns([3, 1])
    with col_input1:
        address_query = st.text_input("הכנס כתובת / צומת לחיפוש בגוגל מפס:", "אלנבי מנחם בגין תל אביב")
    with col_input2:
        zoom_level = st.slider("רמת זום (Zoom):", 15, 19, 17)

    # מנגנון המרת כתובת לתצלום אוויר/מפה
    bg_image = None
    if st.button("🔍 טען תצלום אוויר של הצומת"):
        with st.spinner("שולף תצלום מפה..."):
            try:
                geolocator = Nominatim(user_agent="traffic_junction_app")
                location = geolocator.geocode(address_query)
                
                if location:
                    lat, lon = location.latitude, location.longitude
                    st.success(f"נמצאה כתובת: {location.address} ({lat:.5f}, {lon:.5f})")
                    
                    # שליפת אריח מפה/לוויין משרת מפות (OpenStreetMap/Esri Satellite)
                    # טעינת תצלום אוויר באמצעות Esri World Imagery (חינמי וללא API Key)
                    map_url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom_level}/{int((1 - float(location.latitude)) / 180 * 2**zoom_level)}/{int((lon + 180) / 360 * 2**zoom_level)}"
                    
                    # חלופה יציבה לשליפת תצלום לוויין בפורמט Static Map:
                    static_map_url = f"https://static-map.openstreetmap.fr/staticmap.php?center={lat},{lon}&zoom={zoom_level}&size=800x450&maptype=mapnik"
                    
                    response = requests.get(static_map_url)
                    if response.status_code == 200:
                        bg_image = Image.open(io.BytesIO(response.content))
                        st.session_state["loaded_bg_image"] = bg_image
                else:
                    st.error("הכתובת לא נמצאה, אנה נסה לחפש שנית או להעלות קובץ תמונה ידנית.")
            except Exception as e:
                st.error(f"שגיאה בשליפת המפה: {e}")

    # בדיקה אם קיימת תמונה טעונה ב-Session State
    if "loaded_bg_image" in st.session_state:
        bg_image = st.session_state["loaded_bg_image"]

    st.divider()
    st.subheader("📐 לוח שרטוט, הוספה והזזת אלמנטים ע״ג הצומת")
    
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        drawing_mode = st.selectbox(
            "כלי שרטוט:",
            ("freedraw", "circle", "rect", "line", "transform"),
            format_func=lambda x: {
                "freedraw": "✏️ תוואי כבלים (ציור חופשי)",
                "circle": "🟢 פנס / עמוד (עיגול)",
                "rect": "🟦 ארון פיקוד / גומחה",
                "line": "📏 קו ישר",
                "transform": "🖐️ הזזה ושיונוי גודל אלמנטים"
            }.get(x, x)
        )
    with col_t2:
        stroke_color = st.color_picker("צבע אלמנט/תוואי:", "#FF0000")
    with col_t3:
        stroke_width = st.slider("עובי קו:", 1, 12, 4)
    with col_t4:
        st.write("")
        st.write("")
        if st.button("🗑️ נקה שרטוט"):
            st.session_state["canvas_junction_sketch"] = None

    # לוח השרטוט שיושב ע"ג התצלום הטעון
    canvas_result = st_canvas(
        fill_color="rgba(255, 230, 0, 0.4)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#E5E7EB" if bg_image is None else None,
        background_image=bg_image,
        height=450,
        width=800,
        drawing_mode=drawing_mode,
        key="canvas_junction_sketch",
    )

    if canvas_result.image_data is not None:
        st.session_state["final_sketch_matrix"] = canvas_result.image_data

# ---------------------------------------------------------
# כרטיסייה 2: כתב כמויות
# ---------------------------------------------------------
with tab2:
    st.subheader("🔢 רישום כמויות ציוד וכבלים")
    col1, col2 = st.columns(2)
    with col1:
        poles_num = st.number_input("כמות עמודי תאורה/רמזור:", value=6)
        car_lights = st.number_input("כמות פנסי רכב:", value=8)
    with col2:
        ped_lights = st.number_input("כמות פנסי הולכי רגל:", value=4)
        cables_meters = st.number_input("אורך כבלים כולל (מטרים):", value=180)

# ---------------------------------------------------------
# כרטיסייה 3: הפקת Excel עם תצלום המפה והשרטוט
# ---------------------------------------------------------
with tab3:
    st.subheader("📥 הפקת דוח Excel להדפסה / למנכ״ל")

    def create_excel():
        output = io.BytesIO()
        wb = openpyxl.Workbook()
        
        # גיליון 1: סקיצה ותצלום אוויר
        ws1 = wb.active
        ws1.title = "סקיצת תוואי צומת"
        ws1.views.sheetView[0].rightToLeft = True
        
        ws1.merge_cells("A1:F1")
        title_cell = ws1["A1"]
        title_cell.value = f"תצלום אוויר וסקיצת תוואי צומת - {address_query}"
        title_cell.font = Font(name="Arial", size=14, bold=True, color="FFFFFF")
        title_cell.fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        title_cell.alignment = Alignment(horizontal="center", vertical="center")

        # שמירת תמונת הלוח והטמעתה ב-Excel
        if "final_sketch_matrix" in st.session_state and st.session_state["final_sketch_matrix"] is not None:
            img_data = st.session_state["final_sketch_matrix"]
            img = Image.fromarray(img_data.astype('uint8'), 'RGBA')
            
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            
            img_byte_arr = io.BytesIO()
            bg.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            excel_img = OpenpyxlImage(img_byte_arr)
            excel_img.width = 650
            excel_img.height = 360
            ws2_img_cell = "B3"
            ws1.add_image(excel_img, ws2_img_cell)

        # גיליון 2: כתב כמויות
        ws2 = wb.create_sheet(title="כתב כמויות")
        ws2.views.sheetView[0].rightToLeft = True
        ws2.append(["תיאור רכיב", "כמות"])
        ws2.append(["עמודי תאורה/רמזור", poles_num])
        ws2.append(["פנסי רכב", car_lights])
        ws2.append(["פנסי הולכי רגל", ped_lights])
        ws2.append(["אורך כבלים (מטר)", cables_meters])

        wb.save(output)
        return output.getvalue()

    excel_data = create_excel()
    st.download_button(
        label="📊 הורד דוח Excel (כולל תצלום הלוויין והסקיצה)",
        data=excel_data,
        file_name="Junction_Sketch_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
