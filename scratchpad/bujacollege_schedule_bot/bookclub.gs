/************************************************************
 * 독서클럽 모임 관리 (bookclub.gs)
 ************************************************************/

var BOOKCLUB_SHEET_NAME = "독서클럽_스케줄"; 
var RECORD_SHEET_NAME = "독서클럽_기록";

/************************************************************
 * 1) 시트 자동 생성 및 기본 데이터 입력 (미확정 일정 10개 유지)
 ************************************************************/
function initializeBookClubSheet() {
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = ss.getSheetByName(BOOKCLUB_SHEET_NAME);

  // 시트가 없으면 생성
  if (!sheet) {
    sheet = ss.insertSheet(BOOKCLUB_SHEET_NAME);
    sheet.appendRow(["날짜", "담당자", "수행여부"]);
    // 초기 확정 일정 2개 + 나머지 미확정 일정
    sheet.appendRow(["2025-03-06 21시", "김은태", "미수행"]);
    sheet.appendRow(["2025-03-20 21시", "강공현", "미수행"]);
  } else {
    // 시트가 이미 있는 경우: 헤더 맞춰주기
    var header = sheet.getRange(1, 1, 1, 3).getValues()[0];
    // 만약 기존에 헤더가 다르다면 강제로 수정
    if (header[0] !== "날짜" || header[1] !== "담당자" || header[2] !== "수행여부") {
      sheet.getRange(1, 1).setValue("날짜");
      sheet.getRange(1, 2).setValue("담당자");
      sheet.getRange(1, 3).setValue("수행여부");
    }
  }

  // 미확정 일정이 5개가 되도록 유지
  maintainUnconfirmedSessions(sheet);

  // 수행 횟수 기록 시트 확인
  var recordSheet = ss.getSheetByName(RECORD_SHEET_NAME);
  if (!recordSheet) {
    recordSheet = ss.insertSheet(RECORD_SHEET_NAME);
    recordSheet.appendRow(["이름", "수행 횟수"]);
    recordSheet.appendRow(["김은태", 0]);
    recordSheet.appendRow(["강공현", 0]);
    recordSheet.appendRow(["김민지", 0]);
    recordSheet.appendRow(["박경욱", 0]);
    recordSheet.appendRow(["박종욱", 0]);
  }
}


/************************************************************
 * 2) 미확정 일정이 항상 5개 유지되도록 관리
 ************************************************************/
function maintainUnconfirmedSessions(sheet) {
  var members = ["김은태", "강공현", "김민지", "박경욱", "박종욱"];
  var data = sheet.getDataRange().getValues();
  
  // 헤더를 제외한 전체 데이터 행 수
  var totalRows = data.length - 1;
  
  // 현재 pending 행의 수를 센다 (날짜가 "(미확정)"인 행)
  var pendingCount = 0;
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] === "(미확정)") {
      pendingCount++;
    }
  }
  
  // 만약 pending 행이 5개 미만이면, 추가로 5개를 입력한다.
  if (pendingCount < 5) {
    for (var j = 0; j < 5; j++) {
      // 전체 행 수를 기준으로 멤버 배열 순환: 
      // 예) totalRows가 13이면, 13 mod members.length = 13 mod 5 = 3 → members[3]부터 할당
      var index = (totalRows + j) % members.length;
      sheet.appendRow(["(미확정)", members[index], "미수행"]);
    }
  }
}





/************************************************************
 * 3) /start2 - 독서클럽 관리용 인라인 버튼 제공
 ************************************************************/
function startBookClub(chatId) {
  var keyboard = {
    inline_keyboard: [
      [
        { text: "📅 다음 모임 일정", callback_data: "/nextsession" }
      ],
      [
        { text: "📝 일정 확정하기", callback_data: "/setdate" }
      ],
      [
        // ★ 수정: "🔄 담당자 변경하기" → "🔄 일정 변경"
        { text: "🔄 일정 변경", callback_data: "/modify" }
      ],
      [
        { text: "📊 수행 횟수 조회", callback_data: "/record" }
      ]
    ]
  };
  sendTelegramMessage(chatId, "📖 독서클럽 모임 관리", {
    reply_markup: JSON.stringify(keyboard)
  });
}



/************************************************************
 * 4) /nextsession - 기본 3명 일정 조회 (10명 확장)
 ************************************************************/
