/* ==========================================================
   סקיצת צומת + כתב כמויות
   אפליקציה עצמאית (ללא תלות בשרת) לסימון אלמנטי תנועה
   על גבי סקיצת צומת X / T, וחישוב כתב כמויות אוטומטי.
   ========================================================== */

const SVG_NS = "http://www.w3.org/2000/svg";

/* ----------------------------------------------------------
   1. קטלוג אלמנטים
   כל אלמנט: מזהה, תווית בעברית, וציור SVG (כפונקציה שמחזירה
   מחרוזת <g> פנימית, סביב נקודת (0,0) באורך/רוחב של כ-40 יח').
   ---------------------------------------------------------- */
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

/* ----------------------------------------------------------
   2. מצב האפליקציה
   ---------------------------------------------------------- */
const state = {
  shape: "X",              // 'X' | 'T'
  elements: [],            // {id, type, x, y, action}
  nextId: 1
};

/* ----------------------------------------------------------
   3. אתחול
   ---------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("siteDate").valueAsDate = new Date();
  renderPalette();
  renderJunctionBase();
  bindJunctionToggle();
  bindCanvasDropTarget();
  bindClearButton();
  bindCableInputs();
  bindReportButton();
  renderBoqTable();
});

/* ----------------------------------------------------------
   4. בנק אלמנטים (palette)
   ---------------------------------------------------------- */
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

/* ----------------------------------------------------------
   5. בחירת צורת צומת (X / T)
   ---------------------------------------------------------- */
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

/* ----------------------------------------------------------
   6. ציור בסיס הצומת (כביש + קווי נתיב) לפי צורה
   ---------------------------------------------------------- */
function renderJunctionBase() {
  const svg = document.getElementById("sketchSvg");
  // מסירים רק את שכבת הרקע (base-layer), שומרים את האלמנטים שהוצבו
  let base = svg.querySelector("#baseLayer");
  if (base) base.remove();

  base = document.createElementNS(SVG_NS, "g");
  base.setAttribute("id", "baseLayer");
  svg.insertBefore(base, svg.firstChild);

  // רשת עזר (blueprint grid)
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
    // dashed center lines - 4 approaches
    base.appendChild(line(cx, 0, cx, cy - ROAD_W/2, "lane-dash"));
    base.appendChild(line(cx, cy + ROAD_W/2, cx, 600, "lane-dash"));
    base.appendChild(line(0, cy, cx - ROAD_W/2, cy, "lane-dash"));
    base.appendChild(line(cx + ROAD_W/2, cy, 800, cy, "lane-dash"));
  } else {
    // T: כביש אופקי מלא + כביש אנכי רק מלמעלה עד קו הכביש האופקי
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

/* ----------------------------------------------------------
   7. גרירת אלמנט מהבנק אל הסקיצה
   ---------------------------------------------------------- */
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

/* ----------------------------------------------------------
   8. ציור אלמנט שהוצב על הסקיצה + אינטראקציה
      (לחיצה = מחזור פעולה, גרירה = הזזה, X = מחיקה)
   ---------------------------------------------------------- */
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
  ring.setAttribute("class", "action-ring");
  g.appendChild(ring);

  const icon = document.createElementNS(SVG_NS, "g");
  icon.innerHTML = type.icon();
  g.appendChild(icon);

  const label = document.createElementNS(SVG_NS, "text");
  label.setAttribute("class", "el-label");
  label.setAttribute("y", 24);
  label.textContent = `${type.label} · ${ACTION_LABEL[elData.action]}`;
  g.appendChild(label);

  // כפתור מחיקה (X קטן)
  const delCircle = document.createElementNS(SVG_NS, "circle");
  delCircle.setAttribute("class", "el-remove");
  delCircle.setAttribute("cx", 16); delCircle.setAttribute("cy", -22); delCircle.setAttribute("r", 7);
  const delX = document.createElementNS(SVG_NS, "text");
  delX.setAttribute("class", "el-remove-x");
  delX.setAttribute("x", 16); delX.setAttribute("y", -19.5);
  delX.textContent = "×";
  g.appendChild(delCircle);
  g.appendChild(delX);

  delCircle.addEventListener("click", (e) => {
    e.stopPropagation();
    removeElement(elData.id);
  });
  delX.addEventListener("click", (e) => {
    e.stopPropagation();
    removeElement(elData.id);
  });

  icon.addEventListener("click", (e) => {
    e.stopPropagation();
    cycleAction(elData.id);
  });

  // גרירה להזזה בתוך הסקיצה
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

/* ----------------------------------------------------------
   9. ניקוי סקיצה
   ---------------------------------------------------------- */
function bindClearButton() {
  document.getElementById("clearCanvas").addEventListener("click", () => {
    if (state.elements.length && !confirm("לנקות את כל האלמנטים מהסקיצה?")) return;
    state.elements = [];
    document.querySelectorAll(".placed-el").forEach(n => n.remove());
    renderBoqTable();
    updateCanvasCount();
  });
}

/* ----------------------------------------------------------
   10. כתב כמויות — חישוב אוטומטי מתוך האלמנטים בסקיצה
   ---------------------------------------------------------- */
function computeBoq() {
  const rows = ELEMENT_TYPES.map(type => {
    const counts = { add: 0, remove: 0, dismantle: 0 };
    state.elements.filter(e => e.type === type.id).forEach(e => counts[e.action]++);
    return { label: type.label, ...counts };
  });
  return rows;
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

function bindCableInputs() {
  // לא נדרש לוגיקה מיוחדת — הערכים נקראים ישירות בעת הפקת הדוח
}

/* ----------------------------------------------------------
   11. הפקת דוח (תצוגת הדפסה / שמירה כ-PDF דרך הדפדפן)
   ---------------------------------------------------------- */
function bindReportButton() {
  document.getElementById("generateReport").addEventListener("click", () => {
    fillReportView();
    window.print();
  });
}

function fillReportView() {
  document.getElementById("r_siteName").textContent = document.getElementById("siteName").value || "—";
  document.getElementById("r_inspector").textContent = document.getElementById("inspectorName").value || "—";
  document.getElementById("r_date").textContent = document.getElementById("siteDate").value || "—";
  document.getElementById("r_shape").textContent = state.shape === "X" ? "צומת X (4 גישות)" : "צומת T (3 גישות)";

  // שיבוט הסקיצה כפי שהיא (כולל אלמנטים שהוצבו)
  const sketchHost = document.getElementById("r_sketch");
  sketchHost.innerHTML = "";
  const svgClone = document.getElementById("sketchSvg").cloneNode(true);
  svgClone.querySelectorAll(".el-remove, .el-remove-x").forEach(n => n.remove());
  sketchHost.appendChild(svgClone);

  // טבלת כתב כמויות
  const tbody = document.querySelector("#r_boqTable tbody");
  tbody.innerHTML = "";
  computeBoq().forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${row.label}</td><td>${row.add}</td><td>${row.remove}</td><td>${row.dismantle}</td>`;
    tbody.appendChild(tr);
  });

  document.getElementById("r_cableOverhead").textContent =
    (document.getElementById("cableOverhead").value || "0") + " מטר";
  document.getElementById("r_cableUnderground").textContent =
    (document.getElementById("cableUnderground").value || "0") + " מטר";

  const notes = document.getElementById("boqNotes").value.trim();
  const notesSection = document.getElementById("r_notesSection");
  if (notes) {
    document.getElementById("r_notes").textContent = notes;
    notesSection.style.display = "";
  } else {
    notesSection.style.display = "none";
  }
}
