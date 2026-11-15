'use strict';
const API = '/api';
const $ = (id) => document.getElementById(id);
let discos = [];
let toastTimer;
const modal = $('registroModal');

function loadTheme() {
  let saved = null;
  try { saved = localStorage.getItem('g3-theme'); } catch (_) {}
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  setTheme(saved === 'dark' || saved === 'light' ? saved : (prefersDark ? 'dark' : 'light'), false);
}
function setTheme(theme, persist = true) {
  document.documentElement.dataset.theme = theme;
  $('themeIcon').textContent = theme === 'dark' ? '☀' : '☾';
  $('themeText').textContent = theme === 'dark' ? 'Claro' : 'Oscuro';
  $('themeToggle').setAttribute('aria-label', theme === 'dark' ? 'Activar tema claro' : 'Activar tema oscuro');
  document.querySelector('meta[name="theme-color"]').setAttribute('content', theme === 'dark' ? '#0b1220' : '#f6f8fc');
  if (persist) { try { localStorage.setItem('g3-theme', theme); } catch (_) {} }
}
function toast(text, isError = false) {
  const t = $('toast');
  t.textContent = text;
  t.className = 'toast visible' + (isError ? ' toast-error' : '');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.className = 'toast'; }, 4200);
}
function abrirModal() {
  $('mensaje').textContent = '';
  $('mensaje').className = 'form-message';
  if (!modal.open) modal.showModal();
  const campo = modal.querySelector('[name="marca"]');
  campo.focus();
}
function cerrarModal() { if (modal.open) modal.close(); }
async function verificarAPI() {
  try {
    const r = await fetch(`${API}/estado`, {cache:'no-store'});
    if (!r.ok) throw new Error('No disponible');
    const data = await r.json();
    $('apiStatus').textContent = `${data.aplicacion} · Online`;
    $('apiDot').className = 'connection-dot online';
  } catch (_) {
    $('apiStatus').textContent = 'API desconectada';
    $('apiDot').className = 'connection-dot offline';
  }
}
async function cargarDiscos() {
  const boton = $('btnActualizar');
  boton.disabled = true;
  try {
    const r = await fetch(`${API}/discos`, {cache:'no-store'});
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    if (!Array.isArray(data.discos)) throw new Error('Formato inesperado');
    discos = data.discos;
    actualizarIndicadores();
    renderizarTabla();
  } catch (err) {
    $('tablaDiscos').replaceChildren();
    const tr = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 6;
    td.className = 'empty-state';
    td.textContent = 'No se pudo consultar el inventario. ' + err.message;
    tr.append(td);
    $('tablaDiscos').append(tr);
    $('contadorTabla').textContent = 'Error de conexión';
    toast('No se pudo cargar el inventario', true);
  } finally {
    boton.disabled = false;
    await verificarAPI();
  }
}
function actualizarIndicadores() {
  const ssd = discos.filter(d => d.tipo === 'SSD').length;
  const hdd = discos.filter(d => d.tipo === 'HDD').length;
  const gb = discos.reduce((acc, d) => acc + Number(d.capacidad_gb || 0), 0);
  $('totalDiscos').textContent = discos.length;
  $('totalSSD').textContent = ssd;
  $('totalHDD').textContent = hdd;
  $('capacidadTotal').textContent = gb >= 1000 ? `${(gb / 1000).toFixed(2)} TB` : `${gb} GB`;
  $('inventarioCount').textContent = discos.length;
}
function renderizarTabla() {
  const search = $('busqueda').value.trim().toLocaleLowerCase('es');
  const filter = $('filtroTipo').value;
  const matches = discos.filter(d => [d.marca,d.modelo,d.interfaz].some(s => String(s ?? '').toLocaleLowerCase('es').includes(search)) && (!filter || d.tipo === filter));
  const tbody = $('tablaDiscos');
  tbody.replaceChildren();
  if (matches.length === 0) {
    const tr = document.createElement('tr'); const td = document.createElement('td');
    td.colSpan = 6; td.className = 'empty-state'; td.textContent = 'No hay discos que coincidan con tu búsqueda.';
    tr.append(td); tbody.append(tr);
  }
  matches.forEach(d => {
    const tr = document.createElement('tr');
    const cells = [String(d.id), '', d.tipo, `${Number(d.capacidad_gb).toLocaleString('es')} GB`, d.interfaz, `$${Number(d.precio_usd).toFixed(2)}`];
    cells.forEach((value, index) => {
      const td = document.createElement('td');
      if (index === 1) {
        const strong = document.createElement('strong'); strong.textContent = d.marca;
        const sub = document.createElement('small'); sub.textContent = d.modelo;
        td.className = 'model-cell'; td.append(strong, sub);
      } else if (index === 2) {
        const badge = document.createElement('span'); badge.className = 'type-badge ' + (d.tipo === 'SSD' ? 'ssd' : 'hdd'); badge.textContent = value; td.append(badge);
      } else { td.textContent = value; }
      if (index === 5) td.className = 'align-right price-cell';
      if (index === 0) td.className = 'id-cell';
      tr.append(td);
    });
    tbody.append(tr);
  });
  $('contadorTabla').textContent = `Mostrando ${matches.length} de ${discos.length} dispositivos`;
}
async function registrarDisco(e) {
  e.preventDefault();
  const f = $('formDisco'), data = new FormData(f), button = $('btnGuardar'), msg = $('mensaje');
  const payload = {
    marca: String(data.get('marca')).trim(),
    modelo: String(data.get('modelo')).trim(),
    tipo: String(data.get('tipo')),
    capacidad_gb: Number(data.get('capacidad_gb')),
    interfaz: String(data.get('interfaz')).trim(),
    precio_usd: Number(data.get('precio_usd'))
  };
  button.disabled = true;
  msg.className = 'form-message';
  msg.textContent = 'Guardando dispositivo...';
  try {
    const r = await fetch(`${API}/discos`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
    const result = await r.json();
    if (!r.ok) throw new Error(result.error || `HTTP ${r.status}`);
    f.reset();
    cerrarModal();
    await cargarDiscos();
    toast(`Disco registrado correctamente · ID ${result.disco.id}`);
  } catch (err) {
    msg.className = 'form-message error';
    msg.textContent = err.message;
  } finally { button.disabled = false; }
}
$('themeToggle').addEventListener('click', () => setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'));
$('btnActualizar').addEventListener('click', cargarDiscos);
$('busqueda').addEventListener('input', renderizarTabla);
$('filtroTipo').addEventListener('change', renderizarTabla);
$('navRegistrar').addEventListener('click', abrirModal);
$('btnNuevo').addEventListener('click', abrirModal);
$('cerrarModal').addEventListener('click', cerrarModal);
$('cancelarModal').addEventListener('click', cerrarModal);
$('formDisco').addEventListener('submit', registrarDisco);
modal.addEventListener('click', (e) => { if (e.target === modal) cerrarModal(); });
document.querySelectorAll('.nav-link[href]').forEach(link => link.addEventListener('click', () => {
  document.querySelectorAll('.nav-link[href]').forEach(item => item.classList.remove('active'));
  link.classList.add('active');
}));
loadTheme();
cargarDiscos();
