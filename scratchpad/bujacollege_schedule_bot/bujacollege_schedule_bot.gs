/************************************************************
 * 전역 상수
 ************************************************************/
var BOT_TOKEN = "7524488237:AAHqO35TON-hdu9HjstMfkZLHSa5NhaKww4"; // 🔹 텔레그램 봇 토큰
var SPREADSHEET_ID = "1qY1ISdrJVwioZQ_UHZoVoRrIL3Dfrf8utEXeu9zbays"; // 🔹 Google Sheets ID
var SHEET_NAME = "밸리AI_스케줄";         // 🔹 스케줄이 저장된 시트 이름
var CHAT_SHEET_NAME = "ChatIDs";   // 🔹 Chat ID를 저장할 시트

/************************************************************
 * 1) 텔레그램 메시지 전송 (재시도 로직 보강) + Markdown
 ************************************************************/
/**
 * 주어진 chatId로 Telegram 메시지를 전송합니다.
 * 메시지가 비어있으면 오류를 기록하며, 재시도 로직을 포함합니다.
 */
function sendTelegramMessage(chatId, text, extraOptions) {
  if (!text || text.trim() === "") {
    Logger.log("⚠️ 오류: 메시지 내용이 비어 있습니다.");
    return;
  }

  var telegramUrl = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage";
  var payload = {
    "chat_id": chatId,
    "text": text,
    "parse_mode": "Markdown"
  };

  if (extraOptions) {
    for (var key in extraOptions) {
      payload[key] = extraOptions[key];
    }
  }

  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload)
  };

  var attempts = 0;
  var maxAttempts = 3;
  while (attempts < maxAttempts) {
    try {
      var response = UrlFetchApp.fetch(telegramUrl, options);
      Logger.log("✅ 메시지 전송 완료: " + response.getContentText());
      return;
    } catch (e) {
      attempts++;
      Logger.log("⚠️ 메시지 전송 실패 (시도 " + attempts + "회): " + e.message);
      Utilities.sleep(1000);
    }
  }
  Logger.log("❌ 최종 메시지 전송 실패 (chatId: " + chatId + ")");
}

/************************************************************
 * 2) doPost: 텔레그램 웹훅 수신 & processCommand 호출
 ************************************************************/
function doPost(e) {
  Logger.log("📩 [DEBUG] doPost() 함수 실행됨");

  var data = e && e.postData ? JSON.parse(e.postData.contents) : null;
  Logger.log("📩 [DEBUG] 수신된 데이터: " + JSON.stringify(data));

  // 인라인 키보드(콜백 쿼리) 클릭: toLowerCase() 적용하지 않음 (형식 유지)
  if (data && data.callback_query) {
    var chatId = data.callback_query.message.chat.id;
    var text = data.callback_query.data.trim();  // 그대로 사용

    answerCallbackQuery(data.callback_query.id);

    // 필요시 @봇이름 제거
    text = text.replace(/@\S+/, "").trim();
    Logger.log("📩 [DEBUG] 콜백 쿼리로 받은 명령어: " + text);

    processCommand(chatId, text);

  // 일반 메시지: 사용자 입력은 toLowerCase() 적용 (명령어 통일)
  } else if (data && data.message && data.message.text) {
    var chatId = data.message.chat.id;
    var text = data.message.text.trim().toLowerCase();

    text = text.replace(/@\S+/, "").trim();
    Logger.log("📩 [DEBUG] 메시지로 받은 명령어: " + text);

    processCommand(chatId, text);

  } else {
    Logger.log("⚠️ [ERROR] 유효하지 않은 데이터 형식");
  }
}



/**
 * 콜백 쿼리 응답: 로딩 스피너 제거
 */
function answerCallbackQuery(callbackQueryId) {
  var url = "https://api.telegram.org/bot" + BOT_TOKEN + "/answerCallbackQuery";
  var payload = { "callback_query_id": callbackQueryId };

  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload)
  };

  try {
    var response = UrlFetchApp.fetch(url, options);
    Logger.log("✅ 콜백 쿼리 응답 완료: " + response.getContentText());
  } catch (e) {
    Logger.log("⚠️ 콜백 쿼리 응답 실패: " + e.message);
  }
}

/************************************************************
 * 3) 명령어 분기 처리
 ************************************************************/
/**
 * 사용자가 입력한 명령어(또는 콜백) text에 따라 각 기능을 실행
 */
function processCommand(chatId, text) {
  // 업데이트 대화 흐름 처리 (기존)
  if (handleUpdateFlow(chatId, text)) {
    return;
  }

  // 일반 메시지: 슬래시로 시작하지 않으면 무시
  if (!text.startsWith("/")) {
    Logger.log("슬래시로 시작하지 않으므로 무시: " + text);
    return;
  }

  // /start 명령어 통합: 인라인 키보드로 모드 선택 제공
  if (text === "/start") {
    registerChatId(chatId);
    var keyboard = {
      inline_keyboard: [
        [
          { text: "📅 벨리스케줄", callback_data: "/select_schedule" },
          { text: "📚 독서클럽",   callback_data: "/select_bookclub" }
        ]
      ]
    };
    sendTelegramMessage(
      chatId,
      "🚀 *부자칼리지 스케줄 봇 활성화*\n\n원하는 모드를 선택하세요:",
      { reply_markup: JSON.stringify(keyboard) }
    );
    return;
  }

  // 모드 선택 후 콜백 처리
  if (text === "/select_schedule") {
    setOrigin(chatId, "schedule");
    sendTelegramMessage(chatId, "✅ 스케줄 모드.\n원하는 기능을 선택하세요.", {
      reply_markup: JSON.stringify(getMainMenuInlineKeyboard(chatId))
    });
    return;
  }
  if (text === "/select_bookclub") {
    setOrigin(chatId, "bookclub");
    startBookClub(chatId);
    return;
  }

  // 모드에 따라 명령어 처리 분기; 캐시에서 origin이 없으면 기본 "schedule"로 설정
  var origin = getOrigin(chatId) || "schedule";
  Logger.log("processCommand: chatId=" + chatId + ", text=" + text + ", origin=" + origin);
  if (origin === "bookclub") {
    processBookClubCommand(chatId, text);
    return;
  } else if (origin === "schedule") {
    processScheduleCommand(chatId, text);
    return;
  }

  // 사용자 정의 알림 설정
  if (text.indexOf("/setnotify") === 0) {
    setUserNotificationTime(chatId, text);
    return;
  }
  
  // 일정 내보내기
  if (text === "/export") {
    var keyboard = {
      inline_keyboard: [
        [
          { text: "1주일", callback_data: "/export_week" },
          { text: "1개월", callback_data: "/export_month" }
        ],
        [
          { text: "전체", callback_data: "/export_all" },
          { text: "취소", callback_data: "/cancel_inline" }
        ]
      ]
    };
    
    sendTelegramMessage(chatId, "📤 *일정 내보내기*\n\n어느 기간의 일정을 내보내시겠습니까?", {
      reply_markup: JSON.stringify(keyboard)
    });
    return;
  }
  
  if (text === "/export_week") {
    exportCalendar(chatId, "week");
    return;
  }
  
  if (text === "/export_month") {
    exportCalendar(chatId, "month");
    return;
  }
  
  if (text === "/export_all") {
    exportCalendar(chatId, "all");
    return;
  }
  
  // 통계 명령어
  if (text === "/stats") {
    generateStatistics(chatId);
    return;
  }

  // 그 외: 알 수 없는 명령어 처리
  sendTelegramMessage(chatId, "⚠️ 알 수 없는 명령어입니다.\n\n💡 `/help` 명령어를 입력하여 사용 가능한 명령어를 확인하세요.");
}




