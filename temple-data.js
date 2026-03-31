// ============================================================
// temple-data.js — Shared data layer: fetches from Supabase
// and transforms rows into the shapes each page expects.
// ============================================================

const SUPABASE_REST = 'https://uopxibyowyqirpeuylot.supabase.co/rest/v1';
const SUPABASE_ANON = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVvcHhpYnlvd3lxaXJwZXV5bG90Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1MzgzODcsImV4cCI6MjA5MDExNDM4N30.68ArhHCqqE_X_byTFQ_0KEfynwfXIScY3sHGo0mF7pc';
const PHOTO_BASE = 'https://uopxibyowyqirpeuylot.supabase.co/storage/v1/object/public/temple-photos';

// ── Photo overrides (temples where hero/thumbnail use a gallery image) ──
const PHOTO_OVERRIDES = {
  'watpah-subthawee':            { hero: 'gallery_2.jpg', thumb: 'gallery_2.jpg' },
  'suan-mokkh-bangkok':          { hero: 'gallery_3.jpg', thumb: 'gallery_3.jpg' },
  'ybat-young-buddhist-association': { hero: 'gallery_2.jpg', thumb: 'gallery_2.jpg' },
  'suan-usom':                   { hero: 'gallery_2.jpg', thumb: 'gallery_2.jpg' },
};

function _photoUrl(slug, file) {
  return PHOTO_BASE + '/' + slug + '/' + file;
}

function _heroUrl(slug) {
  var ov = PHOTO_OVERRIDES[slug];
  return _photoUrl(slug, ov ? ov.hero : 'hero.jpg');
}

function _thumbUrl(slug) {
  var ov = PHOTO_OVERRIDES[slug];
  return _photoUrl(slug, ov ? ov.thumb : 'thumbnail.jpg');
}

// ── Helpers ──
function _yn(v) { return v && v.trim().toUpperCase() === 'Y'; }
function _s(v, def) { return (v && v.trim()) ? v.trim() : (def || ''); }

// ── Gradient from temple_id (deterministic hash) ──
var _PALETTES = [
  ['#1A3A2A','#2D5C3E'], ['#0B3D2E','#1A6644'], ['#1A2A4A','#2C4A80'],
  ['#2A1A3A','#4A2D5C'], ['#3A2A1A','#5C4A2D'], ['#1A3A3A','#2D5C5C'],
  ['#2A3A1A','#4A5C2D'], ['#3A1A2A','#5C2D4A'], ['#1A2A2A','#2D4A4A'],
  ['#2A2A3A','#4A4A5C'],
];
function _gradient(id) {
  var h = 0;
  for (var i = 0; i < id.length; i++) { h = ((h << 5) - h + id.charCodeAt(i)) | 0; }
  var idx = Math.abs(h) % _PALETTES.length;
  return 'linear-gradient(135deg, ' + _PALETTES[idx][0] + ', ' + _PALETTES[idx][1] + ')';
}

function _truncate(text, max) {
  max = max || 200;
  if (!text || text.length <= max) return text || '';
  var cut = text.substring(0, max);
  var sp = cut.lastIndexOf(' ');
  if (sp > max / 2) cut = cut.substring(0, sp);
  return cut + '...';
}

// ── Fetch all temples from Supabase ──
function fetchTemples() {
  return fetch(SUPABASE_REST + '/temples?select=*&order=temple_id', {
    headers: { 'apikey': SUPABASE_ANON, 'Authorization': 'Bearer ' + SUPABASE_ANON }
  }).then(function(r) {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  });
}

