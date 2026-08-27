import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="מחולל סקיצות צומת וכתב כמויות",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# HTML / JS / SVG Engine
# -----------------------------------------------------------------------------
HTML_CODE = """
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
  <meta charset="UTF-8">
  <style>
    :root {
      --bg-color: #0f172a;
      --card-bg: #1e293b;
      --border-color: #334155;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #38bdf8;
      --add-color: #2f9e8f;
      --remove-color: #d8555a;
      --dismantle-color: #d99a2b;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }
    body { background-color: var(--bg-color); color: var(--text-main); padding: 15px; }

    .app-container { display: grid; grid-template-columns: 280px 1fr; gap: 20px; height: calc(100vh - 30px); }

    /* Palette Sidebar */
    .sidebar {
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 15px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      overflow-y: auto;
    }
    .sidebar h3 { font-size: 1.1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; color: var(--primary); }
    .palette-item {
      background: #0f172a;
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 10px;
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: grab;
      user-select: none;
      transition: all 0.2s;
    }
    .palette-item:hover { border-color: var(--primary); background: #1e293b; }
    .palette-item svg { width: 32px; height: 32px; flex-shrink: 0; }
    .palette-item span { font-size: 0.95rem; font-weight: 500; }

    /* Main Area */
    .main-area { display: flex; flex-direction: column; gap: 15px; }

    .toolbar {
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 10px 15px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .junction-toggle { display: flex; gap: 8px; }
    .junction-toggle__btn {
      background: #0f172a;
      border: 1px solid var(--border-color);
      color: var(--text-main);
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: bold;
    }
    .junction-toggle__btn.is-active { background: var(--primary); color: #0f172a; border-color: var(--primary); }

    .btn-danger {
      background: #991b1b;
      color: white;
      border: none;
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: bold;
    }
    .btn-danger:hover { background: #dc2626; }

    /* Canvas */
    .canvas-container {
      flex: 1;
      background: #000000;
      border: 1px solid var(--border-color);
      border-radius: 12px;
      position: relative;
      overflow: hidden;
      min-height: 500px;
    }
    #sketchSvg { width: 100%; height: 100%; display: block; }

    /* SVG Elements Styling */
    .grid-line { stroke: #1e293b; stroke-width: 1; }
    .road { fill: #1e293b; stroke: #334155; stroke-width: 2; }
    .lane-dash { stroke: #64748b; stroke-width: 2; stroke-dasharray: 8 8; }
    .placed-el { cursor: move; }
    .el-label { fill: #f8fafc; font-size: 11px; text-anchor: middle; font-weight: 500; pointer-events: none; }
    .el-remove { fill: #ef4444; cursor: pointer; }
    .el-remove-x { fill: white; font-size: 10px; font-weight: bold; text-anchor: middle; cursor: pointer; pointer-events: none; }

    /* BOQ Panel */
    .boq-panel {
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 15px;
    }
    .boq-panel h3 { margin-bottom: 10px; color: var(--primary); }
    table { width: 100%; border-collapse: collapse; text-align: right; }
    th, td { padding: 8px 12px; border-bottom: 1px solid var(--border-color); font-size: 0.9rem; }
    th { background: #0f172a; color: var(--text-muted); }
    .zero { opacity: 0.3; }

    /* Print Mode Hide */
    @media print {
      .sidebar, .toolbar, .btn-danger { display: none !important; }
      .app-container { display: block; }
      body { background: white; color: black; }
    }
  </style>
</head>
<body>

<div class="app-container">
  <!-- סיידבר אלמנטים -->
  <div class="sidebar">
    <h3>בנק אלמנטים</h3>
    <div id="paletteItems"></div>
  </div>

  <!-- אזור מרכזי -->
  <div class="main-area">
    <div class="toolbar">
      <div class="junction-toggle" id="junctionToggle">
        <button class="junction-toggle__btn is-active" data-shape="X">צומת X</button>
        <button class="junction-toggle__btn" data-shape="T">צומת T</button>
      </div>
      <span id="canvasCount" style="color: var(--text-muted); font-size: 0.9rem;">0 אלמנטים בסקיצה</span>
      <button class="btn-danger" id="clearCanvas">ניקוי סקיצה</button>
    </div>

    <div class="canvas-container">
      <svg id="sketchSvg" viewBox="0 0 800 600"></svg>
    </div>

    <!-- טבלת כמויות בתוך הממשק -->
    <div class="boq-panel">
      <h3>כתב כמויות אוטומטי (מתוך הסקיצה)</h3>
      <table id="boqTable">
        <thead>
          <tr>
            <th>תיאור האלמנט</th>
            <th>הוספה (יח')</th>
            <th>הסרה (יח')</th>
            <th>פירוק (יח')</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </div>
</div>

<script>
const SVG_NS = "http://www.w3.org/2000/svg";

const ELEMENT_TYPES = [
  { id: "trafficLight", label: "רמזור תנועה", icon: () => `<rect x="-6" y="-16" width="12" height="30" rx="2" fill="#2b2b2b"/><circle cx="0" cy="-10" r="3.2" fill="#d8555a"/><circle cx="0" cy="-2" r="3.2" fill="#d99a2b"/><circle cx="0" cy="6" r="3.2" fill="#2f9e8f"/>` },
  { id: "pedLight", label: "רמזור הולכי רגל", icon: () => `<rect x="-6" y="-13" width="12" height="24" rx="2" fill="#2b2b2b"/><circle cx="0" cy="-6" r="3.4" fill="#d8555a"/><circle cx="0" cy="3" r="3.4" fill="#2f9e8f"/>` },
  { id: "crosswalk", label: "מעבר חציה", icon: () => `<g><rect x="-16" y="-8" width="32" height="16" fill="none"/>${[-12,-4,4,12].map(x=>`<rect x="${x-2.5}" y="-8" width="5" height="16" fill="#e9edf3"/>`).join("")}</g>` },
  { id: "blinker", label: "מהבהב", icon: () => `<rect x="-2.5" y="-14" width="5" height="16" fill="#2b2b2b"/><circle cx="0" cy="-16" r="5.5" fill="#d99a2b"/><line x1="0" y1="-24" x2="0" y2="-20" stroke="#d99a2b" stroke-width="2"/><line x1="-7" y1="-21" x2="-4.5" y2="-19" stroke="#d99a2b" stroke-width="2"/><line x1="7" y1="-21" x2="4.5" y2="-19" stroke="#d99a2b" stroke-width="2"/>` },
  { id: "poleConcrete", label: "עמוד בטון", icon: () => `<circle cx="0" cy="0" r="9" fill="#9aa3ad" stroke="#5c636b" stroke-width="1.5"/>` },
  { id: "poleWood", label: "עמוד עץ", icon: () => `<circle cx="0" cy="0" r="9" fill="#a9784f" stroke="#6e4c2f" stroke-width="1.5"/>` },
  { id: "camera", label: "מצלמה", icon: () => `<rect x="-9" y="-6" width="18" height="12" rx="2" fill="#2b2b2b"/><circle cx="6" cy="0" r="4" fill="#111"/><circle cx="6" cy="0" r="1.6" fill="#4fb3ff"/>` },
  { id: "sign", label: "תמרור", icon: () => `<rect x="-1.8" y="-2" width="3.6" height="16" fill="#2b2b2b"/><polygon points="0,-18 10,-8 0,2 -10,-8" fill="#fff" stroke="#d8555a" stroke-width="2.2"/>` }
];

const ACTIONS = ["add", "remove", "dismantle"];
const ACTION_LABEL = { add: "הוספה", remove: "הסרה", dismantle: "פירוק" };
const ACTION_COLOR = { add: "#2f9e8f", remove: "#d8555a", dismantle: "#d99a2b" };

const state = { shape: "X", elements: [], nextId: 1 };

document.addEventListener("DOMContentLoaded", () => {
  renderPalette();
  renderJunctionBase();
  bindJunctionToggle();
  bindCanvasDropTarget();
  bindClearButton();
  renderBoqTable();
});

function renderPalette() {
  const wrap = document.getElementById("paletteItems");
  wrap.innerHTML = "";
  ELEMENT_TYPES.forEach(type => {
    const item = document.createElement("div");
    item.className = "palette-item";
    item.draggable = true;
    item.dataset.type = type.id;
    item.innerHTML = `<svg viewBox="-20 -28 40 40">${type.icon()}</svg><span>${type.label}</span>`;
    item.addEventListener("dragstart", e => {
      e.dataTransfer.setData("text/plain", type.id);
      e.dataTransfer.effectAllowed = "copy";
    });
    wrap.appendChild(item);
  });
}

function bindJunctionToggle() {
  const toggle = document.getElementById("junctionToggle");
  toggle.querySelectorAll(".junction-toggle__btn").forEach(btn => {
    btn.addEventListener("click", () => {
      toggle.querySelectorAll(".junction-toggle__btn").forEach(b => b.classList.remove("is-active"));
      btn.classList.add("is-active");
      state.shape = btn.dataset.shape;
      renderJunctionBase();
    });
  });
}

function renderJunctionBase() {
  const svg = document.getElementById("sketchSvg");
  let base = svg.querySelector("#baseLayer");
  if (base) base.remove();

  base = document.createElementNS(SVG_NS, "g");
  base.setAttribute("id", "baseLayer");
  svg.insertBefore(base, svg.firstChild);

  for (let x = 0; x <= 800; x += 40) base.appendChild(line(x, 0, x, 600, "grid-line"));
  for (let y = 0; y <= 600; y += 40) base.appendChild(line(0, y, 800, y, "grid-line"));

  const ROAD_W = 140, cx = 400, cy = 300;

  if (state.shape === "X") {
    base.appendChild(rect(cx - ROAD_W/2, 0, ROAD_W, 600, "road"));
    base.appendChild(rect(0, cy - ROAD_W/2, 800, ROAD_W, "road"));
    base.appendChild(line(cx, 0, cx, cy - ROAD_W/2, "lane-dash"));
    base.appendChild(line(cx, cy + ROAD_W/2, cx, 600, "lane-dash"));
    base.appendChild(line(0, cy, cx - ROAD_W/2, cy, "lane-dash"));
    base.appendChild(line(cx + ROAD_W/2, cy, 800, cy, "lane-dash"));
  } else {
    base.appendChild(rect(0, cy - ROAD_W/2, 800, ROAD_W, "road"));
    base.appendChild(rect(cx - ROAD_W/2, 0, ROAD_W, cy + ROAD_W/2, "road"));
    base.appendChild(line(cx, 0, cx, cy - ROAD_W/2, "lane-dash"));
    base.appendChild(line(0, cy, cx - ROAD_W/2, cy, "lane-dash"));
    base.appendChild(line(cx + ROAD_W/2, cy, 800, cy, "lane-dash"));
  }
}

function line(x1,y1,x2,y2,cls){
  const el = document.createElementNS(SVG_NS,"line");
  el.setAttribute("x1",x1); el.setAttribute("y1",y1);
  el.setAttribute("x2",x2); el.setAttribute("y2",y2);
  el.setAttribute("class",cls); return el;
}
function rect(x,y,w,h,cls){
  const el = document.createElementNS(SVG_NS,"rect");
  el.setAttribute("x",x); el.setAttribute("y",y);
  el.setAttribute("width",w); el.setAttribute("height",h);
  el.setAttribute("class",cls); return el;
}

function bindCanvasDropTarget() {
  const svg = document.getElementById("sketchSvg");
  svg.addEventListener("dragover", e => e.preventDefault());
  svg.addEventListener("drop", e => {
    e.preventDefault();
    const typeId = e.dataTransfer.getData("text/plain");
    const type = ELEMENT_TYPES.find(t => t.id === typeId);
    if (!type) return;
    const pt = clientToSvgPoint(svg, e.clientX, e.clientY);
    addElement(type.id, pt.x, pt.y);
  });
}

function clientToSvgPoint(svg, clientX, clientY) {
  const p = svg.createSVGPoint();
  p.x = clientX; p.y = clientY;
  const ctm = svg.getScreenCTM().inverse();
  return p.matrixTransform(ctm);
}

function addElement(typeId, x, y) {
  const el = { id: state.nextId++, type: typeId, x, y, action: "add" };
  state.elements.push(el);
  renderPlacedElement(el);
  renderBoqTable();
  updateCanvasCount();
}

function renderPlacedElement(elData) {
  const svg = document.getElementById("sketchSvg");
  const type = ELEMENT_TYPES.find(t => t.id === elData.type);

  const g = document.createElementNS(SVG_NS, "g");
  g.setAttribute("class", "placed-el");
  g.dataset.id = elData.id;
  g.setAttribute("transform", `translate(${elData.x},${elData.y})`);

  const ring = document.createElementNS(SVG_NS, "circle");
  ring.setAttribute("cx", 0); ring.setAttribute("cy", -8); ring.setAttribute("r", 20);
  ring.setAttribute("fill", "none"); ring.setAttribute("stroke", ACTION_COLOR[elData.action]);
  ring.setAttribute("stroke-width", 2.5); ring.setAttribute("class", "action-ring");
  g.appendChild(ring);

  const icon = document.createElementNS(SVG_NS, "g");
  icon.innerHTML = type.icon();
  g.appendChild(icon);

  const label = document.createElementNS(SVG_NS, "text");
  label.setAttribute("class", "el-label"); label.setAttribute("y", 24);
  label.textContent = `${type.label} · ${ACTION_LABEL[elData.action]}`;
  g.appendChild(label);

  const delCircle = document.createElementNS(SVG_NS, "circle");
  delCircle.setAttribute("class", "el-remove");
  delCircle.setAttribute("cx", 16); delCircle.setAttribute("cy", -22); delCircle.setAttribute("r", 7);
  const delX = document.createElementNS(SVG_NS, "text");
  delX.setAttribute("class", "el-remove-x");
  delX.setAttribute("x", 16); delX.setAttribute("y", -19.5); delX.textContent = "×";
  
  g.appendChild(delCircle); g.appendChild(delX);

  delCircle.addEventListener("click", (e) => { e.stopPropagation(); removeElement(elData.id); });
  icon.addEventListener("click", (e) => { e.stopPropagation(); cycleAction(elData.id); });

  let dragging = false;
  g.addEventListener("pointerdown", (e) => {
    if (e.target === delCircle || e.target === delX) return;
    dragging = true; g.setPointerCapture(e.pointerId);
  });
  g.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    const pt = clientToSvgPoint(svg, e.clientX, e.clientY);
    elData.x = pt.x; elData.y = pt.y;
    g.setAttribute("transform", `translate(${elData.x},${elData.y})`);
  });
  g.addEventListener("pointerup", () => { dragging = false; });

  svg.appendChild(g);
}

function cycleAction(id) {
  const el = state.elements.find(e => e.id === id);
  if (!el) return;
  const idx = ACTIONS.indexOf(el.action);
  el.action = ACTIONS[(idx + 1) % ACTIONS.length];
  redrawElement(el);
  renderBoqTable();
}

function removeElement(id) {
  state.elements = state.elements.filter(e => e.id !== id);
  const svg = document.getElementById("sketchSvg");
  const g = svg.querySelector(`.placed-el[data-id="${id}"]`);
  if (g) g.remove();
  renderBoqTable();
  updateCanvasCount();
}

function redrawElement(elData) {
  const svg = document.getElementById("sketchSvg");
  const g = svg.querySelector(`.placed-el[data-id="${elData.id}"]`);
  if (g) g.remove();
  renderPlacedElement(elData);
}

function updateCanvasCount() {
  document.getElementById("canvasCount").textContent = `${state.elements.length} אלמנטים בסקיצה`;
}

function bindClearButton() {
  document.getElementById("clearCanvas").addEventListener("click", () => {
    if (state.elements.length && !confirm("לנקות את כל האלמנטים מהסקיצה?")) return;
    state.elements = [];
    document.querySelectorAll(".placed-el").forEach(n => n.remove());
    renderBoqTable();
    updateCanvasCount();
  });
}

function computeBoq() {
  return ELEMENT_TYPES.map(type => {
    const counts = { add: 0, remove: 0, dismantle: 0 };
    state.elements.filter(e => e.type === type.id).forEach(e => counts[e.action]++);
    return { label: type.label, ...counts };
  });
}

function renderBoqTable() {
  const tbody = document.querySelector("#boqTable tbody");
  tbody.innerHTML = "";
  computeBoq().forEach(row => {
    const total = row.add + row.remove + row.dismantle;
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.label}</td>
      <td class="${row.add ? "" : "zero"}">${row.add}</td>
      <td class="${row.remove ? "" : "zero"}">${row.remove}</td>
      <td class="${row.dismantle ? "" : "zero"}">${row.dismantle}</td>
    `;
    if (total === 0) tr.style.opacity = "0.4";
    tbody.appendChild(tr);
  });
}
</script>
</body>
</html>
"""

