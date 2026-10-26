// === ОСНОВНОЙ МОДУЛЬ ПРИЛОЖЕНИЯ LIFERIDELIFE ===

let postsData = [];
let currentCategory = 'bikes';
let selectedTags = new Set();
window.selectedTags = selectedTags;
let currentBikeType = 'road_race';
window.currentBikeType = currentBikeType;
let hasHandledDeepLink = false;

const bikeFactors = {
  'road_race': 0.665,
  'endurance': 0.65,
  'gravel': 0.63
};

const tg = window.Telegram?.WebApp;
if (tg) {
  tg.ready();
  tg.expand();
}

const fallbackImg = 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600';

// Нативный шеринг велосипеда в Telegram
function shareBike(bikeId, bikeTitle, bikePrice) {
  const botUsername = "liferidelife_bot";
  const cleanId = String(bikeId).replace(/\s+/g, '_');
  const directLink = `https://t.me/${botUsername}?startapp=bike_${encodeURIComponent(cleanId)}`;
  const shareText = `Зацени велосипед в LifeRideLife: ${bikeTitle} (${bikePrice}) 🚲🔥`;
  const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(directLink)}&text=${encodeURIComponent(shareText)}`;
  
  if (window.Telegram?.WebApp?.openTelegramLink) {
    window.Telegram.WebApp.openTelegramLink(shareUrl);
  } else {
    window.open(shareUrl, '_blank');
  }
}

// Обработка диплинка товара
function handleBikeDeepLink(startParam) {
  if (hasHandledDeepLink || !postsData || postsData.length === 0) return;

  const rawId = decodeURIComponent(startParam.replace('bike_', '')).trim().toLowerCase();

  const targetBike = postsData.find(post => {
    const bId = String(post.id || '').toLowerCase();
    const bTitle = String(post.title || '').toLowerCase().replace(/\s+/g, '_');
    return bId === rawId || bTitle.includes(rawId) || rawId.includes(bTitle);
  });

  if (targetBike) {
    hasHandledDeepLink = true;

    let targetCat = (targetBike.category || 'bikes').toLowerCase();
    if (targetCat === 'reviews' && !targetBike.tags?.some(t => t.includes('отзыв'))) {
      targetCat = 'bikes';
    }

    setCategory(targetCat);

    setTimeout(() => {
      const card = document.getElementById(`bike-${targetBike.id}`);
      if (card) {
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        card.style.border = '2px solid #24a1de';
        card.style.boxShadow = '0 0 18px rgba(36, 161, 222, 0.7)';
      }
    }, 350);
  }
}

// Внешние ссылки с Яндекс Метрикой
function openExternalLink(url) {
  if (window.ym) {
    ym(112661781, 'reachGoal', 'click_fititi');
  }
  if (window.Telegram?.WebApp?.openLink) {
    window.Telegram.WebApp.openLink(url);
  } else {
    window.open(url, '_blank');
  }
}

// Переключение главных категорий
function setCategory(cat) {
  currentCategory = cat;

  if (cat === 'winspace') {
    if (typeof openWinspaceCatalog === 'function') {
      openWinspaceCatalog('complete', 'all');
    } else {
      console.error('Функция openWinspaceCatalog не найдена!');
    }
    return;
  }

  selectedTags.clear();
  document.querySelectorAll('.tag-pill').forEach(pill => pill.classList.remove('active'));

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('active');
    const onclickAttr = btn.getAttribute('onclick') || '';
    const dataCat = btn.getAttribute('data-cat') || '';
    if (dataCat === cat || onclickAttr.includes(`'${cat}'`)) {
      btn.classList.add('active');
    }
  });

  const filtersDiv = document.getElementById('filters');
  if (filtersDiv) {
    filtersDiv.style.display = (cat === 'bikes') ? 'block' : 'none';
  }

  const calcDiv = document.getElementById('size-calculator');
  const fititiDiv = document.getElementById('fititi-card');

  if (cat === 'guides') {
    if (calcDiv) {
      calcDiv.style.display = 'block';
      if (typeof updateCalc === 'function') updateCalc();
    }
    if (fititiDiv) fititiDiv.style.display = 'block';
  } else {
    if (calcDiv) calcDiv.style.display = 'none';
    if (fititiDiv) fititiDiv.style.display = 'none';
  }

  renderCatalog();
}

// Переключение фильтра-тега
function toggleTag(el, tag) {
  if (selectedTags.has(tag)) {
    selectedTags.delete(tag);
    el.classList.remove('active');
  } else {
    selectedTags.add(tag);
    el.classList.add('active');
  }
  renderCatalog();
}

// Загрузка products.json
async function loadProducts() {
  const catalogEl = document.getElementById('catalog');
  try {
    const response = await fetch('./products.json?v=' + Date.now());
    if (!response.ok) throw new Error('products.json not found');
    
    postsData = await response.json();
    
    const startParam = tg?.initDataUnsafe?.start_param;
    if (startParam === 'calculator') {
      setCategory('guides');
      setTimeout(() => {
        const calcEl = document.getElementById('size-calculator');
        if (calcEl) {
          calcEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 300);
    } else if (startParam && startParam.startsWith('bike_')) {
      renderCatalog();
      handleBikeDeepLink(startParam);
    } else if (startParam && ['bikes', 'upgrade_kits', 'components', 'guides', 'reviews', 'winspace'].includes(startParam)) {
      setCategory(startParam);
    } else {
      renderCatalog();
    }
  } catch (err) {
    console.error(err);
    if (catalogEl) {
      catalogEl.innerHTML = '<div class="status-msg">⚠️ Ошибка загрузки базы товаров. Проверьте наличие products.json.</div>';
    }
  }
}

// Отрисовка каталога
function renderCatalog() {
  const catalogEl = document.getElementById('catalog');
  if (!catalogEl) return;

  if (!postsData || postsData.length === 0) {
    catalogEl.innerHTML = '<div class="status-msg">⏳ Загрузка базы товаров...</div>';
    return;
  }

  const filtered = postsData.filter(post => {
    let cat = (post.category || 'bikes').toLowerCase();
    const tags = (post.tags || []).map(t => t.toLowerCase());
    const raw = (post.rawText || '').toLowerCase();

    const isReview = tags.some(t => t.includes('отзыв')) || raw.includes('#отзыв');
    const isGuide = tags.some(t => t.includes('полезное') || t.includes('гайд')) || raw.includes('#полезное') || raw.includes('#гайд');
    
    if (isReview) {
      cat = 'reviews';
    } else if (isGuide) {
      cat = 'guides';
    } else if (cat === 'reviews' || cat === 'guides') {
      cat = 'bikes'; 
    }

    if (currentCategory !== cat) return false;

    for (let tag of selectedTags) {
      const cleanTag = tag.toLowerCase().replace('к', 'k');
      const match = tags.some(t => t.includes(cleanTag)) || raw.includes(cleanTag);
      if (!match) return false;
    }

    return true;
  });

  if (filtered.length === 0) {
    catalogEl.innerHTML = '<div class="status-msg">🚴‍♂️ Ничего не найдено по выбранным фильтрам</div>';
    return;
  }

  catalogEl.innerHTML = filtered.map(post => {
    const titleText = post.title || 'Товар LifeRideLife';
    const imgUrl = post.imgUrl || fallbackImg;

    return `
      <div class="card" id="bike-${post.id}">
        <img
          src="${imgUrl}" 
          class="card-img" 
          alt="${titleText}" 
          loading="lazy"
          onerror="this.onerror=null; this.src='${fallbackImg}';"
        >
        <div class="card-body">
          <div class="card-title">${titleText}</div>
          <div class="card-tags">${post.originalTagsText || ''}</div>
          <div class="card-footer">
            <div class="card-price">${post.price || 'По запросу'}</div>
            <div class="badge">🟢 в наличии / под заказ</div>
          </div>
          <div class="card-actions" style="display: flex; gap: 4px; align-items: center; margin-top: 8px;">
            <a href="${post.postUrl || 'https://t.me/LifeRideLife'}" target="_blank" class="btn btn-secondary" style="flex: 1; text-align: center; padding: 8px 2px; font-size: 11px;">📖 Пост</a>
            <a href="https://t.me/Piti4?text=${encodeURIComponent('Здравствуйте! Интересует: ' + titleText + '\n' + (post.postUrl || ''))}" target="_blank" class="btn btn-primary" style="flex: 1; text-align: center; padding: 8px 2px; font-size: 11px;">💬 Обсудить</a>
            <button onclick="shareBike('${post.id || post.title}', '${titleText.replace(/'/g, "\\'")}', '${post.price || 'По запросу'}')" class="btn" style="flex: 1; padding: 8px 2px; background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: #fff; cursor: pointer; font-size: 11px; text-align: center;">🔗 Отправить</button>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// Запуск при загрузке DOM
document.addEventListener("DOMContentLoaded", () => {
  loadProducts();
});
