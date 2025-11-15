// document.addEventListener('DOMContentLoaded', function () {
//       var calendarEl = document.getElementById('calendar');
//       var calendar = new FullCalendar.Calendar(calendarEl, {
//         initialView: 'timeGridWeek',
//         locale: 'ja',
//         allDaySlot: false,
//         nowIndicator: true,
//         headerToolbar: {
//           left: 'prev,next',
//           center: 'title',
//           right: 'timeGridWeek,timeGridDay'
//         },
//         slotMinTime: '04:00:00',
//         slotMaxTime: '22:00:00',
//       });
//       calendar.render();
//     });

// htmlが全て読み込まれてから実行
document.addEventListener('DOMContentLoaded', function () {
  // ①毎週の日にちを取得する
  // 当日から１週間分の日付を取得
  function getWeek(){
    const week = [];
    // 変数todayは現在の日時を示すDateオブジェクトになる
    const today =  new Date();
    // 曜日の番号を取得（今日が週の中で何番目か）
    const date = today.getDay();
    // todayをコピーした新しいsundayというDateオブジェクトを作る
    const sunday = new Date(today);
    // 今日の日付から曜日番号を引いて日曜日の日付を算出。setDate()でsundayに日付を入れ直している
    sunday.setDate(today.getDate()- date);
    // 1週間分繰り返す
    for (let i = 0; i < 7; i++) {
      // sundayのコピーを作る（new Dateを使う理由はsundayを元に別のDateオブジェクトを作るため）
      let d = new Date(sunday);
      // 日曜日にi日追加して一、日から土の１週間分作る
      d.setDate(sunday.getDate()+i);
      // weekに入れる
      week.push(d);
    }
    // 最後に返す
    return week
  }
  // htmlの.week_dateクラスがついた要素を全部取得してweek_day変数に入れる
  const week_day = document.querySelectorAll('.week_date');
  // 日曜日から始まる一週間の日にちを取得してweekDates変数に入れる
  const weekDates = getWeek();
  // weekDatesを0から順番にみて、同じインデックス番号（i）のところに書き込む
  for (let i = 0; i < weekDates.length; i ++) {
    // weekDates[i]の日にちだけを取り出す
    // 同じインデックス番号の対応するセル（week_day[i]）の中身を書き換える
    week_day[i].textContent = weekDates[i].getDate();
  };

  // ②タイトルに入れる月を取得する
  const today = new Date();
  const month = today.getMonth() + 1;
  const calenderTitle = document.getElementById("calender");
  calenderTitle.textContent = `${month}月：週ローテ表`;

  // ③データベースに登録されている家事と担当者を取得、行を作って入れる


});