const ctx = document.getElementById("family_chart");
  const myDoughnutChart= new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ["父", "母", "娘", "息子"], //データ項目のラベル
      datasets: [{
          backgroundColor: [
              "#CD7257",
              "#ED6C00",
              "#EC6D56",
              "#F6BBA6"
          ],
          data: [45, 32, 18, 5] //グラフのデータ
      }]
    },
    options: {
      title: {
        display: true,
        //グラフタイトル
        text: '家族の家事達成率'
      }
    }
  });