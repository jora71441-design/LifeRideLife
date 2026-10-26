// === АНАТОМИЧЕСКИЙ КАЛЬКУЛЯТОР РОСТОВКИ (Smartfit, Ergon & LeMond) ===

// Таблица рекомендуемого ETT под рост и тип байка
const sizeTable = [
  { minH: 155, maxH: 162, road_race: "500–510 мм (XXS)", endurance: "505–515 мм (XXS)", gravel: "505–520 мм (XXS)" },
  { minH: 163, maxH: 170, road_race: "515–530 мм (XS)",  endurance: "520–535 мм (XS/S)", gravel: "525–540 мм (XS)" },
  { minH: 171, maxH: 178, road_race: "535–550 мм (S/M)", endurance: "540–555 мм (M)",   gravel: "545–560 мм (S/M)" },
  { minH: 179, maxH: 186, road_race: "555–570 мм (M/L)", endurance: "560–575 мм (L)",   gravel: "565–580 мм (M/L)" },
  { minH: 187, maxH: 194, road_race: "575–590 мм (L/XL)", endurance: "580–595 мм (XL)",  gravel: "585–605 мм (XL)" },
  { minH: 195, maxH: 205, road_race: "595–615 мм (XXL)", endurance: "600–615 мм (XXL)", gravel: "605–625 мм (XXL)" }
];

function setType(type) {
  window.currentBikeType = type;
  const btnRoad = document.getElementById('btn-road');
  const btnEndurance = document.getElementById('btn-endurance');
  const btnGravel = document.getElementById('btn-gravel');

  if (btnRoad) btnRoad.classList.toggle('active', type === 'road_race');
  if (btnEndurance) btnEndurance.classList.toggle('active', type === 'endurance');
  if (btnGravel) btnGravel.classList.toggle('active', type === 'gravel');
  
  updateCalc();
}

function updateCalc() {
  const heightEl = document.getElementById('calc-height');
  const inseamEl = document.getElementById('calc-inseam');
  if (!heightEl || !inseamEl) return;
  if (window.ym) ym(112661781, 'reachGoal', 'calc_ett');
  
  const height = parseInt(heightEl.value);
  const inseam = parseInt(inseamEl.value);

  // Обновляем значения над слайдерами
  const valHeight = document.getElementById('val-height');
  const valInseam = document.getElementById('val-inseam');
  if (valHeight) valHeight.innerText = height;
  if (valInseam) valInseam.innerText = inseam;

  // Высота седла по методу Greg LeMond
  const saddleHeight = (inseam * 0.883).toFixed(1);
  const resSaddle = document.getElementById('res-saddle');
  if (resSaddle) resSaddle.innerText = `${saddleHeight} см`;

  // Поиск подходящего диапазона ETT
  let matchedData = sizeTable.find(row => height >= row.minH && height <= row.maxH);
  if (!matchedData) {
    matchedData = height < 155 ? sizeTable[0] : sizeTable[sizeTable.length - 1];
  }

  const typeKey = window.currentBikeType || 'road_race';
  const ettResult = matchedData[typeKey] || matchedData['road_race'];

  const resSize = document.getElementById('res-size');
  if (resSize) resSize.innerText = ettResult;

  // Анализ анатомических пропорций
  const ratio = inseam / height;
  let anatomyText = "";
  let tipText = "";

  if (ratio > 0.470) {
    anatomyText = "🦵 Длинные ноги относительно торса (высокий инсим).";
    tipText = "При пограничном росте выбирайте меньшую нижнюю границу ETT. Длину посадки компенсируйте высотой седла, а Reach регулируйте выносом 80–90 мм.";
  } else if (ratio < 0.445) {
    anatomyText = "🏃‍♂️ Удлиненный торс относительно длины ног.";
    tipText = "Рама выбирается с акцентом на ETT (длину). Рассмотрите верхнее значение диапазона ETT или увеличьте длину выноса до 110–120 мм.";
  } else {
    anatomyText = "⚖️ Пропорциональное телосложение (стандартный антропометрический баланс).";
    tipText = "Вам идеально подходит указанный диапазон ETT. Рекомендуемая базовая длина выноса: 100–110 мм.";
  }

  const resAnatomy = document.getElementById('res-anatomy');
  const resTip = document.getElementById('res-tip');
  if (resAnatomy) resAnatomy.innerText = anatomyText;
  if (resTip) resTip.innerText = tipText;

  // Текст кнопки подбора
  const btnShow = document.getElementById('btn-show-matched-bikes');
  if (btnShow) {
    let rangeText = "170–180 см";
    if (height < 160) rangeText = "150–160 см";
    else if (height < 170) rangeText = "160–170 см";
    else if (height < 180) rangeText = "170–180 см";
    else if (height < 190) rangeText = "180–190 см";
    else rangeText = "190–200 см";

    btnShow.innerText = `🚴 Подобрали для тебя! (${rangeText})`;
  }
}

function applyMatchedBikeFilter() {
  const heightEl = document.getElementById('calc-height');
  if (!heightEl) return;
  if (window.ym) ym(112661781, 'reachGoal', 'click_matched');

  const height = parseInt(heightEl.value);
  let targetTag = '#170_180cm';

  if (height < 160) targetTag = '#150_160cm';
  else if (height < 170) targetTag = '#160_170cm';
  else if (height < 180) targetTag = '#170_180cm';
  else if (height < 190) targetTag = '#180_190cm';
  else targetTag = '#190_200cm';

  if (typeof setCategory === 'function') {
    setCategory('bikes');
  }

  if (window.selectedTags) {
    window.selectedTags.add(targetTag);
  }

  document.querySelectorAll('.tag-pill').forEach(pill => {
    const onclickAttr = pill.getAttribute('onclick') || '';
    if (onclickAttr.includes(`'${targetTag}'`)) {
      pill.classList.add('active');
    } else {
      pill.classList.remove('active');
    }
  });

  if (typeof renderCatalog === 'function') {
    renderCatalog();
  }

  const catalogEl = document.getElementById('catalog');
  if (catalogEl) {
    catalogEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

function shareCalculatorLink() {
  const botUsername = "liferidelife_bot";
  const directLink = `https://t.me/${botUsername}?startapp=calculator`;
  const shareText = "🚴‍♂️ Пользуйся удобным калькулятором подбора размера велосипеда, ETT и высоты седла в LifeRideLife:";
  const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(directLink)}&text=${encodeURIComponent(shareText)}`;
  
  if (window.Telegram?.WebApp?.openTelegramLink) {
    window.Telegram.WebApp.openTelegramLink(shareUrl);
  } else {
    window.open(shareUrl, '_blank');
  }
}
