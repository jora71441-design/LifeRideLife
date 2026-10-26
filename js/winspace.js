// === КАТАЛОГ И КОНФИГУРАТОР WINSPACE & LÚN ===

if (typeof window.winspaceState === 'undefined') {
  window.winspaceState = { subCat: 'complete', profile: 'all' };
}

function openWinspaceCatalog(subCat = window.winspaceState.subCat, profile = window.winspaceState.profile) {
  window.winspaceState.subCat = subCat;
  window.winspaceState.profile = profile;

  // 1. Скрываем стандартные фильтры и калькуляторы
  const filtersDiv = document.getElementById('filters');
  const calcDiv = document.getElementById('size-calculator');
  const fititiDiv = document.getElementById('fititi-card');
  if (filtersDiv) filtersDiv.style.display = 'none';
  if (calcDiv) calcDiv.style.display = 'none';
  if (fititiDiv) fititiDiv.style.display = 'none';

  // Снимаем активную подсветку с главных вкладок
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

  const container = document.getElementById('products-container') || document.querySelector('.products-grid') || document.getElementById('catalog');

  if (!container || !window.WINSPACE_CATALOG) {
    console.error('Контейнер или база Winspace не найдены');
    return;
  }

  // Карта соответствия чипсов профилей категориям из winspaceCatalog.js
  const profileMap = {
    'aero': ['road_aero', 'aero'],
    'climbing': ['road_climbing', 'climbing', 'climb'],
    'gravel': ['gravel', 'gravel_aero'],
    'endurance': ['endurance'],
    'tt': ['tt', 'triathlon']
  };

  // 2. ФИЛЬТРАЦИЯ
  const filteredItems = window.WINSPACE_CATALOG.filter(item => {
    const isComplete = item.type === 'complete';
    
    // Разделение на "Готовый байк" (complete) и "Рамы и Компоненты" (frameset/wheels)
    if (subCat === 'complete' && !isComplete) return false;
    if (subCat === 'parts' && isComplete) return false;

    // Фильтр по профилю катания для готовых байков
    if (subCat === 'complete' && profile !== 'all') {
      const itemCat = (item.category || '').toLowerCase();
      const allowedCategories = profileMap[profile] || [profile];
      return allowedCategories.some(catKey => itemCat.includes(catKey));
    }

    return true;
  });

  // 3. Шаблон переключателя подкатегорий (Байки / Рамы)
  const subCatHTML = `
    <div class="winspace-nav" style="display: flex; gap: 8px; margin-bottom: 12px;">
      <button onclick="openWinspaceCatalog('complete', 'all')" 
        style="flex: 1; padding: 10px; border-radius: 8px; border: none; font-weight: bold; cursor: pointer; background: ${subCat === 'complete' ? '#ff3b30' : '#2c2c2e'}; color: #fff;">
        🚲 Готовый байк
      </button>
      <button onclick="openWinspaceCatalog('parts', 'all')" 
        style="flex: 1; padding: 10px; border-radius: 8px; border: none; font-weight: bold; cursor: pointer; background: ${subCat === 'parts' ? '#ff3b30' : '#2c2c2e'}; color: #fff;">
        🛠️ Рамы и Компоненты
      </button>
    </div>
  `;

  // 4. Шаблон чипсов профилей катания
  const profilesHTML = subCat === 'complete' ? `
    <div class="winspace-profiles" style="display: flex; gap: 6px; overflow-x: auto; padding-bottom: 8px; margin-bottom: 12px; scrollbar-width: none;">
      ${[
        { id: 'all', name: 'Все' },
        { id: 'aero', name: '🚀 Аэро' },
        { id: 'climbing', name: '⛰️ Горы' },
        { id: 'gravel', name: '🏕️ Гравий' },
        { id: 'endurance', name: '🚴 Эндуранс' },
        { id: 'tt', name: '⏱️ Триатлон / ТТ' }
      ].map(p => `
        <button onclick="openWinspaceCatalog('complete', '${p.id}')"
          style="padding: 6px 12px; border-radius: 16px; border: none; font-size: 13px; white-space: nowrap; cursor: pointer; background: ${profile === p.id ? '#ff3b30' : '#2c2c2e'}; color: #fff;">
          ${p.name}
        </button>
      `).join('')}
    </div>
  ` : '';

  const fallbackImg = 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600';

  // 5. Отрисовка карточек
  const cardsHTML = filteredItems.length > 0 ? filteredItems.map(item => {
    const price = item.priceRrp || item.basePrice || 0;
    const deposit = Math.round(price * 0.5);
    const rawTitle = item.title || item.name || 'Winspace';
    const title = rawTitle.replace(/\s*Complete$/i, '');
    const badge = item.badge || 'Официальный заказ';
    const imgSrc = item.image || fallbackImg;

    return `
      <div class="product-card" style="border: 1px solid #ff3b30; position: relative; padding: 12px; background: #1c1c1e; border-radius: 12px; margin-bottom: 12px;">
        <span class="badge" style="position: absolute; top: 12px; right: 12px; background: #ff3b30; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">
          ${badge}
        </span>
        <img 
          src="${imgSrc}" 
          alt="${title}" 
          loading="lazy"
          style="width: 100%; border-radius: 8px; object-fit: cover;"
          onerror="this.onerror=null; this.src='${fallbackImg}';"
        >
        <h3 style="font-size: 16px; margin: 10px 0 4px; color: #fff;">${title}</h3>
        <div style="margin-bottom: 10px;">
          <span style="font-size: 13px; color: #8e8e93; text-decoration: line-through;">RRP: ${price.toLocaleString('ru-RU')} ₽</span>
          <p style="font-weight: bold; font-size: 16px; color: #34c759; margin: 2px 0 0 0;">
            Предоплата 50%: ${deposit.toLocaleString('ru-RU')} ₽
          </p>
        </div>
        <button 
          onclick="openWinspaceConfigurator('${item.id}')"
          style="width: 100%; background: linear-gradient(90deg, #ff3b30, #ff2d55); color: #fff; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer;">
          ⚙️ Сконфигурировать
        </button>
      </div>
    `;
  }).join('') : `<p style="color: #8e8e93; text-align: center; padding: 20px;">В выбранном профиле пока нет доступных моделей</p>`;

  container.innerHTML = subCatHTML + profilesHTML + cardsHTML;
}