function processScheduleCommand(chatId, text) {
  // (B) 날짜 조회 인라인 버튼: "/day_select_YYYY-MM-DD"
  if (text.indexOf("/day_select_") === 0) {
    var selectedDate = text.replace("/day_select_", "");
    sendTelegramMessage(chatId, getDayMessage(selectedDate));
    sendTelegramMessage(chatId, "메인 메뉴로 돌아갑니다.", {
      reply_markup: JSON.stringify(getMainMenuInlineKeyboard(chatId))
    });
    return;
  }
  
  // (C) 사용자별 조회 인라인 버튼: "/user_select_사용자이름"
  if (text.indexOf("/user_select_") === 0) {
    var selectedUser = text.replace("/user_select_", "");
    var userScheduleMsg = getUserScheduleInNextDays(selectedUser, 10);
    sendTelegramMessage(chatId, userScheduleMsg);
    sendTelegramMessage(chatId, "메인 메뉴로 돌아갑니다.", {
      reply_markup: JSON.stringify(getMainMenuInlineKeyboard(chatId))
    });
    return;
  }
  
  // (D) 인라인 버튼: 알람 설정/해제
  if (text === "/alarm_on") {
    registerChatId(chatId);
    sendTelegramMessage(chatId, "🔔 알람이 설정되었습니다!");
    sendTelegramMessage(chatId, "메인 메뉴", {
      reply_markup: JSON.stringify(getMainMenuInlineKeyboard(chatId))
    });
    return;
  }
  if (text === "/alarm_off") {
    removeChatId(chatId);
    sendTelegramMessage(chatId, "🔕 알람이 취소되었습니다!");
    sendTelegramMessage(chatId, "메인 메뉴", {
      reply_markup: JSON.stringify(getMainMenuInlineKeyboard(chatId))
    });
    return;
  }
  
  // (E) 인라인 버튼: "↩️" 뒤로가기 처리
  if (text === "/cancel_inline") {
    clearUpdateState(chatId);
    sendTelegramMessage(chatId, "메인 메뉴로 돌아갑니다.", {
      reply_markup: JSON.stringify(getMainMenuInlineKeyboard(chatId))
    });
    return;
  }
  
  // (G) 스케줄 모드 명령어 처리
  if (text === "/today") {
    sendTelegramMessage(chatId, getTodayMessage());
    return;
  }
  if (text === "/weekly") {
    sendTelegramMessage(chatId, getWeeklyMessage());
    return;
  }
  if (text === "/thismonth") {
    sendTelegramMessage(chatId, getMonthlyMessage(false));
    return;
  }
  if (text === "/nextmonth") {
    sendTelegramMessage(chatId, getMonthlyMessage(true));
    return;
  }
  if (text === "/day") {
    sendInlineDateKeyboard(chatId, "day_select_", 14, true);
    sendTelegramMessage(chatId, "📆 *원하는 날짜를 선택해주세요:*");
    return;
  }
  if (text.indexOf("/day ") === 0) {
    var parts = text.split(" ");
    if (parts.length >= 2) {
      var dateStr = parts[1];
      sendTelegramMessage(chatId, getDayMessage(dateStr));
    } else {
      sendTelegramMessage(chatId, "⚠️ 날짜 형식이 올바르지 않습니다. 예: `/day 2025-12-01`");
    }
    return;
  }
  
  if (text === "/user") {
    sendInlineUserOptions(chatId);
    sendTelegramMessage(chatId, "👥 *어떤 사용자를 조회하시겠습니까?*\n메뉴로 돌아가려면 아래 [🔙] 버튼을 누르세요.");
    return;
  }
  
  if (text === "/update") {
    setUpdateState(chatId, { step: "waiting_for_first_date" });
    sendInlineDateKeyboard(chatId, "update_select_first_", 14, true);
    sendTelegramMessage(chatId, "✏️ *스케줄 업데이트 진행*\n수정할 첫 번째 날짜를 선택해주세요.\n*취소하려면 `/cancel` 입력*");
    return;
  }
  if (text.indexOf("/update ") === 0) {
    updateSchedule(chatId, text);
    return;
  }
  if (text === "/cancel") {
    if (getUpdateState(chatId)) {
      clearUpdateState(chatId);
      sendTelegramMessage(chatId, "메인 메뉴로 돌아갑니다.", {
        reply_markup: JSON.stringify(getMainMenuInlineKeyboard(chatId))
      });
    } else {
      sendTelegramMessage(chatId, "진행 중인 작업이 없습니다.");
    }
    return;
  }
  if (text === "/rules") {
    sendTelegramMessage(chatId, getRulesText());
    return;
  }
  if (text === "/help") {
    sendTelegramMessage(chatId, getHelpMessage(), {
      reply_markup: JSON.stringify(getMainMenuInlineKeyboard(chatId))
    });
    return;
  }
  
  // 기본: 알 수 없는 명령어 처리
  sendTelegramMessage(chatId, "⚠️ 알 수 없는 명령어입니다.\n\n💡 `/help` 명령어를 입력하여 사용 가능한 명령어를 확인하세요.");
}

function processBookClubCommand(chatId, text) {
  if (text.indexOf("/modify_date_row_") === 0) {
    var rowIndex = parseInt(text.replace("/modify_date_row_", ""), 10);
    sendModifyAssigneeOptions(chatId, rowIndex);
    return;
  }


  if (text.indexOf("/modify_assignee_row_") === 0) {
    var parts = text.split("_");
    if (parts.length < 5) {
      sendTelegramMessage(chatId, "⚠️ 데이터 형식이 올바르지 않습니다.");
      return;
    }
    var rowIndex = parseInt(parts[3], 10);
    var newAssignee = decodeURIComponent(parts[4]);
    updateBookClubAssignee(chatId, rowIndex, newAssignee);
    return;
  }


  if (text.indexOf("/delete_date_row_") === 0) {
    var rowIndex = parseInt(text.replace("/delete_date_row_", ""), 10);
    deleteBookClubDate(chatId, rowIndex);
    return;
  }


  if (text === "/modify") {
    sendModifyDateOptions(chatId);
    return;
  }

  if (text.indexOf("/setdate") === 0) {
    setBookClubDate(chatId, text);
    return;
  }
  if (text.indexOf("/nextsession") === 0) {
    if (text === "/nextsession" || text === "/nextsession_3") {
      getNextSessions(chatId, 3, "3");
    } else if (text === "/nextsession_5") {
      getNextSessions(chatId, 5, "5");
    }
    return;
  }
  if (text === "/record") {
    getBookClubRecords(chatId);
    return;
  }

  if (text === "/cancel_inline") {
    clearUpdateState(chatId);
    startBookClub(chatId);
    return;
  }

    sendTelegramMessage(chatId, "⚠️ 알 수 없는 명령어입니다.\n\n💡 `/help` 명령어를 입력하여 사용 가능한 명령어를 확인하세요.");
}



/************************************************************
 * 4) Chat ID 등록/해제/조회
 ************************************************************/
/**
 * Chat ID 등록 함수: 사용자의 Chat ID를 시트에 저장 (알람 ON)
 */
function registerChatId(chatId) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(CHAT_SHEET_NAME);
  if (!sheet) {
    Logger.log("⚠️ 오류: ChatIDs 시트가 없음. 새로 생성합니다.");
    sheet = SpreadsheetApp.openById(SPREADSHEET_ID).insertSheet(CHAT_SHEET_NAME);
    sheet.appendRow(["Chat ID"]);
  }

  var chatIds = sheet.getDataRange().getValues().map(function(row) {
    return row[0];
  });

  if (!chatIds.includes(chatId)) {
    sheet.appendRow([chatId]);
    Logger.log("✅ [SUCCESS] 새로운 Chat ID 저장됨: " + chatId);
  } else {
    Logger.log("⚠️ [INFO] 이미 등록된 Chat ID: " + chatId);
  }
}

/**
 * Chat ID 해제 함수: 사용자의 Chat ID를 시트에서 제거 (알람 OFF)
 */
function removeChatId(chatId) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(CHAT_SHEET_NAME);
  if (!sheet) return;

  var range = sheet.getDataRange();
  var values = range.getValues();
  for (var i = 0; i < values.length; i++) {
    if (values[i][0] === chatId) {
      sheet.deleteRow(i + 1);
      Logger.log("✅ [SUCCESS] Chat ID 삭제됨: " + chatId);
      return;
    }
  }
  Logger.log("⚠️ [INFO] 삭제할 Chat ID가 목록에 없음: " + chatId);
}

