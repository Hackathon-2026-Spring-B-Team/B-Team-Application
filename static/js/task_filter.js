// HTMLを全て読み取ってから実行
document.addEventListener('DOMContentLoaded', () => {
  const buttons = document.querySelectorAll('.filter-btn'); // ページ内の全てのボタンを取得

  // 全てのボタンを対象に処理
  buttons.forEach(button => {

    // ボタンがクリックされると以下の処理を実行
    button.addEventListener('click', () => {
      
      // ボタンの見た目の切り替え
      const container = button.closest('.filter-container'); // クリックされたボタンのあるコンテナを探す
      const siblingButtons = container.querySelectorAll('.filter-btn'); // そのコンテナ内のボタンを全て格納
      
      // 全てのボタンを未選択の白にする
      siblingButtons.forEach(btn => {
        btn.classList.remove('bg-green-600', 'text-white');
        btn.classList.add('bg-white', 'text-gray-600', 'border', 'border-gray-200');
      });
      // クリックされているボタンのみ選択中の緑にする
      button.classList.remove('bg-white', 'text-gray-600', 'border', 'border-gray-200');
      button.classList.add('bg-green-600', 'text-white');

      // 絞り込み処理（押されたボタンのトグルだけを取得）
      const target = button.getAttribute('data-target'); // フィルターボタンに設定されたターゲットを取得
      const filterType = container.getAttribute('data-filter-type'); //フィルターのタイプを取得
      
      const parentDetails = button.closest('details'); // 自分がいるトグルを取得
      const cardsInThisToggle = parentDetails.querySelectorAll('.task-card'); // その中のカードだけを取得
      
      // 今日の日付を取得
      const today = new Date();
      const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
      
      // カードの判別と表示・非表示
      cardsInThisToggle.forEach(card => {

        const endDate = card.getAttribute('data-end-date');
        const evaluation = card.getAttribute('data-evaluation')


        let isShow = false;

        if (target === 'all') {
          isShow = true;
        } 

        // 期間別フィルター用処理
        else if (filterType === 'period') {
          
          if (target === '遅延') {
            if (endDate < todayStr && evaluation === '0') {
              isShow = true;
            }
          } 
          else if (target === 'これまで') {
            if (endDate < todayStr || evaluation !== '0') {
              isShow = true;
            }
          } 
          else if (target === 'これから') {
            if (endDate >= todayStr && evaluation === '0') {
              isShow = true;
            }
          }
        } 

        // 理解度別フィルター用処理
        else if (filterType === 'evaluation') {
          if (target === evaluation) {
            isShow = true;
          }
        }

        // 表示・非表示の切り替え
        if (isShow) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }

      });

    });
  });
});