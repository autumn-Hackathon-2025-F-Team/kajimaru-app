const complete = JSON.parse('{{ completion_rate_family | default:0 }}');
const incomplete = 100 - complete;

const ctx = document.getElementById("family_chart");
  const myDoughnutChart= new Chart(ctx, {
  type: 'doughnut',
    data: {
      labels: ["達成", "未達成"], //データ項目のラベル(データを入れ込む)
      datasets: [{
          backgroundColor: [
              "#c97586",
              "#bbbcde",
          ],
          data: [complete,incomplete] //グラフのデータ（データを入れ込む）
      }]
    },
    options: {
      plugins: {
        title: {
          display: true,
          //グラフタイトル
          text: '家族の家事達成率'
        }
      }
    }
  });

   // options: {
    //   plugins: {
    //       colorschemes: {
    //       scheme: 'brewer.Paired12'
    //       }
    //   }
    // }