/**
 * Chat ID 등록 여부 확인: 알람이 ON인지 OFF인지 판단
 */
function isChatIdRegistered(chatId) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(CHAT_SHEET_NAME);
  if (!sheet) return false;

  var values = sheet.getDataRange().getValues();
  for (var i = 0; i < values.length; i++) {
    if (values[i][0] === chatId) {
      return true;
    }
  }
  return false;
}

/************************************************************
 * 5) /help 메시지
 ************************************************************/
function getHelpMessage() {
  return (
    "❓ *도움말 / 사용 가능한 명령어*\n" +
    "────────\n" +
    "🔹 `/today`     - 오늘/내일/모레 일정 확인\n" +
    "🔹 `/weekly`    - 이번 주와 다음 주 일정 확인\n" +
    "🔹 `/thismonth` - 이번 달 일정 확인\n" +
    "🔹 `/nextmonth` - 다음 달 일정 확인\n" +
    "🔹 `/day`       - 특정 날짜 스케줄 조회\n" +
    "      예: `/day 2025-12-01`\n" +
    "🔹 `/update`    - 특정 날짜끼리 스케줄 교환\n" +
    "      예: `/update 2025-12-01 김민지`\n" +
    "🔹 `/setnotify` - 알림 시간 설정\n" +
    "      예: `/setnotify 08:00`\n" +
    "🔹 `/export`    - 일정 내보내기(iCal)\n" +
    "🔹 `/stats`     - 사용 통계 확인\n" +
    "🔹 `/rules`     - 플랫폼 및 사용 규칙 안내\n" +
    "🔹 `/start`     - 봇 활성화 및 안내 메시지\n" +
    "🔹 `/help`      - 명령어 목록 + 메인 메뉴\n" +
    "────────\n" +
    "원하는 기능을 선택하거나 직접 명령어를 입력하세요!"
  );
}


/************************************************************
 * 6) 오늘/내일/모레 메시지
 ************************************************************/
/**
 * 오늘, 내일, 모레 일정 표시
 */
function getTodayMessage(baseDate) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
  var data = sheet.getDataRange().getValues();
  if (data.length === 0) return "⚠️ 오류: 스프레드시트 데이터가 없습니다.";

  if (!baseDate) {
    baseDate = new Date();
    baseDate.setHours(0, 0, 0, 0);
  }

  var timeZone = Session.getScriptTimeZone();

  function formatKoreanDateFull(date) {
    var formatted = Utilities.formatDate(date, timeZone, "yyyy년 M월 d일 E요일");
    return formatted
      .replace("Sun요일", "일요일")
      .replace("Mon요일", "월요일")
      .replace("Tue요일", "화요일")
      .replace("Wed요일", "수요일")
      .replace("Thu요일", "목요일")
      .replace("Fri요일", "금요일")
      .replace("Sat요일", "토요일");
  }

  var today = new Date(baseDate);
  var tomorrow = new Date(baseDate);    tomorrow.setDate(tomorrow.getDate() + 1);
  var dayAfter = new Date(baseDate);    dayAfter.setDate(dayAfter.getDate() + 2);

  var todayLabel = formatKoreanDateFull(today);
  var tomorrowLabel = formatKoreanDateFull(tomorrow);
  var dayAfterLabel = formatKoreanDateFull(dayAfter);

  var todayKey = Utilities.formatDate(today, timeZone, "yyyy-MM-dd");
  var tomorrowKey = Utilities.formatDate(tomorrow, timeZone, "yyyy-MM-dd");
  var dayAfterKey = Utilities.formatDate(dayAfter, timeZone, "yyyy-MM-dd");

  function getUsers(dateKey) {
    var list = data.filter(function(row) {
      var rowDate = new Date(row[0]);
      rowDate.setHours(0, 0, 0, 0);
      return Utilities.formatDate(rowDate, timeZone, "yyyy-MM-dd") === dateKey;
    }).map(function(row) {
      return row[2];
    }).join(", ") || "없음";

    if (list === "없음") return "   ┗ 없음";
    return list.split(",").map(function(name) {
      return "   ┗ " + name.trim();
    }).join("\n");
  }

  var txtToday = getUsers(todayKey);
  var txtTomorrow = getUsers(tomorrowKey);
  var txtDayAfter = getUsers(dayAfterKey);

  return (
    "🌟 *오늘: " + todayLabel + "*\n" + txtToday +
    "\n────────\n" +
    "💫 *내일: " + tomorrowLabel + "*\n" + txtTomorrow +
    "\n────────\n" +
    "✨ *모레: " + dayAfterLabel + "*\n" + txtDayAfter
  );
}

/************************************************************
 * 7) 이번 주 & 다음 주
 ************************************************************/
function getWeeklyMessage() {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
  var data = sheet.getDataRange().getValues();
  if (data.length === 0) return "⚠️ 오류: 스프레드시트 데이터가 없습니다.";

  var timeZone = Session.getScriptTimeZone();
  var today = new Date();
  today.setHours(0, 0, 0, 0);

  var startOfWeek = new Date(today);
  startOfWeek.setDate(today.getDate() - today.getDay());
  startOfWeek.setHours(0, 0, 0, 0);

  var endOfWeek = new Date(startOfWeek);
  endOfWeek.setDate(startOfWeek.getDate() + 6);
  endOfWeek.setHours(23, 59, 59, 999);

  var nextStartOfWeek = new Date(startOfWeek);
  nextStartOfWeek.setDate(nextStartOfWeek.getDate() + 7);
  nextStartOfWeek.setHours(0, 0, 0, 0);

  var nextEndOfWeek = new Date(nextStartOfWeek);
  nextEndOfWeek.setDate(nextStartOfWeek.getDate() + 6);
  nextEndOfWeek.setHours(23, 59, 59, 999);

  function formatDateKorean(date) {
    var f = Utilities.formatDate(date, timeZone, "yyyy-MM-dd (E)");
    return f.replace("Sun", "일").replace("Mon", "월").replace("Tue", "화")
            .replace("Wed", "수").replace("Thu", "목").replace("Fri", "금")
            .replace("Sat", "토");
  }

  var currentWeekRows = data.filter(function(row) {
    var rd = new Date(row[0]);
    rd.setHours(0, 0, 0, 0);
    return (rd >= startOfWeek && rd <= endOfWeek);
  });
  var nextWeekRows = data.filter(function(row) {
    var rd = new Date(row[0]);
    rd.setHours(0, 0, 0, 0);
    return (rd >= nextStartOfWeek && rd <= nextEndOfWeek);
  });

  function formatRows(rows) {
    if (rows.length === 0) return "   ┗ 없음";
    return rows.map(function(row) {
      var dateLabel = formatDateKorean(new Date(row[0]));
      var userName = row[2] || "없음";
      return "   • " + dateLabel + " → *" + userName + "*";
    }).join("\n");
  }

  var currentWeekMsg = formatRows(currentWeekRows);
  var nextWeekMsg = formatRows(nextWeekRows);

  return (
    "💠 *이번 주 & 다음 주 스케줄*\n" +
    "────────\n" +
    "💠 *이번 주:* " + formatDateKorean(startOfWeek) + " ~ " + formatDateKorean(endOfWeek) + "\n" +
    currentWeekMsg +
    "\n────────\n" +
    "💠 *다음 주:* " + formatDateKorean(nextStartOfWeek) + " ~ " + formatDateKorean(nextEndOfWeek) + "\n" +
    nextWeekMsg
  );
}

/************************************************************
 * 8) 월간 스케줄 (주간 단위)
 ************************************************************/