// ── Transform for DIRECTORY page ──
function toDirectoryFormat(row) {
  var isFree = (_s(row.retreat_cost).toLowerCase() === 'free');
  var isBKK = (_s(row.province_en) === 'Bangkok');
  var tags = [];
  if (isBKK) tags.push('bkk'); else tags.push('upcountry');
  if (_yn(row.act_lay_retreat)) tags.push('retreat');
  if (_yn(row.act_monk_ordination)) tags.push('ordain');
  if (_yn(row.act_online_live)) tags.push('online');
  if (_yn(row.act_white_robe) || _yn(row.act_nun_program)) tags.push('women');
  var tradEn = _s(row.tradition_en).toLowerCase();
  var nameEn = _s(row.name_en).toLowerCase();
  if (tradEn.indexOf('forest') >= 0 || nameEn.indexOf('forest') >= 0) tags.push('forest');

  var chips = [];
  if (_yn(row.act_lay_retreat)) chips.push('คอร์สปฏิบัติ');
  if (_yn(row.act_monk_ordination)) chips.push('บวชพระ');
  if (_yn(row.act_online_live)) chips.push('ออนไลน์');
  if (_yn(row.act_nun_program) || _yn(row.act_white_robe)) chips.push('ผู้หญิง/แม่ชี');
  var trad = _s(row.tradition_th);
  if (trad.indexOf('ธรรมยุต') >= 0) chips.push('ธรรมยุต');
  else if (trad.indexOf('เถรวาท') >= 0) chips.push('เถรวาท');

  return {
    id: row.temple_id,
    slug: _s(row.slug),
    thumbnailUrl: PHOTO_OVERRIDES[_s(row.slug)] ? _thumbUrl(_s(row.slug)) : '',
    nameTh: _s(row.name_th),
    nameEn: _s(row.name_en),
    placeType: _s(row.place_type_th),
    province: _s(row.province_th),
    district: _s(row.district_th),
    tradition: _s(row.tradition_th) + ' – ' + _s(row.tradition_en),
    cost: isFree ? 'free' : 'paid',
    tags: tags,
    actRetreats: _yn(row.act_lay_retreat),
    actOrdain: _yn(row.act_monk_ordination),
    actOnline: _yn(row.act_online_live),
    actWomen: _yn(row.act_white_robe) || _yn(row.act_nun_program),
    isFree: isFree,
    isBKK: isBKK,
    abbotTh: _s(row.abbot_th),
    blurb: _truncate(_s(row.blurb_th)),
    costLabel: isFree ? 'ฟรี' : _s(row.retreat_cost),
    costClass: isFree ? 'chip-cost' : 'chip-cost-paid',
    chips: chips,
    gradient: _gradient(row.temple_id),
    link: 'temple-detail.html?id=' + row.temple_id,
  };
}

// ── Transform for RECOMMENDATION page ──
function toRecommendationFormat(row) {
  var isBKK = (_s(row.province_en) === 'Bangkok');
  var isFree = (_s(row.retreat_cost).toLowerCase() === 'free');
  var minDays = parseFloat(_s(row.retreat_min_days, '0')) || 0;

  var scores = {};
  if (isBKK) scores.location_bkk = 3; else scores.location_upcountry = 3;
  scores.location_any = 2;

  if (minDays <= 0.5)      { scores.duration_halfday = 3; scores.duration_weekend = 3; scores.duration_week = 3; }
  else if (minDays <= 1)   { scores.duration_halfday = 3; scores.duration_weekend = 3; scores.duration_week = 3; }
  else if (minDays <= 3)   { scores.duration_weekend = 3; scores.duration_week = 3; scores.duration_long = 3; }
  else if (minDays <= 7)   { scores.duration_week = 3; scores.duration_long = 3; }
  else                     { scores.duration_long = 3; }

  if (isFree) { scores.budget_free = 3; scores.budget_any = 2; }
  else        { scores.budget_mid = 2; scores.budget_any = 2; }

  if (_yn(row.act_daily_meditation)) scores.activity_meditation = 3;
  if (_yn(row.act_dhamma_talk)) scores.activity_dhamma_talk = 3;
  if (_yn(row.act_monk_ordination)) scores.activity_ordain = 3;
  if (!isBKK) scores.activity_nature = (_s(row.tradition_en).toLowerCase().indexOf('forest') >= 0) ? 3 : 2;

  scores.profile_beginner = 3;
  if (minDays >= 5) { scores.profile_intermediate = 3; scores.profile_beginner = 2; }
  if (_yn(row.act_white_robe) || _yn(row.act_nun_program)) scores.profile_women = 3;
  if (isBKK && minDays <= 1) scores.profile_family = 2;

  var whys = [];
  if (isFree) whys.push('ฟรีทุกกิจกรรม บริจาคตามศรัทธา');
  whys.push('เปิดรับผู้ปฏิบัติธรรม ขั้นต่ำ ' + _s(row.retreat_min_days, '0') + ' วัน');
  if (_yn(row.act_monk_ordination)) whys.push('รับบวชพระ/สามเณร');
  if (_yn(row.act_online_live)) whys.push('ถ่ายทอดสดออนไลน์');
  if (isBKK) whys.push('เดินทางสะดวก ในกรุงเทพฯ');
  else whys.push('สงบ ไกลเมือง เหมาะปฏิบัติจริงจัง');
  if (_yn(row.act_white_robe) || _yn(row.act_nun_program)) whys.push('เปิดรับสตรี/แม่ชี');

  return {
    id: row.temple_id,
    nameTh: _s(row.name_th),
    nameEn: _s(row.name_en),
    province: _s(row.province_th),
    district: _s(row.district_th),
    scores: scores,
    whys: whys.slice(0, 4),
    link: 'temple-detail.html?id=' + row.temple_id,
  };
}

