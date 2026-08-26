import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="סקיצת צומת + כתב כמויות - פיקוח רק\"ל")

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
  .app-container {
    display: flex;
    gap: 15px;
  }
  .palette {
    width: 240px;
    background: #fff;
    padding: 12px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    max-height: 800px;
    overflow-y: auto;
  }
  .palette h3, .palette h4 { margin: 8px 0 4px 0; font-size: 14px; color: #1e293b; border-bottom: 1px solid #e2e8f0; pb: 4px; }
  .palette-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px;
    margin-bottom: 6px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    cursor: grab;
    user-select: none;
    font-size: 13px;
  }
  .palette-item svg { width: 26px; height: 26px; flex-shrink: 0; }
  .canvas-area {
    flex: 1;
    background: #fff;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  .controls {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
    align-items: center;
    background: #fff;
    padding: 10px 15px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  }
  .junction-toggle__btn {
    padding: 6px 14px;
    border: 1px solid #cbd5e1;
    background: #fff;
    cursor: pointer;
    border-radius: 4px;
    font-weight: bold;
  }
  .junction-toggle__btn.is-active {
    background: #2563eb;
    color: white;
    border-color: #2563eb;
  }
  .btn-action {
    padding: 6px 12px;
    border: 1px solid #cbd5e1;
    background: #f8fafc;
    cursor: pointer;
    border-radius: 4px;
    font-weight: 500;
  }
  .btn-primary { background: #16a34a; color: white; border-color: #16a34a; }
  
  svg#sketchSvg {
    width: 100%;
    height: 520px;
    background-color: #334155;
    border: 1px solid #94a3b8;
    border-radius: 6px;
  }
  .grid-line { stroke: #475569; stroke-width: 0.8; stroke-dasharray: 2 4; }
  .road { fill: #1e293b; }
  .lane-dash { stroke: #f8fafc; stroke-width: 2; stroke-dasharray: 8 8; }
  .placed-el { cursor: move; }
  .el-label { font-size: 10px; fill: #ffffff; text-anchor: middle; font-weight: bold; text-shadow: 0 0 3px #000; }
  .el-remove { fill: #ef4444; cursor: pointer; }
  .el-remove-x { fill: white; font-size: 11px; font-weight: bold; text-anchor: middle; cursor: pointer; pointer-events: none; }
  
  .boq-section, .photos-section {
    margin-top: 15px;
    background: #fff;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }
  th, td { border: 1px solid #cbd5e1; padding: 8px; text-align: center; }
  th { background-color: #f1f5f9; color: #0f172a; }
  .zero { color: #94a3b8; }
  
  .photo-inputs {
    display: flex;
    gap: 20px;
    margin-top: 10px;
  }
  .photo-box {
    flex: 1;
    border: 2px dashed #cbd5e1;
    padding: 12px;
    border-radius: 6px;
    text-align: center;
    background: #f8fafc;
  }
  .photo-box img {
    max-width: 100%;
    max-height: 180px;
    margin-top: 8px;
    border-radius: 4px;
    display: none;
  }
  .cables-inputs {
    display: flex;
    gap: 15px;
    margin-top: 10px;
    background: #f8fafc;
    padding: 10px;
    border-radius: 6px;
  }
  .cables-inputs label { font-size: 13px; font-weight: bold; }
  .cables-inputs input { width: 80px; padding: 4px; text-align: center; }

  @media print {
    .palette, .controls, .no-print, input[type="file"] { display: none !important; }
    .canvas-area, .boq-section, .photos-section { box-shadow: none; border: none; padding: 0; }
    body { background: white; }
    svg#sketchSvg { height: 400px; }
  }
</style>
</head>
<body>

<div class="controls">
  <div id="junctionToggle">
    <button class="junction-toggle__btn is-active" data-shape="X">צומת X (4 גישות)</button>
    <button class="junction-toggle__btn" data-shape="T">צומת T (3 גישות)</button>
  </div>
  <div id="canvasCount" style="font-weight: bold; color: #475569;">0 אלמנטים בסקיצה</div>
  <div>
    <button id="clearCanvas" class="btn-action">ניקוי סקיצה</button>
    <button id="generateReport" class="btn-action btn-primary">הדפסת דוח / יצוא ל-PDF</button>
  </div>
</div>

<div class="app-container">
  <div class="palette" id="paletteItems"></div>
  <div class="canvas-area">
    <svg id="sketchSvg" viewBox="0 0 800 600"></svg>
  </div>
</div>

<div class="boq-section">
  <h3>כתב כמויות וחישוב עבודות צומת</h3>
  <div class="cables-inputs">
    <div>
      <label>כבל רמזורים עליון/עילי (מטרים):</label>
      <input type="number" id="cableOverhead" value="0" min="0">
    </div>
    <div>
      <label>כבל רמזורים תת-קרקעי (מטרים):</label>
      <input type="number" id="cableUnderground" value="0" min="0">
    </div>
  </div>
  <table id="boqTable">
    <thead>
      <tr>
        <th>אלמנט</th>
        <th>קיים בצומת</th>
        <th>הוספה (חדש)</th>
        <th>פירוק</th>
        <th>הסרה</th>
      </tr>
    </thead>
    <tbody></tbody>
  </table>
</div>

<div class="photos-section">
  <h3>תיעוד מצולם מהשטח (לדוח)</h3>
  <div class="photo-inputs">
    <div class="photo-box">
      <label><b>תמונת ארון רמזורים</b></label><br>
      <input type="file" id="cabinetPhotoInput" accept="image/*" onchange="previewImage(this, 'cabinetImg')">
      <br><img id="cabinetImg" src="" alt="תמונת ארון רמזורים">
    </div>
    <div class="photo-box">
      <label><b>תמונת חיבורי הארקה</b></label><br>
      <input type="file" id="groundingPhotoInput" accept="image/*" onchange="previewImage(this, 'groundingImg')">
      <br><img id="groundingImg" src="" alt="תמונת חיבורי הארקה">
    </div>
  </div>
</div>

<script>
const SVG_NS = "http://www.w3.org/2000/svg";

const ELEMENT_TYPES = [
  // רמזורים
  {
    category: "רמזורים",
    id: "trafficLight",
    label: "רמזור תנועה",
    icon: () => `
      <rect x="-6" y="-16" width="12" height="30" rx="2" fill="#1e293b" stroke="#fff" stroke-width="0.5"/>
      <circle cx="0" cy="-10" r="3.2" fill="#ef4444"/>
      <circle cx="0" cy="-2"  r="3.2" fill="#f59e0b"/>
      <circle cx="0" cy="6"   r="3.2" fill="#10b981"/>
    `
  },
  {
    category: "רמזורים",
    id: "pedLight",
    label: "רמזור הולכי רגל",
    icon: () => `
      <rect x="-6" y="-13" width="12" height="24" rx="2" fill="#1e293b" stroke="#fff" stroke-width="0.5"/>
      <circle cx="0" cy="-6" r="3.4" fill="#ef4444"/>
      <circle cx="0" cy="3"  r="3.4" fill="#10b981"/>
    `
  },
  {
    category: "רמזורים",
    id: "bikeLight",
    label: "רמזור אופניים",
    icon: () => `
      <rect x="-6" y="-13" width="12" height="24" rx="2" fill="#1e293b" stroke="#60a5fa" stroke-width="1"/>
      <circle cx="0" cy="-6" r="3" fill="#ef4444"/>
      <circle cx="0" cy="3"  r="3" fill="#10b981"/>
      <path d="M-2,3 L2,3" stroke="#fff" stroke-width="0.8"/>
    `
  },
  {
    category: "רמזורים",
    id: "lrtLight",
    label: "רמזור רק\"ל",
    icon: () => `
      <rect x="-7" y="-14" width="14" height="26" rx="2" fill="#0f172a" stroke="#f59e0b" stroke-width="1.2"/>
      <line x1="-3" y1="-7" x2="3" y2="-7" stroke="#white" stroke-width="2"/>
      <circle cx="0" cy="0" r="2.5" fill="#white"/>
      <line x1="0" y1="4" x2="0" y2="10" stroke="#white" stroke-width="2"/>
    `
  },
  {
    category: "רמזורים",
    id: "blinker",
    label: "פנס מהבהב",
    icon: () => `
      <rect x="-2.5" y="-12" width="5" height="14" fill="#1e293b"/>
      <circle cx="0" cy="-14" r="5" fill="#f59e0b"/>
    `
  },
  // סימוני כביש וחצים
  {
    category: "סימוני כביש",
    id: "arrowStraight",
    label: "חץ ישר",
    icon: () => `
      <path d="M0,10 L0,-10 M-5,-4 L0,-12 L5,-4" stroke="#ffffff" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    `
  },
  {
    category: "סימוני כביש",
    id: "arrowLeft",
    label: "חץ שמאלה",
    icon: () => `
      <path d="M4,10 L4,-1 C4,-5 -1,-8 -8,-8 M-4,-13 L-10,-8 L-4,-3" stroke="#ffffff" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    `
  },
  {
    category: "סימוני כביש",
    id: "arrowRight",
    label: "חץ ימינה",
    icon: () => `
      <path d="M-4,10 L-4,-1 C-4,-5 1,-8 8,-8 M4,-13 L10,-8 L4,-3" stroke="#ffffff" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    `
  },
  {
    category: "סימוני כביש",
    id: "arrowStraightLeft",
    label: "חץ ישר+שמאלה",
    icon: () => `
      <path d="M2,10 L2,-10 M-3,-4 L2,-12 L7,-4" stroke="#ffffff" stroke-width="2" fill="none"/>
      <path d="M2,2 C2,-3 -2,-5 -8,-5 M-4,-9 L-9,-5 L-4,-1" stroke="#ffffff" stroke-width="2" fill="none"/>
    `
  },
  {
    category: "סימוני כביש",
    id: "arrowUturn",
    label: "חץ פרסה",
    icon: () => `
      <path d="M5,10 L5,-2 C5,-8 -5,-8 -5,-2 L-5,4 M-9,0 L-5,5 L-1,0" stroke="#ffffff" stroke-width="2" fill="none"/>
    `
  },
  {
    category: "סימוני כביש",
    id: "crosswalk",
    label: "מעבר חציה",
    icon: () => `
      <g>
        <rect x="-14" y="-7" width="28" height="14" fill="none"/>
        ${[-10,-3,4,11].map(x=>`<rect x="${x-2}" y="-7" width="4" height="14" fill="#ffffff"/>`).join("")}
      </g>
    `
  },
  // תשתיות ועמודים
  {
    category: "תשתיות ועמודים",
    id: "poleConcrete",
    label: "עמוד בטון",
    icon: () => `
      <circle cx="0" cy="0" r="8" fill="#94a3b8" stroke="#334155" stroke-width="1.5"/>
    `
  },
  {
    category: "תשתיות ועמודים",
    id: "poleWood",
    label: "עמוד עץ",
    icon: () => `
      <circle cx="0" cy="0" r="8" fill="#b45309" stroke="#451a03" stroke-width="1.5"/>
    `
  },
  {
    category: "תשתיות ועמודים",
    id: "camera",
    label: "מצלמה",
    icon: () => `
      <rect x="-8" y="-5" width="16" height="10" rx="2" fill="#0f172a"/>
      <circle cx="4" cy="0" r="3" fill="#38bdf8"/>
    `
  },
  {
    category: "תשתיות ועמודים",
    id: "sign",
    label: "תמרור",
    icon: () => `
      <polygon points="0,-14 8,-6 0,2 -8,-6" fill="#fff" stroke="#ef4444" stroke-width="2"/>
    `
  }
];

const ACTIONS = ["existing", "add", "dismantle", "remove"];
const ACTION_LABEL = { existing: "קיים", add: "הוספה", dismantle: "פירוק", remove: "הסרה" };
const ACTION_COLOR = { existing: "#94a3b8", add: "#10b981", dismantle: "#f59e0b", remove: "#ef4444" };

const state = {
  shape: "X",
  elements: [],
  nextId: 1
};

document.addEventListener("DOMContentLoaded", () => {
  renderPalette();
  initJunctionWithDefaults();
  bindJunctionToggle();
  bindCanvasDropTarget();
  bindClearButton();
  bindReportButton();
  renderBoqTable();
});

function renderPalette() {
  const wrap = document.getElementById("paletteItems");
  wrap.innerHTML = "";

  const categories = [...new Set(ELEMENT_TYPES.map(t => t.category))];

  categories.forEach(cat => {
    const catTitle = document.createElement("h4");
    catTitle.textContent = cat;
    wrap.appendChild(catTitle);

    ELEMENT_TYPES.filter(t => t.category === cat).forEach(type => {
      const item = document.createElement("div");
      item.className = "palette-item";
      item.draggable = true;
      item.dataset.type = type.id;
      item.innerHTML = `
        <svg viewBox="-16 -20 32 32">${type.icon()}</svg>
        <span>${type.label}</span>
      `;
      item.addEventListener("dragstart", e => {
        e.dataTransfer.setData("text/plain", type.id);
        e.dataTransfer.effectAllowed = "copy";
      });
      wrap.appendChild(item);
    });
  });
}

function bindJunctionToggle() {
  const toggle = document.getElementById("junctionToggle");
  toggle.querySelectorAll(".junction-toggle__btn").forEach(btn => {
    btn.addEventListener("click", () => {
      toggle.querySelectorAll(".junction-toggle__btn").forEach(b => b.classList.remove("is-active"));
      btn.classList.add("is-active");
      state.shape = btn.dataset.shape;
      initJunctionWithDefaults();
    });
  });
}

function initJunctionWithDefaults() {
  state.elements = [];
  document.querySelectorAll(".placed-el").forEach(n => n.remove());
  renderJunctionBase();

  const cx = 400, cy = 300, offset = 110;
  
  // הוספת מעברי חצייה מובנים כברירת מחדל במצב "קיים"
  const defaultCrosswalks = [
    { x: cx, y: cy - offset, action: "existing" },
    { x: cx, y: cy + offset, action: "existing" },
    { x: cx - offset, y: cy, action: "existing" },
    { x: cx + offset, y: cy, action: "existing" }
  ];

  if (state.shape === "T") {
    defaultCrosswalks.splice(1, 1); // ללא מעבר דרומי ב-T
  }

  defaultCrosswalks.forEach(cw => {
    addElement("crosswalk", cw.x, cw.y, cw.action);
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
    addElement(type.id, pt.x, pt.y, "add");
  });
}

function clientToSvgPoint(svg, clientX, clientY) {
  const p = svg.createSVGPoint();
  p.x = clientX; p.y = clientY;
  const ctm = svg.getScreenCTM().inverse();
  return p.matrixTransform(ctm);
}

function addElement(typeId, x, y, action = "add") {
  const el = { id: state.nextId++, type: typeId, x, y, action };
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
  ring.setAttribute("cx", 0); ring.setAttribute("cy", 0);
  ring.setAttribute("r", 18);
  ring.setAttribute("fill", "none");
  ring.setAttribute("stroke", ACTION_COLOR[elData.action]);
  ring.setAttribute("stroke-width", 2.5);
  g.appendChild(ring);

  const icon = document.createElementNS(SVG_NS, "g");
  icon.innerHTML = type.icon();
  g.appendChild(icon);

  const label = document.createElementNS(SVG_NS, "text");
  label.setAttribute("class", "el-label");
  label.setAttribute("y", 26);
  label.textContent = `${type.label} (${ACTION_LABEL[elData.action]})`;
  g.appendChild(label);

  const delCircle = document.createElementNS(SVG_NS, "circle");
  delCircle.setAttribute("class", "el-remove");
  delCircle.setAttribute("cx", 14); delCircle.setAttribute("cy", -14); delCircle.setAttribute("r", 6.5);
  
  const delX = document.createElementNS(SVG_NS, "text");
  delX.setAttribute("class", "el-remove-x");
  delX.setAttribute("x", 14); delX.setAttribute("y", -11.5);
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
    if (confirm("האם לנקות את כל הסקיצה ולאפס את הצומת?")) {
      initJunctionWithDefaults();
    }
  });
}

function computeBoq() {
  return ELEMENT_TYPES.map(type => {
    const counts = { existing: 0, add: 0, dismantle: 0, remove: 0 };
    state.elements.filter(e => e.type === type.id).forEach(e => counts[e.action]++);
    return { label: type.label, ...counts };
  });
}

function renderBoqTable() {
  const tbody = document.querySelector("#boqTable tbody");
  tbody.innerHTML = "";
  computeBoq().forEach(row => {
    const total = row.existing + row.add + row.dismantle + row.remove;
    if (total === 0) return; // מציגים בטבלה רק אלמנטים שקיימים בצומת

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td style="text-align: right; font-weight: bold;">${row.label}</td>
      <td class="${row.existing ? "" : "zero"}">${row.existing}</td>
      <td class="${row.add ? "" : "zero"}" style="color: #10b981; font-weight: bold;">${row.add}</td>
      <td class="${row.dismantle ? "" : "zero"}" style="color: #f59e0b;">${row.dismantle}</td>
      <td class="${row.remove ? "" : "zero"}" style="color: #ef4444;">${row.remove}</td>
    `;
    tbody.appendChild(tr);
  });
}

function previewImage(input, imgId) {
  const file = input.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      const img = document.getElementById(imgId);
      img.src = e.target.result;
      img.style.display = "block";
    }
    reader.readAsDataURL(file);
  }
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

components.html(html_code, height=1100, scrolling=True)