function getMonthlyMessage(isNextMonth) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
  var data = sheet.getDataRange().getValues();
  if (data.length === 0) return "⚠️ 오류: 스프레드시트 데이터가 없습니다.";

  var today = new Date();
  var targetMonth = isNextMonth ? today.getMonth() + 1 : today.getMonth();
  var targetYear = today.getFullYear();
  if (targetMonth > 11) {
    targetMonth = 0;
    targetYear += 1;
  }

  var timeZone = Session.getScriptTimeZone();

  function formatDateKorean(d) {
    var f = Utilities.formatDate(d, timeZone, "yyyy-MM-dd (E)");
    return f.replace("Sun", "일").replace("Mon", "월").replace("Tue", "화")
            .replace("Wed", "수").replace("Thu", "목").replace("Fri", "금")
            .replace("Sat", "토");
  }

  var monthlyRows = data.filter(function(row) {
    var rd = new Date(row[0]);
    return rd.getFullYear() === targetYear && rd.getMonth() === targetMonth;
  });

  var firstDay = new Date(targetYear, targetMonth, 1);
  var lastDay = new Date(targetYear, targetMonth + 1, 0);
  lastDay.setHours(23, 59, 59, 999);

  var allDays = [];
  var current = new Date(firstDay);
  while (current <= lastDay) {
    var dayKey = Utilities.formatDate(current, timeZone, "yyyy-MM-dd");
    var dayRows = monthlyRows.filter(function(r) {
      var rd = new Date(r[0]);
      return Utilities.formatDate(rd, timeZone, "yyyy-MM-dd") === dayKey;
    });
    var users = dayRows.map(function(r) {
      return r[2] || "없음";
    }).join(", ") || "없음";

    allDays.push({ dateObj: new Date(current), users: users });
    current.setDate(current.getDate() + 1);
  }

  var weeks = [];
  var currentWeek = [];
  for (var i = 0; i < allDays.length; i++) {
    var dayInfo = allDays[i];
    var dow = dayInfo.dateObj.getDay();
    if (dow === 0 && currentWeek.length > 0) {
      weeks.push(currentWeek);
      currentWeek = [];
    }
    currentWeek.push(dayInfo);
  }
  if (currentWeek.length > 0) {
    weeks.push(currentWeek);
  }

  // [수정] 주차 헤더에 아이콘(🔷) 사용
  function formatWeek(weekIndex, weekDays) {
    if (weekDays.length === 0) return "";
    var startDay = weekDays[0].dateObj;
    var endDay = weekDays[weekDays.length - 1].dateObj;

    var startLabel = Utilities.formatDate(startDay, timeZone, "M월 d일 (E)");
    var endLabel   = Utilities.formatDate(endDay,   timeZone, "M월 d일 (E)");

    startLabel = startLabel.replace("(Sun)", "(일)").replace("(Mon)", "(월)").replace("(Tue)", "(화)")
                           .replace("(Wed)", "(수)").replace("(Thu)", "(목)").replace("(Fri)", "(금)")
                           .replace("(Sat)", "(토)");
    endLabel   = endLabel  .replace("(Sun)", "(일)").replace("(Mon)", "(월)").replace("(Tue)", "(화)")
                           .replace("(Wed)", "(수)").replace("(Thu)", "(목)").replace("(Fri)", "(금)")
                           .replace("(Sat)", "(토)");

    var weekNum = (weekIndex + 1) + "주차";
    // 아이콘 "🔷"로 변경
    var header = "\n🔷 *" + weekNum + "* " + startLabel + " ~ " + endLabel + "\n";

    var lines = weekDays.map(function(d) {
      var dateStr = formatDateKorean(d.dateObj);
      if (d.users === "없음") {
        return "   ┗ " + dateStr + " → 없음";
      } else {
        var arr = d.users.split(",");
        if (arr.length === 1) {
          return "   ┗ " + dateStr + " → *" + arr[0].trim() + "*";
        } else {
          var subLines = arr.map(function(u) {
            return "      - " + u.trim();
          }).join("\n");
          return "   ┗ " + dateStr + "\n" + subLines;
        }
      }
    });
    return header + lines.join("\n");
  }

  var allWeeksMsg = weeks.map(function(weekDays, idx) {
    return formatWeek(idx, weekDays);
  }).join("\n────────\n");

  var monthLabel = isNextMonth ? "다음 달" : "이번 달";
  var monthStr   = Utilities.formatDate(new Date(targetYear, targetMonth, 1), timeZone, "yyyy년 M월");

  return "✨ *" + monthLabel + " 스케줄: " + monthStr + "*\n" + allWeeksMsg;
}

/************************************************************
 * 9) 특정 날짜 스케줄
 ************************************************************/
function getDayMessage(dateStr) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
  var data = sheet.getDataRange().getValues();
  if (data.length === 0) return "⚠️ 오류: 스프레드시트 데이터가 없습니다.";

  var dateParts = dateStr.split("-");
  if (dateParts.length !== 3) {
    return "⚠️ 날짜 형식이 올바르지 않습니다. 예: `/day 2025-12-01`";
  }

  var year = parseInt(dateParts[0], 10);
  var month = parseInt(dateParts[1], 10) - 1;
  var day = parseInt(dateParts[2], 10);
  var targetDate = new Date(year, month, day);
  if (isNaN(targetDate.getTime())) {
    return "⚠️ 날짜 형식이 올바르지 않습니다. 예: `/day 2025-12-01`";
  }

  var timeZone = Session.getScriptTimeZone();
  function formatDateKorean(d) {
    var f = Utilities.formatDate(d, timeZone, "yyyy-MM-dd (E)");
    return f.replace("Sun", "일").replace("Mon", "월").replace("Tue", "화")
            .replace("Wed", "수").replace("Thu", "목").replace("Fri", "금")
            .replace("Sat", "토");
  }

  var targetStr = formatDateKorean(targetDate);

  var rows = data.filter(function(row) {
    var rd = new Date(row[0]);
    var rdStr = Utilities.formatDate(rd, timeZone, "yyyy-MM-dd");
    return rdStr === targetStr.substring(0, 10);
  });
  if (rows.length === 0) {
    return "🔖 *" + targetStr + "*\n   ┗ 없음";
  } else {
    var userList = rows.map(function(r) {
      return r[2] || "없음";
    }).join(", ");
    var formatted = userList.split(",").map(function(name) {
      return "   ┗ " + name.trim();
    }).join("\n");
    return "🔖 *" + targetStr + "*\n" + formatted;
  }
}

/************************************************************
 * 10) 사용 규칙 안내
 ************************************************************/
function getRulesText() {
  return (
    "📌 *플랫폼 사용 규칙*\n" +
    "━━━━━━━━━━━━━━━━━\n" +
    "✅ *1. 사용 시간 제한*\n" +
    "  ┗ 각 사용자는 *정해진 날짜의 오전 7시부터 다음 날 오전 7시까지* 이용 가능\n\n" +
    "✅ *2. 중복 로그인 금지*\n" +
    "  ┗ 한 명당 *PC 1대 + 모바일 1대* 사용 가능\n" +
    "  ┗ 여러 기기에서 동시 접속 시 계정 차단 가능\n\n" +
    "✅ *3. 계정 사용 후 반드시 로그아웃*\n" +
    "  ┗ 보안 강화를 위해 *사용 종료 후 반드시 로그아웃* 필요\n\n" +
    "✅ *4. 할당된 사용자만 접속 가능*\n" +
    "  ┗ *당일 배정된 사용자만 접속 가능* (다른 사용자의 접속 금지)\n\n" +
    "✅ *5. 정보 공유 및 커뮤니케이션*\n" +
    "  ┗ *당일 사용자는 중요한 정보나 뉴스*를 공유해 주세요\n\n" +
    "📢 *문의 사항이 있으면 관리자에게 연락 바랍니다.*"
  );
}

/************************************************************
 * 11) 매일 아침 알림 (시트 등록된 Chat ID에게 발송)
 ************************************************************/
