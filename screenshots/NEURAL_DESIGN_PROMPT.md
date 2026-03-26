# ЗАДАЧА: Сделай дизайн в стиле SYNAPSE Neural Platform

Ты получишь полную дизайн-систему ниже. Прочитай её внимательно и применяй точно.
Найди все существующие frontend файлы проекта (HTML / CSS / React / Vue) и перепиши
их в этом стиле. Если проект пустой — создай index.html с нуля.

---

## ДИЗАЙН-СИСТЕМА: SYNAPSE NEURAL

### 1. CSS ПЕРЕМЕННЫЕ (обязательно в :root)

```css
:root {
  --void:    #020408;        /* главный фон страницы */
  --deep:    #050d1a;        /* фон карточек */
  --layer:   #0a1628;        /* hover состояние карточек */
  --node:    #0e2040;        /* бордер-акцент */
  --pulse:   #00e5ff;        /* ГЛАВНЫЙ акцент — cyan */
  --fire:    #ff6b2b;        /* вторичный акцент — оранжевый */
  --synapse: #7c3aed;        /* третичный акцент — фиолетовый */
  --signal:  #00ff88;        /* зелёный — статусы, лейблы */
  --text:    #e8f4f8;        /* основной текст */
  --muted:   #4a6580;        /* приглушённый текст */
  --border:  rgba(0,229,255,0.12); /* бордеры */
}
```

---

### 2. ШРИФТЫ (Google Fonts — подключить в <head>)

```html
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400&display=swap" rel="stylesheet">
```

| Роль               | Семейство      | Weight | Применение                        |
|--------------------|----------------|--------|-----------------------------------|
| Заголовки H1-H3    | Syne           | 800    | letter-spacing: -0.02em           |
| Лейблы / теги / nav | Space Mono    | 400    | uppercase, letter-spacing: 0.2em  |
| Основной текст     | DM Sans        | 300    | line-height: 1.75                 |

---

### 3. ЖИВАЯ НЕЙРОСЕТЬ НА CANVAS (фон всей страницы)

Вставь в HTML `<canvas id="neural-bg">` и следующий JS:

```javascript
const bgCanvas = document.getElementById('neural-bg');
const bgCtx = bgCanvas.getContext('2d');
let bgNodes = [];

// Стили canvas (position: fixed, z-index: 0, opacity: 0.55)
bgCanvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;opacity:0.55;pointer-events:none;';

function resizeBg() {
  bgCanvas.width = window.innerWidth;
  bgCanvas.height = window.innerHeight;
}
resizeBg();
window.addEventListener('resize', resizeBg);

// Создаём 80 узлов
for (let i = 0; i < 80; i++) {
  bgNodes.push({
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    vx: (Math.random() - 0.5) * 0.3,
    vy: (Math.random() - 0.5) * 0.3,
    r: Math.random() * 2 + 1,
    pulse: Math.random() * Math.PI * 2,
    active: Math.random() > 0.7
  });
}

let signals = [];

// Спауним сигналы каждые 120мс
setInterval(() => {
  const a = bgNodes[Math.floor(Math.random() * bgNodes.length)];
  const b = bgNodes[Math.floor(Math.random() * bgNodes.length)];
  if (a === b) return;
  const dx = b.x - a.x, dy = b.y - a.y;
  if (Math.sqrt(dx*dx+dy*dy) < 250) {
    signals.push({ ax: a.x, ay: a.y, bx: b.x, by: b.y, t: 0, speed: 0.008 + Math.random()*0.012 });
  }
}, 120);

function drawBg() {
  bgCtx.clearRect(0, 0, bgCanvas.width, bgCanvas.height);

  // Связи между узлами
  for (let i = 0; i < bgNodes.length; i++) {
    for (let j = i+1; j < bgNodes.length; j++) {
      const dx = bgNodes[j].x - bgNodes[i].x;
      const dy = bgNodes[j].y - bgNodes[i].y;
      const d = Math.sqrt(dx*dx+dy*dy);
      if (d < 180) {
        bgCtx.beginPath();
        bgCtx.strokeStyle = `rgba(0,229,255,${(1 - d/180) * 0.15})`;
        bgCtx.lineWidth = 0.5;
        bgCtx.moveTo(bgNodes[i].x, bgNodes[i].y);
        bgCtx.lineTo(bgNodes[j].x, bgNodes[j].y);
        bgCtx.stroke();
      }
    }
  }

  // Сигналы (летящие точки)
  signals = signals.filter(s => s.t < 1);
  for (const s of signals) {
    s.t += s.speed;
    const px = s.ax + (s.bx - s.ax) * s.t;
    const py = s.ay + (s.by - s.ay) * s.t;
    const grd = bgCtx.createRadialGradient(px, py, 0, px, py, 6);
    grd.addColorStop(0, 'rgba(0,229,255,0.9)');
    grd.addColorStop(1, 'rgba(0,229,255,0)');
    bgCtx.beginPath();
    bgCtx.arc(px, py, 6, 0, Math.PI*2);
    bgCtx.fillStyle = grd;
    bgCtx.fill();
  }

  // Узлы
  for (const n of bgNodes) {
    n.x += n.vx; n.y += n.vy;
    if (n.x < 0 || n.x > bgCanvas.width) n.vx *= -1;
    if (n.y < 0 || n.y > bgCanvas.height) n.vy *= -1;
    n.pulse += 0.03;
    const alpha = n.active ? 0.6 + Math.sin(n.pulse) * 0.4 : 0.15;
    bgCtx.beginPath();
    bgCtx.arc(n.x, n.y, n.r, 0, Math.PI*2);
    bgCtx.fillStyle = n.active ? `rgba(0,229,255,${alpha})` : `rgba(74,101,128,${alpha})`;
    bgCtx.fill();
  }

  requestAnimationFrame(drawBg);
}
requestAnimationFrame(drawBg);
```

