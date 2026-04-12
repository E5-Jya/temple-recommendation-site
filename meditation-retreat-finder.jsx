import { useState, useEffect } from "react";

// ─── Icon Components ────────────────────────────────────────────────────────

const LotusIcon = ({ size = 32, color = "#fff" }) => (
  <svg width={size} height={size} viewBox="0 0 64 64" fill="none">
    <path d="M32 8C32 8 24 20 24 32C24 44 32 52 32 52C32 52 40 44 40 32C40 20 32 8 32 8Z" fill={color} opacity="0.9"/>
    <path d="M32 52C32 52 16 44 12 32C8 20 16 12 16 12C16 12 20 24 24 32C28 40 32 52 32 52Z" fill={color} opacity="0.6"/>
    <path d="M32 52C32 52 48 44 52 32C56 20 48 12 48 12C48 12 44 24 40 32C36 40 32 52 32 52Z" fill={color} opacity="0.6"/>
    <path d="M32 52C32 52 8 40 4 32C0 24 8 16 8 16C8 16 12 28 20 36C28 44 32 52 32 52Z" fill={color} opacity="0.3"/>
    <path d="M32 52C32 52 56 40 60 32C64 24 56 16 56 16C56 16 52 28 44 36C36 44 32 52 32 52Z" fill={color} opacity="0.3"/>
  </svg>
);

const SearchIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
  </svg>
);

const MapPinIcon = ({ size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
  </svg>
);

const ClockIcon = ({ size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
  </svg>
);

const HeartIcon = ({ filled, size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill={filled ? "#EF4444" : "none"} stroke={filled ? "#EF4444" : "currentColor"} strokeWidth="2" strokeLinecap="round">
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
  </svg>
);

const StarIcon = ({ filled }) => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill={filled ? "#F59E0B" : "none"} stroke="#F59E0B" strokeWidth="2">
    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
  </svg>
);

const NavigationIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <polygon points="3 11 22 2 13 21 11 13 3 11"/>
  </svg>
);

const UsersIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
  </svg>
);

const ChevronDown = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="m6 9 6 6 6-6"/>
  </svg>
);

const ArrowRight = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
  </svg>
);

// ─── Data ───────────────────────────────────────────────────────────────────

const intentOptions = [
  {
    icon: "🧘",
    label: "เริ่มต้นนั่งสมาธิ",
    sublabel: "เหมาะสำหรับผู้เริ่มต้น ไม่เคยปฏิบัติมาก่อน",
    color: "#E8F0E8",
    borderColor: "#A8C5A8",
  },
  {
    icon: "🌿",
    label: "หาความสงบจากความเครียด",
    sublabel: "ปลีกวิเวกจากชีวิตประจำวัน รีเซ็ตจิตใจ",
    color: "#E5EEF5",
    borderColor: "#9BBDD4",
  },
  {
    icon: "📿",
    label: "ต่อยอดการปฏิบัติ",
    sublabel: "มีประสบการณ์แล้ว อยากลงลึกขึ้น",
    color: "#F0ECF5",
    borderColor: "#B8A9D0",
  },
  {
    icon: "🏕️",
    label: "ปฏิบัติธรรมระยะยาว",
    sublabel: "คอร์ส 7 วันขึ้นไป ฝึกอย่างเข้มข้น",
    color: "#FDF2E9",
    borderColor: "#D4B896",
  },
];

