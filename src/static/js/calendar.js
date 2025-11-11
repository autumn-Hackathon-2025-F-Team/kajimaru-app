document.addEventListener('DOMContentLoaded', function () {
      var calendarEl = document.getElementById('calendar');
      var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        locale: 'ja',
        allDaySlot: false,
        nowIndicator: true,
        headerToolbar: {
          left: 'prev,next',
          center: 'title',
          right: 'timeGridWeek,timeGridDay'
        },
        slotMinTime: '04:00:00',
        slotMaxTime: '22:00:00',
      });
      calendar.render();
    });
