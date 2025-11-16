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
    let mondaySet = today.getDay();
    // もし今日が０（日曜）なら、modaySetには６を代入。そうでないなら、modaySetから１引いた数を代入
    if (mondaySet === 0) {
      mondaySet = 6;
    } else {
      mondaySet = mondaySet - 1
    }
    // todayをコピーした新しいmondayというDateオブジェクトを作る
    const monday = new Date(today);
    // 今日の日付から曜日番号を引いて月曜日の日付を算出。setDate()でmondayに日付を入れ直している
    monday.setDate(today.getDate()- mondaySet);
    // 1週間分繰り返す
    for (let i = 0; i < 7; i++) {
      // mondayのコピーを作る（new Dateを使う理由はmondayを元に別のDateオブジェクトを作るため）
      let d = new Date(monday);
      // 月曜にi日追加して、月から日の１週間分作る
      d.setDate(monday.getDate()+i);
      // weekに入れる
      week.push(d);
    }
    // 最後に返す
    return week
  }
  // htmlの.week_dateクラスがついた要素を全部取得してweek_day変数に入れる
  const weekCells = document.querySelectorAll('.week_date');
  // 月曜日から始まる一週間の日にちを取得してweekDates変数に入れる
  const weekDates = getWeek();
  // weekDatesを0から順番にみて、同じインデックス番号（i）のところに書き込む
  for (let i = 0; i < weekDates.length; i ++) {
    // weekDates[i]の日にちだけを取り出す
    // 同じインデックス番号の対応するセル（week_day[i]）の中身を書き換える
    weekCells[i].textContent = weekDates[i].getDate();
  };

  // ②タイトルに入れる月を取得する
  const today = new Date();
  const month = today.getMonth() + 1;
  const calendarTitle = document.getElementById("calendar");
  calendarTitle.textContent = `${month}月：週ローテ表`;

  // ③データベースに登録されている家事と担当者を取得、行を作って入れる


});