const meditationData = [
  {
    id: 1,
    name: "วัดป่าสุคะโต",
    location: "ชัยภูมิ",
    image: "https://images.unsplash.com/photo-1545389336-cf090694435e?w=600&h=400&fit=crop",
    rating: 4.9,
    reviews: 328,
    type: "วิปัสสนา",
    duration: "3-7 วัน",
    difficulty: "ทุกระดับ",
    price: "ฟรี",
    highlight: "ธรรมชาติร่มรื่น ครูบาอาจารย์มากประสบการณ์",
    tags: ["วิปัสสนา", "ป่า", "เงียบสงบ"],
    distance: "3.2 กม.",
    nextSession: "5 เม.ย. 2026",
  },
  {
    id: 2,
    name: "ศูนย์วิปัสสนาธรรมอาภา",
    location: "เชียงใหม่",
    image: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&h=400&fit=crop",
    rating: 4.8,
    reviews: 512,
    type: "วิปัสสนา (โกเอ็นก้า)",
    duration: "10 วัน",
    difficulty: "ระดับกลาง",
    price: "ฟรี",
    highlight: "หลักสูตรวิปัสสนาแบบโกเอ็นก้า มาตรฐานสากล",
    tags: ["วิปัสสนา", "10 วัน", "โกเอ็นก้า"],
    distance: "12.5 กม.",
    nextSession: "10 เม.ย. 2026",
  },
  {
    id: 3,
    name: "วัดมเหยงคณ์",
    location: "อยุธยา",
    image: "https://images.unsplash.com/photo-1528164344705-47542687000d?w=600&h=400&fit=crop",
    rating: 4.7,
    reviews: 245,
    type: "สมถะ-วิปัสสนา",
    duration: "3-14 วัน",
    difficulty: "ผู้เริ่มต้น",
    price: "ฟรี",
    highlight: "บรรยากาศสงบ เหมาะสำหรับผู้เริ่มต้น",
    tags: ["สมถะ", "ผู้เริ่มต้น", "ประวัติศาสตร์"],
    distance: "45 กม.",
    nextSession: "1 เม.ย. 2026",
  },
  {
    id: 4,
    name: "สวนโมกขพลาราม",
    location: "สุราษฎร์ธานี",
    image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&h=400&fit=crop",
    rating: 4.9,
    reviews: 678,
    type: "อานาปานสติ",
    duration: "10 วัน",
    difficulty: "ระดับกลาง",
    price: "ฟรี",
    highlight: "สถานปฏิบัติธรรมในตำนาน โดยท่านพุทธทาส",
    tags: ["อานาปานสติ", "พุทธทาส", "ธรรมชาติ"],
    distance: "680 กม.",
    nextSession: "1 พ.ค. 2026",
  },
  {
    id: 5,
    name: "วัดอัมพวัน",
    location: "สิงห์บุรี",
    image: "https://images.unsplash.com/photo-1508672019048-805c876b67e2?w=600&h=400&fit=crop",
    rating: 4.6,
    reviews: 890,
    type: "วิปัสสนา",
    duration: "3-7 วัน",
    difficulty: "ผู้เริ่มต้น",
    price: "ฟรี",
    highlight: "สถานที่ปฏิบัติธรรมยอดนิยมอันดับ 1 ของไทย",
    tags: ["วิปัสสนา", "ยอดนิยม", "ผู้เริ่มต้น"],
    distance: "142 กม.",
    nextSession: "3 เม.ย. 2026",
  },
  {
    id: 6,
    name: "ยุวพุทธิกสมาคม",
    location: "กรุงเทพฯ",
    image: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&h=400&fit=crop",
    rating: 4.7,
    reviews: 1203,
    type: "หลากหลาย",
    duration: "1-7 วัน",
    difficulty: "ทุกระดับ",
    price: "ฟรี",
    highlight: "หลากหลายคอร์ส เดินทางสะดวกในกรุงเทพ",
    tags: ["หลากหลาย", "กรุงเทพ", "สะดวก"],
    distance: "8 กม.",
    nextSession: "2 เม.ย. 2026",
  },
];

const provinces = ["ทั้งหมด", "กรุงเทพฯ", "เชียงใหม่", "ชัยภูมิ", "สิงห์บุรี", "อยุธยา", "สุราษฎร์ธานี"];
const types = ["ทั้งหมด", "วิปัสสนา", "สมถะ", "อานาปานสติ", "หลากหลาย"];

// ─── Main App ───────────────────────────────────────────────────────────────

