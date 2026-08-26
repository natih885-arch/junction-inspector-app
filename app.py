import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="סקיצת צומת + כתב כמויות")

html_code = """
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; }
  body {
    font-family: system-ui, -apple-system, sans-serif;
    margin: 0;
    padding: 15px;
    background-color: #f4f6f8;
    color: #333;
  }
  
  /* טופס פרטי אתר */
  .site-details {
    background: #fff;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 15px;
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
  }
  .form-group {
    display: flex;
    flex-direction: column;
    gap: 5px;
    flex: 1;
    min-width: 180px;
  }
  .form-group label { font-size: 13px; font-weight: bold; }
  .form-group input { padding: 6px 10px; border: 1px solid #ccc; border-radius: 4px; }

  .controls {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
    align-items: center;
    background: #fff;
    padding: 10px 15px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  .junction-toggle__btn {
    padding: 6px 16px;
    border: 1px solid #ccc;
    background: #fff;
    cursor: pointer;
    border-radius: 4px;
    font-weight: bold;
  }
  .junction-toggle__btn.is-active {
    background: #007bff;
    color: white;
    border-color: #007bff;
  }
  .btn-action {
    padding: 6px 14px;
    border: 1px solid #ccc;
    background: #fff;
    cursor: pointer;
    border-radius: 4px;
  }
  .btn-primary { background: #28a745; color: white; border-color: #28a745; font-weight: bold; }

  .app-container {
    display: flex;
    gap: 15px;
  }
  .palette {
    width: 220px;
    background: #fff;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    max-height: 600px;
    overflow-y: auto;
  }
  .palette h3 { margin-top: 0; margin-bottom: 10px; font-size: 16px; }
  .palette-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px;
    margin-bottom: 8px;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    cursor: grab;
    user-select: none;
    font-size: 13px;
  }
  .palette-item svg { width: 30px; height: 30px; flex-shrink: 0; }
  
  .canvas-area {
    flex: 1;
    background: #fff;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  svg#sketchSvg {
    width: 100%;
    height: 520px;
    background-color: #eef2f5;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
  .grid-line { stroke: #e0e0e0; stroke-width: 1; }
  .road { fill: #4a5568; }
  .lane-dash { stroke: #ffffff; stroke-width: 2; stroke-dasharray: 8 8; }
  .placed-el { cursor: move; }
  .el-label { font-size: 11px; fill: #1a202c; text-anchor: middle; font-weight: bold; }
  .el-remove { fill: #ef4444; cursor: pointer; }
  .el-remove-x { fill: white; font-size: 12px; font-weight: bold; text-anchor: middle; cursor: pointer; pointer-events: none; }
  
  .boq-section {
    margin-top: 15px;
    background: #fff;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  .boq-section h3 { margin-top: 0; }
  table { width: 100%; border-collapse: collapse; margin-top: 10px; }
  th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
  th { background-color: #f2f2f2; }
  .zero { color: #ccc; }
  
  .cables-inputs {
    display: flex;
    gap: 20px;
    margin-bottom: 15px;
    background: #f8f9fa;
    padding: 10px;
    border-radius: 6px;
  }

  @media print {
    .palette, .controls, .no-print { display: none !important; }
    .canvas-area, .boq-section, .site-details { box-shadow: none; border: none; }
    body { background: white; }
  }
</style>
</head>
<body>

<div class="site-details">
  <div class="form-group">
    <label>שם האתר / צומת:</label>
    <input type="text" id="siteName" placeholder="לדוגמה: צומת הרצל-ז'בוטינסקי">
  </div>
  <div class="form-group">
    <label>שם המפקח:</label>
    <input type="text" id="inspectorName" placeholder="שם המפקח">
  </div>
  <div class="form-group">
    <label>תאריך:</label>
    <input type="date" id="siteDate">
  </div>
</div>

<div class="controls">
  <div id="junctionToggle">
    <button class="junction-toggle__btn is-active" data-shape="X">צומת X</button>
    <button class="junction-toggle__btn" data-shape="T">צומת T</button>
  </div>
  <div id="canvasCount">0 אלמנטים בסקיצה</div>
  <div>
    <button id="clearCanvas" class="btn-action">ניקוי סקיצה</button>
    <button id="generateReport" class="btn-action btn-primary">הדפסת דוח / PDF</button>
  </div>
</div>

<div class="app-container">
  <div class="palette" id="paletteItems"></div>
  <div class="canvas-area">
    <svg id="sketchSvg" viewBox="0 0 800 600"></svg>
  </div>
</div>

<div class="boq-section">
  <h3>כתב כמויות</h3>
  <div class="cables-inputs">
    <div class="form-group">
      <label>כבל עילי (מטרים):</label>
      <input type="number" id="cableOverhead" value="0">
    </div>
    <div class="form-group">
      <label>כבל תת-קרקעי (מטרים):</label>
      <input type="number" id="cableUnderground" value="0">
    </div>
    <div class="form-group" style="flex: 2;">
      <label>הערות מפקח:</label>
      <input type="text" id="boqNotes" placeholder="הערות נוספות לכתב הכמויות...">
    </div>
  </div>
  <table id="boqTable">
    <thead>
      <tr>
        <th>אלמנט</th>
        <th>הוספה</th>
        <th>הסרה</th>
        <th>פירוק</th>
      </tr>
    </thead>
    <tbody></tbody>
  </table>
</div>

<script>
const SVG_NS = "http://www.w3.org/2000/svg";

const ELEMENT_TYPES = [
  {
    id: "trafficLight",
    label: "רמזור תנועה",
    icon: () => `
      <rect x="-6" y="-16" width="12" height="30" rx="2" fill="#2b2b2b"/>
      <circle cx="0" cy="-10" r="3.2" fill="#d8555a"/>
      <circle cx="0" cy="-2"  r="3.2" fill="#d99a2b"/>
      <circle cx="0" cy="6"   r="3.2" fill="#2f9e8f"/>
    `
  },
  {
    id: "pedLight",
    label: "רמזור הולכי רגל",
    icon: () => `
      <rect x="-6" y="-13" width="12" height="24" rx="2" fill="#2b2b2b"/>
      <circle cx="0" cy="-6" r="3.4" fill="#d8555a"/>
      <circle cx="0" cy="3"  r="3.4" fill="#2f9e8f"/>
    `
  },
  {
    id: "bikeLight",
    label: "רמזור אופניים",
    icon: () => `
      <rect x="-6" y="-13" width="12" height="24" rx="2" fill="#2b2b2b" stroke="#3b82f6" stroke-width="1"/>
      <circle cx="0" cy="-6" r="3" fill="#d8555a"/>
      <circle cx="0" cy="3"  r="3" fill="#2f9e8f"/>
    `
  },
  {
    id: "lrtLight",
    label: "רמזור רק\"ל",
    icon: () => `
      <rect x="-7" y="-14" width="14" height="26" rx="2" fill="#111827" stroke="#f59e0b" stroke-width="1"/>
      <line x1="-3" y1="-7" x2="3" y2="-7" stroke="#fff" stroke-width="2"/>
      <circle cx="0" cy="0" r="2" fill="#fff"/>
      <line x1="0" y1="4" x2="0" y2="9" stroke="#fff" stroke-width="2"/>
    `
  },
  {
    id: "arrowStraight",
    label: "חץ ישר",
    icon: () => `
      <path d="M0,8 L0,-8 M-4,-2 L0,-9 L4,-2" stroke="#2b2b2b" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    `
  },
  {
    id: "arrowLeft",
    label: "חץ שמאלה",
    icon: () => `
      <path d="M3,8 L3,-1 C3,-4 -1,-7 -7,-7 M-3,-11 L-8,-7 L-3,-3" stroke="#2b2b2b" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    `
  },
  {
    id: "arrowRight",
    label: "חץ ימינה",
    icon: () => `
      <path d="M-3,8 L-3,-1 C-3,-4 1,-7 7,-7 M3,-11 L8,-7 L3,-3" stroke="#2b2b2b" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    `
  },
  {
    id: "arrowStraightLeft",
    label: "חץ ישר+שמאלה",
    icon: () => `
      <path d="M2,8 L2,-8 M-2,-2 L2,-9 L6,-2" stroke="#2b2b2b" stroke-width="2" fill="none"/>
      <path d="M2,1 C2,-3 -2,-4 -7,-4 M-3,-7 L-7,-4 L-3,-1" stroke="#2b2b2b" stroke-width="2" fill="none"/>
    `
  },
  {
    id: "arrowUturn",
    label: "חץ פרסה",
    icon: () => `
      <path d="M4,8 L4,-2 C4,-7 -4,-7 -4,-2 L-4,3 M-7,0 L-4,4 L-1,0" stroke="#2b2b2b" stroke-width="2" fill="none"/>
    `
  },
  {
    id: "crosswalk",
    label: "מעבר חציה",
    icon: () => `
      <g>
        <rect x="-16" y="-8" width="32" height="16" fill="none"/>
        ${[-12,-4,4,12].map(x=>`<rect x="${x-2.5}" y="-8" width="5" height="16" fill="#e9edf3"/>`).join("")}
      </g>
    `
  },
  {
    id: "blinker",
    label: "מהבהב",
    icon: () => `
      <rect x="-2.5" y="-14" width="5" height="16" fill="#2b2b2b"/>
      <circle cx="0" cy="-16" r="5.5" fill="#d99a2b"/>
      <line x1="0" y1="-24" x2="0" y2="-20" stroke="#d99a2b" stroke-width="2"/>
      <line x1="-7" y1="-21" x2="-4.5" y2="-19" stroke="#d99a2b" stroke-width="2"/>
      <line x1="7" y1="-21" x2="4.5" y2="-19" stroke="#d99a2b" stroke-width="2"/>
    `
  },
  {
    id: "poleConcrete",
    label: "עמוד בטון",
    icon: () => `
      <circle cx="0" cy="0" r="9" fill="#9aa3ad" stroke="#5c636b" stroke-width="1.5"/>
    `
  },
  {
    id: "poleWood",
    label: "עמוד עץ",
    icon: () => `
      <circle cx="0" cy="0" r="9" fill="#a9784f" stroke="#6e4c2f" stroke-width="1.5"/>
    `
  },
  {
    id: "camera",
    label: "מצלמה",
    icon: () => `
      <rect x="-9" y="-6" width="18" height="12" rx="2" fill="#2b2b2b"/>
      <circle cx="6" cy="0" r="4" fill="#111"/>
      <circle cx="6" cy="0" r="1.6" fill="#4fb3ff"/>
    `
  },
  {
    id: "sign",
    label: "תמרור",
    icon: () => `
      <rect x="-1.8" y="-2" width="3.6" height="16" fill="#2b2b2b"/>
      <polygon points="0,-18 10,-8 0,2 -10,-8" fill="#fff" stroke="#d8555a" stroke-width="2.2"/>
    `
  }
];

const ACTIONS = ["add", "remove", "dismantle"];
const ACTION_LABEL = { add: "הוספה", remove: "הסרה", dismantle: "פירוק" };
const ACTION_COLOR = { add: "#2f9e8f", remove: "#d8555a", dismantle: "#d99a2b" };

const state = {
  shape: "X",
  elements: [],
  nextId: 1
};

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("siteDate").valueAsDate = new Date();
  renderPalette();
  renderJunctionBase();
  bindJunctionToggle();
  bindCanvasDropTarget();
  bindClearButton();
  bindReportButton();
  renderBoqTable();
});

function renderPalette() {
  const wrap = document.getElementById("paletteItems");
  wrap.innerHTML = "";
  const heading = document.createElement("h3");
  heading.textContent = "אלמנטים";
  wrap.appendChild(heading);

  ELEMENT_TYPES.forEach(type => {
    const item = document.createElement("div");
    item.className = "palette-item";
    item.draggable = true;
    item.dataset.type = type.id;
    item.innerHTML = `
      <svg viewBox="-20 -28 40 40">${type.icon()}</svg>
      <span>${type.label}</span>
    `;
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

  for (let x = 0; x <= 800; x += 40) {
    base.appendChild(line(x, 0, x, 600, "grid-line"));
  }
  for (let y = 0; y <= 600; y += 40) {
    base.appendChild(line(0, y, 800, y, "grid-line"));
  }

  const ROAD_W = 140;
  const cx = 400, cy = 300;

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
  el.setAttribute("class",cls);
  return el;
}
function rect(x,y,w,h,cls){
  const el = document.createElementNS(SVG_NS,"rect");
  el.setAttribute("x",x); el.setAttribute("y",y);
  el.setAttribute("width",w); el.setAttribute("height",h);
  el.setAttribute("class",cls);
  return el;
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
  ring.setAttribute("cx", 0); ring.setAttribute("cy", -8);
  ring.setAttribute("r", 20);
  ring.setAttribute("fill", "none");
  ring.setAttribute("stroke", ACTION_COLOR[elData.action]);
  ring.setAttribute("stroke-width", 2.5);
  g.appendChild(ring);

  const icon = document.createElementNS(SVG_NS, "g");
  icon.innerHTML = type.icon();
  g.appendChild(icon);

  const label = document.createElementNS(SVG_NS, "text");
  label.setAttribute("class", "el-label");
  label.setAttribute("y", 24);
  label.textContent = `${type.label} · ${ACTION_LABEL[elData.action]}`;
  g.appendChild(label);

  const delCircle = document.createElementNS(SVG_NS, "circle");
  delCircle.setAttribute("class", "el-remove");
  delCircle.setAttribute("cx", 16); delCircle.setAttribute("cy", -22); delCircle.setAttribute("r", 7);
  
  const delX = document.createElementNS(SVG_NS, "text");
  delX.setAttribute("class", "el-remove-x");
  delX.setAttribute("x", 16); delX.setAttribute("y", -18.5);
  delX.textContent = "×";
  
  g.appendChild(delCircle);
  g.appendChild(delX);

  delCircle.addEventListener("click", (e) => { e.stopPropagation(); removeElement(elData.id); });
  delX.addEventListener("click", (e) => { e.stopPropagation(); removeElement(elData.id); });

  icon.addEventListener("click", (e) => {
    e.stopPropagation();
    cycleAction(elData.id);
  });

  let dragging = false;
  g.addEventListener("pointerdown", (e) => {
    if (e.target === delCircle || e.target === delX) return;
    dragging = true;
    g.setPointerCapture(e.pointerId);
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
    if (total === 0) tr.style.opacity = "0.55";
    tbody.appendChild(tr);
  });
}

function bindReportButton() {
  document.getElementById("generateReport").addEventListener("click", () => {
    window.print();
  });
}
</script>
</body>
</html>
"""

components.html(html_code, height=1000, scrolling=True)
