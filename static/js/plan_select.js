const plan_card = document.querySelectorAll(".plan-card");
const carousel = document.getElementById("carousel");
const dotsContainer = document.getElementById("dots");
const hiddenInput = document.getElementById("selected_plan_index");

const planNumber = plan_card.length;

// ドットを作成
function createdots() {
  for (let i = 0; i < planNumber; i++) {
    dotsContainer.innerHTML += `<div class="indicator w-3 h-3 bg-gray-200 rounded-full transition-colors duration-300"></div>`;
  }
}


createdots();
const indicators = document.querySelectorAll(".indicator");

// 距離計算
function updatedots() {
  const carouselRect = carousel.getBoundingClientRect();
  const carouselCenter = carouselRect.left + carouselRect.width / 2;

  let closestIndex = 0;
  let closestDistance = Infinity;

  plan_card.forEach((card, index) => {
    const cardRect = card.getBoundingClientRect();
    const cardCenter = cardRect.left + cardRect.width / 2;
    const distance = Math.abs(carouselCenter - cardCenter);

    // 
    if (distance < closestDistance) {
      closestDistance = distance;
      closestIndex = index;
    }
  });

  // 選択中ドットの色更新
  indicators.forEach((dot) => {
    dot.classList.remove("bg-green-600", "scale-110");
    dot.classList.add("bg-gray-200");
  });
  indicators[closestIndex].classList.remove("bg-gray-200");
  indicators[closestIndex].classList.add("bg-green-600", "scale-110");

  // formのinputのvalueに中心のカードのindexを代入
  const selectedPlanId = plan_card[closestIndex].dataset.index;
  hiddenInput.value = selectedPlanId;
}

// ページを開いた時とスクロールが行われるたびにスクリプトを実行
updatedots();
carousel.addEventListener("scroll", updatedots);