# -----------------------------------------------------------------------------
# Streamlit UI Layout
# -----------------------------------------------------------------------------
st.title("🚦 מחולל סקיצות צומת ודוח כתב כמויות")

# סיידבר פרטי דוח
with st.sidebar:
    st.header("📋 פרטי דוח הפיקוח")
    site_name = st.text_input("שם האתר / צומת", placeholder="לדוגמה: צומת אלנבי / רוטשילד")
    inspector_name = st.text_input("שם המפקח", placeholder="שם מלא")
    site_date = st.date_input("תאריך בדיקה")
    
    st.subheader("🔌 תשתיות כבלים")
    cable_overhead = st.number_input("כבל עילי (מטרים)", min_value=0, value=0, step=5)
    cable_underground = st.number_input("כבל תת-קרקעי (מטרים)", min_value=0, value=0, step=5)
    
    notes = st.text_area("הערות נוספות לדוח", placeholder="פירוט תקלות, דגשים לביצוע...")

# תצוגה ראשית: 2 טאבים (סקיצה אינטראקטיבית / הפקת דוח)
tab1, tab2 = st.tabs(["🎨 סקיצה אינטראקטיבית", "📄 תצוגת דוח מלא להדפסה"])

with tab1:
    components.html(HTML_CODE, height=920, scrolling=False)