function openWinspaceConfigurator(itemId) {
  const item = window.WINSPACE_CATALOG?.find(i => i.id === itemId);
  if (!item) return;

  const rawTitle = item.title || item.name || 'Winspace';
  const title = rawTitle.replace(/\s*Complete$/i, '');
  const price = item.priceRrp || 0;
  const deposit = Math.round(price * 0.5);

  const opts = item.options || {};
  const sizes = opts.sizes || ["XS (440)", "S (470)", "M (490)", "L (510)", "XL (540)"];
  const colors = opts.colors || ["Obsidian Gold", "Nebula Green", "Stealth Black"];
  const stems = opts.stems || [85, 95, 105, 115, 125];
  const handlebars = opts.handlebars || [360, 380, 400, 420];

  const modalHTML = `
    <div id="winspace-modal" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); display: flex; align-items: flex-end; z-index: 9999;">
      <div style="background: #1c1c1e; width: 100%; max-height: 90vh; overflow-y: auto; border-top-left-radius: 16px; border-top-right-radius: 16px; padding: 20px; box-sizing: border-box; color: #fff;">
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <h2 style="margin: 0; font-size: 18px;">${title}</h2>
          <button onclick="closeWinspaceModal()" style="background: #2c2c2e; border: none; color: #fff; width: 32px; height: 32px; border-radius: 50%; font-size: 16px; cursor: pointer;">✕</button>
        </div>

        <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px;">
          <div>
            <label style="font-size: 12px; color: #8e8e93; display: block; margin-bottom: 4px;">Размер рамы</label>
            <select id="cfg-size" style="width: 100%; padding: 10px; background: #2c2c2e; border: 1px solid #3a3a3c; color: #fff; border-radius: 8px;">
              ${sizes.map(s => `<option value="${s}">${s}</option>`).join('')}
            </select>
          </div>

          <div>
            <label style="font-size: 12px; color: #8e8e93; display: block; margin-bottom: 4px;">Цвет рамы</label>
            <select id="cfg-color" style="width: 100%; padding: 10px; background: #2c2c2e; border: 1px solid #3a3a3c; color: #fff; border-radius: 8px;">
              ${colors.map(c => `<option value="${c}">${c}</option>`).join('')}
            </select>
          </div>

          <div>
            <label style="font-size: 12px; color: #8e8e93; display: block; margin-bottom: 4px;">Длина выноса (мм)</label>
            <select id="cfg-stem" style="width: 100%; padding: 10px; background: #2c2c2e; border: 1px solid #3a3a3c; color: #fff; border-radius: 8px;">
              ${stems.map(st => `${st} мм`).map((txt, idx) => `<option value="${stems[idx]}">${txt}</option>`).join('')}
            </select>
          </div>

          <div>
            <label style="font-size: 12px; color: #8e8e93; display: block; margin-bottom: 4px;">Ширина руля (мм)</label>
            <select id="cfg-handlebar" style="width: 100%; padding: 10px; background: #2c2c2e; border: 1px solid #3a3a3c; color: #fff; border-radius: 8px;">
              ${handlebars.map(h => `${h} мм`).map((txt, idx) => `<option value="${handlebars[idx]}">${txt}</option>`).join('')}
            </select>
          </div>
        </div>

        <div style="background: #2c2c2e; padding: 12px; border-radius: 8px; margin-bottom: 16px;">
          <div style="display: flex; justify-content: space-between; font-size: 13px; color: #8e8e93;">
            <span>Розничная цена:</span>
            <span>${price.toLocaleString('ru-RU')} ₽</span>
          </div>
          <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 15px; color: #34c759; margin-top: 4px;">
            <span>Предоплата (50%):</span>
            <span>${deposit.toLocaleString('ru-RU')} ₽</span>
          </div>
        </div>

        <button onclick="submitWinspaceOrder('${itemId}')" style="width: 100%; background: #34c759; color: #fff; border: none; padding: 14px; border-radius: 10px; font-weight: bold; font-size: 16px; cursor: pointer;">
          Подтвердить и отправить
        </button>

      </div>
    </div>
  `;

  const existingModal = document.getElementById('winspace-modal');
  if (existingModal) existingModal.remove();

  document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function closeWinspaceModal() {
  const modal = document.getElementById('winspace-modal');
  if (modal) modal.remove();
}

function submitWinspaceOrder(itemId) {
  const item = window.WINSPACE_CATALOG?.find(i => i.id === itemId);
  if (!item) return;

  const rawTitle = item.title || item.name || 'Winspace';
  const title = rawTitle.replace(/\s*Complete$/i, '');

  const size = document.getElementById('cfg-size')?.value || 'Не выбран';
  const color = document.getElementById('cfg-color')?.value || 'Не выбран';
  const stem = document.getElementById('cfg-stem')?.value || 'Не выбран';
  const handlebar = document.getElementById('cfg-handlebar')?.value || 'Не выбран';

  const price = item.priceRrp || 0;
  const deposit = Math.round(price * 0.5);

  const messageText = `Здравствуйте! Интересует конфигурация байка Winspace:\n\n` +
    `🚴 Модель: ${title}\n` +
    `📏 Размер рамы: ${size}\n` +
    `🎨 Цвет: ${color}\n` +
    `📐 Вынос: ${stem}\n` +
    `🚲 Руль: ${handlebar}\n\n` +
    `💰 РРЦ: ${price.toLocaleString('ru-RU')} ₽\n` +
    `🟢 Предоплата (50%): ${deposit.toLocaleString('ru-RU')} ₽`;

  const tgUrl = `https://t.me/Piti4?text=${encodeURIComponent(messageText)}`;

  if (window.Telegram?.WebApp?.openTelegramLink) {
    window.Telegram.WebApp.openTelegramLink(tgUrl);
  } else {
    window.open(tgUrl, '_blank');
  }

  closeWinspaceModal();
}
