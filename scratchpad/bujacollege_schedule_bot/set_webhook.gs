function setTelegramWebhook() {
  var botToken = "7524488237:AAHqO35TON-hdu9HjstMfkZLHSa5NhaKww4";
  var webhookUrl = "https://script.google.com/macros/s/AKfycby_v30pLZvZ6qIvsKyXveP4tpWPDP6cIe9JXyjybgrfljYCzua29Tpt5NOG5iy_7u92/exec";
  
  // 기존 웹훅 삭제
  var deleteUrl = "https://api.telegram.org/bot" + botToken + "/deleteWebhook";
  UrlFetchApp.fetch(deleteUrl);
  Logger.log("✅ 기존 웹훅 삭제 완료");

  // 새로운 웹훅 설정
  var setUrl = "https://api.telegram.org/bot" + botToken + "/setWebhook?url=" + encodeURIComponent(webhookUrl);
  var response = UrlFetchApp.fetch(setUrl);
  Logger.log("✅ 새로운 웹훅 설정 완료: " + response.getContentText());

  // 설정 확인
  var getInfoUrl = "https://api.telegram.org/bot" + botToken + "/getWebhookInfo";
  var webhookInfo = UrlFetchApp.fetch(getInfoUrl);
  Logger.log("📢 웹훅 정보: " + webhookInfo.getContentText());
}