function sendDailyNotification() {
  Logger.log("📢 [DEBUG] sendDailyNotification() 실행됨");

  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(CHAT_SHEET_NAME);
  if (!sheet) {
    Logger.log("⚠️ 오류: ChatIDs 시트가 존재하지 않음.");
    return;
  }

  // 1) Chat ID 목록
  var chatIds = sheet.getDataRange().getValues()
    .map(function(row) { return row[0]; })
    .filter(function(chatId) {
      return chatId && typeof chatId === "number";
    });

  if (chatIds.length === 0) {
    Logger.log("⚠️ 오류: Chat ID가 등록된 사용자가 없습니다.");
    return;
  }

  // 2) 오늘 0시
  var baseDate = new Date();
  baseDate.setHours(0, 0, 0, 0);
  Logger.log("기준 날짜(오늘 0시): " + baseDate);

  // 3) 일요일 여부
  var isSunday = (baseDate.getDay() === 0);

  // 4) 이달 마지막 날 여부
  var lastDayOfMonth = new Date(baseDate.getFullYear(), baseDate.getMonth() + 1, 0).getDate();
  var isLastDayOfMonth = (baseDate.getDate() === lastDayOfMonth);

  // (1) 다음 달
  if (isLastDayOfMonth) {
    var nextMonthMsg = getMonthlyMessage(true);
    if (nextMonthMsg && nextMonthMsg.trim() !== "") {
      chatIds.forEach(function(chatId) {
        try {
          sendTelegramMessage(chatId, nextMonthMsg);
        } catch (error) {
          Logger.log("⚠️ [ERROR] (nextMonth) " + chatId + " 전송 실패: " + error.message);
        }
      });
    }
  }

  // (2) 주간
  if (isSunday) {
    var weeklyMsg = getWeeklyMessage();
    if (weeklyMsg && weeklyMsg.trim() !== "") {
      chatIds.forEach(function(chatId) {
        try {
          sendTelegramMessage(chatId, weeklyMsg);
        } catch (error) {
          Logger.log("⚠️ [ERROR] (weekly) " + chatId + " 전송 실패: " + error.message);
        }
      });
    }
  }

  // (3) 데일리
  var dailyMsg = getTodayMessage(baseDate);
  if (dailyMsg && dailyMsg.trim() !== "") {
    chatIds.forEach(function(chatId) {
      try {
        sendTelegramMessage(chatId, dailyMsg);
      } catch (error) {
        Logger.log("⚠️ [ERROR] (daily) " + chatId + " 전송 실패: " + error.message);
      }
    });
  }

  // (4) 독서클럽 알림 (새로 추가)
  try {
    sendBookClubNotification();
  } catch (error) {
    Logger.log("⚠️ [ERROR] 독서클럽 알림 함수 실행 실패: " + error.message);
  }

  Logger.log("✅ [SUCCESS] 모든 메시지 전송 로직 완료!");
}

/************************************************************
 * 12) 매일 06:00 트리거 설정
 ************************************************************/
function createDailyTrigger() {
  Logger.log("📢 [DEBUG] createDailyTrigger() 실행됨");

  // 기존에 걸려있는 트리거들 중복 방지 위해 삭제
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    var funcName = trigger.getHandlerFunction();
    if (funcName === "sendDailyNotification" || funcName === "updatePerformedEvents") {
      ScriptApp.deleteTrigger(trigger);
    }
  });

  // (A) 매일 05:00에 updatePerformedEvents 실행
  ScriptApp.newTrigger("updatePerformedEvents")
    .timeBased()
    .atHour(5)
    .everyDays(1)
    .create();

  // (B) 매일 06:00에 기존 알림 함수(sendDailyNotification) 실행
  ScriptApp.newTrigger("sendDailyNotification")
    .timeBased()
    .atHour(6)
    .everyDays(1)
    .create();

  Logger.log("✅ [SUCCESS] 매일 05:00 수행횟수 갱신 + 06:00 알림 트리거 생성 완료");
}


/************************************************************
 * updateSchedule & logUpdateHistory
 ************************************************************/
function updateSchedule(chatId, text) {
  // 입력 형식: /update 2025-02-25 김은태
  var parts = text.split(" ");
  if (parts.length < 3) {
    sendTelegramMessage(chatId, "⚠️ 형식이 올바르지 않습니다. 예: `/update 2025-02-25 김민지`");
    return;
  }
  var dateStr = parts[1]; 
  var newUsers = parts.slice(2).join(" "); // 여러 사용자 가능

  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
  if (!sheet) {
    sendTelegramMessage(chatId, "⚠️ 스케줄 시트를 찾을 수 없습니다.");
    return;
  }

  var range = sheet.getDataRange();
  var values = range.getValues();
  var timeZone = Session.getScriptTimeZone();

  var found = false;
  var oldUsers = "없음"; // 변경 전 사용자 (기본값)

  for (var i = 0; i < values.length; i++) {
    var rowDate = new Date(values[i][0]);
    var rowKey = Utilities.formatDate(rowDate, timeZone, "yyyy-MM-dd");
    if (rowKey === dateStr) {
      // 변경 전 사용자값 저장
      oldUsers = values[i][2] || "없음";

      // 3번째 열(인덱스 2)을 newUsers로 업데이트
      sheet.getRange(i + 1, 3).setValue(newUsers);

      found = true;
      break;
    }
  }

  if (!found) {
    // 해당 날짜 데이터가 없으면 새 행 추가
    sheet.appendRow([new Date(dateStr), "", newUsers]);
  }

  // 변경 이력 로그 기록
  logUpdateHistory(dateStr, oldUsers, newUsers, chatId);

  // 사용자에게 안내 메시지
  sendTelegramMessage(chatId, "✅ 스케줄이 업데이트되었습니다: " + dateStr + " → " + newUsers);
}


/**
 * [새 함수] 스케줄 변경 이력을 "변경이력" 시트에 기록
 * @param {string} dateStr   변경된 날짜 (예: "2025-02-25")
 * @param {string} oldUsers  변경 전 사용자 문자열 (예: "박종욱")
 * @param {string} newUsers  변경 후 사용자 문자열 (예: "김민지")
 * @param {number} chatId    변경을 실행한 사용자의 Chat ID
 */
function logUpdateHistory(dateStr, oldUsers, newUsers, chatId) {
  var historySheetName = "밸리AI_변경이력"; // 미리 만들어 둔 시트 이름
  var historySheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(historySheetName);

  if (!historySheet) {
    historySheet = SpreadsheetApp.openById(SPREADSHEET_ID).insertSheet(historySheetName);
    historySheet.appendRow(["변경 시각", "변경된 날짜", "이전 사용자", "변경 후 사용자", "Chat ID"]);
  }

  var now = new Date();
  var rowData = [now, dateStr, oldUsers, newUsers, chatId];
  historySheet.appendRow(rowData);
}

/************************************************************
 * 업데이트 대화형 흐름 (스케줄 교환)
 ************************************************************/
function handleUpdateFlow(chatId, text) {
  var state = getUpdateState(chatId);
  if (!state) return false; // 업데이트 대화 진행 중이 아니면 false

  // 언제든 /cancel 처리
  if (text === "/cancel") {
    clearUpdateState(chatId);
    sendTelegramMessage(chatId, "🚫 업데이트가 취소되었습니다.");
    return true;
  }

  // 타임아웃 확인 (이미 getUpdateState에서 처리됨)

  // 첫 번째 날짜 선택 (인라인 버튼 선택)
  if (text.indexOf("/update_select_first_") === 0) {
    var selectedDate = text.replace("/update_select_first_", "");
    state.firstDate = selectedDate;
    state.firstSchedule = getScheduleForDate(selectedDate);
    state.step = "waiting_for_second_date";
    setUpdateState(chatId, state);
    // 두 번째 날짜 선택 옵션 표시 (예: 오늘부터 14일 범위)
    sendInlineDateOptions(chatId, "second");
    sendTelegramMessage(chatId, "✅ *첫 번째 날짜 선택됨*: `" + selectedDate + "`\n현재 스케줄: " + state.firstSchedule +
      "\n\n교환할 두 번째 날짜를 선택해주세요.\n*취소하려면 `/cancel` 입력*");
    return true;
  }

  // 두 번째 날짜 선택 (인라인 버튼 선택)
  if (text.indexOf("/update_select_second_") === 0) {
    var selectedDate = text.replace("/update_select_second_", "");
    state.secondDate = selectedDate;
    state.secondSchedule = getScheduleForDate(selectedDate);
    state.step = "waiting_for_confirmation";
    setUpdateState(chatId, state);
    sendUpdateConfirmationOptions(chatId);
    sendTelegramMessage(chatId, "✏️ *업데이트 확인*\n" +
      "첫 번째 날짜: `" + state.firstDate + "` → 스케줄: " + state.firstSchedule +
      "\n두 번째 날짜: `" + state.secondDate + "` → 스케줄: " + state.secondSchedule +
      "\n\n이 두 날짜의 스케줄을 교환하시겠습니까? (인라인 버튼 또는 '예'/'아니오')\n*취소하려면 `/cancel` 입력*");
    return true;
  }

  // 확인 단계 (텍스트 입력 또는 인라인 버튼)
  if (text === "/update_confirm_yes" || text === "예") {
    updateSwapCore(chatId, state.firstDate, state.secondDate);
    clearUpdateState(chatId);
    return true;
  }
  if (text === "/update_confirm_no" || text === "아니오") {
    clearUpdateState(chatId);
    sendTelegramMessage(chatId, "🚫 업데이트가 취소되었습니다.");
    return true;
  }

  // 그 외 알 수 없는 입력은 업데이트 흐름 내에서 다시 안내
  sendTelegramMessage(chatId, "⚠️ '예' 또는 '아니오'로 답해주세요.\n*취소하려면 `/cancel` 입력*");
  return true;
}