/**
 * /nextsession 명령어로 호출됨
 * - limit: 보여줄 개수 (3 또는 5)
 * - mode: "3" 또는 "5" (지금 몇 개 보여주는 모드인지)
 *   => 반대 모드의 버튼을 아래에 띄우기 위해 사용
 */
function getNextSessions(chatId, limit, mode) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(BOOKCLUB_SHEET_NAME);
  if (!sheet) {
    sendTelegramMessage(chatId, "⚠️ [오류] 독서클럽 시트를 찾을 수 없습니다.");
    return;
  }

  // 매번 미확정 일정이 5개인지 확인/보정
  maintainUnconfirmedSessions(sheet);

  var data = sheet.getDataRange().getValues();
  if (data.length <= 1) {
    sendTelegramMessage(chatId, "⚠️ 모임 일정이 없습니다.");
    return;
  }

  // 오늘 0시
  var today = new Date();
  today.setHours(0, 0, 0, 0);

  // 확정 + 미확정 일정 모두 추출
  var events = [];
  for (var i = 1; i < data.length; i++) {
    var dateVal = data[i][0]; 
    var assignee = data[i][1] || "미정";

    if (dateVal === "(미확정)") {
      events.push({
        dateVal: dateVal,
        isConfirmed: false,
        assignee: assignee
      });
    } else {
      var dObj = parseDateTimeString(dateVal);
      if (!dObj) continue;
      if (dObj.getTime() <= today.getTime()) {
        // 이미 지난 일정은 표시 안 함
        continue;
      }
      events.push({
        dateVal: dateVal,
        isConfirmed: true,
        assignee: assignee,
        dateObj: dObj
      });
    }
  }

  // 확정은 날짜 오름차순, 미확정은 뒤로
  events.sort(function(a, b) {
    if (!a.isConfirmed && b.isConfirmed) return 1;
    if (a.isConfirmed && !b.isConfirmed) return -1;
    if (a.isConfirmed && b.isConfirmed) {
      return a.dateObj - b.dateObj;
    }
    return 0;
  });

  var sliced = events.slice(0, limit);
  if (sliced.length === 0) {
    sendTelegramMessage(chatId, "⚠️ 앞으로 표시할 일정이 없습니다.");
    return;
  }

  var msg = "📢 *독서클럽 모임 일정* 📢\n";
  sliced.forEach(function(ev) {
    msg += "📅 " + ev.dateVal + " - 👤 " + ev.assignee + "\n";
  });

  var oppositeMode = (mode === "3") ? "5" : "3";
  var buttonLabel = oppositeMode + "회 조회";
  var callbackData = "/nextsession_" + oppositeMode;

  var keyboard = {
    inline_keyboard: [
      [
        { text: buttonLabel, callback_data: callbackData }
      ]
    ]
  };

  sendTelegramMessage(chatId, msg, {
    reply_markup: JSON.stringify(keyboard)
  });
}


/************************************************************
 * 5) 일정 확정하기 (/setdate YYYY-MM-DD HH)
 ************************************************************/
/**
 * 정확히 수정한 일정 확정하기 로직 (기존 담당자 유지, 날짜만 정렬)
 */
// 1. 일정 등록(setBookClubDate) 날짜만 정렬 (담당자 유지)
function setBookClubDate(chatId, text) {
  var dateMatch = text.match(/\/setdate (\d{4}-\d{2}-\d{2} \d{2})/);
  if (!dateMatch) {
    sendTelegramMessage(chatId, "⚠️ 날짜 형식 오류: /setdate YYYY-MM-DD HH");
    return;
  }

  var dateStr = dateMatch[1] + "시";
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(BOOKCLUB_SHEET_NAME);
  var data = sheet.getDataRange().getValues();

  var unconfirmedIdx = data.findIndex(row => row[0] === "(미확정)");
  if (unconfirmedIdx === -1) {
    sendTelegramMessage(chatId, "⚠️ 미확정 일정이 없습니다.");
    return;
  }

  // 미확정 일정 날짜만 변경 (담당자 유지)
  sheet.getRange(unconfirmedIdx + 1, 1).setValue(dateMatch[1] + "시");

  // 데이터를 다시 가져와서 정렬 처리
  data = sheet.getDataRange().getValues().slice(1);
  var confirmed = data.filter(row => row[0] !== "(미확정)");
  confirmed.sort((a, b) => new Date(a[0].replace("시", ":00")) - new Date(b[0].replace("시", ":00")));

  var unconfirmed = data.filter(row => row[0] === "(미확정)");

  var sortedData = confirmed.concat(unconfirmed);

  // 날짜만 정렬 (담당자와 수행여부는 원래 순서 유지)
  for (var i = 0; i < confirmed.length; i++) {
    sheet.getRange(i + 2, 1).setValue(confirmed[i][0]);
  }

  sendTelegramMessage(chatId, `✅ 일정이 등록되었습니다: ${dateMatch[1]}시`);
}