---

### 4. КАСТОМНЫЙ КУРСОР

```html
<div class="cursor" id="cursor"></div>
<div class="cursor-ring" id="cursor-ring"></div>
```

```css
body { cursor: none; }
.cursor {
  position: fixed; width: 8px; height: 8px;
  background: #00e5ff; border-radius: 50%;
  pointer-events: none; z-index: 9999;
  box-shadow: 0 0 12px #00e5ff, 0 0 24px rgba(0,229,255,0.4);
}
.cursor-ring {
  position: fixed; width: 36px; height: 36px;
  border: 1px solid rgba(0,229,255,0.4); border-radius: 50%;
  pointer-events: none; z-index: 9998;
  transition: all 0.15s ease; transform: translate(-14px,-14px);
}
```

```javascript
const cursor = document.getElementById('cursor');
const ring = document.getElementById('cursor-ring');
let mx=0,my=0,rx=0,ry=0;
document.addEventListener('mousemove', e => {
  mx=e.clientX; my=e.clientY;
  cursor.style.left = mx-4+'px'; cursor.style.top = my-4+'px';
});
(function anim(){
  rx += (mx-rx-18)*0.15; ry += (my-ry-18)*0.15;
  ring.style.left=rx+'px'; ring.style.top=ry+'px';
  requestAnimationFrame(anim);
})();
```

---

### 5. КОМПОНЕНТЫ

#### NAV (фиксированный, с blur)
```css
nav {
  position: fixed; top:0; left:0; right:0; z-index:100;
  display: flex; align-items:center; justify-content:space-between;
  padding: 24px 60px;
  backdrop-filter: blur(20px);
  background: rgba(2,4,8,0.6);
  border-bottom: 1px solid var(--border);
}
.logo { font-family:'Syne',sans-serif; font-weight:800; font-size:20px; letter-spacing:0.12em; color:var(--pulse); }
nav a { font-family:'Space Mono',monospace; font-size:11px; letter-spacing:0.2em; text-transform:uppercase; color:var(--muted); text-decoration:none; transition:color 0.3s; }
nav a:hover { color:var(--pulse); }
```

#### КНОПКА PRIMARY
```css
.btn-primary {
  display:inline-flex; align-items:center; gap:12px;
  padding:16px 36px; background:var(--pulse); color:var(--void);
  font-family:'Space Mono',monospace; font-size:11px;
  letter-spacing:0.15em; text-transform:uppercase; font-weight:700;
  text-decoration:none; position:relative; overflow:hidden; cursor:none;
  transition: all 0.3s;
}
.btn-primary::after {
  content:''; position:absolute; inset:0; background:white;
  transform:translateX(-100%); transition:transform 0.3s; mix-blend-mode:overlay;
}
.btn-primary:hover::after { transform:translateX(0); }
```