/************************************************************
 * 공통 유틸: 상태 저장, 삭제
 ************************************************************/
function clearUpdateState(chatId) {
  var cache = CacheService.getScriptCache();
  cache.remove("update_" + chatId);
}

function setUpdateState(chatId, stateObj) {
  stateObj.timestamp = new Date().getTime();
  var cache = CacheService.getScriptCache();
  cache.put("update_" + chatId, JSON.stringify(stateObj), 300); // 5분
}

function getUpdateState(chatId) {
  var cache = CacheService.getScriptCache();
  var stateStr = cache.get("update_" + chatId);
  if (stateStr) {
    var state = JSON.parse(stateStr);
    if (new Date().getTime() - state.timestamp > 300000) {
      clearUpdateState(chatId);
      return null;
    }
    return state;
  }
  return null;
}

/************************************************************
 * 날짜 인라인 키보드 (공통화)
 ************************************************************/
/**
 * (중복 함수 통합) 
 * - 특정 prefix로 days일간 날짜 버튼을 만든다.
 * - showCancel=true 면 마지막에 "🔙 돌아가기" 버튼 추가
 */
/**
 * 특정 prefix로 days일간 날짜 버튼을 만든다.
 * showCancel=true 이면 마지막에 "↩️" 버튼을
 * 마지막 행에 함께 배치 (자리가 없으면 새 행)
 */
function sendInlineDateKeyboard(chatId, prefix, days, showCancel) {
  var today = new Date();
  today.setHours(0, 0, 0, 0);

  var options = [];
  for (var i = 0; i < days; i++) {
    var d = new Date(today);
    d.setDate(d.getDate() + i);

    var shortLabel = Utilities.formatDate(d, Session.getScriptTimeZone(), "M/d(E)");
    var fullDateKey = Utilities.formatDate(d, Session.getScriptTimeZone(), "yyyy-MM-dd");

    options.push({
      text: shortLabel,
      callback_data: "/" + prefix + fullDateKey
    });
  }

  // 한 행에 3개씩
  var keyboard = [];
  for (var j = 0; j < options.length; j += 3) {
    keyboard.push(options.slice(j, j + 3));
  }

  // "↩️" 버튼을 마지막 행에 합치기 (자리가 없으면 새 행)
  if (showCancel) {
    if (keyboard.length === 0) {
      // 날짜가 하나도 없을 상황은 거의 없지만, 혹시 대비
      keyboard.push([{ text: "↩️", callback_data: "/cancel_inline" }]);
    } else {
      var lastRow = keyboard[keyboard.length - 1];
      if (lastRow.length < 3) {
        lastRow.push({ text: "↩️", callback_data: "/cancel_inline" });
      } else {
        keyboard.push([{ text: "↩️", callback_data: "/cancel_inline" }]);
      }
    }
  }

  var replyMarkup = { inline_keyboard: keyboard };
  sendTelegramMessage(chatId, "📆 날짜를 선택해주세요:", {
    reply_markup: JSON.stringify(replyMarkup)
  });
}


/************************************************************
 * 사용자 목록 인라인 키보드
 ************************************************************/
/**
 * 사용자 목록을 인라인 키보드로 전송
 * - 한 줄에 3명씩
 * - 마지막에 "↩️" 버튼을 같은 행에 배치 (자리가 없으면 새 행)
 */
function sendInlineUserOptions(chatId) {
  var userList = ["김은태", "강공현", "김민지", "박경욱", "박종욱"];
  var rowSize = 3;  // 한 줄에 3개씩

  var inlineKeyboardRows = [];
  for (var i = 0; i < userList.length; i += rowSize) {
    var row = [];
    for (var j = 0; j < rowSize; j++) {
      if (i + j < userList.length) {
        var userName = userList[i + j];
        row.push({
          text: userName,
          callback_data: "/user_select_" + userName
        });
      }
    }
    inlineKeyboardRows.push(row);
  }

  // 마지막 행에 "↩️" 버튼 합치기
  var lastRow = inlineKeyboardRows[inlineKeyboardRows.length - 1] || [];
  if (lastRow.length < rowSize) {
    lastRow.push({ text: "↩️", callback_data: "/cancel_inline" });
  } else {
    // 만약 이미 꽉 차 있으면 새 행 추가
    inlineKeyboardRows.push([{ text: "↩️", callback_data: "/cancel_inline" }]);
  }

  var replyMarkup = { inline_keyboard: inlineKeyboardRows };
  sendTelegramMessage(chatId, "👥 사용자 목록:", {
    reply_markup: JSON.stringify(replyMarkup)
  });
}


/**
 * 오늘부터 nextDays일 동안, 특정 사용자가 있는 날짜를 조회
 * @param {string} userName - 조회할 사용자 이름
 * @param {number} nextDays - 오늘 포함 몇 일 후까지?
 * @returns {string} 포맷된 메시지
 */
/**
 * 특정 사용자(userName)가 "향후 N번" 일정이 잡혀있는 날짜를 찾는다.
 * - 오늘부터 최대 365일 이내에서 userName이 등장하는 날짜를
 *   N번(occurrences) 찾으면 중단.
 */
function getUserScheduleInNextDays(userName, occurrences) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
  var data = sheet.getDataRange().getValues();
  if (data.length === 0) {
    return "⚠️ 오류: 스프레드시트 데이터가 없습니다.";
  }

  var timeZone = Session.getScriptTimeZone();
  var today = new Date();
  today.setHours(0, 0, 0, 0);

  var results = [];
  var dayCount = 0;
  // 최대 365일까지만 검색 (무한루프 방지)
  while (results.length < occurrences && dayCount < 365) {
    var targetDate = new Date(today);
    targetDate.setDate(today.getDate() + dayCount);

    var dateKey = Utilities.formatDate(targetDate, timeZone, "yyyy-MM-dd");

    // 스프레드시트에 해당 dateKey가 있고, userName이 포함되어 있으면 매칭
    var matched = data.some(function(row) {
      var rowDate = new Date(row[0]);
      rowDate.setHours(0, 0, 0, 0);
      var rowKey = Utilities.formatDate(rowDate, timeZone, "yyyy-MM-dd");
      // row[2]에 "김은태, 박종욱" 이런 식으로 들어갈 수 있으므로 indexOf로 확인
      return (
        rowKey === dateKey &&
        row[2] &&
        row[2].indexOf(userName) !== -1
      );
    });

    if (matched) {
      // 날짜 포맷: "M/d (E)"
      var formattedDate = Utilities.formatDate(targetDate, timeZone, "M/d (E)");
      formattedDate = formattedDate
        .replace("(Sun)", "(일)")
        .replace("(Mon)", "(월)")
        .replace("(Tue)", "(화)")
        .replace("(Wed)", "(수)")
        .replace("(Thu)", "(목)")
        .replace("(Fri)", "(금)")
        .replace("(Sat)", "(토)");

      results.push("• " + formattedDate);
    }

    dayCount++;
  }

  if (results.length === 0) {
    return "🔎 *" + userName + "*님은 향후 일정이 없습니다.";
  } else {
    return (
      "🔎 *" + userName + "*님의 향후 " + results.length + "회 스케줄:\n" +
      results.join("\n")
    );
  }
}