/************************************************************
 * 6) 수행 횟수 조회 (/record)
 ************************************************************/
function getBookClubRecords(chatId) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(RECORD_SHEET_NAME);
  var data = sheet.getDataRange().getValues();
  if (data.length === 0) {
    sendTelegramMessage(chatId, "⚠️ 기록이 없습니다.");
    return;
  }

  var message = "📊 *독서클럽 수행 횟수 현황*\n\n";
  for (var i = 1; i < data.length; i++) {
    message += "• " + data[i][0] + ": " + data[i][1] + "회\n";
  }

  sendTelegramMessage(chatId, message);
}



/************************************************************
 * 7) 알림 시스템 (자동)
 ************************************************************/
function sendBookClubNotification() {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(BOOKCLUB_SHEET_NAME);
  var data = sheet.getDataRange().getValues();
  if (data.length === 0) return;

  var today = new Date();
  today.setHours(0, 0, 0, 0); // 오늘 0시 기준으로 설정

  // ChatIDs 시트에서 모든 채팅 ID 가져오기
  var chatSheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(CHAT_SHEET_NAME);
  if (!chatSheet) {
    Logger.log("⚠️ 오류: ChatIDs 시트가 존재하지 않음.");
    return;
  }

  var chatIds = chatSheet.getDataRange().getValues()
    .map(function(row) { return row[0]; })
    .filter(function(chatId) {
      return chatId && (typeof chatId === "number" || typeof chatId === "string");
    });

  if (chatIds.length === 0) {
    Logger.log("⚠️ 오류: Chat ID가 등록된 사용자가 없습니다.");
    return;
  }

  // 미래 일정 중 확정된 것만 필터링
  var upcomingEvents = [];
  for (var i = 1; i < data.length; i++) {
    var dateVal = data[i][0];
    if (dateVal === "(미확정)") continue;
    
    try {
      // 날짜 문자열을 Date 객체로 변환
      var sessionDate = DateUtils.parse(dateVal.toString());
      if (!sessionDate) continue;
      
      // 오늘과의 날짜 차이 계산 (일 단위)
      var diff = Math.ceil((sessionDate - today) / (1000 * 60 * 60 * 24));
      var host = data[i][1];
      
      // 오늘 포함 3일 이내 일정만 알림
      if (diff >= 0 && diff <= 3) {
        upcomingEvents.push({
          date: dateVal,
          host: host,
          daysLeft: diff
        });
      }
    } catch (e) {
      Logger.log("⚠️ 날짜 파싱 오류: " + dateVal + " - " + e.message);
      continue;
    }
  }

  if (upcomingEvents.length === 0) {
    Logger.log("📅 독서클럽 알림: 3일 이내 예정된 일정이 없습니다.");
    return;
  }

  // 각 일정에 대해 모든 채팅 ID로 알림 전송
  for (var j = 0; j < upcomingEvents.length; j++) {
    var event = upcomingEvents[j];
    var daysText = "";
    
    switch(event.daysLeft) {
      case 0:
        daysText = "오늘";
        break;
      case 1:
        daysText = "내일";
        break;
      case 2:
        daysText = "모레";
        break;
      case 3:
        daysText = "3일 후";
        break;
    }
    
    var message = `📢 *독서클럽 모임 알림* 📢\n\n📅 일정: ${event.date}\n👤 담당자: ${event.host}\n⏰ ${daysText} 진행됩니다!`;
    
    for (var k = 0; k < chatIds.length; k++) {
      try {
        sendTelegramMessage(chatIds[k], message);
        Logger.log("✅ 독서클럽 알림 전송 완료: " + chatIds[k]);
      } catch (error) {
        Logger.log("⚠️ [ERROR] 독서클럽 알림 전송 실패: " + chatIds[k] + " - " + error.message);
      }
    }
  }
  
  Logger.log("✅ 독서클럽 알림 전송 완료: " + upcomingEvents.length + "개 일정");
}



