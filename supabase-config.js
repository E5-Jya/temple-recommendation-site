// ============================================================
// supabase-config.js — Shared auth + DB helpers for all pages
// ============================================================
// STEP 1: Replace these with your real Supabase project values
const SUPABASE_URL = 'https://uopxibyowyqirpeuylot.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVvcHhpYnlvd3lxaXJwZXV5bG90Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1MzgzODcsImV4cCI6MjA5MDExNDM4N30.68ArhHCqqE_X_byTFQ_0KEfynwfXIScY3sHGo0mF7pc';

// Init client
const _supabase = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// ── Auth helpers ──────────────────────────────────────────────

async function signUp(email, password) {
  const { data, error } = await _supabase.auth.signUp({ email, password });
  if (error) throw error;
  return data;
}

async function signIn(email, password) {
  const { data, error } = await _supabase.auth.signInWithPassword({ email, password });
  if (error) throw error;
  return data;
}

async function signInWithGoogle() {
  const { data, error } = await _supabase.auth.signInWithOAuth({
    provider: 'google',
    options: { redirectTo: window.location.origin + window.location.pathname }
  });
  if (error) throw error;
  return data;
}

async function signOut() {
  const { error } = await _supabase.auth.signOut();
  if (error) throw error;
}

async function getUser() {
  const { data: { user } } = await _supabase.auth.getUser();
  return user;
}

function onAuthChange(callback) {
  _supabase.auth.onAuthStateChange((event, session) => {
    callback(session?.user || null, event);
  });
}

// ── Recommendation DB helpers ────────────────────────────────

async function saveRecommendation(answers, results) {
  const user = await getUser();
  if (!user) throw new Error('Not logged in');

  const { data, error } = await _supabase
    .from('saved_recommendations')
    .upsert({
      user_id: user.id,
      answers: answers,
      results: results.map(r => ({
        id: r.id,
        nameTh: r.nameTh,
        nameEn: r.nameEn,
        province: r.province,
        district: r.district,
        score: r.score,
        matchPct: r.matchPct,
        whys: r.whys,
        link: r.link
      })),
      updated_at: new Date().toISOString()
    }, { onConflict: 'user_id' });

  if (error) throw error;
  return data;
}

async function loadRecommendation() {
  const user = await getUser();
  if (!user) return null;

  const { data, error } = await _supabase
    .from('saved_recommendations')
    .select('*')
    .eq('user_id', user.id)
    .single();

  if (error && error.code !== 'PGRST116') throw error; // PGRST116 = no rows
  return data;
}

async function deleteRecommendation() {
  const user = await getUser();
  if (!user) throw new Error('Not logged in');

  const { error } = await _supabase
    .from('saved_recommendations')
    .delete()
    .eq('user_id', user.id);

  if (error) throw error;
}

// ── Auth Modal UI ────────────────────────────────────────────

