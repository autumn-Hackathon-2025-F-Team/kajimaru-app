// htmlが全て読み込まれてから実行
document.addEventListener('DOMContentLoaded', function () {
  // 変数todayは現在の日時を示すDateオブジェクトになる
  const today =  new Date();
  // 今日の月を取得
  const month = today.getMonth() + 1;
  // 今日の日にちを取得
  const date = today.getDate();
  const todayHouseworklist = document.getElementById("today_houseworklist");
  todayHouseworklist.textContent = `${month}月${date}日`;
    

  // データベースに登録されている当日の家事と担当者を取得して表示


});