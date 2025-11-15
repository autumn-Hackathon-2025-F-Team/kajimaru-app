const ctx = document.getElementById("family_chart");
  const myDoughnutChart= new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ["父", "母", "娘", "息子","孫"], //データ項目のラベル(データを入れ込む)
      datasets: [{
          
          data: [5, 5, 18, 5, 5] //グラフのデータ（データを入れ込む）
      }]
    },
    options: {
      title: {
        display: true,
        //グラフタイトル
        text: '家族の家事達成率'
      }
    },
    options: {
      plugins: {
          colorschemes: {
          scheme: 'brewer.Paired12'
          }
      }
    }
  });