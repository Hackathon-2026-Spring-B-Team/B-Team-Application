document.addEventListener('DOMContentLoaded', () => {
  const openBtns = document.querySelectorAll('.deleteOpenBtn'); // ゴミ箱ボタン
  const closeBtn = document.getElementById('deleteCancelBtn'); //キャンセルボタン
  const confirmBtn = document.getElementById('deleteConfirmBtn'); // 削除ボタン
  const modal = document.getElementById('deleteModal'); // モーダル表示中の半透明の黒い背景
  const modalCard = document.getElementById('deleteModalCard'); // モーダルのカード本体


  // モーダルを開く処理
  openBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    // 押されたゴミ箱が持っているURLを取得
    const targetUrl = btn.getAttribute('data-url');
    
    // モーダル内のformの送信先（action）に、そのURLをセット！
    deleteForm.setAttribute('action', targetUrl);

    // モーダルを開く
    modal.classList.remove('hidden');
    setTimeout(() => {
      modal.classList.remove('opacity-0');
      modalCard.classList.remove('scale-95');
      modalCard.classList.add('scale-100');
    }, 10);
  });
});

  // モーダルを閉じる処理
  const closeModal = () => {

    //開く処理と逆
    modal.classList.add('opacity-0');
    modalCard.classList.remove('scale-100');
    modalCard.classList.add('scale-95');
    
    // 300ミリ秒(duration-300)アニメーション後消える
    setTimeout(() => {
      modal.classList.add('hidden');
      deleteForm.setAttribute('action', ''); // formのURLが空の状態で閉じるように
    }, 300); 
  };

  // キャンセルボタンを押すと閉じる
  closeBtn.addEventListener('click', closeModal);

  // モーダルの外側を押すと閉じる
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeModal();
    }
  });

  // 二重送信防止の処理（連打対策） ===
  deleteForm.addEventListener('submit', () => {
  // 送信ボタンを無効化（クリックできないようにする）
  confirmBtn.disabled = true;
  
  // 見た目を「グレー」にして「削除中...」のテキストに変更
  confirmBtn.classList.remove('bg-negative-red', 'hover:bg-red-700');
  confirmBtn.classList.add('bg-gray-300', 'cursor-not-allowed');
  confirmBtn.textContent = '削除中...';
  });
});