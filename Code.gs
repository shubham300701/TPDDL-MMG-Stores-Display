/**
 * ============================================================================
 * TATA POWER-DDL (MMG STORES, KESHAVPURAM) — GOOGLE APPS SCRIPT WEB BACKEND (Code.gs)
 * ============================================================================
 * Instructions:
 * 1. Open your Google Spreadsheet (with Master_Inventory, Predictive_Engine_3Day, etc.).
 * 2. Click "Extensions" -> "Apps Script".
 * 3. Replace all existing text in Code.gs with this entire script.
 * 4. Click the Save icon (Disk).
 * 5. Click "Deploy" (top right) -> "Manage deployments" (or "New deployment").
 *    - Click the Edit (pencil) icon -> select "New version".
 *    - Execute as: "Me"
 *    - Who has access: "Anyone"
 *    - Click "Deploy".
 * ============================================================================
 */

function doGet(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Master_Inventory");
  
  if (!sheet) {
    return ContentService.createTextOutput(JSON.stringify({ error: "Master_Inventory sheet not found" }))
      .setMimeType(ContentService.MimeType.JSON);
  }
  
  // Read Master Inventory rows (rows 4 to 13)
  var data = sheet.getRange("A4:M13").getValues();
  var inventory = [];
  
  for (var i = 0; i < data.length; i++) {
    var row = data[i];
    if (!row[1]) continue; // skip if code empty
    
    inventory.push({
      id: row[0],
      code: row[1],
      name: row[2],
      category: row[3],
      uom: row[4],
      opening: Number(row[5]) || 0,
      inward: Number(row[6]) || 0,
      issued: Number(row[7]) || 0,
      available: Number(row[8]) || 0,
      low: Number(row[9]) || 20,
      high: Number(row[10]) || 60,
      condition: row[11] || "NORMAL",
      lastUpdated: row[12] ? String(row[12]) : "18.10.2026, 09:30 AM"
    });
  }

  // Also read 3-Day predictions from Predictive_Engine_3Day
  var predSheet = ss.getSheetByName("Predictive_Engine_3Day");
  if (predSheet) {
    var predData = predSheet.getRange("A3:N12").getValues();
    for (var j = 0; j < predData.length && j < inventory.length; j++) {
      inventory[j].d1 = Number(predData[j][7]) || 15;
      inventory[j].d2 = Number(predData[j][8]) || 12;
      inventory[j].d3 = Number(predData[j][9]) || 10;
      inventory[j].total3D = Number(predData[j][10]) || 37;
      inventory[j].advisory = predData[j][13] || "✓ SAFE BUFFER";
    }
  }

  // Read Recent Audit Logs
  var auditSheet = ss.getSheetByName("Audit_Log_Immutable");
  var recentAudit = [];
  if (auditSheet) {
    var auditRows = auditSheet.getRange("A3:J15").getValues();
    for (var k = 0; k < auditRows.length; k++) {
      if (auditRows[k][0]) {
        recentAudit.push({
          logId: auditRows[k][0],
          time: auditRows[k][1],
          event: auditRows[k][2],
          code: auditRows[k][3],
          name: auditRows[k][4],
          delta: auditRows[k][5],
          before: auditRows[k][6],
          after: auditRows[k][7],
          user: auditRows[k][8]
        });
      }
    }
  }

  var response = {
    status: "success",
    timestamp: new Date().toISOString(),
    inventory: inventory,
    audit: recentAudit
  };

  return ContentService.createTextOutput(JSON.stringify(response))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    var payload = {};
    if (e.postData && e.postData.contents) {
      payload = JSON.parse(e.postData.contents);
    } else {
      payload = e.parameter || {};
    }

    var action = payload.action || "APPROVE_TRANSACTION";
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var now = new Date();
    var timeStampStr = Utilities.formatDate(now, "Asia/Kolkata", "dd.MM.yyyy, hh:mm a");

    if (action === "SUBMIT_REQUISITION") {
      var reqSheet = ss.getSheetByName("Store_Requisitions_Approval");
      if (reqSheet) {
        reqSheet.appendRow([
          payload.reqId || ("REQ-" + now.getTime()),
          timeStampStr,
          payload.type || "OUTWARD",
          payload.meter || "",
          payload.qty || 1,
          payload.staff || "Field Staff",
          payload.site || "General Feeder",
          "PENDING",
          "",
          "",
          "AWAITING_PIN_AUTH"
        ]);
      }
      return ContentService.createTextOutput(JSON.stringify({ success: true, message: "Requisition queued for manager PIN" }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    if (action === "APPROVE_TRANSACTION") {
      var masterSheet = ss.getSheetByName("Master_Inventory");
      var auditSheet = ss.getSheetByName("Audit_Log_Immutable");
      var dispatchSheet = ss.getSheetByName("Outward_Dispatch");
      var inwardSheet = ss.getSheetByName("Inward_Receipts");

      var meterTarget = (payload.meter || "").toLowerCase();
      var qty = Number(payload.qty) || 0;
      var isIssue = (payload.type || "ISSUE").toUpperCase() === "ISSUE" || (payload.type || "").toUpperCase() === "OUTWARD";
      var staffName = payload.staff || "Store Staff";
      var managerAuth = payload.manager || "Store Manager (Auth-999)";

      var updatedRowIndex = -1;
      var balanceBefore = 0;
      var balanceAfter = 0;
      var meterCode = "";
      var meterFullName = "";

      // 1. Locate row in Master_Inventory (Rows 4 to 13)
      var masterData = masterSheet.getRange("A4:M13").getValues();
      for (var r = 0; r < masterData.length; r++) {
        var rowCode = String(masterData[r][1]).toLowerCase();
        var rowName = String(masterData[r][2]).toLowerCase();

        if (rowCode.indexOf(meterTarget) !== -1 || meterTarget.indexOf(rowCode) !== -1 ||
            rowName.indexOf(meterTarget) !== -1 || meterTarget.indexOf(rowName) !== -1) {
          
          updatedRowIndex = r + 4; // 1-based row index in sheet
          meterCode = masterData[r][1];
          meterFullName = masterData[r][2];
          balanceBefore = Number(masterData[r][8]) || 0;

          if (isIssue) {
            var currIssued = Number(masterData[r][7]) || 0;
            masterSheet.getRange(updatedRowIndex, 8).setValue(currIssued + qty); // Col H (Issued)
          } else {
            var currInward = Number(masterData[r][6]) || 0;
            masterSheet.getRange(updatedRowIndex, 7).setValue(currInward + qty); // Col G (Inward)
          }

          // Stamp individual row's Last Updated (Col M)
          masterSheet.getRange(updatedRowIndex, 13).setValue(timeStampStr);
          SpreadsheetApp.flush();

          balanceAfter = Number(masterSheet.getRange(updatedRowIndex, 9).getValue()) || 0;
          break;
        }
      }

      // 2. Append to Dispatch or Inward Register
      if (isIssue && dispatchSheet) {
        dispatchSheet.appendRow([
          "ISS-" + Utilities.formatDate(now, "Asia/Kolkata", "yyyyMMdd-HHmm"),
          timeStampStr,
          meterCode,
          meterFullName,
          qty,
          staffName,
          payload.empId || "EMP-LINE",
          payload.site || "Sub-Division Site",
          payload.scheme || "Work Order Issuance",
          payload.vehicle || "Store Dispatch",
          managerAuth
        ]);
      } else if (!isIssue && inwardSheet) {
        inwardSheet.appendRow([
          "GRN-" + Utilities.formatDate(now, "Asia/Kolkata", "yyyyMMdd-HHmm"),
          timeStampStr,
          payload.poNo || "PO-ONLINE-STOCK",
          payload.vendor || "Manufacturer Shipment",
          meterCode,
          meterFullName,
          "BATCH-" + now.getTime(),
          qty,
          "NABL Testing Lab",
          "QC PASSED - RECORDED",
          "Main Store Rack"
        ]);
      }

      // 3. Append to Immutable Audit Log
      if (auditSheet) {
        auditSheet.appendRow([
          "AUD-" + Utilities.formatDate(now, "Asia/Kolkata", "yyyyMMdd-HHmmss"),
          timeStampStr,
          isIssue ? "OUTWARD_DISPATCH_APPROVED" : "INWARD_STOCK_ENTRY",
          meterCode,
          meterFullName,
          isIssue ? -qty : qty,
          balanceBefore,
          balanceAfter,
          managerAuth,
          "Cloud Webhook API"
        ]);
      }

      SpreadsheetApp.flush();

      return ContentService.createTextOutput(JSON.stringify({
        success: true,
        message: "Stock successfully updated in Google Sheets",
        meter: meterFullName,
        code: meterCode,
        qty: qty,
        balanceBefore: balanceBefore,
        balanceAfter: balanceAfter,
        timestamp: timeStampStr
      })).setMimeType(ContentService.MimeType.JSON);
    }

    return ContentService.createTextOutput(JSON.stringify({ success: false, error: "Invalid action" }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ success: false, error: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