/**
 * [최종] 담당자 교환: targetDate 일정 → newAssignee
 * 그리고 newAssignee가 가진 "미확정" 일정 중 가장 빠른(상단) 일정을 oldAssignee로 교체
 */
/**
 * 담당자 교환: 특정 확정된 일정 담당자와 선택한 새 담당자의 가장 빠른 미수행 일정을 서로 교체
 */
/**
 * 정확히 담당자 교환 로직 (위아래 모두 검색하여 가장 가까운 미수행 일정과 담당자 교체)
 */
function updateBookClubAssignee(chatId, rowIndex, newAssignee) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(BOOKCLUB_SHEET_NAME);
  var data = sheet.getDataRange().getValues();
  
  var currentDate = data[rowIndex - 1][0];
  var currentAssignee = data[rowIndex - 1][1];

  if (currentDate === "(미확정)") {
    sendTelegramMessage(chatId, "⚠️ 확정된 일정만 담당자 변경이 가능합니다.");
    return;
  }

  var nearestIndex = -1;
  var nearestDistance = data.length;

  // 위쪽 방향 탐색
  for (var i = rowIndex - 2; i >= 1; i--) {
    if (data[i][1] === newAssignee && data[i][2] === "미수행") {
      nearestIndex = i;
      nearestDistance = Math.abs(rowIndex - 1 - i);
      break; // 위에서 발견되면 즉시 종료
    }
  }

  // 아래쪽 방향 탐색 (위쪽보다 더 가까운 거리일 경우만 업데이트)
  for (var i = rowIndex; i < data.length; i++) {
    if (data[i][1] === newAssignee && data[i][2] === "미수행") {
      if ((i - (rowIndex - 1)) < nearestDistance) {
        nearestIndex = i;
        nearestDistance = i - rowIndex;
        break;
      }
    }
  }

  if (nearestIndex === -1) {
    sendTelegramMessage(chatId, `⚠️ "${newAssignee}"님의 미수행 일정이 없습니다.`);
    return;
  }

  // 담당자 교체 수행
  var currentAssigneeCell = sheet.getRange(rowIndex, 2);
  var targetAssigneeCell = sheet.getRange(nearestIndex + 1, 2);

  currentAssigneeCell.setValue(newAssignee);
  targetAssigneeCell.setValue(currentAssignee);

  sendTelegramMessage(chatId, `✅ 일정 담당자가 교환되었습니다.\n\n📅 ${data[rowIndex - 1][0]}: ${currentAssignee} → ${newAssignee}\n📅 ${data[nearestIndex][0]}: ${newAssignee} → ${currentAssignee}`);
}





/**
 * 담당자 변경 시작 함수: 미래 일정 중 확정된 것만 인라인 버튼으로 띄움
 */
function sendModifyDateOptions(chatId) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(BOOKCLUB_SHEET_NAME);
  var data = sheet.getDataRange().getValues();

  var today = new Date();
  today.setHours(0, 0, 0, 0);
  var futureRows = [];

  // 미래 확정 일정의 행 번호 수집
  for (var i = 1; i < data.length; i++) {
    var dateVal = data[i][0];
    if (!dateVal || dateVal === "(미확정)") continue;

    var dateObj = parseDateTimeString(convertCellToString(dateVal));
    if (dateObj && dateObj.getTime() > today.getTime()) {
      futureRows.push({ rowIndex: i + 1, dateStr: convertCellToString(dateVal) });
    }
  }

  if (futureRows.length === 0) {
    sendTelegramMessage(chatId, "⚠️ 변경 가능한 미래 일정이 없습니다.");
    return;
  }

  // 인라인 버튼 (두 개씩)
  var inlineRows = [];
  var rowSize = 2;
  for (var i = 0; i < futureRows.length; i += rowSize) {
    var row = [];
    for (var j = 0; j < rowSize; j++) {
      if (i + j < futureRows.length) {
        var dateStr = futureRows[i + j].dateStr;
        var rowIndex = futureRows[i + j].rowIndex;
        row.push({
          text: dateStr,
          callback_data: "/modify_date_row_" + rowIndex
        });
      }
    }
    inlineRows.push(row);
  }

  inlineRows.push([{ text: "↩️", callback_data: "/cancel_inline" }]);

  sendTelegramMessage(chatId, "🔄 변경할 확정된 미래 일정을 선택하세요:", {
    reply_markup: JSON.stringify({ inline_keyboard: inlineRows })
  });
}