// ── Transform for DETAIL page ──
function toDetailFormat(row) {
  var activityMap = [
    ['act_daily_meditation', 'นั่งสมาธิประจำวัน'],
    ['act_dhamma_talk', 'บรรยายธรรม'],
    ['act_lay_retreat', 'คอร์สปฏิบัติ'],
    ['act_monk_ordination', 'บวชพระ'],
    ['act_novice_ordination', 'บวชสามเณร'],
    ['act_white_robe', 'บวชชีพราหมณ์'],
    ['act_nun_program', 'โครงการแม่ชี'],
    ['act_annual_kathin', 'ทอดกฐิน'],
    ['act_special_events', 'กิจกรรมพิเศษ'],
    ['act_online_live', 'ถ่ายทอดสดออนไลน์'],
    ['act_community_service', 'บริการสังคม'],
  ];

  var slug = _s(row.slug);
  var ov = PHOTO_OVERRIDES[slug];

  return {
    slug: slug,
    heroUrl: ov ? _heroUrl(slug) : '',
    nameTh: _s(row.name_th),
    nameEn: _s(row.name_en),
    province: _s(row.province_th),
    district: _s(row.district_th),
    tradition: _s(row.tradition_th),
    abbot: _s(row.abbot_th),
    blurbTh: _s(row.blurb_th),
    blurbEn: _s(row.blurb_en),
    activities: activityMap.map(function(pair) {
      return { name: pair[1], available: _yn(row[pair[0]]) };
    }),
    retreatInfo: {
      minDays: _s(row.retreat_min_days, 'N/A'),
      cost: _s(row.retreat_cost, 'N/A'),
      bookingReq: _yn(row.retreat_booking_req),
      bookingChannel: _s(row.retreat_booking_channel, '-'),
      capacity: _s(row.retreat_capacity, 'ไม่ระบุ'),
    },
    ordinationInfo: {
      minDays: _s(row.ord_min_days, 'N/A'),
      cost: _s(row.ord_cost, 'N/A'),
      prerequisite: _s(row.ord_prerequisite, '-'),
    },
    schedule: {
      wake: _s(row.sched_wake_time, 'N/A'),
      morningChant: _s(row.sched_morning_chant, 'N/A'),
      mealCount: _s(row.sched_meal_count, 'N/A'),
      mealType: _s(row.sched_meal_type, 'N/A'),
      eveningChant: _s(row.sched_evening_chant, 'N/A'),
    },
    contact: {
      website: _s(row.website),
      facebook: _s(row.facebook_main),
      facebookEn: _s(row.facebook_en),
      line: _s(row.line_oa),
      phone: _s(row.phone),
      address: _s(row.address_th),
    },
    gradient: _gradient(row.temple_id),
    foundedBe: _s(row.founded_be, '-'),
    foundedCe: _s(row.founded_ce, '-'),
    lastUpdated: _s(row.last_updated, '-'),
  };
}