with tab2:
    st.subheader("תצוגת דוח סופי")
    st.info("💡 להדפסה או שמירה כ-PDF, לחץ Ctrl+P במקלדת (או Cmd+P ב-Mac)")
    
    # תצוגת הדוח
    st.markdown(f"""
    <div style="background: white; color: black; padding: 25px; border-radius: 8px; font-family: sans-serif; direction: rtl;">
        <h2 style="text-align: center; margin-bottom: 20px; border-bottom: 2px solid #333; padding-bottom: 10px;">דוח פיקוח ותשתיות צומת</h2>
        
        <table style="width: 100%; margin-bottom: 20px; border-collapse: collapse; border: none;">
            <tr style="border: none;">
                <td style="border: none;"><strong>אתר:</strong> {site_name or '—'}</td>
                <td style="border: none;"><strong>תאריך:</strong> {site_date}</td>
                <td style="border: none;"><strong>מפקח:</strong> {inspector_name or '—'}</td>
            </tr>
        </table>
        
        <hr style="margin: 15px 0;">
        
        <h4>תשתיות כבלים:</h4>
        <ul>
            <li><strong>כבל עילי:</strong> {cable_overhead} מטר</li>
            <li><strong>כבל תת-קרקעי:</strong> {cable_underground} מטר</li>
        </ul>
        
        <hr style="margin: 15px 0;">
        
        <h4>הערות מפקח:</h4>
        <p style="background: #f8f9fa; padding: 10px; border-radius: 4px; border: 1px solid #ddd;">{notes or 'אין הערות נוספות.'}</p>
    </div>
    """, unsafe_allow_html=True)