/**
 * 문자열(예: "2025-03-20 21시") → Date 객체로 파싱
 * 파싱 실패 시 null
 */
function parseDateTimeString(dateStr) {
  try {
    var parts = dateStr.trim().split(" ");
    if (parts.length < 2) return null;

    var dateParts = parts[0].split("-");
    if (dateParts.length < 3) return null;

    var year = parseInt(dateParts[0], 10);
    var month = parseInt(dateParts[1], 10) - 1;
    var day = parseInt(dateParts[2], 10);
    var hour = parseInt(parts[1].replace("시", ""), 10);

    var d = new Date(year, month, day, hour);
    if (isNaN(d.getTime())) return null;
    return d;
  } catch (e) {
    return null;
  }
}



/**
 * 선택된 일정(날짜)이 주어지면, 현재 담당자를 제외한 나머지 4명 인라인 버튼을 표시
 */
function sendChangeAssigneeOptions(chatId, targetDate) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(BOOKCLUB_SHEET_NAME);
  var data = sheet.getDataRange().getValues();

  // targetDate 일정의 현재 담당자 찾기 (문자열 앞뒤 공백 제거)
  var currentAssignee = "";
  for (var i = 1; i < data.length; i++) {
    if (typeof data[i][0] === "string" && data[i][0].trim() === targetDate.trim()) {
      currentAssignee = data[i][1];
      break;
    }
  }
  if (!currentAssignee) {
    sendTelegramMessage(chatId, "⚠️ 해당 일정(" + targetDate + ")을 찾을 수 없습니다.");
    return;
  }

  // 전체 멤버 중 현재 담당자를 제외
  var members = ["김은태", "강공현", "김민지", "박경욱", "박종욱"];
  var others = members.filter(function(m) { return m !== currentAssignee; });
  
  // 인라인 버튼 생성 (두 개씩)
  var rowSize = 2;
  var inlineRows = [];
  for (var i = 0; i < others.length; i += rowSize) {
    var row = [];
    for (var j = 0; j < rowSize; j++) {
      if (i + j < others.length) {
        var name = others[i + j];
        var cb = "/change_assignee_" + encodeURIComponent(targetDate) + "_" + encodeURIComponent(name);
        row.push({ text: name, callback_data: cb });
      }
    }
    inlineRows.push(row);
  }
  // 마지막 행에 "↩️" 버튼 추가
  inlineRows.push([{ text: "↩️", callback_data: "/cancel_inline" }]);
  
  var replyMarkup = { inline_keyboard: inlineRows };
  sendTelegramMessage(
    chatId,
    "🔄 `" + targetDate + "` 일정\n현재 담당자: *" + currentAssignee + "*\n\n새 담당자를 선택하세요:",
    { reply_markup: JSON.stringify(replyMarkup) }
  );
}



/**
 * 매일 한 번씩 실행 → 지났지만 수행횟수가 0인 일정의 담당자 수행 횟수 +=1
 */
