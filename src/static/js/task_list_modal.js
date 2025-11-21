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
  const updateForm    = document.getElementById("updateTaskForm");

  if (updateModal && updateClose && updateTaskId && updateForm) {
    // js-open-updateがついた要素を全て取得してbuttonsに入れる（家事リストにはいくつもあるので）
    const buttons = document.querySelectorAll(".js-open-update");
    // buttonsの要素分の回数をループする
    for (let i = 0; i < buttons.length; i++) {
      // i番目の編集ボタンがクリックされたら
      buttons[i].addEventListener("click", () => {
        // 押された家事のid,name,weekdays,weightを取得
        const id = buttons[i].dataset.id;
        const name = buttons[i].dataset.name;
        const frequency = buttons[i].dataset.frequency;
        const homemakers = buttons[i].dataset.homemakers;
        const weight = buttons[i].dataset.weight;
        // 取得したidをtype=hiddenのinputにセットしサーバーに伝える
        updateTaskId.value = id;

        const nameInput   = updateForm.querySelector('[name="task_name"]');
        if (nameInput) {
          nameInput.value = name || "";
        }
        const freqInputs  = updateForm.querySelectorAll('[name="frequency"]');
        // if (freqInputs) {
        //   freqInput.value = frequency || "";
        // }
        // 曜日（frequency）
        if (freqInputs.length > 0 && frequency) {
          const freq = Number(frequency);  // "21" → 21

          freqInputs.forEach((checkbox) => {
            const bit = Number(checkbox.value);  // 1,2,4,8,...
            checkbox.checked = (freq & bit) > 0;
          });
        }


        const homemakersInputs = updateForm.querySelectorAll('[name="homemakers"]');
        // if (homemakersInputs) {
        //   homemakersInput.value = homemakers || "";
        // }
        // 担当者（homemakers）
        if (homemakersInputs.length > 0 && homemakers) {
          const selected = homemakers.split(",");  // "1,3,5" → ["1","3","5"]

          homemakersInputs.forEach((checkbox) => {
            checkbox.checked = selected.includes(checkbox.value);
          });
        }

        const weightInput = updateForm.querySelector('[name="weight"]');
        if (weightInput) {
          weightInput.value = weight || "";
        }
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