function injectAuthModal() {
  if (document.getElementById('authModal')) return;

  const modal = document.createElement('div');
  modal.id = 'authModal';
  modal.innerHTML = `
    <div class="auth-overlay" onclick="closeAuthModal()"></div>
    <div class="auth-card">
      <button class="auth-close" onclick="closeAuthModal()">&times;</button>

      <div class="auth-header">
        <div class="auth-logo">
          <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="white" stroke-width="1.5">
            <path d="M12 2L2 22h20L12 2zM12 2v20M7.5 12L12 22l4.5-10"/>
          </svg>
        </div>
        <h3 id="authTitle">เข้าสู่ระบบ</h3>
        <p id="authSubtitle">เข้าสู่ระบบเพื่อบันทึกผลแนะนำของคุณ</p>
      </div>

      <div id="authMessage" class="auth-message" style="display:none"></div>

      <form id="authForm" onsubmit="handleAuthSubmit(event)">
        <div class="auth-field">
          <label>อีเมล</label>
          <input type="email" id="authEmail" required placeholder="you@example.com">
        </div>
        <div class="auth-field">
          <label>รหัสผ่าน</label>
          <input type="password" id="authPassword" required placeholder="อย่างน้อย 6 ตัวอักษร" minlength="6">
        </div>
        <button type="submit" class="auth-btn-primary" id="authSubmitBtn">เข้าสู่ระบบ</button>
      </form>

      <div class="auth-divider"><span>หรือ</span></div>

      <button class="auth-btn-google" onclick="handleGoogleLogin()">
        <svg width="18" height="18" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18A10.96 10.96 0 001 12c0 1.77.42 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
        เข้าสู่ระบบด้วย Google
      </button>

      <div class="auth-switch">
        <span id="authSwitchText">ยังไม่มีบัญชี?</span>
        <button type="button" id="authSwitchBtn" onclick="toggleAuthMode()">สมัครสมาชิก</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);

  // Inject styles
  if (!document.getElementById('authStyles')) {
    const style = document.createElement('style');
    style.id = 'authStyles';
    style.textContent = `
      #authModal { display:none; position:fixed; inset:0; z-index:9999; align-items:center; justify-content:center; }
      #authModal.open { display:flex; }
      .auth-overlay { position:absolute; inset:0; background:rgba(0,0,0,0.5); backdrop-filter:blur(4px); }
      .auth-card {
        position:relative; z-index:1; width:400px; max-width:92vw;
        background:var(--surface,#fff); border-radius:var(--radius-lg,18px);
        box-shadow:var(--shadow-lg,0 8px 24px rgba(0,0,0,0.12));
        padding:32px; animation:slideIn 0.3s ease;
      }
      .auth-close {
        position:absolute; top:12px; right:16px;
        background:none; border:none; font-size:24px;
        color:var(--muted,#7A7670); cursor:pointer;
      }
      .auth-header { text-align:center; margin-bottom:24px; }
      .auth-logo {
        width:48px; height:48px; margin:0 auto 12px;
        background:var(--primary,#4A7C59); border-radius:50%;
        display:flex; align-items:center; justify-content:center;
      }
      .auth-header h3 { font-size:20px; font-weight:700; color:var(--foreground,#2D3436); margin:0 0 4px; }
      .auth-header p { font-size:13px; color:var(--muted,#7A7670); margin:0; }
      .auth-message {
        padding:10px 14px; border-radius:8px; font-size:13px; margin-bottom:16px;
      }
      .auth-message.error { background:#FDF2F0; color:var(--warning-dark,#A96B52); border:1px solid var(--warning-light,#D9A08B); }
      .auth-message.success { background:#EFF8F2; color:var(--primary-dark,#3A6C49); border:1px solid var(--secondary,#A8D5BA); }
      .auth-field { margin-bottom:16px; }
      .auth-field label { display:block; font-size:13px; font-weight:600; color:var(--foreground,#2D3436); margin-bottom:6px; }
      .auth-field input {
        width:100%; padding:10px 14px; border-radius:var(--radius-sm,6px);
        border:1.5px solid var(--border,#D1CCC4); background:var(--surface,#fff);
        font-size:15px; font-family:inherit; color:var(--foreground,#2D3436);
        outline:none; transition:border-color 0.2s;
      }
      .auth-field input:focus { border-color:var(--primary,#4A7C59); }
      .auth-btn-primary {
        width:100%; padding:12px; border:none; border-radius:var(--radius-sm,6px);
        background:var(--primary,#4A7C59); color:#fff;
        font-size:15px; font-weight:600; font-family:inherit;
        cursor:pointer; transition:background 0.2s;
      }
      .auth-btn-primary:hover { background:var(--primary-dark,#3A6C49); }
      .auth-btn-primary:disabled { opacity:0.5; cursor:not-allowed; }
      .auth-divider {
        display:flex; align-items:center; gap:12px;
        margin:20px 0; color:var(--muted,#7A7670); font-size:12px;
      }
      .auth-divider::before, .auth-divider::after {
        content:''; flex:1; height:1px; background:var(--border,#D1CCC4);
      }
      .auth-btn-google {
        width:100%; padding:10px; border:1.5px solid var(--border,#D1CCC4);
        border-radius:var(--radius-sm,6px); background:var(--surface,#fff);
        font-size:14px; font-weight:500; font-family:inherit;
        color:var(--foreground,#2D3436); cursor:pointer;
        display:flex; align-items:center; justify-content:center; gap:10px;
        transition:all 0.2s;
      }
      .auth-btn-google:hover { background:var(--surface-alt,#F0EDE6); border-color:var(--muted,#7A7670); }
      .auth-switch {
        text-align:center; margin-top:20px; font-size:13px; color:var(--muted,#7A7670);
      }
      .auth-switch button {
        background:none; border:none; color:var(--primary,#4A7C59);
        font-weight:600; cursor:pointer; font-size:13px; font-family:inherit;
        text-decoration:underline;
      }

      /* User menu (shown when logged in) */
      .user-menu {
        display:flex; align-items:center; gap:10px;
        margin-left:auto; padding-left:20px;
      }
      .user-avatar {
        width:28px; height:28px; border-radius:50%;
        background:var(--primary,#4A7C59); color:#fff;
        display:flex; align-items:center; justify-content:center;
        font-size:12px; font-weight:700;
      }
      .user-email { font-size:12px; color:rgba(255,255,255,0.7); max-width:140px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
      .btn-logout {
        padding:5px 12px; border-radius:var(--radius-sm,6px);
        border:1px solid rgba(255,255,255,0.2); background:transparent;
        color:rgba(255,255,255,0.7); font-size:11px; font-family:inherit;
        cursor:pointer; transition:all 0.2s;
      }
      .btn-logout:hover { background:rgba(255,255,255,0.1); color:#fff; }

      /* Save button */
      .btn-save-result {
        display:inline-flex; align-items:center; gap:8px;
        padding:12px 28px; border-radius:var(--radius-sm,6px);
        background:var(--accent,#D4A847); color:#fff;
        font-size:14px; font-weight:600; font-family:inherit;
        border:none; cursor:pointer; transition:all 0.2s;
      }
      .btn-save-result:hover { background:var(--accent-dark,#B8902E); }
      .btn-save-result:disabled { opacity:0.5; cursor:not-allowed; }
      .btn-save-result svg { width:16px; height:16px; stroke:currentColor; fill:none; stroke-width:2; }
      .save-status { font-size:13px; color:var(--primary,#4A7C59); margin-top:8px; }
    `;
    document.head.appendChild(style);
  }
}

let authMode = 'login'; // or 'signup'

function openAuthModal(mode) {
  authMode = mode || 'login';
  injectAuthModal();
  updateAuthModalUI();
  document.getElementById('authModal').classList.add('open');
  document.getElementById('authMessage').style.display = 'none';
}

function closeAuthModal() {
  document.getElementById('authModal')?.classList.remove('open');
}

function toggleAuthMode() {
  authMode = authMode === 'login' ? 'signup' : 'login';
  updateAuthModalUI();
}

function updateAuthModalUI() {
  const isLogin = authMode === 'login';
  document.getElementById('authTitle').textContent = isLogin ? 'เข้าสู่ระบบ' : 'สมัครสมาชิก';
  document.getElementById('authSubtitle').textContent = isLogin
    ? 'เข้าสู่ระบบเพื่อบันทึกผลแนะนำของคุณ'
    : 'สร้างบัญชีเพื่อบันทึกและดูผลแนะนำย้อนหลัง';
  document.getElementById('authSubmitBtn').textContent = isLogin ? 'เข้าสู่ระบบ' : 'สมัครสมาชิก';
  document.getElementById('authSwitchText').textContent = isLogin ? 'ยังไม่มีบัญชี?' : 'มีบัญชีแล้ว?';
  document.getElementById('authSwitchBtn').textContent = isLogin ? 'สมัครสมาชิก' : 'เข้าสู่ระบบ';
  document.getElementById('authMessage').style.display = 'none';
}

function showAuthMessage(msg, type) {
  const el = document.getElementById('authMessage');
  el.textContent = msg;
  el.className = 'auth-message ' + type;
  el.style.display = 'block';
}

async function handleAuthSubmit(e) {
  e.preventDefault();
  const email = document.getElementById('authEmail').value;
  const password = document.getElementById('authPassword').value;
  const btn = document.getElementById('authSubmitBtn');

  btn.disabled = true;
  btn.textContent = 'กำลังดำเนินการ...';

  try {
    if (authMode === 'login') {
      await signIn(email, password);
      closeAuthModal();
    } else {
      await signUp(email, password);
      showAuthMessage('สมัครสำเร็จ! กรุณาตรวจสอบอีเมลเพื่อยืนยันบัญชี', 'success');
    }
  } catch (err) {
    const msg = err.message.includes('Invalid login')
      ? 'อีเมลหรือรหัสผ่านไม่ถูกต้อง'
      : err.message.includes('already registered')
        ? 'อีเมลนี้ถูกใช้แล้ว'
        : err.message;
    showAuthMessage(msg, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = authMode === 'login' ? 'เข้าสู่ระบบ' : 'สมัครสมาชิก';
  }
}

async function handleGoogleLogin() {
  try {
    await signInWithGoogle();
  } catch (err) {
    showAuthMessage(err.message, 'error');
  }
}

// ── Topbar user state ────────────────────────────────────────

function updateTopbarAuth(user) {
  // Remove existing user menu
  document.querySelectorAll('.user-menu').forEach(el => el.remove());
  document.querySelectorAll('.topbar-login').forEach(el => el.remove());

  const topbar = document.querySelector('.topbar') || document.querySelector('.actions-bar');
  if (!topbar) return;

  if (user) {
    const initial = (user.email || 'U')[0].toUpperCase();
    const menu = document.createElement('div');
    menu.className = 'user-menu';
    menu.innerHTML = `
      <div class="user-avatar">${initial}</div>
      <span class="user-email">${user.email}</span>
      <button class="btn-logout" onclick="handleLogout()">ออกจากระบบ</button>
    `;
    topbar.appendChild(menu);
  } else {
    const loginBtn = document.createElement('button');
    loginBtn.className = 'btn-logout topbar-login';
    loginBtn.textContent = 'เข้าสู่ระบบ';
    loginBtn.style.marginLeft = 'auto';
    loginBtn.onclick = () => openAuthModal('login');
    topbar.appendChild(loginBtn);
  }
}

async function handleLogout() {
  await signOut();
  window.location.reload();
}

// ── Local Storage fallback (save without login) ─────────────

const LOCAL_STORAGE_KEY = 'temple_recommendation_local';

function saveRecommendationLocal(answers, results) {
  try {
    const payload = {
      answers,
      results: results.map(r => ({
        id: r.id, nameTh: r.nameTh, nameEn: r.nameEn,
        province: r.province, district: r.district,
        score: r.score, matchPct: r.matchPct,
        whys: r.whys, link: r.link
      })),
      saved_at: new Date().toISOString()
    };
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(payload));
    return payload;
  } catch (e) {
    console.warn('localStorage not available:', e);
    return null;
  }
}

function loadRecommendationLocal() {
  try {
    const raw = localStorage.getItem(LOCAL_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

function deleteRecommendationLocal() {
  try { localStorage.removeItem(LOCAL_STORAGE_KEY); } catch (e) {}
}

// Smart save: if logged in → Supabase; otherwise → localStorage
async function smartSaveRecommendation(answers, results) {
  const user = await getUser();
  if (user) {
    await saveRecommendation(answers, results);
    deleteRecommendationLocal(); // clear local copy after cloud sync
    return { method: 'cloud', user };
  } else {
    saveRecommendationLocal(answers, results);
    return { method: 'local', user: null };
  }
}

// Smart load: try Supabase first, fall back to localStorage
async function smartLoadRecommendation() {
  const user = await getUser();
  if (user) {
    const cloud = await loadRecommendation();
    if (cloud) return { ...cloud, method: 'cloud' };
  }
  const local = loadRecommendationLocal();
  if (local) return { ...local, method: 'local' };
  return null;
}

// Sync local data to cloud after login
async function syncLocalToCloud() {
  const user = await getUser();
  if (!user) return;
  const local = loadRecommendationLocal();
  if (!local) return;
  try {
    await saveRecommendation(local.answers, local.results.map(r => ({
      ...r, score: r.score || 0, matchPct: r.matchPct || 0
    })));
    deleteRecommendationLocal();
    console.log('Synced local recommendation to cloud');
  } catch (e) {
    console.warn('Failed to sync local to cloud:', e);
  }
}

// ── Temple Submission helpers ────────────────────────────────

async function submitTemple(data) {
  const user = await getUser();
  if (!user) throw new Error('กรุณาเข้าสู่ระบบก่อนส่งข้อมูลวัด');

  const { data: result, error } = await _supabase
    .from('temple_submissions')
    .insert({
      user_id: user.id,
      name_th: data.name_th,
      name_en: data.name_en || null,
      province: data.province,
      district: data.district || null,
      description: data.description,
      tradition: data.tradition || null,
      activities: data.activities || null,
      contact_info: data.contact_info || null,
      website_url: data.website_url || null
    })
    .select()
    .single();

  if (error) throw error;
  return result;
}

async function loadMySubmissions() {
  const user = await getUser();
  if (!user) return [];

  const { data, error } = await _supabase
    .from('temple_submissions')
    .select('*')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false });

  if (error) throw error;
  return data || [];
}

// ── Admin check ─────────────────────────────────────────────

const ADMIN_EMAILS = ['nattawat.vitta@gmail.com', 'earthyinw@gmail.com'];

async function isAdmin() {
  const user = await getUser();
  return user && ADMIN_EMAILS.includes(user.email);
}

// Auto-init when script loads
function initAuth() {
  injectAuthModal();
  getUser().then(user => {
    updateTopbarAuth(user);
    // Auto-sync local data to cloud when user logs in
    if (user) syncLocalToCloud();
  });
  onAuthChange((user) => {
    updateTopbarAuth(user);
    if (user) syncLocalToCloud();
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAuth);
} else {
  initAuth();
}