#### СЕКЦИЯ-ТЕГ (лейбл над заголовком)
```css
.section-tag {
  font-family:'Space Mono',monospace; font-size:10px;
  letter-spacing:0.4em; text-transform:uppercase; color:var(--fire);
  margin-bottom:20px;
}
```

#### КАРТОЧКА FEATURE
```css
.feature-card {
  background:var(--deep); padding:48px 40px;
  border: 1px solid transparent;
  position:relative; overflow:hidden; transition:background 0.4s;
}
.feature-card::before {
  content:''; position:absolute; top:0; left:0; right:0; height:2px;
  background:linear-gradient(90deg, transparent, var(--pulse), transparent);
  transform:translateX(-100%); transition:transform 0.6s;
}
.feature-card:hover::before { transform:translateX(100%); }
.feature-card:hover { background:var(--layer); }
.feature-card h3 { font-family:'Syne',sans-serif; font-weight:700; font-size:22px; }
.feature-card p { font-size:14px; line-height:1.75; color:rgba(232,244,248,0.45); }
```

#### МЕТРИКА
```css
.metric-val {
  font-family:'Syne',sans-serif; font-weight:800; font-size:54px; line-height:1;
  background:linear-gradient(135deg, var(--pulse), var(--synapse));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.metric-label {
  font-family:'Space Mono',monospace; font-size:10px;
  letter-spacing:0.3em; text-transform:uppercase; color:var(--muted);
}
```

#### SCROLL REVEAL (добавить всем секциям класс .reveal)
```css
.reveal { opacity:0; transform:translateY(30px); transition:opacity 0.8s, transform 0.8s; }
.reveal.visible { opacity:1; transform:translateY(0); }
```
```javascript
const obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if(e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
```

#### БЕГУЩАЯ СТРОКА (ticker)
```css
.ticker { overflow:hidden; border-top:1px solid var(--border); border-bottom:1px solid var(--border); padding:14px 0; background:rgba(5,13,26,0.6); }
.ticker-track { display:flex; gap:80px; animation:ticker 30s linear infinite; white-space:nowrap; }
.ticker-item { font-family:'Space Mono',monospace; font-size:10px; letter-spacing:0.3em; text-transform:uppercase; color:var(--muted); display:flex; align-items:center; gap:16px; }
.ticker-item span { color:var(--signal); }
@keyframes ticker { to { transform:translateX(-50%); } }
```

---

### 6. ТИПОГРАФИКА

```css
h1 { font-family:'Syne',sans-serif; font-weight:800; font-size:clamp(48px,5.5vw,80px); line-height:1.0; letter-spacing:-0.02em; }
h2 { font-family:'Syne',sans-serif; font-weight:800; font-size:clamp(36px,3.5vw,56px); line-height:1.05; letter-spacing:-0.02em; }
h3 { font-family:'Syne',sans-serif; font-weight:700; font-size:22px; letter-spacing:-0.01em; }
p  { font-size:16px; line-height:1.75; color:rgba(232,244,248,0.55); }

/* Градиентный текст для акцентов */
.gradient-text {
  background:linear-gradient(135deg, var(--pulse) 0%, var(--synapse) 60%, var(--fire) 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
```

---

### 7. СЕТКА И ОТСТУПЫ

- Стандартный padding секции: `120px 60px`
- Gap между карточками: `2px` (на фоне `var(--border)` — создаёт эффект тонкой линии)
- Grid карточек: `repeat(3, 1fr)` → на мобиле `1fr`
- Grid метрик: `repeat(4, 1fr)` → на мобиле `repeat(2, 1fr)`

---

### 8. ЧТО НУЖНО СДЕЛАТЬ

Прочитай все существующие файлы проекта.
Перепиши frontend полностью в стиле выше.
Сохрани всю существующую логику и данные — меняй только визуал.

Если в проекте есть:
- `index.html` → примени стили напрямую
- React (`App.tsx`, `*.tsx`) → создай `theme.css` с переменными, перепиши компоненты
- Vue → то же самое

Обязательно добавь:
1. Canvas нейросеть на фон (секция 3)
2. Все CSS переменные (секция 1)
3. Шрифты через Google Fonts (секция 2)
4. Scroll reveal на основные блоки (секция 5)

Начни с команды: прочитай структуру проекта командой `find . -name "*.html" -o -name "*.tsx" -o -name "*.vue" -o -name "*.css" | head -30`
