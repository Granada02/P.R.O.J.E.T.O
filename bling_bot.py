
import time
import threading
import pyautogui
import pygetwindow as gw
import keyboard
import clipboard

pyautogui.PAUSE = 0.02  # reduz a pausa padrao entre acoes

# ==========================
# ESTADO GLOBAL
# ==========================
g_notasX, g_notasY = 97, 381   # posição padrão das notas
janela_danfe = "Bling - DANFE Simplificado"
janela_checkout = "Checkout de pedido"
janela_bling = "Bling"

g_allow_pasting_liberado = False  # registra se o "allow pasting" ja foi executado

# ==========================
# FUNÇÕES DE SUPORTE
# ==========================
def focar_janela(titulo):
    """Ativa uma janela pelo título"""
    try:
        janela = gw.getWindowsWithTitle(titulo)[0]
        janela.activate()
        return True
    except:
        return False

def pagina_danfe_pronta(timeout=10):
    """Verifica se a DANFE carregou pelo texto do clipboard"""
    if not focar_janela(janela_danfe):
        return False

    start = time.time()
    while time.time() - start < timeout:
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.3)
        txt = clipboard.paste()
        if txt and ("DANFE" in txt or "Chave de Acesso" in txt):
            return True
    return False

def clicar_ok_checkout():
    """Clica no botão OK (ajuste X,Y se necessário)"""
    pyautogui.click(x=1190, y=680)
    time.sleep(0.2)

def clicar_notas():
    """Clica nas notas (posição configurável)"""
    global g_notasX, g_notasY
    pyautogui.click(x=g_notasX, y=g_notasY)
    time.sleep(0.2)

# ==========================
# FLUXO PRINCIPAL
# ==========================
def fluxo_danfe():
    """Executa o fluxo completo da DANFE"""
    if not focar_janela(janela_danfe):
        return

    if not pagina_danfe_pronta():
        print("❌ DANFE não carregou")
        return

    # Imprimir
    pyautogui.hotkey("ctrl", "p")
    time.sleep(1)
    pyautogui.press("enter")
    print("✅ Impressão enviada")

    # Fechar aba
    time.sleep(1)
    pyautogui.hotkey("ctrl", "w")
    print("✅ Aba DANFE fechada")

    # Checkout
    if focar_janela(janela_checkout):
        time.sleep(1)
        clicar_ok_checkout()
        print("✅ Clique no OK")
        clicar_notas()
        print("✅ Clique nas notas")
        pyautogui.press("winleft")
        time.sleep(0.2)
        pyautogui.press("winleft")
        print("✅ Win pressionado duas vezes")

# ==========================
# HOTKEYS
# ==========================
def configurar_hotkeys():
    keyboard.add_hotkey("F9", capturar_mouse_com_feedback)
    keyboard.add_hotkey("F10", injetar_contador)

def capturar_mouse():
    global g_notasX, g_notasY
    x, y = pyautogui.position()
    g_notasX, g_notasY = x, y
    print(f"✅ Coordenadas salvas: X={x}, Y={y}")

def capturar_mouse_com_feedback():
    """Wrapper do F9: captura e mostra animação visual no ponto escolhido."""
    capturar_mouse()
    try:
        x, y = g_notasX, g_notasY
    except Exception:
        x, y = pyautogui.position()
    mostrar_feedback_reposicionamento(x, y)

