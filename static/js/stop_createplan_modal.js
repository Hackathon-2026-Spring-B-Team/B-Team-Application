document.addEventListener('DOMContentLoaded', () => {
  const openBtn = document.getElementById('cancelOpenBtn'); // 左上の×ボタン
  const closeBtn = document.getElementById('cancelCloseBtn'); // キャンセルボタン
  const modal = document.getElementById('cancelModal'); // モーダル表示中の半透明の黒い背景
  const modalCard = document.getElementById('cancelModalCard'); // モーダルのカード本体

  // モーダルを開く処理
  openBtn.addEventListener('click', () => {
    modal.classList.remove('hidden');
    setTimeout(() => {
      modal.classList.remove('opacity-0');
      modalCard.classList.remove('scale-95');
      modalCard.classList.add('scale-100');
    }, 10);
  });

  // モーダルを閉じる処理
  const closeModal = () => {
    modal.classList.add('opacity-0');
    modalCard.classList.remove('scale-100');
    modalCard.classList.add('scale-95');
    
    setTimeout(() => {
      modal.classList.add('hidden');
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
});