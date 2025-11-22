// htmlが全て読み込まれてから実行
document.addEventListener('DOMContentLoaded', function () {
  
  const checkboxes = document.querySelectorAll(".task-checkbox");

  checkboxes.forEach(checkbox => {
    // changeは値が変わった時（チェック状態が変わった時）
    checkbox.addEventListener("change", function() {
      // このチェックボックスが属している一番近くのtask-itemを探して取得
      const li = this.closest(".task-item");
      // 一番近いtask-itemのタスクIDを取得
      const taskId = li.dataset.taskId;
      // チェック状態する（チェックが入っていたらtrue、入っていなければfalse）
      const isChecked = this.checked;
      // 表示（横線）の更新
      // チェックが入ったら、completedというクラスをliに追加する
      if (isChecked) {
        li.classList.add("completed");
      // チェックが外されたら、completedというクラスをliから外す
      } else {
        li.classList.remove("completed");
      }

      // サーバーに状態送信（関数を定義する前に呼んでいる：巻き上げ）
      updateTaskStatus(taskId, isChecked);
    });
  });
  // サーバーに状態を送信する関数を定義（引数にタスクIDと家事が完了したか否かが入る変数）
  function updateTaskStatus(taskId, isCompleted) {
    // 「タスク○番の完了状態を切り替えてください」とJavascriptからDjangoのサーバーにお願いしている
    fetch(`/tasks/${taskId}/toggle/`, {
      method: "POST",
      // 送るデータについて
      headers: {
        // データはJSON形式
        "Content-Type": "application/json",
        // Djangoのセキュリティ
        // ブラウザの中のcsrftokenと今送っているX-CSRFTokenを比較する
        "X-CSRFToken": getCookie("csrftoken"),
      },
      // サーバーに送る中身
      // 家事が完了しているか否かがisCompletedに入っている
      body: JSON.stringify({
        completed: isCompleted
      })
    })
    // サーバーから返事を読み取る（なくても動くが通信できたか確認するためにつける）
    // Djangoサーバーから帰ってきた返事をjavascriptのオブジェクトに変えている
    .then(response => response.json())
    // うまくいけばコンソールに「更新完了」と表示
    .then(data => {
      console.log("更新完了:", data);
    })
    // 失敗した時は「通信エラー」を表示
    .catch(error => {
      console.error("通信エラー:", error);
    });
  }

  // ブラウザに保存されている Cookie の中から、欲しい名前のものを探して取り出す関数
  // 今回はDjangoが発行したcsrftokenを探している
  function getCookie(name) {
    // 何もない状態を設定
    let cookieValue = null;
    // cookieが存在しており、空じゃなければ
    if (document.cookie && document.cookie !== "") {
      // cookieの文字列を;で分割してリストにする
      const cookies = document.cookie.split(";");
      // cookiesの値を１個ずつ取り出す
      for (let cookie of cookies) {
        // 余計なスペースを消す
        cookie = cookie.trim();
        // csrftoken=から始まるcookieであれば
        if (cookie.startsWith(name + "=")) {
          // cookieの名前部分（csrftoken=の後の部分）を取り出す
          // 取り出した文字を人間が読める形に直す
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          // ループ終了
          break;

        }
      }
    }
    // 見つけたcookieの値を関数の外に返す
    return cookieValue;
  }
});