def mostrar_feedback_reposicionamento(x, y):
    """Exibe um efeito de ripple onde a coordenada foi capturada (F9)."""
    def _anim():
        try:
            import tkinter as tk
        except Exception:
            return
        size = 140
        left = max(0, x - size // 2)
        top = max(0, y - size // 2)
        root = tk.Tk()
        try:
            root.overrideredirect(True)
            root.attributes("-topmost", True)
            try:
                root.wm_attributes("-transparentcolor", "magenta")
                transparent = "magenta"
            except Exception:
                transparent = None
                root.attributes("-alpha", 0.0)
            root.geometry(f"{size}x{size}+{left}+{top}")
            if transparent:
                root.configure(bg=transparent)
            canvas = tk.Canvas(root, width=size, height=size, highlightthickness=0,
                               bg=(transparent if transparent else "black"))
            canvas.pack()
            cx = cy = size // 2
            steps = 18
            for i in range(steps):
                r = 10 + int(((size // 2) - 12) * (i / (steps - 1)))
                canvas.delete("all")
                canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                   outline="#00E5FF", width=3)
                if i % 2 == 0:
                    canvas.create_oval(cx - int(r*0.7), cy - int(r*0.7), cx + int(r*0.7), cy + int(r*0.7),
                                       outline="#21CBF3", width=2)
                canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4,
                                   fill="#00E5FF", outline="")
                canvas.update()
                time.sleep(0.02)
            root.destroy()
        except Exception:
            try:
                root.destroy()
            except Exception:
                pass

    threading.Thread(target=_anim, daemon=True).start()

def injetar_contador():
    global g_allow_pasting_liberado
    if not focar_janela(janela_bling):
        print("⚠️ Janela do Bling não encontrada.")
        return

    pyautogui.hotkey("ctrl", "shift", "j")
    time.sleep(0.5 if not g_allow_pasting_liberado else 0.3)

    if not g_allow_pasting_liberado:
        keyboard.write("allow pasting", delay=0)
        time.sleep(0.05)
        pyautogui.press("enter")
        g_allow_pasting_liberado = True
        time.sleep(0.12)
    else:
        time.sleep(0.1)

    contador_js = r"""
(function () {
  if (document.getElementById("contadorNotasContainer")) return;

  // === Criar estilos para animações ===
  const style = document.createElement("style");
  style.innerHTML = `
    @keyframes slideDown {
      0% { transform: translateY(-50px); opacity: 0; }
      100% { transform: translateY(0); opacity: 1; }
    }
    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.1); }
      100% { transform: scale(1); }
    }
  `;
  document.head.appendChild(style);

  // === Criar container central para os cards ===
  let container = document.createElement("div");
  container.id = "contadorNotasContainer";
  Object.assign(container.style, {
    position: "fixed",
    top: "15px",                // mais próximo do topo da barra verde
    left: "50%",
    transform: "translateX(-50%)",
    display: "flex",
    gap: "20px",
    alignItems: "center",
    zIndex: 99999,
    animation: "slideDown 0.6s ease-out",
  });
  document.body.appendChild(container);

  // === Função para criar um card bonito ===
  function criarCard(id, gradiente, texto) {
    const div = document.createElement("div");
    div.id = id;
    Object.assign(div.style, {
      minWidth: "160px",
      padding: "12px 24px",
      borderRadius: "20px",
      background: gradiente,
      color: "white",
      fontSize: "18px",
      fontWeight: "600",
      fontFamily: "system-ui, sans-serif",
      textAlign: "center",
      backdropFilter: "blur(10px)",
      WebkitBackdropFilter: "blur(10px)",
      boxShadow: "0 6px 20px rgba(0,0,0,0.25)",
      transition: "all 0.3s ease-in-out",
      animation: "slideDown 0.8s ease-out",
    });
    div.innerText = texto;
    container.appendChild(div);
    return div;
  }

  // === Checkout (azul) ===
  const div1 = criarCard(
    "contadorNotasDiv",
    "linear-gradient(135deg, #2196F3, #21CBF3)",
    "Checkout: 0"
  );

  // === Hoje (laranja) ===
  const div2 = criarCard(
    "contadorNotasFeitasDiv",
    "linear-gradient(135deg, #FF9800, #F57C00)",
    "Hoje: 0"
  );

  // ==== Reset diário ====
  function resetIfNeeded() {
    const hoje = new Date().toISOString().split("T")[0];
    const ultimaData = localStorage.getItem("notasData");
    if (ultimaData !== hoje) {
      localStorage.setItem("notasData", hoje);
      localStorage.setItem("notasFeitas", 0);
    }
  }

  resetIfNeeded();
  let notasFeitas = parseInt(localStorage.getItem("notasFeitas") || "0");
  div2.innerText = "Hoje: " + notasFeitas;

  // ==== Atualiza checkout ====
  function atualizarContadorCheckout() {
    const notas = document.querySelectorAll("ul li[data-v-731ca16e]");
    const total = notas.length;
    div1.innerText = "Checkout: " + total;

    if (total === 0) {
      div1.style.background = "linear-gradient(135deg, #E53935, #B71C1C)";
      div1.style.boxShadow = "0 6px 20px rgba(229, 57, 53, 0.4)";
    } else {
      div1.style.background = "linear-gradient(135deg, #2196F3, #21CBF3)";
      div1.style.boxShadow = "0 6px 20px rgba(33, 150, 243, 0.4)";
    }
    return total;
  }

  // ==== Atualiza o "Feitas no Dia" ====
  function registrarNotasFeitas(qtd) {
    resetIfNeeded();
    notasFeitas = parseInt(localStorage.getItem("notasFeitas") || "0") + qtd;
    localStorage.setItem("notasFeitas", notasFeitas);
    div2.innerText = "Hoje: " + notasFeitas;

    // Animação pulse
    div2.style.animation = "pulse 0.4s ease-out";
    setTimeout(() => div2.style.animation = "", 400);
  }

  // Monitorar mudanças
  let ultimoTotal = atualizarContadorCheckout();
  setInterval(() => {
    const total = atualizarContadorCheckout();
    if (total < ultimoTotal) {
      const diferenca = ultimoTotal - total;
      registrarNotasFeitas(diferenca);
    }
    ultimoTotal = total;
  }, 3000);
})();
"""

    # Copia o código para a área de transferência
    # Substitui o JS pelos cards alinhados e profissionais
    contador_js = r"""
(function () {
  if (document.getElementById('blingCounters')) return;

  // ===== Styles (tipografia e alinhamento profissional)
  const style = document.createElement('style');
  style.id = 'blingCountersStyle';
  style.textContent = `
    @keyframes slideDown { 0% { transform: translateY(-12px); opacity: 0 } 100% { transform: translateY(0); opacity: 1 } }
    @keyframes pulse { 0% { transform: scale(1) } 50% { transform: scale(1.06) } 100% { transform: scale(1) } }

    .bling-counters { position: fixed; display: flex; gap: 12px; z-index: 2147483647; pointer-events: none; transform-origin: top left; animation: slideDown .35s ease-out; }
    .bling-card { pointer-events: none; min-width: 150px; height: 68px; padding: 8px 14px; border-radius: 12px; color: #fff; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji"; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; box-shadow: 0 4px 14px rgba(0,0,0,.2); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,.16) }
    .bling-card--ok { background: linear-gradient(135deg, #2196F3, #21CBF3) }
    .bling-card--alert { background: linear-gradient(135deg, #E53935, #B71C1C) }
    .bling-card--today { background: linear-gradient(135deg, #FF9800, #F57C00) }
    .bling-label { font-size: 10px; letter-spacing: .06em; text-transform: uppercase; opacity: .85; line-height: 1; margin-bottom: 4px }
    .bling-value { font-size: 28px; font-weight: 800; line-height: 1; font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased }
    .bling-pulse { animation: pulse .35s ease-out }
    @keyframes rippleExpand { 0% { transform: scale(0); opacity: .45 } 80% { opacity:.18 } 100% { transform: scale(12); opacity: 0 } }
    .bling-ripple { position: fixed; width: 14px; height: 14px; margin:-7px 0 0 -7px; border-radius: 9999px; background: radial-gradient(circle at center, rgba(255,255,255,.75), rgba(255,255,255,.35) 40%, rgba(255,255,255,0) 60%); pointer-events:none; z-index: 2147483647; animation: rippleExpand .6s ease-out forwards; mix-blend-mode: screen }
    .bling-snap { transition: top .28s cubic-bezier(.2,.8,.2,1), left .28s cubic-bezier(.2,.8,.2,1) }
    .bling-counters.bling-edit { pointer-events: auto; cursor: grab; outline: 1px dashed rgba(255,255,255,.28); border-radius: 12px }
    .bling-button { pointer-events: auto; height: 68px; padding: 0 22px; border-radius: 14px; border: none; background: linear-gradient(135deg, #5B86E5, #36D1DC); color: #fff; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji"; font-size: 15px; font-weight: 600; letter-spacing: .01em; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 22px rgba(33,150,243,.28); cursor: pointer; transition: transform .2s ease, box-shadow .2s ease, filter .2s ease; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,.16) }
    .bling-button:hover { transform: translateY(-1px); box-shadow: 0 16px 28px rgba(33,150,243,.32); filter: brightness(1.05); }
    .bling-button:active { transform: scale(.98); box-shadow: 0 6px 16px rgba(33,150,243,.24); }
    .bling-button:focus-visible { outline: 2px solid rgba(255,255,255,.7); outline-offset: 3px; }
    .bling-button.bling-secondary { background: rgba(255,255,255,.18); box-shadow: inset 0 0 0 1px rgba(255,255,255,.26); }
    .bling-counters.bling-edit .bling-button { pointer-events: none; filter: saturate(.4); cursor: default; }
    .bling-modal-overlay { position: fixed; inset: 0; background: rgba(9,17,34,.65); display: flex; align-items: center; justify-content: center; z-index: 2147483647; opacity: 0; pointer-events: none; transition: opacity .25s ease; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); padding: 24px; }
    .bling-modal-overlay.open { opacity: 1; pointer-events: auto; }
    .bling-modal { width: min(380px, 92vw); max-height: min(90vh, 620px); background: linear-gradient(165deg, #0f172a, #1d2a52 50%, #274082); border-radius: 22px; padding: 22px 22px 26px; color: #fff; box-shadow: 0 24px 60px rgba(8,14,40,.55); position: relative; font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; display: flex; flex-direction: column; gap: 16px; overflow-y: auto; }

    .bling-modal h2 { margin: 0 0 8px; font-size: 22px; font-weight: 700; letter-spacing: .01em; }
    .bling-modal p { margin: 0 0 18px; font-size: 14px; opacity: .85; line-height: 1.5; }
    .bling-close { position: absolute; top: 14px; right: 14px; width: 32px; height: 32px; border-radius: 10px; border: none; background: rgba(255,255,255,.18); color: #fff; font-size: 18px; cursor: pointer; transition: transform .2s ease, background .2s ease; }
    .bling-close:hover { transform: rotate(8deg) scale(1.04); background: rgba(255,255,255,.26); }
    .bling-close:active { transform: scale(.94); }
    .bling-input { width: 100%; border: 1px solid rgba(255,255,255,.18); border-radius: 14px; background: rgba(255,255,255,.15); padding: 12px 16px; color: #fff; font-size: 15px; font-weight: 500; outline: none; transition: border .2s ease, background .2s ease; }
    .bling-input:focus { border-color: rgba(120,178,255,.8); background: rgba(255,255,255,.22); }
    .bling-input::placeholder { color: rgba(255,255,255,.55); font-weight: 400; }
    .bling-helper { display: block; margin-top: 6px; font-size: 12px; opacity: .75; letter-spacing: .02em; }
    .bling-label-wrapper { margin-top: 12px; display: flex; flex-direction: column; align-items: center; gap: 12px; width: 100%; }
    .bling-caption { font-size: 12px; letter-spacing: .08em; text-transform: uppercase; opacity: .72; }
    .bling-label-preview { background: #fff; border-radius: 18px; width: min(260px, 90%); aspect-ratio: 2 / 3; padding: 16px 12px; box-shadow: 0 18px 40px rgba(15,23,42,.32); display: flex; align-items: center; justify-content: center; flex-direction: column; color: #0f172a; }
    .bling-label-preview svg { width: 92%; height: 92%; }
    .bling-status { margin-top: 8px; font-size: 13px; min-height: 18px; opacity: .8; transition: opacity .2s ease; }
    .bling-status.error { color: #ffd1d1; opacity: 1; }
    .bling-status.ok { color: #8ff7c9; opacity: 1; }
    .bling-modal-actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 12px; }
    @media (max-width: 720px) {
      .bling-counters { flex-wrap: wrap; justify-content: center; }
      .bling-card { min-width: 140px; }
      .bling-button { width: 100%; }
    }
  `;
  document.head.appendChild(style);

  // ===== Container
  const container = document.createElement('div');
  container.id = 'blingCounters';
  container.className = 'bling-counters';
  document.body.appendChild(container);

  // ===== Card factory (label + number)
  function createCard({ id, label, theme }) {
    const card = document.createElement('div');
    card.id = id;
    card.className = `bling-card ${theme}`;

    const lbl = document.createElement('div');
    lbl.className = 'bling-label';
    lbl.textContent = label;

    const val = document.createElement('div');
    val.className = 'bling-value';
    val.setAttribute('aria-live', 'polite');
    val.textContent = '0';

    card.appendChild(lbl);
    card.appendChild(val);
    container.appendChild(card);
    return { card, val };
  }

  // ===== Cards
  const checkout = createCard({ id: 'blingCheckout', label: 'Checkout', theme: 'bling-card--ok' });
  const today = createCard({ id: 'blingToday', label: 'Hoje', theme: 'bling-card--today' });

  const barcodeButton = document.createElement('button');
  barcodeButton.type = 'button';
  barcodeButton.className = 'bling-button';
  barcodeButton.textContent = 'Gerar codigo de barras';
  container.appendChild(barcodeButton);

  let barcodeUI = null;
  let barcodeScriptPromise = null;

  const ensureJsBarcode = () => {
    if (window.JsBarcode) return Promise.resolve(window.JsBarcode);
    if (barcodeScriptPromise) return barcodeScriptPromise;
    barcodeScriptPromise = new Promise((resolve, reject) => {
      let script = document.getElementById('blingJsBarcodeScript');
      if (!script) {
        script = document.createElement('script');
        script.id = 'blingJsBarcodeScript';
        script.src = 'https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js';
        script.crossOrigin = 'anonymous';
        script.onload = () => resolve(window.JsBarcode);
        script.onerror = () => {
          barcodeScriptPromise = null;
          reject(new Error('load error'));
        };
        document.head.appendChild(script);
      } else {
        script.addEventListener('load', () => resolve(window.JsBarcode), { once: true });
        script.addEventListener('error', () => {
          barcodeScriptPromise = null;
          reject(new Error('load error'));
        }, { once: true });
      }
    });
    return barcodeScriptPromise;
  };

  function createBarcodeModal() {
    if (barcodeUI) return barcodeUI;

    const overlay = document.createElement('div');
    overlay.id = 'blingBarcodeOverlay';
    overlay.className = 'bling-modal-overlay';

    const modal = document.createElement('div');
    modal.className = 'bling-modal';
    overlay.appendChild(modal);

    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'bling-close';
    close.innerHTML = '&times;';
    modal.appendChild(close);

    const title = document.createElement('h2');
    title.textContent = 'Gerar codigo de barras';
    modal.appendChild(title);

    const subtitle = document.createElement('p');
    subtitle.textContent = 'Digite o codigo que deseja imprimir na etiqueta 100 x 150 mm.';
    modal.appendChild(subtitle);

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'bling-input';
    input.placeholder = 'Ex: 7891234567890';
    modal.appendChild(input);

    const helper = document.createElement('span');
    helper.className = 'bling-helper';
    helper.textContent = 'O formato CODE-128 e padrao e aceita letras e numeros.';
    modal.appendChild(helper);

    const wrapper = document.createElement('div');
    wrapper.className = 'bling-label-wrapper';
    modal.appendChild(wrapper);

    const caption = document.createElement('span');
    caption.className = 'bling-caption';
    caption.textContent = 'Pre-visualizacao 100 x 150 mm';
    wrapper.appendChild(caption);

    const preview = document.createElement('div');
    preview.className = 'bling-label-preview';
    wrapper.appendChild(preview);

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    svg.setAttribute('width', '100mm');
    svg.setAttribute('height', '150mm');
    svg.setAttribute('viewBox', '0 0 400 600');
    svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    preview.appendChild(svg);

    const status = document.createElement('div');
    status.className = 'bling-status';
    modal.appendChild(status);

    const actions = document.createElement('div');
    actions.className = 'bling-modal-actions';
    modal.appendChild(actions);

    const generateBtn = document.createElement('button');
    generateBtn.type = 'button';
    generateBtn.className = 'bling-button';
    generateBtn.textContent = 'Gerar etiqueta';
    actions.appendChild(generateBtn);

    const printBtn = document.createElement('button');
    printBtn.type = 'button';
    printBtn.className = 'bling-button bling-secondary';
    printBtn.textContent = 'Imprimir';
    actions.appendChild(printBtn);

    function setStatus(message, type) {
      status.textContent = message || '';
      status.className = 'bling-status' + (type ? ' ' + type : '');
    }

    function closeModal() {
      overlay.classList.remove('open');
    }

    function renderBarcode() {
      const value = (input.value || '').trim();
      if (!value) {
        setStatus('Digite um codigo valido para gerar.', 'error');
        input.focus();
        return;
      }
      setStatus('Gerando etiqueta...');
      ensureJsBarcode()
        .then(() => {
          try {
            svg.innerHTML = '';
            window.JsBarcode(svg, value, {
              format: 'CODE128',
              lineColor: '#0f172a',
              width: 1.6,
              height: 70,
              margin: 6,
              displayValue: true,
              font: 'Segoe UI, Roboto, sans-serif',
              fontSize: 18,
              textMargin: 4
            });
            svg.setAttribute('data-code', value);
            setStatus('Etiqueta pronta. Utilize o botao imprimir.', 'ok');
          } catch (err) {
            setStatus('Nao foi possivel gerar o codigo. Verifique o valor digitado.', 'error');
          }
        })
        .catch(() => {
          setStatus('Falha ao carregar a biblioteca de codigo de barras.', 'error');
        });
    }

    function printLabel() {
      if (!svg.innerHTML.trim()) {
        setStatus('Gere um codigo antes de imprimir.', 'error');
        return;
      }
      const labelHTML = preview.innerHTML;
      const printWindow = window.open('', '_blank', 'width=900,height=700');
      if (!printWindow) {
        setStatus('Desbloqueie pop-ups para imprimir.', 'error');
        return;
      }
      printWindow.document.write(`<!DOCTYPE html><html><head><meta charset="utf-8"><title>Etiqueta</title><style>
  @page {
    size: 100mm 150mm;
    margin: 0;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #f1f5ff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Segoe UI', Roboto, sans-serif;
    margin: 0;
  }
  .label {
    width: 100mm;
    height: 150mm;
    background: #fff;
    border: 1px solid rgba(15,23,42,.12);
    border-radius: 8px;
    box-shadow: 0 6px 18px rgba(0,0,0,.25);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 12mm 8mm;
  }
  svg {
    width: 100%;
    height: auto;
  }
</style></head><body><div class="label">${labelHTML}</div></body></html>`);
      printWindow.document.close();
      printWindow.focus();
      setTimeout(() => { try { printWindow.print(); } catch (err) {} }, 300);
    }

    generateBtn.addEventListener('click', renderBarcode);
    printBtn.addEventListener('click', printLabel);
    input.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        renderBarcode();
      }
    });
    close.addEventListener('click', closeModal);
    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) {
        closeModal();
      }
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && overlay.classList.contains('open')) {
        closeModal();
      }
    });

    document.body.appendChild(overlay);
    barcodeUI = { overlay, input, setStatus, renderBarcode };
    return barcodeUI;
  }

  function openBarcodeModal() {
    const ui = createBarcodeModal();
    ui.setStatus('');
    ui.overlay.classList.add('open');
    setTimeout(() => {
      try {
        ui.input.focus({ preventScroll: true });
      } catch (err) {
        ui.input.focus();
      }
    }, 120);
  }

  barcodeButton.addEventListener('click', openBarcodeModal);


  // ===== Posição e tamanho ajustáveis (persistidos em localStorage)
  const K_TOP = 'blingTop';
  const K_LEFT = 'blingLeft';
  const K_SCALE = 'blingScale';

  function loadNum(key, def){ const v = parseFloat(localStorage.getItem(key)); return Number.isFinite(v) ? v : def }
  function saveNum(key, val){ localStorage.setItem(key, String(Math.round(val))) }

  let scale = parseFloat(localStorage.getItem(K_SCALE));
  if (!Number.isFinite(scale)) scale = 0.85; // menor por padrão

  function centerLeft() {
    const w = container.offsetWidth * scale;
    return Math.max(8, Math.round((window.innerWidth - w) / 2));
  }

  let topPx = loadNum(K_TOP, 54);
  let leftPx = loadNum(K_LEFT, centerLeft());

  function applyPlacement() {
    container.style.top = topPx + 'px';
    container.style.left = leftPx + 'px';
    container.style.transform = 'scale(' + scale + ')';
  }
  applyPlacement();

  // ===== Controles flutuantes (mover e redimensionar)
  const ENABLE_CTRL = false; // manter fixo na posição salva
  if (ENABLE_CTRL) {
    const ctrl = document.createElement('div');
    ctrl.id = 'blingCtrl';
    ctrl.style.cssText = 'position:fixed;z-index:2147483647;display:flex;gap:4px;';
    const btnStyle = 'width:18px;height:18px;border:none;border-radius:6px;background:rgba(25,25,25,.6);color:#fff;line-height:18px;font-size:12px;padding:0;cursor:pointer;user-select:none;';
    const move = document.createElement('button'); move.textContent = '⠿'; move.title='Arraste para mover'; move.style.cssText = btnStyle + 'cursor:grab;';
    const minus = document.createElement('button'); minus.textContent = '−'; minus.title='Diminuir'; minus.style.cssText = btnStyle;
    const plus = document.createElement('button'); plus.textContent = '+'; plus.title='Aumentar'; plus.style.cssText = btnStyle;
    const reset = document.createElement('button'); reset.textContent='⟲'; reset.title='Centralizar'; reset.style.cssText = btnStyle;
    ctrl.append(move, minus, plus, reset);
    document.body.appendChild(ctrl);

    function updateCtrlPos(){ ctrl.style.top = (topPx - 12) + 'px'; ctrl.style.left = (leftPx - 12) + 'px' }
    updateCtrlPos();

    // Drag to move
    let dragging = false, dx = 0, dy = 0;
    move.addEventListener('mousedown', (e)=>{ dragging = true; move.style.cursor='grabbing'; dx = e.clientX - leftPx; dy = e.clientY - topPx; e.preventDefault(); e.stopPropagation(); });
    window.addEventListener('mouseup', ()=>{ if (dragging){ dragging=false; move.style.cursor='grab'; saveNum(K_TOP, topPx); saveNum(K_LEFT, leftPx); }});
    window.addEventListener('mousemove', (e)=>{
      if (!dragging) return;
      const w = container.offsetWidth * scale; const h = container.offsetHeight * scale;
      leftPx = Math.min(Math.max(8, e.clientX - dx), Math.max(8, window.innerWidth - w - 8));
      topPx = Math.min(Math.max(8, e.clientY - dy), Math.max(8, window.innerHeight - h - 8));
      applyPlacement(); updateCtrlPos();
    }, { passive: true });

    // Scale controls
    function setScale(s){ scale = Math.min(2, Math.max(0.6, s)); container.style.transform = 'scale(' + scale + ')'; localStorage.setItem(K_SCALE, String(scale)); updateCtrlPos(); }
    minus.addEventListener('click', (e)=>{ setScale(scale - 0.05); e.stopPropagation(); });
    plus.addEventListener('click', (e)=>{ setScale(scale + 0.05); e.stopPropagation(); });
    reset.addEventListener('click', (e)=>{ topPx = 54; leftPx = centerLeft(); applyPlacement(); updateCtrlPos(); saveNum(K_TOP, topPx); saveNum(K_LEFT, leftPx); e.stopPropagation(); });
  }

  // ===== Modo reposicionar por clique (efeito visual)
  // ===== Modo de edição (Alt+P): arraste e use scroll para redimensionar
  let positionMode = false; // legado
  function showRipple(x, y){
    const r = document.createElement('div');
    r.className = 'bling-ripple';
    r.style.left = x + 'px';
    r.style.top = y + 'px';
    document.body.appendChild(r);
    setTimeout(()=> r.remove(), 650);
  }
  function clamp(min, v, max){ return Math.max(min, Math.min(max, v)); }
  function placeAt(x, y){
    const w = container.offsetWidth * scale; const h = container.offsetHeight * scale;
    leftPx = clamp(8, Math.round(x - w/2), Math.max(8, window.innerWidth - w - 8));
    topPx  = clamp(8, Math.round(y - h/2), Math.max(8, window.innerHeight - h - 8));
    container.classList.add('bling-snap');
    applyPlacement();
    setTimeout(()=> container.classList.remove('bling-snap'), 320);
    saveNum(K_TOP, topPx); saveNum(K_LEFT, leftPx);
    // leve destaque nos cards
    checkout.card.classList.add('bling-pulse'); today.card.classList.add('bling-pulse');
    setTimeout(()=>{ checkout.card.classList.remove('bling-pulse'); today.card.classList.remove('bling-pulse'); }, 360);
  }
  let editMode = false;
  let dragging = false, dx = 0, dy = 0;
  function setScale(s){
    scale = Math.min(2, Math.max(0.6, s));
    container.style.transform = 'scale(' + scale + ')';
    localStorage.setItem(K_SCALE, String(scale));
  }
  function enableEditMode(){ if (editMode) return; editMode = true; container.classList.add('bling-edit'); }
  function disableEditMode(){ if (!editMode) return; editMode = false; container.classList.remove('bling-edit'); container.style.cursor=''; dragging=false; }
  // Atalho: Alt+P alterna modo de edição
  window.addEventListener('keydown', (e)=>{
    if (e.altKey && String(e.key).toLowerCase()==='p'){ editMode ? disableEditMode() : enableEditMode(); e.preventDefault(); }
    if (editMode && e.key==='Escape'){ disableEditMode(); }
  });
  // Arrastar container quando em edição
  container.addEventListener('mousedown', (e)=>{
    if (!editMode || e.button!==0) return;
    dragging = true; dx = e.clientX - leftPx; dy = e.clientY - topPx; container.style.cursor='grabbing';
    e.preventDefault(); e.stopPropagation();
  });
  window.addEventListener('mousemove', (e)=>{
    if (!dragging) return;
    const w = container.offsetWidth * scale; const h = container.offsetHeight * scale;
    leftPx = Math.min(Math.max(8, e.clientX - dx), Math.max(8, window.innerWidth - w - 8));
    topPx  = Math.min(Math.max(8, e.clientY - dy), Math.max(8, window.innerHeight - h - 8));
    applyPlacement();
  }, { passive: true });
  window.addEventListener('mouseup', (e)=>{
    if (!dragging) return;
    dragging = false; container.style.cursor='grab';
    saveNum(K_TOP, topPx); saveNum(K_LEFT, leftPx);
    showRipple(e.clientX, e.clientY);
  });
  // Clique livre fora do container para reposicionar ao centro
  window.addEventListener('click', (e)=>{
    if (!editMode) return;
    if (e.target && (e.target===container || container.contains(e.target))) return;
    showRipple(e.clientX, e.clientY);
    placeAt(e.clientX, e.clientY);
    e.preventDefault(); e.stopPropagation();
  }, true);
  // Scroll para redimensionar quando em edição
  window.addEventListener('wheel', (e)=>{
    if (!editMode) return;
    e.preventDefault();
    const step = (e.ctrlKey ? 0.10 : 0.05) * (e.deltaY > 0 ? -1 : 1);
    setScale(scale + step);
  }, { passive: false });

  window.addEventListener('resize', ()=>{ leftPx = Math.min(leftPx, Math.max(8, window.innerWidth - container.offsetWidth*scale - 8)); applyPlacement(); if (typeof updateCtrlPos==='function') updateCtrlPos(); });

  // ===== Storage: reset diário
  function resetIfNeeded() {
    const hoje = new Date().toISOString().split('T')[0];
    const ultima = localStorage.getItem('notasData');
    if (ultima !== hoje) {
      localStorage.setItem('notasData', hoje);
      localStorage.setItem('notasFeitas', '0');
    }
  }
  resetIfNeeded();
  let notasFeitas = parseInt(localStorage.getItem('notasFeitas') || '0', 10);
  today.val.textContent = String(notasFeitas);

  // ===== Atualiza checkout (alterna cor quando vazio)
  function updateCheckout() {
    const itens = document.querySelectorAll('ul li[data-v-731ca16e]');
    const total = itens.length;
    checkout.val.textContent = String(total);
    checkout.card.classList.toggle('bling-card--alert', total === 0);
    checkout.card.classList.toggle('bling-card--ok', total !== 0);
    return total;
  }

  // ===== Incrementa "Hoje"
  function addFeitas(qtd) {
    resetIfNeeded();
    notasFeitas = parseInt(localStorage.getItem('notasFeitas') || '0', 10) + qtd;
    localStorage.setItem('notasFeitas', String(notasFeitas));
    today.val.textContent = String(notasFeitas);
    today.card.classList.remove('bling-pulse');
    // reflow para reiniciar animação
    void today.card.offsetWidth;
    today.card.classList.add('bling-pulse');
    setTimeout(() => today.card.classList.remove('bling-pulse'), 350);
  }

  // ===== Loop de monitoramento
  let ultimoTotal = updateCheckout();
  setInterval(() => {
    const total = updateCheckout();
    if (total < ultimoTotal) {
      addFeitas(ultimoTotal - total);
    }
    ultimoTotal = total;
  }, 3000);
})();
"""
    clipboard.copy(contador_js)

    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.18)
    pyautogui.press("enter")
    time.sleep(0.18)

    pyautogui.hotkey("ctrl", "shift", "j")

    print("✅ Contador bonito, centralizado e animado injetado no Bling!")

# ==========================
# LOOP INFINITO
# ==========================
if __name__ == "__main__":
    configurar_hotkeys()
    print("🤖 BlingBot rodando... (Ctrl+C para sair)")
    while True:
        fluxo_danfe()
        time.sleep(2)