function updatePerformedEvents() {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(BOOKCLUB_SHEET_NAME);
  var recordSheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(RECORD_SHEET_NAME);
  if (!sheet || !recordSheet) {
    Logger.log("⚠️ 독서클럽 스케줄 시트 또는 기록 시트를 찾지 못함");
    return;
  }

  var data = sheet.getDataRange().getValues();
  var now = new Date();
  now.setHours(0, 0, 0, 0);

  // 기록 시트(이름→수행횟수) 맵
  var recordData = recordSheet.getDataRange().getValues();
  var recordMap = {};
  for (var i = 1; i < recordData.length; i++) {
    var name = recordData[i][0];
    var count = recordData[i][1];
    recordMap[name] = count;
  }

  for (var i = 1; i < data.length; i++) {
    var dateVal = data[i][0];
    var assignee = data[i][1];
    var performed = data[i][2]; // "미수행" or "완료"
    
    // "(미확정)"은 패스
    if (!dateVal || dateVal === "(미확정)") continue;

    var dObj = parseDateTimeString(dateVal);
    if (!dObj) continue;

    // 만약 일정 날짜가 '오늘 이전'이고 "미수행"이면 → "완료" 처리
    if (dObj.getTime() < now.getTime() && performed === "미수행") {
      Logger.log("✅ 과거 일정 감지: " + dateVal + " / 담당: " + assignee);
      // 시트에서 "완료"로 수정
      sheet.getRange(i + 1, 3).setValue("완료");
      // 기록 시트에서 담당자 수행횟수 +1
      if (!recordMap[assignee]) {
        recordMap[assignee] = 0;
      }
      recordMap[assignee]++;
    }
  }

  // recordSheet에 반영
  for (var i = 1; i < recordData.length; i++) {
    var name = recordData[i][0];
    if (recordMap[name] != null) {
      recordSheet.getRange(i + 1, 2).setValue(recordMap[name]);
    }
  }
}

function sendModifyAssigneeOptions(chatId, rowIndex) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(BOOKCLUB_SHEET_NAME);
  var data = sheet.getDataRange().getValues();

  if (rowIndex <= 1 || rowIndex > data.length) {
    sendTelegramMessage(chatId, "⚠️ 유효하지 않은 일정 선택입니다.");
    return;
  }

  var targetDateStr = convertCellToString(data[rowIndex - 1][0]);
  var currentAssignee = data[rowIndex - 1][1];

  var members = ["김은태", "강공현", "김민지", "박경욱", "박종욱"];
  var others = members.filter(function(m) { return m !== currentAssignee; });

  var inlineRows = [];
  for (var i = 0; i < others.length; i += 2) {
    var row = [];
    for (var j = 0; j < 2; j++) {
      if (i + j < others.length) {
        var name = others[i + j];
        var cb = "/modify_assignee_row_" + rowIndex + "_" + encodeURIComponent(name);
        row.push({ text: name, callback_data: cb });
      }
    }
    inlineRows.push(row);
  }

  inlineRows.push([
    { text: "❌ 일정삭제", callback_data: "/delete_date_row_" + rowIndex }
  ]);

  inlineRows.push([{ text: "↩️", callback_data: "/cancel_inline" }]);

  sendTelegramMessage(
    chatId,
    "🔄 `" + targetDateStr + "` 일정\n현재 담당자: *" + currentAssignee + "*\n\n담당자를 변경하거나 일정삭제를 선택하세요:",
    { reply_markup: JSON.stringify({ inline_keyboard: inlineRows }) }
  );
}

function deleteBookClubDate(chatId, rowIndex) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(BOOKCLUB_SHEET_NAME);
  var data = sheet.getDataRange().getValues();

  if (rowIndex <= 1 || rowIndex > data.length) {
    sendTelegramMessage(chatId, "⚠️ 유효하지 않은 일정 선택입니다.");
    return;
  }

  // 선택된 일정 아래의 모든 날짜를 위로 한 칸씩 당겨옴(담당자, 수행여부는 유지)
  for (var i = rowIndex; i < data.length - 1; i++) {
    sheet.getRange(i, 1).setValue(data[i][0]);
  }

  // 마지막 일정 날짜를 미확정 처리
  sheet.getRange(data.length - 1, 1).setValue("(미확정)");

  sendTelegramMessage(chatId, "✅ 일정이 삭제되고 재정리되었습니다.");
}

function convertCellToString(cellValue) {
  if (cellValue === null || cellValue === "") return "";
  
  // 이미 문자열인 경우 → trim 후 그대로 사용
  if (typeof cellValue === "string") {
    return cellValue.trim();
  }

  // Date 객체인지 확인
  if (Object.prototype.toString.call(cellValue) === "[object Date]" && !isNaN(cellValue)) {
    // "yyyy-MM-dd HH시" 포맷으로 변환
    return Utilities.formatDate(cellValue, "Asia/Seoul", "yyyy-MM-dd HH'시'");
  }

  // 혹시 숫자나 다른 타입이면 그냥 문자열 변환 후 trim
  return String(cellValue).trim();
}

