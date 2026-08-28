import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="מחולל סקיצות צומת וכתב כמויות - נתנאל הררי",
    layout="wide",
    initial_sidebar_state="collapsed"
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
      --existing-color: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }
    body { background-color: var(--bg-color); color: var(--text-main); padding: 15px; }
    .app-container { display: grid; grid-template-columns: 290px 1fr; gap: 20px; height: calc(100vh - 70px); }
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
    .sidebar h3 { font-size: 1.05rem; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; color: var(--primary); }
    .palette-item {
      background: #0f172a;
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 8px 10px;
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: grab;
      user-select: none;
      transition: all 0.2s;
    }
    .palette-item:hover { border-color: var(--primary); background: #1e293b; }
    .palette-item svg { width: 30px; height: 30px; flex-shrink: 0; }
    .palette-item span { font-size: 0.88rem; font-weight: 500; }
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
      min-height: 480px;
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
    
    .btn-primary {
      background: var(--primary);
      color: #0f172a;
      border: none;
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: bold;
    }
    .btn-primary:hover { filter: brightness(1.1); }
    .toolbar-actions { display: flex; gap: 8px; }
    
    /* Modal לטופס פרטי הדוח */
    .modal-overlay {
      position: fixed; inset: 0; background: rgba(0,0,0,0.6);
      display: flex; align-items: center; justify-content: center; z-index: 1000;
    }
    .modal-overlay.hidden { display: none; }
    .modal-box {
      background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px;
      padding: 20px; width: 480px; max-width: 95%; display: flex; flex-direction: column; gap: 10px;
      max-height: 85vh; overflow-y: auto;
    }
    .modal-box h3 { color: var(--primary); border-bottom: 1px solid var(--border-color); padding-bottom: 8px; }
    .modal-field { display: flex; flex-direction: column; gap: 4px; }
    .modal-field label { font-size: 0.85rem; color: var(--text-muted); }
    .modal-field input, .modal-field textarea {
      background: #0f172a; border: 1px solid var(--border-color); border-radius: 6px;
      padding: 7px 9px; color: var(--text-main); font-size: 0.9rem; font-family: inherit;
    }
    .modal-row { display: flex; gap: 10px; }
    .modal-row .modal-field { flex: 1; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 8px; }
    .btn-secondary {
      background: #0f172a; border: 1px solid var(--border-color); color: var(--text-main);
      padding: 8px 16px; border-radius: 6px; cursor: pointer;
    }
    .footer-credits {
      text-align: center; margin-top: 10px; font-size: 0.85rem; color: var(--text-muted);
    }
  </style>
</head>
<body>
<div class="app-container">
  <div class="sidebar">
    <h3>בנק אלמנטים ותשתיות</h3>
    <div id="paletteItems"></div>
  </div>
  <div class="main-area">
    <div class="toolbar">
      <div class="junction-toggle" id="junctionToggle">
        <button class="junction-toggle__btn is-active" data-shape="X">צומת X</button>
        <button class="junction-toggle__btn" data-shape="T">צומת T</button>
      </div>
      <span id="canvasCount" style="color: var(--text-muted); font-size: 0.9rem;">0 אלמנטים בסקיצה</span>
      <div class="toolbar-actions">
        <button class="btn-primary" id="openReportBtn">📄 הפקת דוח</button>
        <button class="btn-danger" id="clearCanvas">ניקוי סקיצה</button>
      </div>
    </div>
    <div class="canvas-container">
      <svg id="sketchSvg" viewBox="0 0 800 600"></svg>
    </div>
    <div class="boq-panel">
      <h3>כתב כמויות אוטומטי (לביצוע בלבד - ללא קיים)</h3>
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
<div class="footer-credits">
  כל הזכויות שמורות לנתנאל הררי | 054-5520445
</div>

<!-- Modal: פרטי הדוח ותמונות -->
<div class="modal-overlay hidden" id="reportModal">
  <div class="modal-box">
    <h3>פרטי דוח הפיקוח</h3>
    <div class="modal-field">
      <label>שם האתר / צומת</label>
      <input type="text" id="rptSite" placeholder="לדוגמה: צומת אלנבי / רוטשילד">
    </div>
    <div class="modal-row">
      <div class="modal-field">
        <label>שם המפקח</label>
        <input type="text" id="rptInspector" placeholder="שם מלא">
      </div>
      <div class="modal-field">
        <label>תאריך בדיקה</label>
        <input type="date" id="rptDate">
      </div>
    </div>
    <div class="modal-row">
      <div class="modal-field">
        <label>כבל עילי (מטרים)</label>
        <input type="number" id="rptCableOverhead" min="0" step="5" value="0">
      </div>
      <div class="modal-field">
        <label>כבל תת-קרקעי (מטרים)</label>
        <input type="number" id="rptCableUnderground" min="0" step="5" value="0">
      </div>
    </div>
    <h4 style="color: var(--primary); margin-top: 5px;">📸 העלאת תמונות לדוח</h4>
    <div class="modal-field">
      <label>צילום לפני הסדר</label>
      <input type="file" id="imgBefore" multiple accept="image/*">
    </div>
    <div class="modal-field">
      <label>צילום אחרי הסדר</label>
      <input type="file" id="imgAfter" multiple accept="image/*">
    </div>
    <div class="modal-field">
      <label>ארון רמזורים / מנגנון</label>
      <input type="file" id="imgCabinet" multiple accept="image/*">
    </div>
    <div class="modal-field">
      <label>חיבורי הארקה</label>
      <input type="file" id="imgGrounding" multiple accept="image/*">
    </div>
    <div class="modal-field">
      <label>הערות נוספות</label>
      <textarea id="rptNotes" rows="3" placeholder="פירוט תקלות, דגשים לביצוע..."></textarea>
    </div>
    <div class="modal-actions">
      <button class="btn-secondary" id="closeReportBtn">ביטול</button>
      <button class="btn-primary" id="generateReportBtn">צור דוח</button>
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
  { id: "railLight", label: "פנס רק\\"ל", icon: () => `<rect x="-7" y="-18" width="14" height="30" rx="2" fill="#2b2b2b"/><rect x="-4" y="-13" width="8" height="3" fill="#f8fafc"/><rect x="-4" y="-6.5" width="8" height="3" fill="#f8fafc"/><rect x="-4" y="0" width="8" height="3" fill="#f8fafc"/>` },
  { id: "poleConcrete", label: "עמוד בטון", icon: () => `<circle cx="0" cy="0" r="9" fill="#9aa3ad" stroke="#5c636b" stroke-width="1.5"/>` },
  { id: "poleWood", label: "עמוד עץ", icon: () => `<circle cx="0" cy="0" r="9" fill="#a9784f" stroke="#6e4c2f" stroke-width="1.5"/>` },
  { id: "camera", label: "מצלמה", icon: () => `<rect x="-9" y="-6" width="18" height="12" rx="2" fill="#2b2b2b"/><circle cx="6" cy="0" r="4" fill="#111"/><circle cx="6" cy="0" r="1.6" fill="#4fb3ff"/>` },
  { id: "sign", label: "תמרור", icon: () => `<rect x="-1.8" y="-2" width="3.6" height="16" fill="#2b2b2b"/><polygon points="0,-18 10,-8 0,2 -10,-8" fill="#fff" stroke="#d8555a" stroke-width="2.2"/>` },
  { id: "medianIsland", label: "אי תנועה (בטון)", icon: () => `<rect x="-15" y="-8" width="30" height="16" rx="8" fill="#64748b" stroke="#94a3b8" stroke-width="1.5"/>` },
  { id: "laneExtension", label: "נתיב נוסף / הרחבה", icon: () => `<rect x="-18" y="-10" width="36" height="20" fill="#334155" stroke="#475569" stroke-dasharray="2 2"/>` },
  { id: "stopLine", label: "קו עצירה לבן", icon: () => `<rect x="-16" y="-3" width="32" height="6" fill="#ffffff"/>` },
  { id: "paintedIsland", label: "שטח הפרדה מבוצע", icon: () => `<g><polygon points="-14,-8 14,-8 10,8 -10,8" fill="none" stroke="#ffffff" stroke-width="1"/><line x1="-8" y1="-8" x2="-4" y2="8" stroke="#fff"/><line x1="0" y1="-8" x2="4" y2="8" stroke="#fff"/><line x1="8" y1="-8" x2="12" y2="8" stroke="#fff"/></g>` },
  { id: "arrowStraight", label: "חץ ישר", icon: () => `<path d="M-2,8 L-2,-4 L-6,-4 L0,-14 L6,-4 L2,-4 L2,8 Z" fill="#ffffff"/>` },
  { id: "arrowLeft", label: "חץ שמאלה", icon: () => `<path d="M3,8 L3,-1 L-3,-1 L-3,-5 L-9,0 L-3,5 L-3,2 L0,2 L0,8 Z" fill="#ffffff"/>` },
  { id: "arrowRight", label: "חץ ימינה", icon: () => `<path d="M-3,8 L-3,-1 L3,-1 L3,-5 L9,0 L3,5 L3,2 L0,2 L0,8 Z" fill="#ffffff"/>` },
  { id: "arrowStraightLeft", label: "חץ ישר + שמאל", icon: () => `<path d="M-2,8 L-2,0 L-5,0 L-5,-4 L-11,1 L-5,6 L-5,3 L-2,3 L-2,-4 L-6,-4 L0,-14 L6,-4 L2,-4 L2,8 Z" fill="#ffffff"/>` },
  { id: "arrowStraightRight", label: "חץ ישר + ימין", icon: () => `<path d="M-2,8 L-2,-4 L-6,-4 L0,-14 L6,-4 L2,-4 L2,3 L5,3 L5,6 L11,1 L5,-4 L5,0 L2,0 L2,8 Z" fill="#ffffff"/>` }
];

const ACTIONS = ["add", "remove", "dismantle", "existing"];
const ACTION_LABEL = { add: "הוספה", remove: "הסרה", dismantle: "פירוק", existing: "קיים" };
const ACTION_COLOR = { add: "#2f9e8f", remove: "#d8555a", dismantle: "#d99a2b", existing: "#94a3b8" };
const state = { shape: "X", elements: [], nextId: 1 };

document.addEventListener("DOMContentLoaded", () => {
  renderPalette();
  renderJunctionBase();
  bindJunctionToggle();
  bindCanvasDropTarget();
  bindClearButton();
  bindReportModal();
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
    drawZebraCrossing(base, cx, cy - ROAD_W/2 - 25, ROAD_W, true);
    drawZebraCrossing(base, cx, cy + ROAD_W/2 + 25, ROAD_W, true);
    drawZebraCrossing(base, cx + ROAD_W/2 + 25, cy, ROAD_W, false);
    drawZebraCrossing(base, cx - ROAD_W/2 - 25, cy, ROAD_W, false);
  } else {
    base.appendChild(rect(0, cy - ROAD_W/2, 800, ROAD_W, "road"));
    base.appendChild(rect(cx - ROAD_W/2, 0, ROAD_W, cy + ROAD_W/2, "road"));
    base.appendChild(line(cx, 0, cx, cy - ROAD_W/2, "lane-dash"));
    base.appendChild(line(0, cy, cx - ROAD_W/2, cy, "lane-dash"));
    base.appendChild(line(cx + ROAD_W/2, cy, 800, cy, "lane-dash"));
    drawZebraCrossing(base, cx, cy - ROAD_W/2 - 25, ROAD_W, true);
    drawZebraCrossing(base, cx + ROAD_W/2 + 25, cy, ROAD_W, false);
    drawZebraCrossing(base, cx - ROAD_W/2 - 25, cy, ROAD_W, false);
  }
}

function drawZebraCrossing(base, x, y, roadWidth, vertical) {
  const g = document.createElementNS(SVG_NS, "g");
  g.setAttribute("class", "crosswalk-base");
  g.setAttribute("transform", `translate(${x},${y})${vertical ? " rotate(90)" : ""}`);
  const stripeW = 6, gap = 6, count = 7;
  const totalW = count * stripeW + (count - 1) * gap;
  const startX = -totalW / 2;
  for (let i = 0; i < count; i++) {
    const sx = startX + i * (stripeW + gap);
    const r = rect(sx, -roadWidth / 2 + 14, stripeW, roadWidth - 28, "");
    r.setAttribute("fill", "#dfe6ee");
    r.setAttribute("opacity", "0.85");
    g.appendChild(r);
  }
  base.appendChild(g);
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
  const el = { id: state.nextId++, type: typeId, x, y, action: "add", rotation: 0 };
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
  ring.setAttribute("cx", 0); ring.setAttribute("cy", 0); ring.setAttribute("r", 20);
  ring.setAttribute("fill", "none"); ring.setAttribute("stroke", ACTION_COLOR[elData.action]);
  ring.setAttribute("stroke-width", 2.5); ring.setAttribute("class", "action-ringui");
  if (elData.action === "existing") {
    ring.setAttribute("stroke-dasharray", "4 3");
  }
  g.appendChild(ring);
  
  // אזור לחיצה שקוף המאפשר זיהוי קל של קליקים להחלפת מצב
  const clickArea = document.createElementNS(SVG_NS, "circle");
  clickArea.setAttribute("cx", 0); clickArea.setAttribute("cy", 0); clickArea.setAttribute("r", 20);
  clickArea.setAttribute("fill", "transparent");
  clickArea.style.cursor = "pointer";
  g.appendChild(clickArea);

  const iconGroup = document.createElementNS(SVG_NS, "g");
  iconGroup.setAttribute("transform", `rotate(${elData.rotation || 0})`);
  iconGroup.style.pointerEvents = "none";
  iconGroup.innerHTML = type.icon();
  g.appendChild(iconGroup);
  
  const label = document.createElementNS(SVG_NS, "text");
  label.setAttribute("class", "el-label el-labelui"); label.setAttribute("y", 32);
  label.textContent = labelText(type, elData);
  g.appendChild(label);
  
  const delCircle = document.createElementNS(SVG_NS, "circle");
  delCircle.setAttribute("class", "el-remove el-removeui");
  delCircle.setAttribute("cx", 16); delCircle.setAttribute("cy", -22); delCircle.setAttribute("r", 7);
  const delX = document.createElementNS(SVG_NS, "text");
  delX.setAttribute("class", "el-remove-x el-removeui");
  delX.setAttribute("x", 16); delX.setAttribute("y", -19.5); delX.textContent = "×";
  g.appendChild(delCircle); g.appendChild(delX);
  
  const rotCircle = document.createElementNS(SVG_NS, "circle");
  rotCircle.setAttribute("class", "el-rotui");
  rotCircle.setAttribute("cx", -16); rotCircle.setAttribute("cy", -22); rotCircle.setAttribute("r", 7);
  rotCircle.setAttribute("fill", "var(--primary)"); rotCircle.style.cursor = "pointer";
  const rotText = document.createElementNS(SVG_NS, "text");
  rotText.setAttribute("class", "el-rotui");
  rotText.setAttribute("x", -16); rotText.setAttribute("y", -19.5);
  rotText.setAttribute("fill", "#0f172a"); rotText.setAttribute("font-size", "9");
  rotText.setAttribute("font-weight", "bold"); rotText.setAttribute("text-anchor", "middle");
  rotText.style.pointerEvents = "none";
  rotText.textContent = "↺";
  g.appendChild(rotCircle); g.appendChild(rotText);
  
  rotCircle.addEventListener("click", (e) => { e.stopPropagation(); rotateElement(elData.id); });
  delCircle.addEventListener("click", (e) => { e.stopPropagation(); removeElement(elData.id); });
  
  let dragging = false;
  let startX = 0, startY = 0;
  
  clickArea.addEventListener("pointerdown", (e) => {
    dragging = false;
    startX = e.clientX;
    startY = e.clientY;
    g.setPointerCapture(e.pointerId);
  });
  
  clickArea.addEventListener("pointermove", (e) => {
    if (Math.hypot(e.clientX - startX, e.clientY - startY) > 5) {
      dragging = true;
      const pt = clientToSvgPoint(svg, e.clientX, e.clientY);
      elData.x = pt.x; elData.y = pt.y;
      g.setAttribute("transform", `translate(${elData.x},${elData.y})`);
    }
  });
  
  clickArea.addEventListener("pointerup", (e) => {
    if (!dragging) {
      cycleAction(elData.id);
    }
    dragging = false;
  });
  
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

function rotateElement(id) {
  const el = state.elements.find(e => e.id === id);
  if (!el) return;
  el.rotation = ((el.rotation || 0) + 90) % 360;
  redrawElement(el);
}

function labelText(type, elData) {
  return `${type.label} · ${ACTION_LABEL[elData.action]}`;
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
    state.elements
      .filter(e => e.type === type.id && e.action !== "existing")
      .forEach(e => counts[e.action]++);
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

function bindReportModal() {
  const modal = document.getElementById("reportModal");
  document.getElementById("openReportBtn").addEventListener("click", () => {
    if (!document.getElementById("rptDate").value) {
      document.getElementById("rptDate").value = new Date().toISOString().slice(0, 10);
    }
    modal.classList.remove("hidden");
  });
  document.getElementById("closeReportBtn").addEventListener("click", () => modal.classList.add("hidden"));
  document.getElementById("generateReportBtn").addEventListener("click", async () => {
    await generateReport();
    modal.classList.add("hidden");
  });
}

async function readFilesAsBase64(inputEl) {
  const files = Array.from(inputEl.files || []);
  const promises = files.map(file => new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = e => resolve(e.target.result);
    reader.readAsDataURL(file);
  }));
  return Promise.all(promises);
}

async function generateReport() {
  const site = document.getElementById("rptSite").value || "—";
  const inspector = document.getElementById("rptInspector").value || "—";
  const date = document.getElementById("rptDate").value || "—";
  const cableOverhead = document.getElementById("rptCableOverhead").value || "0";
  const cableUnderground = document.getElementById("rptCableUnderground").value || "0";
  const notes = document.getElementById("rptNotes").value || "אין הערות נוספות.";

  const imgsBefore = await readFilesAsBase64(document.getElementById("imgBefore"));
  const imgsAfter = await readFilesAsBase64(document.getElementById("imgAfter"));
  const imgsCabinet = await readFilesAsBase64(document.getElementById("imgCabinet"));
  const imgsGrounding = await readFilesAsBase64(document.getElementById("imgGrounding"));

  const photoCategories = [
    { title: "צילום לפני הסדר", imgs: imgsBefore },
    { title: "צילום אחרי הסדר", imgs: imgsAfter },
    { title: "ארון רמזורים / מנגנון", imgs: imgsCabinet },
    { title: "חיבורי הארקה", imgs: imgsGrounding }
  ];

  let photosHtml = "";
  const hasPhotos = photoCategories.some(c => c.imgs.length > 0);
  if (hasPhotos) {
    photosHtml += `<h3>📸 תיעוד מצולם מהשטח</h3><div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; margin-bottom: 20px;">`;
    photoCategories.forEach(cat => {
      cat.imgs.forEach((imgSrc, idx) => {
        const labelSuffix = cat.imgs.length > 1 ? ` (${idx + 1})` : "";
        photosHtml += `
          <div style="border: 1px solid #cbd5e1; padding: 6px; border-radius: 6px; text-align: center; background: #fafafa;">
            <strong style="display:block; margin-bottom: 4px; font-size: 0.85rem; color: #334155;">${cat.title}${labelSuffix}</strong>
            <img src="${imgSrc}" style="max-width: 100%; max-height: 160px; object-fit: contain; border-radius: 4px;">
          </div>`;
      });
    });
    photosHtml += `</div>`;
  }

  const svgEl = document.getElementById("sketchSvg");
  const svgClone = svgEl.cloneNode(true);
  svgClone.querySelectorAll('.action-ringui, .el-labelui, .el-removeui, .el-rotui').forEach(el => el.remove());
  svgClone.setAttribute("xmlns", SVG_NS);
  svgClone.style.background = "#0f172a";
  svgClone.style.width = "100%";
  svgClone.style.maxWidth = "760px";
  svgClone.style.height = "auto";
  const svgMarkup = new XMLSerializer().serializeToString(svgClone);

  const boqRows = computeBoq().map(row => {
    const total = row.add + row.remove + row.dismantle;
    if (total === 0) return "";
    return `<tr>
      <td>${row.label}</td>
      <td>${row.add || "-"}</td>
      <td>${row.remove || "-"}</td>
      <td>${row.dismantle || "-"}</td>
    </tr>`;
  }).join("");

  const reportHtml = `
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
<meta charset="UTF-8">
<title>דוח פיקוח ותשתיות צומת - ${site}</title>
<style>
  * { box-sizing: border-box; font-family: system-ui, -apple-system, sans-serif; }
  body { background: #f1f5f9; color: #111827; padding: 30px; }
  .sheet { background: white; max-width: 900px; margin: 0 auto; padding: 30px 35px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
  h1 { text-align: center; border-bottom: 3px solid #0f172a; padding-bottom: 12px; margin-bottom: 20px; }
  .meta-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
  .meta-table td { padding: 6px 4px; font-size: 0.95rem; }
  .sketch-box { background: #0f172a; border-radius: 10px; padding: 10px; text-align: center; margin-bottom: 20px; }
  h3 { margin: 18px 0 8px; color: #0f172a; border-bottom: 1px solid #cbd5e1; padding-bottom: 6px; }
  table.boq { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
  table.boq th, table.boq td { border: 1px solid #cbd5e1; padding: 8px 10px; text-align: center; font-size: 0.9rem; }
  table.boq th { background: #0f172a; color: white; }
  .notes-box { background: #f8f9fa; padding: 12px; border-radius: 6px; border: 1px solid #ddd; white-space: pre-wrap; margin-bottom: 20px; }
  .print-bar { text-align: center; margin-bottom: 20px; }
  .print-bar button { background: #38bdf8; border: none; padding: 10px 22px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 1rem; }
  .credits { text-align: center; margin-top: 25px; font-size: 0.85rem; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 10px; }
  @media print { .print-bar { display: none; } body { background: white; padding: 0; } .sheet { box-shadow: none; } }
</style>
</head>
<body>
  <div class="print-bar"><button onclick="window.print()">🖨️ הדפס / שמור כ-PDF</button></div>
  <div class="sheet">
    <h1>דוח פיקוח ותשתיות צומת</h1>
    <table class="meta-table">
      <tr>
        <td><strong>אתר:</strong> ${site}</td>
        <td><strong>תאריך:</strong> ${date}</td>
        <td><strong>מפקח:</strong> ${inspector}</td>
      </tr>
    </table>
    <h3>סקיצת הצומת</h3>
    <div class="sketch-box">${svgMarkup}</div>
    <h3>כתב כמויות</h3>
    <table class="boq">
      <thead><tr><th>תיאור האלמנט</th><th>הוספה (יח')</th><th>הסרה (יח')</th><th>פירוק (יח')</th></tr></thead>
      <tbody>${boqRows || '<tr><td colspan="4">לא הוצבו אלמנטים לביצוע בסקיצה</td></tr>'}</tbody>
    </table>
    <h3>תשתיות כבלים</h3>
    <p style="margin-bottom: 15px;">כבל עילי: ${cableOverhead} מטר &nbsp;|&nbsp; כבל תת-קרקעי: ${cableUnderground} מטר</p>
    ${photosHtml}
    <h3>הערות מפקח</h3>
    <div class="notes-box">${notes}</div>
    <div class="credits">
      כל הזכויות שמורות לנתנאל הררי | 054-5520445
    </div>
  </div>
</body>
</html>`;

  const win = window.open("", "_blank");
  if (!win) { alert("הדפדפן חסם את פתיחת החלון החדש. יש לאשר חלונות קופצים עבור עמוד זה."); return; }
  win.document.open();
  win.document.write(reportHtml);
  win.document.close();
}
</script>
</body>
</html>
"""

components.html(HTML_CODE, height=980, scrolling=False)
