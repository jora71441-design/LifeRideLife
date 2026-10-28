// === МОДУЛЬ ЭКСПРЕСС-ПОДБОРА БАЙКА (QUIZ) LIFERIDELIFE ===

(function () {
  let quizState = {
    step: 1,
    height: 175,
    knowInseam: false,
    inseam: 81,
    surface: 'mix', // 'road', 'road_pref', 'mix', 'gravel'
    posture: 'sport_endurance', // 'comfort_endurance', 'sport_endurance', 'race'
    tasks: {
      longDistance: false,
      fasterAsphalt: false,
      bikepacking: false
    },
    budget: '150_250k'
  };

  // Расчет параметров геометрии и строго ОДНОГО класса байка
  function calculateFit() {
    const h = parseInt(quizState.height, 10) || 175;
    
    // Определение размера рамы по росту
    let sizeTag = '#170_180cm';
    let sizeLabel = 'M (54)';
    if (h < 160) { sizeTag = '#150_160cm'; sizeLabel = 'XXS/XS (47–49)'; }
    else if (h < 170) { sizeTag = '#160_170cm'; sizeLabel = 'XS/S (50–52)'; }
    else if (h < 180) { sizeTag = '#170_180cm'; sizeLabel = 'S/M (53–55)'; }
    else if (h < 190) { sizeTag = '#180_190cm'; sizeLabel = 'L/XL (56–58)'; }
    else { sizeTag = '#190_200cm'; sizeLabel = 'XL/XXL (58–61)'; }

    // Логика подбора СТРОГО одного класса рамы
    let recommendedClass = 'Endurance Road';
    let classTag = '#эндуранс';

    if (quizState.surface === 'gravel') {
      // Преимущественно бездорожье -> строго гравел
      recommendedClass = quizState.tasks.bikepacking ? 'Adventure / Touring Gravel' : 'Gravel';
      classTag = '#гравел';
    } else if (quizState.surface === 'mix') {
      // 50/50 микс: если спорт-эндюранс с акцентом на скорость по шоссе -> гоночный эндуранс, иначе гравел
      if (quizState.posture === 'sport_endurance' && quizState.tasks.fasterAsphalt) {
        recommendedClass = 'Гоночный эндюранс / Fast All-Road';
        classTag = '#гоночныйэндуранс';
      } else if (quizState.posture === 'sport_endurance') {
        recommendedClass = 'Fast Gravel / Спорт-гравел';
        classTag = '#гравел';
      } else if (quizState.posture === 'race') {
        recommendedClass = 'Race Gravel';
        classTag = '#гравел';
      } else {
        recommendedClass = 'Comfort Gravel / All-Road';
        classTag = '#гравел';
      }
    } else if (quizState.surface === 'road_pref') {
      // Преимущественно асфальт (70/30)
      if (quizState.posture === 'race') {
        recommendedClass = 'Aero / Race Road';
        classTag = '#шоссер';
      } else if (quizState.posture === 'sport_endurance') {
        recommendedClass = 'Спорт-эндюранс / All-Road';
        classTag = '#гоночныйэндуранс';
      } else {
        recommendedClass = 'Endurance Road';
        classTag = '#эндуранс';
      }
    } else {
      // 100% Шоссе
      if (quizState.posture === 'race') {
        recommendedClass = 'Aero / Race Road';
        classTag = '#шоссер';
      } else if (quizState.posture === 'sport_endurance') {
        recommendedClass = 'Спорт-эндюранс';
        classTag = '#гоночныйэндуранс';
      } else {
        recommendedClass = 'Endurance Road';
        classTag = '#эндуранс';
      }
    }

    return { sizeTag, sizeLabel, recommendedClass, classTag };
  }

  // Создание модального окна в DOM
  function injectQuizModal() {
    if (document.getElementById('lrl-quiz-modal')) return;

    const modal = document.createElement('div');
    modal.id = 'lrl-quiz-modal';
    modal.className = 'quiz-modal-backdrop';
    modal.style.cssText = `
      display: none; position: fixed; inset: 0; z-index: 9999;
      background: rgba(10, 15, 20, 0.85); backdrop-filter: blur(8px);
      align-items: center; justify-content: center; padding: 16px;
    `;

    modal.innerHTML = `
      <div style="
        background: #18222d; border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px; width: 100%; max-width: 440px; max-height: 90vh;
        overflow-y: auto; color: #fff; padding: 22px 18px; box-shadow: 0 16px 36px rgba(0,0,0,0.5);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
          <div style="font-size: 16px; font-weight: 700; color: #24a1de;">🎯 Подбор байка под задачи</div>
          <button onclick="closeQuiz()" style="background: none; border: none; color: #aaa; font-size: 26px; cursor: pointer; line-height: 1;">&times;</button>
        </div>
        <div style="height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-bottom: 18px; overflow: hidden;">
          <div id="quiz-progress-bar" style="width: 25%; height: 100%; background: #24a1de; transition: width 0.3s ease;"></div>
        </div>
        <div id="quiz-content"></div>
      </div>
    `;

    document.body.appendChild(modal);
  }

  function renderStep() {
    const container = document.getElementById('quiz-content');
    const bar = document.getElementById('quiz-progress-bar');
    if (!container || !bar) return;

    bar.style.width = (quizState.step * 25) + '%';

    if (quizState.step === 1) {
      container.innerHTML = `
        <div style="font-size: 14px; font-weight: 600; margin-bottom: 12px;">Шаг 1 из 4: Твой рост и параметры</div>
        
        <div style="margin-bottom: 16px;">
          <label style="font-size: 13px; color: #8fa3b4;">Рост: <strong id="quiz-height-val" style="color: #fff; font-size: 16px;">${quizState.height}</strong> см</label>
          <input type="range" min="145" max="205" value="${quizState.height}" style="width: 100%; accent-color: #24a1de; margin-top: 8px;" oninput="quizUpdateHeight(this.value)">
        </div>

        <div style="margin-bottom: 16px; background: rgba(255,255,255,0.04); padding: 12px; border-radius: 10px;">
          <label style="display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer;">
            <input type="checkbox" ${quizState.knowInseam ? 'checked' : ''} onchange="quizToggleInseam(this.checked)" style="accent-color: #24a1de;">
            <span>Знаю длину ноги по шагу (инсим)</span>
          </label>
          <div id="quiz-inseam-wrap" style="display: ${quizState.knowInseam ? 'block' : 'none'}; margin-top: 10px;">
            <label style="font-size: 12px; color: #8fa3b4;">Инсим: <strong id="quiz-inseam-val" style="color: #fff;">${quizState.inseam}</strong> см</label>
            <input type="range" min="65" max="100" value="${quizState.inseam}" style="width: 100%; accent-color: #24a1de; margin-top: 4px;" oninput="quizUpdateInseam(this.value)">
          </div>
        </div>

        <button onclick="quizNext()" style="width: 100%; padding: 12px; border-radius: 10px; font-weight: 700; background: #24a1de; color: #fff; border: none; cursor: pointer;">Далее: Покрытие ➔</button>
      `;
    } else if (quizState.step === 2) {
      container.innerHTML = `
        <div style="font-size: 14px; font-weight: 600; margin-bottom: 12px;">Шаг 2 из 4: Где планируешь кататься?</div>
        
        <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 18px;">
          ${renderRadio('surface', 'road', '🛣 Только шоссе и асфальт (100%)', 'Гладкий асфальт, быстрый накат, чистая скорость.')}
          ${renderRadio('surface', 'road_pref', '🏙 Асфальт + парки (70% / 30%)', 'Шоссе с выездами на набережные, брусчатку и укатанные тропинки.')}
          ${renderRadio('surface', 'mix', '🌲 Разнообразные покрытия 50/50', 'Асфальт, грунтовки, грейдер, лесные дороги и гравий.')}
          ${renderRadio('surface', 'gravel', '🚵‍♂️ Преимущественно бездорожье (70%+)', 'Гравий, каменистые тропы, сложный грунт, лесные маршруты.')}
        </div>

        <div style="display: flex; gap: 8px;">
          <button onclick="quizPrev()" style="flex: 1; padding: 10px; border-radius: 8px; background: rgba(255,255,255,0.08); border: none; color: #fff; cursor: pointer;">Назад</button>
          <button onclick="quizNext()" style="flex: 2; padding: 10px; border-radius: 8px; background: #24a1de; border: none; color: #fff; font-weight: 700; cursor: pointer;">Далее: Характер посадки ➔</button>
        </div>
      `;
    } else if (quizState.step === 3) {
      container.innerHTML = `
        <div style="font-size: 14px; font-weight: 600; margin-bottom: 12px;">Шаг 3 из 4: Характер посадки и задачи</div>
        
        <div style="font-size: 12px; color: #8fa3b4; margin-bottom: 6px; text-transform: uppercase;">Посадка:</div>
        <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px;">
          ${renderRadio('posture', 'comfort_endurance', '🛋 Классический эндюранс', 'Максимальный комфорт, разгруженные руки и спина, спокойный темп.')}
          ${renderRadio('posture', 'sport_endurance', '🚀 Спорт-эндюранс', 'Бодрый спортивный темп и тренировки, но с комфортом на 4+ часа.')}
          ${renderRadio('posture', 'race', '⚡️ Гонки и агрессивный спорт', 'Низкая плотная аэро-посадка, жесткость рамы, бескомпромиссная скорость.')}
        </div>

        <div style="font-size: 12px; color: #8fa3b4; margin-bottom: 6px; text-transform: uppercase;">Специфика (можно несколько):</div>
        <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 18px;">
          ${renderCheckbox('longDistance', '🏔 Длинные дистанции и объемы')}
          ${renderCheckbox('fasterAsphalt', '⚡️ Быть чуть быстрее на асфальте')}
          ${renderCheckbox('bikepacking', '🎒 Туризм и байкпакинг (бонки под сумки)')}
        </div>

        <div style="display: flex; gap: 8px;">
          <button onclick="quizPrev()" style="flex: 1; padding: 10px; border-radius: 8px; background: rgba(255,255,255,0.08); border: none; color: #fff; cursor: pointer;">Назад</button>
          <button onclick="quizNext()" style="flex: 2; padding: 10px; border-radius: 8px; background: #24a1de; border: none; color: #fff; font-weight: 700; cursor: pointer;">Далее: Бюджет ➔</button>
        </div>
      `;
    } else if (quizState.step === 4) {
      container.innerHTML = `
        <div style="font-size: 14px; font-weight: 600; margin-bottom: 12px;">Шаг 4 из 4: Планируемый бюджет</div>
        
        <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 18px;">
          ${renderRadio('budget', 'under_150k', 'До 150 000 ₽', 'Начальный карбон или предтоповый алюминий.')}
          ${renderRadio('budget', 'under_200k', 'До 200 000 ₽', 'Оптимальный баланс: легкий карбон, надежная гидравлика.')}
          ${renderRadio('budget', '150_250k', '150 000 – 250 000 ₽', 'Топовый любительский уровень, зазоры под широкую резину.')}
          ${renderRadio('budget', '250_400k', '250 000 – 400 000 ₽', 'Электронная трансмиссия (Di2 / AXS), карбоновые вилсеты.')}
          ${renderRadio('budget', 'over_400k', '400 000 ₽ +', 'Флагманские аэро-болиды, кастомные сборки под ключ.')}
        </div>

        <div style="display: flex; gap: 8px;">
          <button onclick="quizPrev()" style="flex: 1; padding: 10px; border-radius: 8px; background: rgba(255,255,255,0.08); border: none; color: #fff; cursor: pointer;">Назад</button>
          <button onclick="quizFinish()" style="flex: 2; padding: 10px; border-radius: 8px; background: #24a1de; border: none; color: #fff; font-weight: 700; cursor: pointer;">Сформировать резюме 🏁</button>
        </div>
      `;
    } else if (quizState.step === 5) {
      const fit = calculateFit();
      
      let surfaceText = '50% асфальт / 50% гравий';
      if (quizState.surface === 'road') surfaceText = '100% асфальт и шоссе';
      if (quizState.surface === 'road_pref') surfaceText = '70% асфальт / 30% парки и тропы';
      if (quizState.surface === 'gravel') surfaceText = '70%+ гравий и бездорожье';

      let postureText = 'Спорт-эндюранс (комфортно для спины, но динамично)';
      if (quizState.posture === 'comfort_endurance') postureText = 'Классический эндюранс (максимальный комфорт)';
      if (quizState.posture === 'race') postureText = 'Гонки и спорт (агрессивная аэро-посадка)';

      let tasksArr = [];
      if (quizState.tasks.longDistance) tasksArr.push('длинные дистанции и объемы');
      if (quizState.tasks.fasterAsphalt) tasksArr.push('накат и скорость на асфальте');
      if (quizState.tasks.bikepacking) tasksArr.push('туризм и крепления под сумки');
      const tasksStr = tasksArr.length > 0 ? tasksArr.join(', ') : 'универсальные тренировки и поездки';

      let budgetText = '150 000 – 250 000 ₽';
      if (quizState.budget === 'under_150k') budgetText = 'до 150 000 ₽';
      if (quizState.budget === 'under_200k') budgetText = 'до 200 000 ₽';
      if (quizState.budget === '250_400k') budgetText = '250 000 – 400 000 ₽';
      if (quizState.budget === 'over_400k') budgetText = 'от 400 000 ₽';

      const fullSummary = `Резюме подбора LifeRideLife:\n\n• Рост: ${quizState.height} см (размер рамы: ${fit.sizeLabel})\n• Покрытие: ${surfaceText}\n• Посадка: ${postureText}\n• Задачи: ${tasksStr}\n• Рекомендованный класс: ${fit.recommendedClass}\n• Бюджет: ${budgetText}`;

      container.innerHTML = `
        <div style="background: rgba(36, 161, 222, 0.1); border: 1px solid rgba(36, 161, 222, 0.3); border-radius: 12px; padding: 14px; margin-bottom: 16px; font-size: 13px; line-height: 1.5;">
          <div style="font-weight: 700; color: #24a1de; margin-bottom: 8px; font-size: 14px;">📋 Твое персональное резюме:</div>
          <div>📏 <strong>Размер рамы:</strong> ${fit.sizeLabel}</div>
          <div>🚲 <strong>Класс:</strong> ${fit.recommendedClass}</div>
          <div>💰 <strong>Бюджет:</strong> ${budgetText}</div>
        </div>

        <div style="display: flex; flex-direction: column; gap: 8px;">
          <button onclick="quizApplyFilters('${fit.sizeTag}', '${fit.classTag}')" style="padding: 12px; border-radius: 10px; background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2); color: #fff; font-weight: 600; cursor: pointer;">
            🔍 Показать подходящие в наличии
          </button>
          
          <button onclick="quizSendToTg('${encodeURIComponent(fullSummary)}')" style="padding: 12px; border-radius: 10px; background: #24a1de; color: #fff; font-weight: 700; border: none; cursor: pointer; text-align: center;">
            📩 Отправить запрос в Telegram
          </button>

          <button onclick="quizPrev()" style="padding: 10px; border-radius: 8px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); color: #aaa; cursor: pointer; font-size: 12px; text-align: center; margin-top: 4px;">
            ⬅️ Назад (изменить параметры)
          </button>
        </div>
      `;
    }
  }

  function renderRadio(name, val, title, desc) {
    const isChecked = quizState[name] === val;
    return `
      <label style="
        display: block; padding: 10px 12px; border-radius: 10px; cursor: pointer;
        background: ${isChecked ? 'rgba(36, 161, 222, 0.18)' : 'rgba(255,255,255,0.04)'};
        border: 1px solid ${isChecked ? '#24a1de' : 'rgba(255,255,255,0.08)'};
      ">
        <div style="display: flex; align-items: center; gap: 8px;">
          <input type="radio" name="${name}" value="${val}" ${isChecked ? 'checked' : ''} onchange="quizSetField('${name}', '${val}')" style="accent-color: #24a1de;">
          <strong style="font-size: 13px; color: #fff;">${title}</strong>
        </div>
        <div style="font-size: 11px; color: #8fa3b4; margin-top: 4px; padding-left: 24px;">${desc}</div>
      </label>
    `;
  }

  function renderCheckbox(key, label) {
    const isChecked = quizState.tasks[key];
    return `
      <label style="
        display: flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 8px; cursor: pointer;
        background: ${isChecked ? 'rgba(36, 161, 222, 0.15)' : 'rgba(255,255,255,0.03)'};
        border: 1px solid ${isChecked ? '#24a1de' : 'rgba(255,255,255,0.06)'};
        font-size: 13px;
      ">
        <input type="checkbox" ${isChecked ? 'checked' : ''} onchange="quizToggleTask('${key}', this.checked)" style="accent-color: #24a1de;">
        <span>${label}</span>
      </label>
    `;
  }

  // Методы управления
  window.openQuiz = function () {
    injectQuizModal();
    quizState.step = 1;
    renderStep();
    const modal = document.getElementById('lrl-quiz-modal');
    if (modal) modal.style.display = 'flex';
  };

  window.closeQuiz = function () {
    const modal = document.getElementById('lrl-quiz-modal');
    if (modal) modal.style.display = 'none';
  };

  window.quizNext = function () {
    quizState.step++;
    renderStep();
  };

  window.quizPrev = function () {
    quizState.step--;
    renderStep();
  };

  window.quizFinish = function () {
    quizState.step = 5;
    renderStep();
  };

  window.quizUpdateHeight = function (val) {
    quizState.height = val;
    const el = document.getElementById('quiz-height-val');
    if (el) el.innerText = val;
  };

  window.quizToggleInseam = function (checked) {
    quizState.knowInseam = checked;
    const wrap = document.getElementById('quiz-inseam-wrap');
    if (wrap) wrap.style.display = checked ? 'block' : 'none';
  };

  window.quizUpdateInseam = function (val) {
    quizState.inseam = val;
    const el = document.getElementById('quiz-inseam-val');
    if (el) el.innerText = val;
  };

  window.quizSetField = function (field, val) {
    quizState[field] = val;
    renderStep();
  };

  window.quizToggleTask = function (taskKey, val) {
    quizState.tasks[taskKey] = val;
    renderStep();
  };

  window.quizApplyFilters = function (sizeTag, singleClassTag) {
    window.closeQuiz();
    if (typeof window.setCategory === 'function') {
      window.setCategory('bikes');
    }
    
    // Сбрасываем старые и выставляем строго 2 фильтра: [Размер, Класс]
    if (window.selectedTags) {
      window.selectedTags.clear();
      document.querySelectorAll('.tag-pill').forEach(p => p.classList.remove('active'));

      const tagsToActivate = [sizeTag, singleClassTag].filter(Boolean);
      tagsToActivate.forEach(t => window.selectedTags.add(t));

      // Подсвечиваем активные пилюли в интерфейсе каталога
      document.querySelectorAll('.tag-pill').forEach(pill => {
        const onclickAttr = pill.getAttribute('onclick') || '';
        if (tagsToActivate.some(t => onclickAttr.includes(`'${t}'`))) {
          pill.classList.add('active');
        }
      });

      if (typeof window.renderCatalog === 'function') {
        window.renderCatalog();
      }
    }
  };

  window.quizSendToTg = function (encodedText) {
    const url = `https://t.me/Piti4?text=${encodedText}`;
    if (window.Telegram?.WebApp?.openTelegramLink) {
      window.Telegram.WebApp.openTelegramLink(url);
    } else {
      window.open(url, '_blank');
    }
  };
})();