/************************************************************
 * 메인 메뉴: 알람 ON/OFF 버튼 포함
 ************************************************************/
/**
 * 메인 메뉴 인라인 키보드를 생성 (알람설정/취소 버튼 동적)
 */
/**
 * 메인 메뉴 인라인 키보드를 생성 (알람설정/취소 버튼 동적)
 * 도움말과 알람 버튼을 한 줄에 배치하도록 수정
 */
function getMainMenuInlineKeyboard(chatId) {
  var isAlarmOn = isChatIdRegistered(chatId);  // 알람 설정 여부
  var alarmLabel = isAlarmOn ? "알람취소" : "알람설정";
  var alarmCallback = isAlarmOn ? "/alarm_off" : "/alarm_on";

  return {
    inline_keyboard: [
      [
        { text: "오늘",       callback_data: "/today" },
        { text: "이번 주",    callback_data: "/weekly" }
      ],
      [
        { text: "이번 달",   callback_data: "/thismonth" },
        { text: "다음 달",   callback_data: "/nextmonth" }
      ],
      [
        { text: "특정 날짜 조회", callback_data: "/day" },
        { text: "스케줄 업데이트", callback_data: "/update" }
      ],
      [
        { text: "사용자별 조회", callback_data: "/user" },
        { text: alarmLabel,     callback_data: alarmCallback }
      ],
      [
        { text: "통계 보기", callback_data: "/stats" },
        { text: "일정 내보내기", callback_data: "/export" }
      ],
      [
        { text: "알림 시간 설정", callback_data: "/setnotify" },
        { text: "도움말", callback_data: "/help" }
      ]
    ]
  };
}


function getScheduleForDate(dateStr) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
  var data = sheet.getDataRange().getValues();
  var timeZone = Session.getScriptTimeZone();
  for (var i = 0; i < data.length; i++) {
    var rowDate = new Date(data[i][0]);
    var rowKey = Utilities.formatDate(rowDate, timeZone, "yyyy-MM-dd");
    if (rowKey === dateStr) {
      return data[i][2] || "없음";
    }
  }
  return "없음";
}

function sendInlineDateOptions(chatId, prefix) {
  // 예: "second"를 전달하면 "/update_select_second_" 형태의 콜백 데이터가 생성됨.
  sendInlineDateKeyboard(chatId, "update_select_" + prefix + "_", 14, true);
}

function sendUpdateConfirmationOptions(chatId) {
  var keyboard = {
    inline_keyboard: [
      [
        { text: "✅ 예", callback_data: "/update_confirm_yes" },
        { text: "❌ 아니오", callback_data: "/update_confirm_no" }
      ],
      [
        { text: "↩", callback_data: "/cancel_inline" }
      ]
    ]
  };
  sendTelegramMessage(chatId, "이대로 진행할까요?", { reply_markup: JSON.stringify(keyboard) });
}

function updateSwapCore(chatId, dateStr1, dateStr2) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
  if (!sheet) {
    sendTelegramMessage(chatId, "⚠️ 스케줄 시트를 찾을 수 없습니다.");
    return;
  }
  var range = sheet.getDataRange();
  var values = range.getValues();
  var timeZone = Session.getScriptTimeZone();
  var schedule1 = "없음", schedule2 = "없음";
  var row1 = -1, row2 = -1;
  
  for (var i = 0; i < values.length; i++) {
    var rowDate = new Date(values[i][0]);
    var rowKey = Utilities.formatDate(rowDate, timeZone, "yyyy-MM-dd");
    if (rowKey === dateStr1) {
      schedule1 = values[i][2] || "없음";
      row1 = i + 1;
    }
    if (rowKey === dateStr2) {
      schedule2 = values[i][2] || "없음";
      row2 = i + 1;
    }
  }
  
  // 교환: 기존 날짜에 업데이트
  if (row1 > 0) {
    sheet.getRange(row1, 3).setValue(schedule2);
  } else {
    sheet.appendRow([new Date(dateStr1), "", schedule2]);
  }
  if (row2 > 0) {
    sheet.getRange(row2, 3).setValue(schedule1);
  } else {
    sheet.appendRow([new Date(dateStr2), "", schedule1]);
  }
  
  logUpdateHistory(dateStr1 + " & " + dateStr2, schedule1 + " ↔ " + schedule2, schedule2 + " ↔ " + schedule1, chatId);
  sendTelegramMessage(chatId, "✅ 스케줄이 업데이트되었습니다:\n• " + dateStr1 + " → " + schedule2 + "\n• " + dateStr2 + " → " + schedule1);
}

function setOrigin(chatId, origin) {
  var cache = CacheService.getScriptCache();
  // 1시간 동안 저장 (필요 시 시간 조정 가능)
  cache.put("origin_" + chatId, origin, 3600);
}


function getOrigin(chatId) {
  var cache = CacheService.getScriptCache();
  return cache.get("origin_" + chatId);
}

/**
 * 시트 존재 확인 및 가져오기 (없으면 생성 옵션)
 * @param {string} sheetName - 시트 이름
 * @param {boolean} createIfNotExist - 존재하지 않을 경우 생성 여부
 * @param {Array<string>} headerRow - 새로 생성 시 헤더 행 (optional)
 * @returns {Sheet|null} 스프레드시트 시트 객체 또는 null
 */
function getOrCreateSheet(sheetName, createIfNotExist, headerRow) {
  var ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet = ss.getSheetByName(sheetName);
  
  if (!sheet && createIfNotExist) {
    sheet = ss.insertSheet(sheetName);
    Logger.log("✅ 시트 생성됨: " + sheetName);
    
    if (headerRow && Array.isArray(headerRow)) {
      sheet.appendRow(headerRow);
      Logger.log("✅ 헤더 행 추가됨: " + headerRow.join(", "));
    }
  }
  
  return sheet;
}


/**
 * 날짜 유틸리티 객체 - 날짜 관련 중복 코드 통합
 */
var DateUtils = {
  parse: function(dateStr) {
    if (!dateStr || dateStr === "(미확정)") return null;
    
    try {
      // "2025-03-20 21시" 형식 변환
      if (typeof dateStr === "string" && dateStr.includes("시")) {
        var parts = dateStr.trim().split(" ");
        if (parts.length < 2) return null;
        
        var dateParts = parts[0].split("-");
        if (dateParts.length !== 3) return null;
        
        var year = parseInt(dateParts[0], 10);
        var month = parseInt(dateParts[1], 10) - 1;
        var day = parseInt(dateParts[2], 10);
        var hour = parseInt(parts[1].replace("시", ""), 10);
        
        var d = new Date(year, month, day, hour);
        if (isNaN(d.getTime())) return null;
        return d;
      }
      
      // 일반 날짜 문자열 (예: "2025-03-20")
      var d = new Date(dateStr);
      if (isNaN(d.getTime())) return null;
      return d;
    } catch (e) {
      Logger.log("⚠️ 날짜 파싱 오류: " + dateStr + " - " + e.message);
      return null;
    }
  },
  
  format: function(date, format) {
    if (!date) return "";
    var timeZone = Session.getScriptTimeZone();
    
    switch(format) {
      case "full":
        var formatted = Utilities.formatDate(date, timeZone, "yyyy년 M월 d일 E요일");
        return formatted
          .replace("Sun", "일").replace("Mon", "월").replace("Tue", "화")
          .replace("Wed", "수").replace("Thu", "목").replace("Fri", "금")
          .replace("Sat", "토") + "요일";
        
      case "short":
        var f = Utilities.formatDate(date, timeZone, "M/d(E)");
        return f.replace("Sun", "일").replace("Mon", "월").replace("Tue", "화")
                .replace("Wed", "수").replace("Thu", "목").replace("Fri", "금")
                .replace("Sat", "토");
        
      case "time":
        return Utilities.formatDate(date, timeZone, "HH:mm");
        
      case "iso":
        return Utilities.formatDate(date, timeZone, "yyyy-MM-dd");
        
      default:
        return Utilities.formatDate(date, timeZone, "yyyy-MM-dd");
    }
  },
  
  daysBetween: function(date1, date2) {
    var d1 = new Date(date1);
    d1.setHours(0, 0, 0, 0);
    var d2 = new Date(date2);
    d2.setHours(0, 0, 0, 0);
    
    var diff = Math.abs(d2 - d1);
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  }
};


