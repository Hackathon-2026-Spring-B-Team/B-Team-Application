// HTMLを全て読み取ってから実行
document.addEventListener('DOMContentLoaded', () => {
  const evalButtons = document.querySelectorAll('.eval-btn'); // ページ内の全てのボタンを取得
  const hiddenInput = document.getElementById('evaluation_input');

  // 全ての理解度ボタンを対象に処理
  evalButtons.forEach(button => {
    // ボタンの見た目の切り替え
    button.addEventListener('click', () => {
      // ボタンの見た目の切り替え
      const container = button.closest('.eval-container'); // クリックされたボタンのあるコンテナを探す
      const siblings = container.querySelectorAll('.eval-btn'); // そのコンテナ内のボタンを全て格納
      
      // 全てのボタンを未選択の白にする
      siblings.forEach(btn => {
        btn.classList.remove('bg-green-600', 'text-white', 'border-transparent');
        btn.classList.add('bg-white', 'text-gray-600', 'border-gray-200');
      });
      // クリックされているボタンのみ選択中の緑にする
      button.classList.remove('bg-white', 'text-gray-600', 'border-gray-200');
      button.classList.add('bg-green-600', 'text-white', 'border-transparent');

      // 隠し入力欄の値を、押されたボタンの data-value に書き換える！
      hiddenInput.value = button.getAttribute('data-value');
    });
  });
});