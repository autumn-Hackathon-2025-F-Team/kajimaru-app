// htmlが全部読み込まれてから実行
document.addEventListener("DOMContentLoaded", () => {
  // 家事追加
  // モーダル本体のidを取得してcreateModalに入れる
  const createModal   = document.getElementById("createTaskModal");
  // 追加モーダルを開くボタンのidを取得してcreateButtonに入れる
  const createButton  = document.getElementById("createTaskButton");
  // モーダルを閉じるボタンのidを取得してcreateCloseに入れる
  const createClose   = document.getElementById("create-task-close");
  
  // 上記３つが全て取得できたら
  if (createModal && createButton && createClose) {
    // 家事追加ボタンが押されたらモーダルを表示させる
    createButton.addEventListener("click", () => {
      createModal.style.display = "flex";   // blockでもOK
    });
    // ×ボタンが押されたらモーダルを非表示にする
    createClose.addEventListener("click", () => {
      createModal.style.display = "none";
    });
  }

  // 家事編集
  const updateModal   = document.getElementById("updateTaskModal");
  const updateClose   = document.getElementById("update-task-close-button");
  const updateTaskId  = document.getElementById("updateTaskId");

  if (updateModal && updateClose && updateTaskId) {
    // js-open-updateがついた要素を全て取得してbuttonsに入れる（家事リストにはいくつもあるので）
    const buttons = document.querySelectorAll(".js-open-update");
    // buttonsの要素分の回数をループする
    for (let i = 0; i < buttons.length; i++) {
      // i番目の編集ボタンがクリックされたら
      buttons[i].addEventListener("click", () => {
        // 押された家事のidを取得
        const id = buttons[i].dataset.id;
        // 取得したidをtype=hiddenのinputにセットしサーバーに伝える
        updateTaskId.value = id;
        // 非表示状態の編集モーダルを表示する
        updateModal.style.display = "flex";
      });
    }
    
  

    updateClose.addEventListener("click", () => {
      updateModal.style.display = "none";
    });
  }

  
  // 家事削除
  const deleteModal   = document.getElementById("deleteTaskModal");
  const deleteClose   = document.getElementById("delete-task-close-button");
  const deleteTaskId  = document.getElementById("deleteTaskId");

  if (deleteModal && deleteClose && deleteTaskId) {
    document.querySelectorAll(".js-open-delete").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.id;
        deleteTaskId.value = id;
        deleteModal.style.display = "flex";
      });
    });

    deleteClose.addEventListener("click", () => {
      deleteModal.style.display = "none";
    });
  }
});
