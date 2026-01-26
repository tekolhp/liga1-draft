const SHEET_NAME = "Sheet1";
const TEAM_COLUMN = 6; // Coluna F (Time)
const CATEGORY_COLUMN = 4; // Coluna D (Categoria)
const ORDER_SHEET = "Sheet2"; // Coluna A = ordem do shuffle

// Draft state cells in Sheet2
const STATE_PICK_CELL = "G1";
const STATE_QUEUE_CELL = "H1";
const ACTIVE_CONTROLLER_CELL = "I1"; // Novo: ID do controlador ativo

function doPost(e) {
  try {
    const body = e.postData && e.postData.contents ? JSON.parse(e.postData.contents) : {};
    const action = (body.action || "").toString();

    if (action === "clear_assignments") {
      clearAssignments();
      return json({ ok: true, action: "clear_assignments" });
    }

    if (action === "clear_assignments_soft") {
      clearAssignmentsSoft();
      return json({ ok: true, action: "clear_assignments_soft" });
    }

    if (action === "save_order") {
      const order = Array.isArray(body.order) ? body.order : [];
      saveOrderToSheet(order);
      return json({ ok: true, action: "save_order", count: order.length });
    }

    if (action === "save_state") {
      saveDraftState(body.pickIndex, body.queue);
      return json({ ok: true, action: "save_state" });
    }

    if (action === "set_controller") {
      const controllerId = (body.controllerId || "").toString();
      setActiveController(controllerId);
      return json({ ok: true, action: "set_controller", controllerId });
    }

    const name = (body.name || "").toString().trim();
    const team = (body.team || "").toString().trim();

    if (!name || !team) {
      return json({ ok: false, error: "Missing name or team" });
    }

    const updated = upsertTeamByName(name, team);
    return json({ ok: true, updated });
  } catch (err) {
    return json({ ok: false, error: err.message });
  }
}

function doGet(e) {
  const action = (e.parameter && e.parameter.action) ? e.parameter.action : "";

  if (action === "read_csv") {
    const csv = getSheetAsCsv();
    return ContentService.createTextOutput(csv)
      .setMimeType(ContentService.MimeType.CSV);
  }

  if (action === "read_order") {
    const order = readOrderFromSheet();
    return json({ ok: true, order });
  }

  if (action === "read_state") {
    const state = readDraftState();
    return json({ ok: true, state });
  }

  if (action === "read_controller") {
    const controllerId = getActiveController();
    return json({ ok: true, controllerId });
  }

  return ContentService.createTextOutput("ok");
}

function saveOrderToSheet(order) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(ORDER_SHEET);
  if (!sheet) sheet = ss.insertSheet(ORDER_SHEET);

  sheet.clearContents();
  if (order.length === 0) return;

  const values = order.map((name) => [name]);
  sheet.getRange(1, 1, values.length, 1).setValues(values);
}

function readOrderFromSheet() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(ORDER_SHEET);
  if (!sheet) return [];
  const lastRow = sheet.getLastRow();
  if (lastRow < 1) return [];
  return sheet.getRange(1, 1, lastRow, 1).getValues()
    .map((r) => (r[0] || "").toString().trim())
    .filter(Boolean);
}

function saveDraftState(pickIndex, queue) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(ORDER_SHEET);
  if (!sheet) return;
  sheet.getRange(STATE_PICK_CELL).setValue(pickIndex || 0);
  sheet.getRange(STATE_QUEUE_CELL).setValue(JSON.stringify(queue || []));
}

function readDraftState() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(ORDER_SHEET);
  if (!sheet) return { pickIndex: 0, queue: "[]" };
  return {
    pickIndex: sheet.getRange(STATE_PICK_CELL).getValue(),
    queue: sheet.getRange(STATE_QUEUE_CELL).getValue()
  };
}

function setActiveController(controllerId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(ORDER_SHEET);
  if (!sheet) sheet = ss.insertSheet(ORDER_SHEET);

  sheet.getRange(ACTIVE_CONTROLLER_CELL).setValue(controllerId);
}

function getActiveController() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(ORDER_SHEET);
  if (!sheet) return "";
  return (sheet.getRange(ACTIVE_CONTROLLER_CELL).getValue() || "").toString();
}

function upsertTeamByName(playerName, teamName) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sheet) throw new Error("Sheet not found: " + SHEET_NAME);

  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return false;

  const names = sheet.getRange(2, 1, lastRow - 1, 1).getValues();
  for (let i = 0; i < names.length; i++) {
    const cellName = (names[i][0] || "").toString().trim().toLowerCase();
    if (cellName === playerName.toLowerCase()) {
      sheet.getRange(i + 2, TEAM_COLUMN).setValue(teamName);
      return true;
    }
  }
  return false;
}

function clearAssignments() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sheet) throw new Error("Sheet not found: " + SHEET_NAME);

  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return;

  sheet.getRange(2, TEAM_COLUMN, lastRow - 1, 1).clearContent();
}

function clearAssignmentsSoft() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sheet) throw new Error("Sheet not found: " + SHEET_NAME);

  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return;

  const categories = sheet.getRange(2, CATEGORY_COLUMN, lastRow - 1, 1).getValues();
  const teamsRange = sheet.getRange(2, TEAM_COLUMN, lastRow - 1, 1);
  const teams = teamsRange.getValues();

  for (let i = 0; i < teams.length; i++) {
    const cat = (categories[i][0] || "").toString().trim().toUpperCase();
    if (cat !== "CAPITÃO" && cat !== "WILDCARD") {
      teams[i][0] = "";
    }
  }
  teamsRange.setValues(teams);
}

function getSheetAsCsv() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sheet) throw new Error("Sheet not found: " + SHEET_NAME);

  const values = sheet.getDataRange().getValues();
  const escape = (v) => {
    const s = (v ?? "").toString();
    if (s.includes('"') || s.includes(",") || s.includes("\n")) {
      return `"${s.replace(/"/g, '""')}"`;
    }
    return s;
  };
  return values.map(row => row.map(escape).join(",")).join("\n");
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