/**
 * 사용자 정의 알림 설정 함수 (새로운 함수)
 */
function setUserNotificationTime(chatId, text) {
  // 형식: /setnotify 08:00
  var timeMatch = text.match(/\/setnotify\s+(\d{1,2}):(\d{2})/);
  if (!timeMatch) {
    sendTelegramMessage(chatId, "⚠️ 시간 형식이 올바르지 않습니다. 예: `/setnotify 08:00`");
    return;
  }
  
  var hour = parseInt(timeMatch[1], 10);
  var minute = parseInt(timeMatch[2], 10);
  
  if (hour < 0 || hour > 23 || minute < 0 || minute > 59) {
    sendTelegramMessage(chatId, "⚠️ 유효하지 않은 시간입니다. 시간은 00:00부터 23:59 사이여야 합니다.");
    return;
  }
  
  // 사용자 설정 시트 가져오기 또는 생성
  var sheet = getOrCreateSheet("UserSettings", true, ["ChatID", "알림시간", "기타설정"]);
  
  // 기존 설정 확인
  var found = false;
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == chatId) {
      sheet.getRange(i + 1, 2).setValue(hour + ":" + (minute < 10 ? "0" + minute : minute));
      found = true;
      break;
    }
  }
  
  // 새 설정 추가
  if (!found) {
    sheet.appendRow([chatId, hour + ":" + (minute < 10 ? "0" + minute : minute), ""]);
  }
  
  sendTelegramMessage(chatId, "✅ 알림 시간이 " + hour + ":" + (minute < 10 ? "0" + minute : minute) + "로 설정되었습니다.");
}


/**
 * 일정을 iCal 형식으로 변환하여 사용자에게 전송 (새로운 함수)
 */
function exportCalendar(chatId, period) {
  var sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
  var data = sheet.getDataRange().getValues();
  
  if (data.length <= 1) {
    sendTelegramMessage(chatId, "⚠️ 내보낼 일정 데이터가 없습니다.");
    return;
  }
  
  var now = new Date();
  now.setHours(0, 0, 0, 0);
  
  var maxDate = new Date(now);
  if (period === "week") {
    maxDate.setDate(now.getDate() + 7);
  } else if (period === "month") {
    maxDate.setMonth(now.getMonth() + 1);
  } else {
    maxDate.setFullYear(now.getFullYear() + 1); // 최대 1년치
  }
  
  var icalContent = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//부자칼리지//스케줄//KO",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH"
  ];
  
  var eventCount = 0;
  for (var i = 1; i < data.length; i++) {
    var dateObj = new Date(data[i][0]);
    if (isNaN(dateObj.getTime())) continue;
    
    if (dateObj >= now && (period === "all" || dateObj <= maxDate)) {
      var dateStr = Utilities.formatDate(dateObj, Session.getScriptTimeZone(), "yyyyMMdd");
      var user = data[i][2] || "미정";
      
      icalContent.push("BEGIN:VEVENT");
      icalContent.push("DTSTART;VALUE=DATE:" + dateStr);
      icalContent.push("DTEND;VALUE=DATE:" + dateStr);
      icalContent.push("SUMMARY:부자칼리지 스케줄 - " + user);
      icalContent.push("DESCRIPTION:담당자: " + user);
      icalContent.push("END:VEVENT");
      
      eventCount++;
    }
  }
  
  icalContent.push("END:VCALENDAR");
  
  if (eventCount === 0) {
    sendTelegramMessage(chatId, "⚠️ 선택한 기간에 내보낼 일정이 없습니다.");
    return;
  }
  
  // 구글 드라이브에 ics 파일 생성
  var fileName = "부자칼리지_스케줄_" + Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyyMMdd") + ".ics";
  var file = DriveApp.createFile(fileName, icalContent.join("\r\n"), "text/calendar");
  
  // 파일 다운로드 URL 생성 및 전송
  var url = file.getDownloadUrl();
  sendTelegramMessage(chatId, "📅 *일정 내보내기 완료*\n\n총 " + eventCount + "개 일정이 포함되었습니다.\n\n[여기를 클릭하여 다운로드](" + url + ")", {
    parse_mode: "Markdown",
    disable_web_page_preview: false
  });
}


/**
 * 사용 통계 생성 및 전송 (새로운 함수)
 * 파일: bujacollege_schedule_bot_gs.txt에 추가
 */
function generateStatistics(chatId) {
  // 1. 밸리AI 스케줄 통계
  var scheduleSheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
  var scheduleData = scheduleSheet.getDataRange().getValues();
  
  // 2. 독서클럽 통계
  var bookClubSheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(BOOKCLUB_SHEET_NAME);
  var bookClubData = bookClubSheet.getDataRange().getValues();
  
  var recordSheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(RECORD_SHEET_NAME);
  var recordData = recordSheet.getDataRange().getValues();
  
  // 3. 변경이력 통계
  var historySheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName("밸리AI_변경이력");
  var historyData = historySheet.getDataRange().getValues();
  
  // 현재 날짜 기준으로 한 달 이내의 데이터만 분석
  var oneMonthAgo = new Date();
  oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
  
  // 1. 사용자별 할당 횟수
  var userCounts = {};
  var userList = ["김은태", "강공현", "김민지", "박경욱", "박종욱"];
  
  for (var i = 0; i < userList.length; i++) {
    userCounts[userList[i]] = 0;
  }
  
  for (var i = 1; i < scheduleData.length; i++) {
    var dateObj = new Date(scheduleData[i][0]);
    if (isNaN(dateObj.getTime())) continue;
    
    if (dateObj >= oneMonthAgo) {
      var users = scheduleData[i][2];
      if (!users) continue;
      
      users.split(",").forEach(function(user) {
        user = user.trim();
        if (userCounts[user] !== undefined) {
          userCounts[user]++;
        }
      });
    }
  }
  
  // 2. 독서클럽 참여율
  var bookClubStats = {};
  for (var i = 1; i < recordData.length; i++) {
    bookClubStats[recordData[i][0]] = {
      total: recordData[i][1] || 0
    };
  }
  
  // 3. 변경이력 통계
  var changeCount = 0;
  for (var i = 1; i < historyData.length; i++) {
    var changeDate = historyData[i][0];
    if (!(changeDate instanceof Date)) {
      changeDate = new Date(changeDate);
    }
    
    if (changeDate >= oneMonthAgo) {
      changeCount++;
    }
  }
  
  // 통계 메시지 작성
  var statsMessage = "📊 *부자칼리지 사용 통계* (최근 1개월)\n\n";
  
  // 1. 사용자별 할당 횟수
  statsMessage += "👤 *사용자별 할당 횟수*\n";
  for (var user in userCounts) {
    statsMessage += "• " + user + ": " + userCounts[user] + "회\n";
  }
  
  // 2. 독서클럽 참여율
  statsMessage += "\n📚 *독서클럽 참여 현황*\n";
  for (var user in bookClubStats) {
    statsMessage += "• " + user + ": " + bookClubStats[user].total + "회\n";
  }
  
  // 3. 변경이력 통계
  statsMessage += "\n🔄 *일정 변경 횟수*: " + changeCount + "회\n";
  
  sendTelegramMessage(chatId, statsMessage);
}

