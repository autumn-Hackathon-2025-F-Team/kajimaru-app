// const weeks = ['日', '月', '火', '水', '木', '金', '土'];
// const date = new Date();
// const year = date.getFullYear();
// const month = date.getMonth()+1;
// const today = date.getDate();
// const startDate = new Date(year, month - 1, 1);
// const endDate = new Date(year, month, 0);
// const endDayCount = endDate.getDate();
// const startDay = startDate.getDay();
// let dayCount = 1;
// let calendarHtml = '' //;
// calendarHtml += '<h1>' + year + '年' + month + '月' + today + '日' + '</h1>';
// calendarHtml += '<table>';

// for (let i = 0; i < weeks.length; i++) {
//     calendarHtml += '<td>' + weeks[i] + '</td>'
// }

// for (let w = 0; w <  6; w++) {
//     calendarHtml += '<tr>'

//     for (let d = 0; d < 7; d++) {
//         if (w == 0 && d < startDay) {
//             calendarHtml += '<td></td>'
//         } else if (dayCount > endDayCount) {
//             calendarHtml += '<td></td>'
//         } else if (dayCount === today) {
//             calendarHtml += "<td class='today'>" + dayCount + "</td>"
//             dayCount++
//         } else {
//             calendarHtml += '<td>' + dayCount + '</td>'
//             dayCount++
//         }
//     }
//     calendarHtml += '</tr>'
// }
// calendarHtml += '</table>'

// document.querySelector('#calendar').innerHTML = calendarHtml



// static/js/calendar.js
document.addEventListener('DOMContentLoaded', () => {

    const mount = document.getElementById('calendar');
    const weeks = ['日', '月', '火', '水', '木', '金', '土'];
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;
    const today = now.getDate();

    const startDate = new Date(year, month - 1, 1);
    const endDate = new Date(year, month, 0);
    const endDayCount = endDate.getDate();
    const startDay = startDate.getDay();

    let dayCount = 1;
    let html = '';

    html += '<h1>' + year + '年' + month + '月' + today + '日' + '</h1>';
    html += '<table>';
    html += '<thead><tr>';
    for (let i = 0; i < weeks.length; i++) {
      html += '<th>' + weeks[i] + '</th>';
    }
    html += '</tr></thead><tbody>';

    for (let w = 0; w < 6; w++) {
      html += '<tr>';
      for (let d = 0; d < 7; d++) {
        if (w === 0 && d < startDay) {
          html += '<td></td>';
        } else if (dayCount > endDayCount) {
          html += '<td></td>';
        } else {
          html += (dayCount === today)
            ? "<td class='today'>" + dayCount + '</td>'
            : '<td>' + dayCount + '</td>';
          dayCount++;
        }
      }
      html += '</tr>';
    }
    html += '</tbody></table>';

    mount.innerHTML = html;

});

