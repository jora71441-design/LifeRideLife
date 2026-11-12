import os
import aiohttp

WIDGET_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  body { background: #18222d; color: #fff; padding: 12px; font-size: 13px; }
  .hdr { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
  .title { font-weight: 700; font-size: 14px; color: #24a1de; }
  .badge { font-size: 10px; background: rgba(36,161,222,0.18); color: #5bc0f8; padding: 2px 7px; border-radius: 6px; font-weight: 600; }
  .res { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px; }
  .box { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 9px; text-align: center; }
  .lbl { font-size: 11px; color: #8fa3b4; margin-bottom: 2px; }
  .bar { font-size: 20px; font-weight: 800; color: #fff; }
  .psi { font-size: 11px; color: #24a1de; font-weight: 600; }
  .grp { margin-bottom: 10px; }
  .glbl { display: flex; justify-content: space-between; font-size: 11px; color: #8fa3b4; margin-bottom: 5px; }
  .glbl b { color: #fff; font-size: 12px; }
  input[type=range] { width: 100%; accent-color: #24a1de; }
  .pills { display: flex; gap: 5px; flex-wrap: wrap; }
  .pill { flex: 1; min-width: 38px; text-align: center; padding: 6px 4px; border-radius: 8px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #cfd9e2; font-size: 11px; font-weight: 600; cursor: pointer; }
  .pill.on { background: rgba(36,161,222,0.22); border-color: #24a1de; color: #fff; }
</style>
</head>
<body>
  <div class="hdr">
    <div class="title">🎯 Давление в шинах</div>
    <div class="badge">LifeRideLife AI</div>
  </div>

  <div class="res">
    <div class="box">
      <div class="lbl">Переднее</div>
      <div class="bar" id="f-bar">4.8 bar</div>
      <div class="psi" id="f-psi">70 psi</div>
    </div>
    <div class="box">
      <div class="lbl">Заднее</div>
      <div class="bar" id="r-bar">5.1 bar</div>
      <div class="psi" id="r-psi">74 psi</div>
    </div>
  </div>

  <div class="grp">
    <div class="glbl"><span>Вес райдер + байк</span><b id="w-val">82 кг</b></div>
    <input type="range" id="w-rng" min="50" max="130" value="82">
  </div>

  <div class="grp">
    <div class="glbl"><span>Ширина покрышки (мм)</span></div>
    <div class="pills" id="tire-pills">
      <div class="pill" data-v="25">25</div>
      <div class="pill on" data-v="28">28</div>
      <div class="pill" data-v="30">30</div>
      <div class="pill" data-v="32">32</div>
      <div class="pill" data-v="38">38</div>
      <div class="pill" data-v="42">42</div>
    </div>
  </div>

  <div class="grp">
    <div class="glbl"><span>Установка</span></div>
    <div class="pills" id="setup-pills">
      <div class="pill on" data-v="0.90">Бескамерка</div>
      <div class="pill" data-v="1.00">Камера</div>
    </div>
  </div>

  <div class="grp" style="margin-bottom:0">
    <div class="glbl"><span>Покрытие</span></div>
    <div class="pills" id="surf-pills">
      <div class="pill on" data-v="1.00">Сухой асфальт</div>
      <div class="pill" data-v="0.92">Мокрый</div>
      <div class="pill" data-v="0.84">Гравий</div>
    </div>
  </div>

<script>
  var st = { w: 82, t: 28, k: 0.90, s: 1.00 };
  function upd() {
    var baseRear = 76 * Math.pow(28 / st.t, 1.35) * Math.pow(st.w / 80, 0.85);
    var rPsi = Math.round(baseRear * st.k * st.s);
    var fPsi = Math.round(rPsi * 0.93);
    document.getElementById('w-val').textContent = st.w + ' кг';
    document.getElementById('r-psi').textContent = rPsi + ' psi';
    document.getElementById('f-psi').textContent = fPsi + ' psi';
    document.getElementById('r-bar').textContent = (rPsi * 0.06895).toFixed(1) + ' bar';
    document.getElementById('f-bar').textContent = (fPsi * 0.06895).toFixed(1) + ' bar';
  }
  document.getElementById('w-rng').oninput = function(e) { st.w = +e.target.value; upd(); };
  function bindGroup(id, key) {
    var box = document.getElementById(id);
    box.onclick = function(e) {
      var el = e.target.closest('.pill');
      if (!el) return;
      box.querySelectorAll('.pill').forEach(function(p) { p.classList.remove('on'); });
      el.classList.add('on');
      st[key] = parseFloat(el.getAttribute('data-v'));
      upd();
    };
  }
  bindGroup('tire-pills', 't');
  bindGroup('setup-pills', 'k');
  bindGroup('surf-pills', 's');
  upd();
</script>
</body>
</html>"""


async def send_pressure_widget(chat_id: int) -> tuple[bool, str]:
    """Отправляет интерактивный HTML-микровиджет через Bot API 10.4 (sendWidget)."""
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        return False, "Не найден BOT_TOKEN."

    url = f"https://api.telegram.org/bot{token}/sendWidget"
    payload = {
        "chat_id": chat_id,
        "widget": {
            "type": "html",
            "html": WIDGET_HTML,
        },
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=15) as resp:
                data = await resp.json()
                if data.get("ok"):
                    return True, "OK"
                desc = data.get("description", "Unknown Telegram API error")
                return False, f"Telegram API ({data.get('error_code')}): {desc}"
    except Exception as e:
        return False, f"Ошибка соединения: {e}"