export default function MeditationRetreatFinder() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedProvince, setSelectedProvince] = useState("ทั้งหมด");
  const [selectedType, setSelectedType] = useState("ทั้งหมด");
  const [favorites, setFavorites] = useState(new Set());
  const [isScrolled, setIsScrolled] = useState(false);
  const [hoveredIntent, setHoveredIntent] = useState(null);
  const [selectedIntent, setSelectedIntent] = useState(null);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 60);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const toggleFavorite = (id) => {
    setFavorites((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const filteredData = meditationData.filter((item) => {
    const q = searchQuery.toLowerCase();
    const matchSearch = !q || item.name.includes(searchQuery) || item.location.includes(searchQuery) || item.type.includes(searchQuery) || item.tags.some(t => t.includes(searchQuery));
    const matchProvince = selectedProvince === "ทั้งหมด" || item.location.includes(selectedProvince);
    const matchType = selectedType === "ทั้งหมด" || item.type.includes(selectedType);
    return matchSearch && matchProvince && matchType;
  });

  return (
    <div style={{ fontFamily: "'Sarabun', 'Noto Sans Thai', -apple-system, sans-serif", background: "#F8F7F4", minHeight: "100vh", color: "#1C1C1C" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&family=Noto+Serif+Thai:wght@400;600;700&display=swap');

        * { margin: 0; padding: 0; box-sizing: border-box; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes breathe { 0%, 100% { opacity: 0.4; } 50% { opacity: 0.7; } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

        .intent-card {
          transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
          cursor: pointer;
        }
        .intent-card:hover {
          transform: translateX(6px);
          box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        }

        .retreat-card {
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .retreat-card:hover {
          transform: translateY(-6px);
          box-shadow: 0 20px 50px rgba(0,0,0,0.1);
        }

        .nav-link { transition: opacity 0.3s; }
        .nav-link:hover { opacity: 1 !important; }

        .btn-primary { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(74, 93, 76, 0.3); }

        .tag-chip { transition: all 0.2s; }
        .tag-chip:hover { background: rgba(74, 93, 76, 0.12) !important; }

        .fav-btn { transition: transform 0.2s; }
        .fav-btn:hover { transform: scale(1.15); }

        .search-box:focus-within { box-shadow: 0 0 0 3px rgba(74, 93, 76, 0.15), 0 8px 32px rgba(0,0,0,0.06); }

        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: #C5BFB3; border-radius: 3px; }
      `}</style>

      {/* ━━━ Navigation ━━━ */}
      <nav style={{
        position: "fixed", top: 0, left: 0, right: 0, zIndex: 1000,
        padding: isScrolled ? "14px 0" : "22px 0",
        background: isScrolled ? "rgba(248, 247, 244, 0.92)" : "transparent",
        backdropFilter: isScrolled ? "blur(24px) saturate(180%)" : "none",
        borderBottom: isScrolled ? "1px solid rgba(0,0,0,0.05)" : "none",
        transition: "all 0.5s cubic-bezier(0.4, 0, 0.2, 1)",
      }}>
        <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "0 32px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer" }}>
            <LotusIcon size={28} color={isScrolled ? "#4A5D4C" : "#fff"} />
            <span style={{
              fontFamily: "'Noto Serif Thai', serif",
              fontSize: "22px", fontWeight: 700,
              color: isScrolled ? "#1C1C1C" : "#fff",
              letterSpacing: "-0.5px",
            }}>
              พักใจ
            </span>
          </div>
          <div style={{ display: "flex", gap: "28px", alignItems: "center" }}>
            {["ค้นหา", "แนวปฏิบัติ", "บทความ", "เกี่ยวกับเรา"].map((item) => (
              <a key={item} className="nav-link" style={{
                color: isScrolled ? "#555" : "rgba(255,255,255,0.85)",
                textDecoration: "none", fontSize: "15px", fontWeight: 400, cursor: "pointer",
                opacity: 0.85,
              }}>
                {item}
              </a>
            ))}
            <button style={{
              padding: "9px 22px", borderRadius: "100px",
              border: isScrolled ? "1.5px solid #4A5D4C" : "1.5px solid rgba(255,255,255,0.45)",
              background: "transparent",
              color: isScrolled ? "#4A5D4C" : "#fff",
              fontSize: "14px", fontWeight: 500, cursor: "pointer",
              transition: "all 0.3s",
            }}>
              เข้าสู่ระบบ
            </button>
          </div>
        </div>
      </nav>

      {/* ━━━ Hero Section (Calm-inspired) ━━━ */}
      <section style={{
        position: "relative",
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        overflow: "hidden",
        /* Replace this with your own photo */
        backgroundImage: "url('https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=1920&q=80')",
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}>
        {/* Overlay — subtle dark + green tint */}
        <div style={{
          position: "absolute", inset: 0,
          background: "linear-gradient(135deg, rgba(30,40,30,0.55) 0%, rgba(40,55,45,0.35) 50%, rgba(20,30,25,0.45) 100%)",
        }} />

        {/* Soft light orb (decorative) */}
        <div style={{
          position: "absolute", top: "15%", right: "20%",
          width: "500px", height: "500px", borderRadius: "50%",
          background: "radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%)",
          animation: "breathe 8s ease-in-out infinite",
        }} />

        {/* Content */}
        <div style={{
          position: "relative", zIndex: 10,
          maxWidth: "1200px", width: "100%", margin: "0 auto",
          padding: "120px 32px 80px",
          display: "flex", justifyContent: "space-between", alignItems: "center", gap: "60px",
        }}>

          {/* Left side — text + intent cards */}
          <div style={{ flex: "1 1 560px", maxWidth: "580px" }}>
            {/* Heading — Calm-style serif */}
            <h1 style={{
              fontFamily: "'Noto Serif Thai', serif",
              fontSize: "clamp(40px, 5.5vw, 58px)",
              fontWeight: 700,
              color: "#fff",
              lineHeight: 1.25,
              letterSpacing: "-1px",
              marginBottom: "16px",
              animation: "fadeIn 0.8s ease-out both",
            }}>
              หาที่พักใจ
            </h1>

            <p style={{
              fontSize: "20px", fontWeight: 300, color: "rgba(255,255,255,0.8)",
              lineHeight: 1.7, marginBottom: "40px", maxWidth: "460px",
              animation: "fadeIn 0.8s ease-out 0.15s both",
            }}>
              เราอยากช่วยให้คุณค้นพบสถานที่ปฏิบัติธรรม
              <br />ที่เหมาะ และใกล้ตัวคุณ
            </p>

            {/* "What can we help with?" */}
            <p style={{
              fontSize: "16px", fontWeight: 500, color: "rgba(255,255,255,0.95)",
              marginBottom: "20px",
              animation: "fadeIn 0.8s ease-out 0.3s both",
            }}>
              วันนี้อยากเริ่มต้นแบบไหน?
            </p>

            {/* Intent option cards — Calm style */}
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {intentOptions.map((opt, i) => (
                <div
                  key={i}
                  className="intent-card"
                  onClick={() => setSelectedIntent(selectedIntent === i ? null : i)}
                  onMouseEnter={() => setHoveredIntent(i)}
                  onMouseLeave={() => setHoveredIntent(null)}
                  style={{
                    display: "flex", alignItems: "center", gap: "16px",
                    padding: "18px 24px",
                    borderRadius: "16px",
                    background: selectedIntent === i
                      ? "rgba(255,255,255,0.98)"
                      : hoveredIntent === i
                        ? "rgba(255,255,255,0.95)"
                        : "rgba(255,255,255,0.88)",
                    backdropFilter: "blur(20px)",
                    border: selectedIntent === i
                      ? `2px solid ${opt.borderColor}`
                      : "2px solid transparent",
                    boxShadow: "0 2px 12px rgba(0,0,0,0.04)",
                    animation: `fadeIn 0.6s ease-out ${0.35 + i * 0.08}s both`,
                  }}
                >
                  {/* Icon circle */}
                  <div style={{
                    width: "48px", height: "48px", borderRadius: "14px",
                    background: opt.color,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: "22px", flexShrink: 0,
                  }}>
                    {opt.icon}
                  </div>
                  {/* Text */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: "16px", fontWeight: 600, color: "#1C1C1C", marginBottom: "2px" }}>
                      {opt.label}
                    </div>
                    <div style={{ fontSize: "13px", color: "#888", fontWeight: 300 }}>
                      {opt.sublabel}
                    </div>
                  </div>
                  {/* Arrow */}
                  <div style={{ color: selectedIntent === i ? opt.borderColor : "#ccc", transition: "color 0.3s" }}>
                    <ArrowRight />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right side — stats floating card (optional decorative) */}
          <div style={{
            flex: "0 1 360px",
            animation: "fadeIn 1s ease-out 0.6s both",
          }}>
            <div style={{
              background: "rgba(255,255,255,0.12)",
              backdropFilter: "blur(24px)",
              borderRadius: "24px",
              padding: "36px 32px",
              border: "1px solid rgba(255,255,255,0.15)",
            }}>
              <p style={{ fontSize: "13px", color: "rgba(255,255,255,0.6)", fontWeight: 500, textTransform: "uppercase", letterSpacing: "1.5px", marginBottom: "24px" }}>
                แหล่งรวบรวมที่มากที่สุด
              </p>
              {[
                { num: "150+", label: "สถานปฏิบัติธรรมทั่วไทย" },
                { num: "52", label: "จังหวัดที่ครอบคลุม" },
                { num: "30+", label: "แนวทางปฏิบัติ" },
                { num: "10K+", label: "ผู้ใช้งานต่อเดือน" },
              ].map((s, i) => (
                <div key={i} style={{
                  display: "flex", alignItems: "baseline", gap: "12px",
                  padding: "14px 0",
                  borderBottom: i < 3 ? "1px solid rgba(255,255,255,0.08)" : "none",
                }}>
                  <span style={{ fontFamily: "'Noto Serif Thai', serif", fontSize: "28px", fontWeight: 700, color: "#fff", minWidth: "70px" }}>
                    {s.num}
                  </span>
                  <span style={{ fontSize: "14px", color: "rgba(255,255,255,0.65)", fontWeight: 300 }}>
                    {s.label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Scroll hint */}
        <div style={{
          position: "absolute", bottom: "32px", left: "50%", transform: "translateX(-50%)",
          display: "flex", flexDirection: "column", alignItems: "center", gap: "6px",
          animation: "breathe 3s ease-in-out infinite", cursor: "pointer",
        }}>
          <span style={{ color: "rgba(255,255,255,0.4)", fontSize: "11px", letterSpacing: "2px", textTransform: "uppercase" }}>เลื่อนลง</span>
          <ChevronDown />
        </div>
      </section>

      {/* ━━━ Search + Filter Bar (sticky) ━━━ */}
      <section style={{
        position: "sticky", top: isScrolled ? "58px" : "70px", zIndex: 100,
        background: "rgba(248, 247, 244, 0.95)",
        backdropFilter: "blur(20px)",
        borderBottom: "1px solid rgba(0,0,0,0.05)",
        transition: "top 0.5s",
      }}>
        <div style={{
          maxWidth: "1200px", margin: "0 auto", padding: "16px 32px",
          display: "flex", alignItems: "center", gap: "12px",
        }}>
          {/* Search input */}
          <div className="search-box" style={{
            flex: 1, display: "flex", alignItems: "center", gap: "10px",
            padding: "12px 20px",
            borderRadius: "14px",
            background: "#fff",
            border: "1.5px solid #E8E6E1",
            transition: "all 0.3s",
          }}>
            <div style={{ color: "#999" }}><SearchIcon /></div>
            <input
              type="text"
              placeholder="ค้นหาชื่อวัด, จังหวัด, แนวปฏิบัติ..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                flex: 1, border: "none", background: "transparent",
                fontSize: "15px", color: "#1C1C1C", fontFamily: "inherit", outline: "none",
              }}
            />
          </div>

          {/* Province select */}
          <select
            value={selectedProvince}
            onChange={(e) => setSelectedProvince(e.target.value)}
            style={{
              padding: "13px 18px", borderRadius: "14px",
              border: "1.5px solid #E8E6E1", background: "#fff",
              fontSize: "14px", color: "#444", fontFamily: "inherit",
              cursor: "pointer", appearance: "none", minWidth: "140px",
            }}
          >
            {provinces.map((p) => <option key={p}>{p}</option>)}
          </select>

          {/* Type select */}
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            style={{
              padding: "13px 18px", borderRadius: "14px",
              border: "1.5px solid #E8E6E1", background: "#fff",
              fontSize: "14px", color: "#444", fontFamily: "inherit",
              cursor: "pointer", appearance: "none", minWidth: "140px",
            }}
          >
            {types.map((t) => <option key={t}>{t}</option>)}
          </select>

          {/* Reset */}
          {(searchQuery || selectedProvince !== "ทั้งหมด" || selectedType !== "ทั้งหมด") && (
            <button
              onClick={() => { setSearchQuery(""); setSelectedProvince("ทั้งหมด"); setSelectedType("ทั้งหมด"); }}
              style={{
                padding: "13px 20px", borderRadius: "14px",
                border: "none", background: "rgba(74, 93, 76, 0.08)",
                color: "#4A5D4C", fontSize: "14px", fontWeight: 500,
                cursor: "pointer", fontFamily: "inherit", whiteSpace: "nowrap",
              }}
            >
              ล้าง
            </button>
          )}
        </div>
      </section>

      {/* ━━━ Results Section ━━━ */}
      <section style={{ maxWidth: "1200px", margin: "0 auto", padding: "40px 32px 100px" }}>
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: "28px" }}>
          <div>
            <h2 style={{
              fontFamily: "'Noto Serif Thai', serif",
              fontSize: "28px", fontWeight: 700, color: "#1C1C1C", letterSpacing: "-0.5px",
            }}>
              สถานปฏิบัติธรรมแนะนำ
            </h2>
            <p style={{ fontSize: "14px", color: "#999", marginTop: "6px" }}>
              พบ {filteredData.length} สถานที่ {searchQuery && `สำหรับ "${searchQuery}"`}
            </p>
          </div>
        </div>

        {/* Cards Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))", gap: "24px" }}>
          {filteredData.map((item, index) => (
            <div
              key={item.id}
              className="retreat-card"
              style={{
                background: "#fff",
                borderRadius: "20px",
                overflow: "hidden",
                border: "1px solid rgba(0,0,0,0.04)",
                boxShadow: "0 1px 8px rgba(0,0,0,0.03)",
                cursor: "pointer",
                animation: `slideUp 0.5s ease-out ${index * 0.07}s both`,
              }}
            >
              {/* Image */}
              <div style={{ position: "relative", height: "210px", overflow: "hidden" }}>
                <img
                  src={item.image} alt={item.name}
                  style={{ width: "100%", height: "100%", objectFit: "cover", transition: "transform 0.7s cubic-bezier(0.4, 0, 0.2, 1)" }}
                  onMouseOver={(e) => e.target.style.transform = "scale(1.06)"}
                  onMouseOut={(e) => e.target.style.transform = "scale(1)"}
                />
                <div style={{ position: "absolute", inset: 0, background: "linear-gradient(transparent 50%, rgba(0,0,0,0.25))" }} />

                {/* Favorite */}
                <button className="fav-btn" onClick={(e) => { e.stopPropagation(); toggleFavorite(item.id); }}
                  style={{
                    position: "absolute", top: "14px", right: "14px",
                    width: "38px", height: "38px", borderRadius: "50%",
                    border: "none", background: "rgba(255,255,255,0.9)",
                    backdropFilter: "blur(8px)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    cursor: "pointer", boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                  }}
                >
                  <HeartIcon filled={favorites.has(item.id)} size={18} />
                </button>

                {/* Price badge */}
                <div style={{
                  position: "absolute", top: "14px", left: "14px",
                  padding: "5px 14px", borderRadius: "100px",
                  background: "rgba(30,40,30,0.75)", backdropFilter: "blur(8px)",
                  color: "#fff", fontSize: "12px", fontWeight: 500,
                }}>
                  {item.price}
                </div>

                {/* Next session */}
                <div style={{
                  position: "absolute", bottom: "14px", left: "14px",
                  display: "flex", alignItems: "center", gap: "6px",
                  color: "rgba(255,255,255,0.9)", fontSize: "13px", fontWeight: 400,
                }}>
                  <ClockIcon size={14} /> รอบถัดไป: {item.nextSession}
                </div>
              </div>

              {/* Content */}
              <div style={{ padding: "22px 24px 24px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "6px" }}>
                  <h3 style={{ fontSize: "17px", fontWeight: 600, color: "#1C1C1C", lineHeight: 1.4 }}>
                    {item.name}
                  </h3>
                  <div style={{ display: "flex", alignItems: "center", gap: "4px", flexShrink: 0, marginLeft: "10px" }}>
                    <StarIcon filled />
                    <span style={{ fontSize: "14px", fontWeight: 600, color: "#1C1C1C" }}>{item.rating}</span>
                    <span style={{ fontSize: "12px", color: "#aaa" }}>({item.reviews})</span>
                  </div>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#999", fontSize: "13px", marginBottom: "10px" }}>
                  <MapPinIcon size={14} />
                  <span>{item.location}</span>
                  <span style={{ color: "#ddd", margin: "0 2px" }}>·</span>
                  <NavigationIcon />
                  <span>{item.distance}</span>
                </div>

                <p style={{ fontSize: "14px", color: "#777", lineHeight: 1.6, marginBottom: "14px", fontWeight: 300 }}>
                  {item.highlight}
                </p>

                {/* Tags */}
                <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginBottom: "16px" }}>
                  {item.tags.map((tag) => (
                    <span key={tag} className="tag-chip" style={{
                      padding: "4px 12px", borderRadius: "100px",
                      background: "rgba(74, 93, 76, 0.06)",
                      color: "#5A6B50", fontSize: "12px", fontWeight: 500,
                    }}>
                      {tag}
                    </span>
                  ))}
                </div>

                {/* Bottom row */}
                <div style={{
                  display: "flex", justifyContent: "space-between", alignItems: "center",
                  paddingTop: "14px", borderTop: "1px solid rgba(0,0,0,0.04)",
                }}>
                  <div style={{ display: "flex", gap: "14px" }}>
                    <span style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "13px", color: "#999" }}>
                      <ClockIcon size={14} /> {item.duration}
                    </span>
                    <span style={{ display: "flex", alignItems: "center", gap: "5px", fontSize: "13px", color: "#999" }}>
                      <UsersIcon /> {item.difficulty}
                    </span>
                  </div>
                  <button className="btn-primary" style={{
                    padding: "8px 18px", borderRadius: "100px",
                    border: "none",
                    background: "linear-gradient(135deg, #4A5D4C, #6B7256)",
                    color: "#fff", fontSize: "13px", fontWeight: 500, cursor: "pointer",
                  }}>
                    ดูรายละเอียด
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty state */}
        {filteredData.length === 0 && (
          <div style={{ textAlign: "center", padding: "80px 20px" }}>
            <div style={{ fontSize: "48px", marginBottom: "16px" }}>🔍</div>
            <p style={{ fontSize: "18px", fontWeight: 500, color: "#555", marginBottom: "8px" }}>ไม่พบสถานที่ที่ตรงกับการค้นหา</p>
            <p style={{ fontSize: "14px", color: "#999" }}>ลองเปลี่ยนคำค้นหาหรือตัวกรอง</p>
          </div>
        )}
      </section>

      {/* ━━━ CTA Section ━━━ */}
      <section style={{
        background: "linear-gradient(160deg, #2D3A2E 0%, #4A5D4C 60%, #5A6B50 100%)",
        padding: "80px 32px",
        textAlign: "center",
      }}>
        <div style={{ maxWidth: "560px", margin: "0 auto" }}>
          <LotusIcon size={44} color="rgba(255,255,255,0.7)" />
          <h2 style={{
            fontFamily: "'Noto Serif Thai', serif",
            fontSize: "30px", fontWeight: 700, color: "#fff",
            margin: "24px 0 14px", letterSpacing: "-0.5px",
          }}>
            พร้อมเริ่มต้นแล้วหรือยัง?
          </h2>
          <p style={{
            fontSize: "16px", color: "rgba(255,255,255,0.65)",
            lineHeight: 1.7, marginBottom: "32px", fontWeight: 300,
          }}>
            ไม่ว่าจะเป็นครั้งแรกหรือปฏิบัติมานาน เราพร้อมช่วยคุณค้นหาสถานที่ที่ใช่
          </p>
          <button className="btn-primary" style={{
            padding: "15px 40px", borderRadius: "100px",
            border: "none", background: "#fff",
            color: "#2D3A2E", fontSize: "16px", fontWeight: 600, cursor: "pointer",
          }}>
            เริ่มค้นหาเลย
          </button>
        </div>
      </section>

      {/* ━━━ Footer ━━━ */}
      <footer style={{ background: "#1A1A1A", padding: "56px 32px 28px", color: "rgba(255,255,255,0.45)" }}>
        <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
          <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr", gap: "40px", marginBottom: "40px" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "14px" }}>
                <LotusIcon size={24} color="#6B7256" />
                <span style={{ fontFamily: "'Noto Serif Thai', serif", fontSize: "18px", fontWeight: 700, color: "#fff" }}>พักใจ</span>
              </div>
              <p style={{ fontSize: "14px", lineHeight: 1.7, maxWidth: "280px" }}>
                แหล่งรวบรวมสถานที่ปฏิบัติธรรมที่มากที่สุดในประเทศไทย
              </p>
            </div>
            {[
              { title: "เมนู", items: ["ค้นหา", "แนวปฏิบัติ", "บทความ", "รีวิว"] },
              { title: "ข้อมูล", items: ["เกี่ยวกับเรา", "ติดต่อ", "นโยบาย", "FAQ"] },
              { title: "ติดตาม", items: ["Facebook", "Line", "Instagram", "YouTube"] },
            ].map((sec) => (
              <div key={sec.title}>
                <h4 style={{ color: "rgba(255,255,255,0.8)", fontSize: "13px", fontWeight: 600, marginBottom: "14px", letterSpacing: "0.5px" }}>{sec.title}</h4>
                {sec.items.map((i) => (
                  <a key={i} style={{ display: "block", color: "rgba(255,255,255,0.35)", fontSize: "14px", textDecoration: "none", marginBottom: "9px", cursor: "pointer", transition: "color 0.2s" }}
                    onMouseOver={(e) => e.target.style.color = "rgba(255,255,255,0.75)"}
                    onMouseOut={(e) => e.target.style.color = "rgba(255,255,255,0.35)"}
                  >{i}</a>
                ))}
              </div>
            ))}
          </div>
          <div style={{ borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: "20px", textAlign: "center", fontSize: "12px", color: "rgba(255,255,255,0.25)" }}>
            © 2026 พักใจ — หาที่พักใจ ที่เหมาะ และใกล้ตัวคุณ
          </div>
        </div>
      </footer>
    </div>
  );
}
