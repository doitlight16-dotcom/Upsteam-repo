import React, { useState, useEffect, useRef } from "react";
import {
  ShieldCheck,
  Car,
  Users,
  TrendingUp,
  MapPin,
  Phone,
  Clock,
  Building2,
  ArrowLeft,
  ChevronRight,
  AlertTriangle,
  Lock,
  Mail,
  KeyRound,
  Navigation,
  X,
  Percent,
  LayoutGrid,
  Star,
  Languages,
  BadgeCheck,
  LogOut,
  Settings,
} from "lucide-react";

import { useTenant } from "./context/TenantContext";
import FloatingActionButton from "./components/FloatingActionButton";
import ChatDrawer from "./components/ChatDrawer";


/* ── Demo Data (unchanged) ── */

const DELEGATE = {
  name: "Асхат Ержанов",
  role: "Директор департамента международных партнёрств",
  org: "АО «НК «КазМунайГаз»",
  badge: "KMG-DLG-0417",
};

const SCHEDULE = [
  { time: "09:30", title: "Открытие павильона КМГ", place: "Холл 7, стенд A12", tag: "Официально" },
  { time: "11:15", title: "Панель: энергопереход в Центральной Азии", place: "Конференц-зал 3", tag: "Сессия" },
  { time: "14:00", title: "Встреча с ADNOC", place: "VIP-лаундж 2", tag: "Переговоры" },
  { time: "18:30", title: "Приём для делегатов КМГ", place: "Emirates Palace, зал Al Majlis", tag: "Приём" },
];

const FLEET = [
  {
    id: "car1",
    model: "Mercedes-Benz S-Class",
    plate: "AUH 4471",
    driver: "Юсуф Аль-Кетби",
    lang: "EN / RU",
    phone: "+971 50 118 22 41",
    eta: "4 мин",
    status: "На парковке P3",
  },
  {
    id: "car2",
    model: "Maybach S 680",
    plate: "AUH 9902",
    driver: "Дмитрий Коваль",
    lang: "RU / EN",
    phone: "+971 55 700 91 03",
    eta: "7 мин",
    status: "В пути к Холлу 7",
  },
  {
    id: "car3",
    model: "Mercedes V-Class (минивэн)",
    plate: "AUH 5518",
    driver: "Омар Хассан",
    lang: "EN / AR",
    phone: "+971 52 340 65 19",
    eta: "2 мин",
    status: "Ожидает у входа B",
  },
];

const PARTNERS = [
  {
    id: "p1",
    company: "ADNOC",
    person: "Sultan Al Mazrouei",
    title: "SVP, International Growth",
    country: "ОАЭ",
    lounge: "VIP-лаундж 2",
    minutesLeft: 47,
    brief:
      "Интерес к совместным нефтесервисным СП в бассейне Каспия. Ранее обсуждали своп-соглашения по СПГ на форуме в Дубае.",
  },
  {
    id: "p2",
    company: "Saudi Aramco",
    person: "Faisal Al-Qahtani",
    title: "Director, Downstream Ventures",
    country: "Саудовская Аравия",
    lounge: "VIP-лаундж 1",
    minutesLeft: 132,
    brief:
      "Рассматривают партнёрство по нефтехимии. На стороне КМГ — интерес к обмену технологиями глубокой переработки.",
  },
  {
    id: "p3",
    company: "TotalEnergies",
    person: "Claire Dubosc",
    title: "VP, Central Asia & Caspian",
    country: "Франция",
    lounge: "VIP-лаундж 3",
    minutesLeft: 268,
    brief:
      "Продление действующего СРП обсуждалось в Q2. Готовы к разговору о декарбонизации добычи.",
  },
];

const LOTS = [
  {
    id: "l1",
    kind: "Недвижимость",
    title: "Коммерческий блок, Al Reem Island",
    detail: "890 м² рядом с ADNEC, класс A",
    roi: "8.4%",
    icon: Building2,
  },
  {
    id: "l2",
    kind: "Недвижимость",
    title: "Офисные лоты, Capital Centre",
    detail: "1 200 м², сдача 2027",
    roi: "9.1%",
    icon: Building2,
  },
  {
    id: "l3",
    kind: "Авто-пул",
    title: "Коллективный выкуп: G-Class (партия из 6)",
    detail: "Прямая поставка с завода, Штутгарт",
    roi: "—",
    icon: Car,
  },
];


/* ---------------------------------------------------------------------- */
/*  ПРИМИТИВЫ (now using TenantContext)                                     */
/* ---------------------------------------------------------------------- */

function GuillochePattern({ id }) {
  const { colors } = useTenant();
  return (
    <svg width="0" height="0" style={{ position: "absolute" }}>
      <defs>
        <pattern id={id} width="64" height="64" patternUnits="userSpaceOnUse">
          {[...Array(6)].map((_, i) => (
            <path
              key={i}
              d={`M -10 ${8 * i} C 16 ${8 * i - 14}, 48 ${8 * i + 14}, 74 ${8 * i}`}
              fill="none"
              stroke={colors.gold}
              strokeWidth="0.6"
              opacity="0.5"
            />
          ))}
        </pattern>
      </defs>
    </svg>
  );
}

function TopBar({ title, onBack, right }) {
  const { colors, fonts } = useTenant();
  return (
    <div
      className="flex items-center justify-between px-5 py-4 sticky top-0 z-20"
      style={{ background: colors.bg, borderBottom: `1px solid ${colors.border}` }}
    >
      <div className="flex items-center gap-3">
        {onBack && (
          <button onClick={onBack} className="p-1 -ml-1" aria-label="Назад">
            <ArrowLeft size={20} color={colors.textMuted} />
          </button>
        )}
        <span style={{ fontFamily: fonts.display, color: colors.text, fontSize: 19, letterSpacing: 0.2 }}>
          {title}
        </span>
      </div>
      {right}
    </div>
  );
}

function EyebrowLabel({ children }) {
  const { colors, fonts } = useTenant();
  return (
    <div
      className="uppercase mb-2"
      style={{
        fontFamily: fonts.mono,
        fontSize: 11,
        letterSpacing: 2,
        color: colors.gold,
      }}
    >
      {children}
    </div>
  );
}

function SosButton({ onClick }) {
  const { colors, fonts } = useTenant();
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-1.5 px-3 py-1.5 rounded-full"
      style={{ background: "rgba(156,63,53,0.14)", border: `1px solid ${colors.accentDanger}` }}
    >
      <AlertTriangle size={13} color={colors.accentDanger} />
      <span style={{ fontFamily: fonts.mono, fontSize: 11, color: colors.accentDanger, letterSpacing: 1 }}>SOS</span>
    </button>
  );
}


function LoginScreen({ onLogin }) {
  const { colors, fonts, tenant } = useTenant();
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [mode, setMode] = useState("email");
  const canSubmit = mode === "email" ? email.includes("@kmg.kz") : token.trim().length >= 6;

  return (
    <div
      className="h-full flex flex-col justify-between px-6 pb-8 pt-16 relative overflow-hidden"
      style={{ background: `radial-gradient(120% 90% at 50% -10%, #221D14 0%, ${colors.bg} 60%)` }}
    >
      <GuillochePattern id="pattern-login" />
      <div
        className="absolute inset-0 opacity-[0.06] pointer-events-none"
        style={{ background: "url(#pattern-login)" }}
      />
      <svg className="absolute inset-0 w-full h-full opacity-10 pointer-events-none">
        <rect width="100%" height="100%" fill="url(#pattern-login)" />
      </svg>

      <div className="relative z-10">
        <div className="flex flex-col items-center text-center mt-4">
          {/* Logo or default shield icon */}
          {tenant.logo_url ? (
            <img
              src={tenant.logo_url}
              alt="Logo"
              className="w-14 h-14 rounded-full object-cover mb-5"
              style={{ border: `1px solid ${colors.borderHi}` }}
            />
          ) : (
            <div
              className="w-14 h-14 rounded-full flex items-center justify-center mb-5"
              style={{ border: `1px solid ${colors.borderHi}`, background: colors.surface }}
            >
              <ShieldCheck size={24} color={colors.gold} strokeWidth={1.5} />
            </div>
          )}
          <div style={{ fontFamily: fonts.mono, fontSize: 11, letterSpacing: 3, color: colors.textFaint }}>
            {tenant.brand_name}
          </div>
          <div
            style={{
              fontFamily: fonts.display,
              fontStyle: "italic",
              fontSize: 30,
              color: colors.text,
              marginTop: 6,
              lineHeight: 1.15,
            }}
          >
            {tenant.event_name}
          </div>
          <div style={{ fontFamily: fonts.body, fontSize: 13, color: colors.textMuted, marginTop: 10 }}>
            {tenant.tagline}
          </div>
        </div>

        <div
          className="mt-10 rounded-2xl p-5"
          style={{ background: colors.surface, border: `1px solid ${colors.border}` }}
        >
          <div className="flex gap-2 mb-5">
            <button
              onClick={() => setMode("email")}
              className="flex-1 py-2 rounded-lg text-center"
              style={{
                fontFamily: fonts.body,
                fontSize: 13,
                background: mode === "email" ? "rgba(201,162,39,0.12)" : "transparent",
                color: mode === "email" ? colors.gold : colors.textMuted,
                border: `1px solid ${mode === "email" ? colors.gold : colors.border}`,
              }}
            >
              Корпоративная почта
            </button>
            <button
              onClick={() => setMode("token")}
              className="flex-1 py-2 rounded-lg text-center"
              style={{
                fontFamily: fonts.body,
                fontSize: 13,
                background: mode === "token" ? "rgba(201,162,39,0.12)" : "transparent",
                color: mode === "token" ? colors.gold : colors.textMuted,
                border: `1px solid ${mode === "token" ? colors.gold : colors.border}`,
              }}
            >
              Токен-приглашение
            </button>
          </div>

          {mode === "email" ? (
            <label className="flex items-center gap-3 px-3 py-3 rounded-lg" style={{ border: `1px solid ${colors.border}` }}>
              <Mail size={16} color={colors.textFaint} />
              <input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="ismail@kmg.kz"
                className="bg-transparent outline-none flex-1"
                style={{ fontFamily: fonts.body, fontSize: 14, color: colors.text }}
              />
            </label>
          ) : (
            <label className="flex items-center gap-3 px-3 py-3 rounded-lg" style={{ border: `1px solid ${colors.border}` }}>
              <KeyRound size={16} color={colors.textFaint} />
              <input
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="ADIPEC-XXXXXX"
                className="bg-transparent outline-none flex-1"
                style={{ fontFamily: fonts.mono, fontSize: 14, color: colors.text, letterSpacing: 1 }}
              />
            </label>
          )}

          <button
            disabled={!canSubmit}
            onClick={onLogin}
            className="w-full mt-5 py-3 rounded-lg flex items-center justify-center gap-2"
            style={{
              fontFamily: fonts.body,
              fontSize: 14,
              fontWeight: 600,
              background: canSubmit ? colors.gold : colors.surfaceHi,
              color: canSubmit ? "#1A1508" : colors.textFaint,
              transition: "all 180ms ease",
            }}
          >
            <Lock size={14} />
            Войти в кабинет делегата
          </button>
        </div>
      </div>

      <div className="relative z-10 flex items-center justify-center gap-2 mt-8">
        <Lock size={12} color={colors.textFaint} />
        <span style={{ fontFamily: fonts.body, fontSize: 11.5, color: colors.textFaint, textAlign: "center" }}>
          Доступ разрешён только верифицированным делегатам
        </span>
      </div>
    </div>
  );
}


function DashboardScreen({ go, onSos }) {
  const { colors, fonts, tenant } = useTenant();
  return (
    <div className="h-full overflow-y-auto pb-28" style={{ background: colors.bg }}>
      <div className="px-5 pt-14 pb-6 relative" style={{ borderBottom: `1px solid ${colors.border}` }}>
        <GuillochePattern id="pattern-dash" />
        <svg className="absolute inset-0 w-full h-full opacity-[0.05] pointer-events-none">
          <rect width="100%" height="100%" fill="url(#pattern-dash)" />
        </svg>
        <div className="relative flex items-start justify-between">
          <div>
            <div style={{ fontFamily: fonts.mono, fontSize: 10.5, letterSpacing: 2, color: colors.textFaint }}>
              БЕЙДЖ {DELEGATE.badge}
            </div>
            <div style={{ fontFamily: fonts.display, fontSize: 24, color: colors.text, marginTop: 4 }}>
              {DELEGATE.name}
            </div>
            <div style={{ fontFamily: fonts.body, fontSize: 12.5, color: colors.textMuted, marginTop: 3, maxWidth: 230 }}>
              {DELEGATE.role}, {DELEGATE.org}
            </div>
          </div>
          <SosButton onClick={onSos} />
        </div>
      </div>

      <div className="px-5 mt-6">
        <EyebrowLabel>Расписание · сегодня</EyebrowLabel>
        <div className="rounded-2xl overflow-hidden" style={{ border: `1px solid ${colors.border}`, background: colors.surface }}>
          {SCHEDULE.map((s, i) => (
            <div
              key={i}
              className="flex items-center gap-4 px-4 py-3.5"
              style={{ borderBottom: i < SCHEDULE.length - 1 ? `1px solid ${colors.border}` : "none" }}
            >
              <div style={{ fontFamily: fonts.mono, fontSize: 13, color: colors.gold, minWidth: 42 }}>{s.time}</div>
              <div className="flex-1">
                <div style={{ fontFamily: fonts.body, fontSize: 13.5, color: colors.text, fontWeight: 600 }}>{s.title}</div>
                <div style={{ fontFamily: fonts.body, fontSize: 12, color: colors.textMuted, marginTop: 1 }}>{s.place}</div>
              </div>
              <div
                className="px-2 py-1 rounded-md"
                style={{ background: colors.surfaceHi, fontFamily: fonts.mono, fontSize: 10, color: colors.textMuted }}
              >
                {s.tag}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="px-5 mt-7">
        <EyebrowLabel>Быстрый переход</EyebrowLabel>
        <div className="grid grid-cols-3 gap-3">
          <NavTile icon={Car} label="Мой автопарк" onClick={() => go("fleet")} />
          <NavTile icon={Users} label="B2B нетворкинг" onClick={() => go("network")} />
          <NavTile icon={TrendingUp} label="Инвест-лоты" onClick={() => go("invest")} />
        </div>
      </div>
    </div>
  );
}

function NavTile({ icon: Icon, label, onClick }) {
  const { colors, fonts } = useTenant();
  return (
    <button
      onClick={onClick}
      className="flex flex-col items-center justify-center gap-2.5 py-5 rounded-2xl"
      style={{ background: colors.surface, border: `1px solid ${colors.border}` }}
    >
      <Icon size={20} color={colors.gold} strokeWidth={1.6} />
      <span style={{ fontFamily: fonts.body, fontSize: 11.5, color: colors.text, textAlign: "center", lineHeight: 1.25 }}>
        {label}
      </span>
    </button>
  );
}

function FleetScreen({ onBack }) {
  const { colors, fonts } = useTenant();
  const [selected, setSelected] = useState(FLEET[0].id);
  const [requesting, setRequesting] = useState(false);
  const [requested, setRequested] = useState(false);
  const car = FLEET.find((c) => c.id === selected);

  useEffect(() => {
    setRequested(false);
  }, [selected]);

  const handleRequest = () => {
    setRequesting(true);
    setTimeout(() => {
      setRequesting(false);
      setRequested(true);
    }, 1400);
  };

  return (
    <div className="h-full flex flex-col" style={{ background: colors.bg }}>
      <TopBar title="Мой автопарк" onBack={onBack} />

      <div className="px-5 pt-4">
        <div
          className="relative rounded-2xl overflow-hidden"
          style={{ height: 168, border: `1px solid ${colors.border}`, background: "#1A2119" }}
        >
          <svg viewBox="0 0 400 168" className="w-full h-full">
            <defs>
              <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#2B3527" strokeWidth="0.6" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
            <path d="M0 60 L400 40" stroke="#3B4A34" strokeWidth="10" />
            <path d="M0 60 L400 40" stroke="#5C6E52" strokeWidth="1.5" strokeDasharray="6 6" />
            <path d="M60 0 L120 168" stroke="#2F3A29" strokeWidth="14" />
            <circle cx="230" cy="46" r="6" fill={colors.gold}>
              <animate attributeName="r" values="5;8;5" dur="2s" repeatCount="indefinite" />
            </circle>
            <circle cx="230" cy="46" r="12" fill="none" stroke={colors.gold} strokeWidth="1" opacity="0.5">
              <animate attributeName="r" values="10;20;10" dur="2s" repeatCount="indefinite" />
              <animate attributeName="opacity" values="0.6;0;0.6" dur="2s" repeatCount="indefinite" />
            </circle>
            <text x="240" y="42" fill={colors.goldBright} fontSize="9" fontFamily={fonts.mono}>
              {car.model.split(" ")[0]}
            </text>
          </svg>
          <div
            className="absolute bottom-3 left-3 px-2.5 py-1 rounded-md flex items-center gap-1.5"
            style={{ background: "rgba(20,18,16,0.85)" }}
          >
            <MapPin size={11} color={colors.gold} />
            <span style={{ fontFamily: fonts.mono, fontSize: 10.5, color: colors.text }}>{car.status}</span>
          </div>
        </div>
      </div>

      <div className="px-5 mt-5">
        <EyebrowLabel>Закреплённые автомобили</EyebrowLabel>
        <div className="flex flex-col gap-2.5">
          {FLEET.map((c) => (
            <button
              key={c.id}
              onClick={() => setSelected(c.id)}
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-left"
              style={{
                background: c.id === selected ? "rgba(201,162,39,0.10)" : colors.surface,
                border: `1px solid ${c.id === selected ? colors.gold : colors.border}`,
              }}
            >
              <div
                className="w-9 h-9 rounded-full flex items-center justify-center shrink-0"
                style={{ background: colors.surfaceHi }}
              >
                <Car size={16} color={c.id === selected ? colors.gold : colors.textMuted} />
              </div>
              <div className="flex-1">
                <div style={{ fontFamily: fonts.body, fontSize: 13.5, color: colors.text, fontWeight: 600 }}>{c.model}</div>
                <div style={{ fontFamily: fonts.mono, fontSize: 11, color: colors.textFaint, marginTop: 1 }}>{c.plate} · ETA {c.eta}</div>
              </div>
              {c.id === selected && <ChevronRight size={15} color={colors.gold} />}
            </button>
          ))}
        </div>
      </div>

      <div className="px-5 mt-5 mb-6">
        <div className="rounded-2xl p-4 flex items-center gap-3" style={{ background: colors.surface, border: `1px solid ${colors.border}` }}>
          <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ background: colors.surfaceHi, border: `1px solid ${colors.border}` }}>
            <span style={{ fontFamily: fonts.display, fontSize: 16, color: colors.gold }}>{car.driver[0]}</span>
          </div>
          <div className="flex-1">
            <div style={{ fontFamily: fonts.body, fontSize: 13.5, color: colors.text, fontWeight: 600 }}>{car.driver}</div>
            <div className="flex items-center gap-1.5 mt-0.5">
              <Languages size={11} color={colors.textFaint} />
              <span style={{ fontFamily: fonts.body, fontSize: 11.5, color: colors.textMuted }}>{car.lang}</span>
            </div>
          </div>
          <a
            href={`tel:${car.phone.replace(/\s/g, "")}`}
            className="w-9 h-9 rounded-full flex items-center justify-center"
            style={{ background: "rgba(201,162,39,0.14)" }}
          >
            <Phone size={14} color={colors.gold} />
          </a>
        </div>
      </div>

      <div className="mt-auto px-5 pb-8">
        <button
          onClick={handleRequest}
          disabled={requesting}
          className="w-full py-3.5 rounded-xl flex items-center justify-center gap-2"
          style={{
            fontFamily: fonts.body,
            fontSize: 14,
            fontWeight: 600,
            background: requested ? colors.accentSuccess : colors.gold,
            color: "#1A1508",
          }}
        >
          <Navigation size={15} />
          {requesting ? "Отправляем запрос…" : requested ? "Машина в пути к вам" : "Вызвать авто к павильону 7"}
        </button>
      </div>
    </div>
  );
}


function minutesToLabel(m) {
  const h = Math.floor(m / 60);
  const mm = m % 60;
  return h > 0 ? `${h} ч ${mm} мин` : `${mm} мин`;
}

function NetworkScreen({ onBack }) {
  const { colors, fonts } = useTenant();
  const [dossier, setDossier] = useState(null);

  return (
    <div className="h-full overflow-y-auto pb-10" style={{ background: colors.bg }}>
      <TopBar title="B2B Нетворкинг" onBack={onBack} />
      <div className="px-5 pt-4 flex flex-col gap-3.5">
        {PARTNERS.map((p) => (
          <div key={p.id} className="rounded-2xl p-4" style={{ background: colors.surface, border: `1px solid ${colors.border}` }}>
            <div className="flex items-start justify-between">
              <div>
                <div style={{ fontFamily: fonts.mono, fontSize: 10.5, letterSpacing: 1.5, color: colors.textFaint }}>
                  {p.country.toUpperCase()}
                </div>
                <div style={{ fontFamily: fonts.display, fontSize: 18, color: colors.text, marginTop: 2 }}>{p.company}</div>
                <div style={{ fontFamily: fonts.body, fontSize: 12.5, color: colors.textMuted, marginTop: 2 }}>
                  {p.person} · {p.title}
                </div>
              </div>
              <BadgeCheck size={17} color={colors.gold} />
            </div>

            <div className="flex items-center gap-4 mt-3.5 pt-3.5" style={{ borderTop: `1px solid ${colors.border}` }}>
              <div className="flex items-center gap-1.5">
                <Clock size={13} color={colors.gold} />
                <span style={{ fontFamily: fonts.mono, fontSize: 12, color: colors.text }}>{minutesToLabel(p.minutesLeft)}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <MapPin size={13} color={colors.textFaint} />
                <span style={{ fontFamily: fonts.body, fontSize: 12, color: colors.textMuted }}>{p.lounge}</span>
              </div>
            </div>

            <button
              onClick={() => setDossier(p)}
              className="w-full mt-3.5 py-2.5 rounded-lg flex items-center justify-center gap-1.5"
              style={{ border: `1px solid ${colors.gold}`, fontFamily: fonts.body, fontSize: 12.5, color: colors.gold, fontWeight: 600 }}
            >
              Посмотреть досье компании
              <ChevronRight size={13} />
            </button>
          </div>
        ))}
      </div>

      {dossier && (
        <div className="fixed inset-0 z-30 flex items-end justify-center" style={{ background: "rgba(10,9,7,0.7)" }} onClick={() => setDossier(null)}>
          <div
            className="w-full rounded-t-3xl p-6 pb-9"
            style={{ background: colors.surface, border: `1px solid ${colors.border}`, borderBottom: "none" }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <div style={{ fontFamily: fonts.mono, fontSize: 10, letterSpacing: 2, color: colors.gold }}>ДОСЬЕ</div>
                <div style={{ fontFamily: fonts.display, fontSize: 22, color: colors.text, marginTop: 3 }}>{dossier.company}</div>
              </div>
              <button onClick={() => setDossier(null)}>
                <X size={18} color={colors.textMuted} />
              </button>
            </div>
            <div style={{ fontFamily: fonts.body, fontSize: 13, color: colors.textMuted, lineHeight: 1.6 }}>{dossier.brief}</div>
            <div className="mt-5 flex items-center gap-2" style={{ fontFamily: fonts.mono, fontSize: 11, color: colors.textFaint }}>
              <Star size={12} color={colors.gold} />
              подготовлено аналитиками AlmaU
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


function InvestScreen({ onBack }) {
  const { colors, fonts, tenant } = useTenant();
  return (
    <div className="h-full overflow-y-auto pb-10" style={{ background: colors.bg }}>
      <TopBar title="Инвестиционные лоты" onBack={onBack} />
      <div className="px-5 pt-3 pb-1">
        <div style={{ fontFamily: fonts.body, fontSize: 12.5, color: colors.textMuted, lineHeight: 1.55 }}>
          Закрытый каталог {tenant.brand_name}. Доступен во время поездки только делегатам.
        </div>
      </div>
      <div className="px-5 mt-4 flex flex-col gap-3">
        {LOTS.map((l) => {
          const Icon = l.icon;
          return (
            <div key={l.id} className="flex items-center gap-4 rounded-2xl p-4" style={{ background: colors.surface, border: `1px solid ${colors.border}` }}>
              <div className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0" style={{ background: colors.surfaceHi }}>
                <Icon size={18} color={colors.gold} strokeWidth={1.6} />
              </div>
              <div className="flex-1">
                <div style={{ fontFamily: fonts.mono, fontSize: 10, letterSpacing: 1.5, color: colors.textFaint }}>{l.kind.toUpperCase()}</div>
                <div style={{ fontFamily: fonts.body, fontSize: 13.5, color: colors.text, fontWeight: 600, marginTop: 2 }}>{l.title}</div>
                <div style={{ fontFamily: fonts.body, fontSize: 12, color: colors.textMuted, marginTop: 1 }}>{l.detail}</div>
              </div>
              {l.roi !== "—" && (
                <div className="flex flex-col items-end shrink-0">
                  <div className="flex items-center gap-0.5">
                    <span style={{ fontFamily: fonts.display, fontSize: 17, color: colors.gold }}>{l.roi}</span>
                    <Percent size={11} color={colors.gold} />
                  </div>
                  <span style={{ fontFamily: fonts.mono, fontSize: 9.5, color: colors.textFaint }}>ROI / год</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}


function BottomNav({ screen, go }) {
  const { colors, fonts } = useTenant();
  const items = [
    { id: "dashboard", icon: LayoutGrid, label: "Кабинет" },
    { id: "fleet", icon: Car, label: "Автопарк" },
    { id: "network", icon: Users, label: "Нетворкинг" },
    { id: "invest", icon: TrendingUp, label: "Инвест-лоты" },
  ];
  return (
    <div
      className="absolute bottom-0 left-0 right-0 flex items-stretch z-20"
      style={{ background: colors.surface, borderTop: `1px solid ${colors.border}` }}
    >
      {items.map((it) => {
        const Icon = it.icon;
        const active = screen === it.id;
        return (
          <button key={it.id} onClick={() => go(it.id)} className="flex-1 flex flex-col items-center gap-1 py-2.5">
            <Icon size={18} color={active ? colors.gold : colors.textFaint} strokeWidth={active ? 1.9 : 1.5} />
            <span style={{ fontFamily: fonts.body, fontSize: 9.5, color: active ? colors.gold : colors.textFaint }}>{it.label}</span>
          </button>
        );
      })}
    </div>
  );
}


/* ---------------------------------------------------------------------- */
/*  APP ROOT                                                                */
/* ---------------------------------------------------------------------- */

export default function App() {
  const { colors, fonts, tenant } = useTenant();
  const [screen, setScreen] = useState("login");
  const [sos, setSos] = useState(false);
  const tabScreens = ["dashboard", "fleet", "network", "invest"];
  const isAuthenticated = tabScreens.includes(screen);

  useEffect(() => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready();
      window.Telegram.WebApp.expand();
    }
  }, []);

  const go = (s) => setScreen(s);

  return (
    <div className="w-full h-full flex items-center justify-center" style={{ background: "#0B0A08", fontFamily: fonts.body }}>
      <div
        className="relative overflow-hidden"
        style={{
          width: 390,
          height: 780,
          maxHeight: "92vh",
          borderRadius: 34,
          border: `1px solid ${colors.borderHi}`,
          boxShadow: "0 30px 80px rgba(0,0,0,0.55)",
        }}
      >
        <div className="w-full h-full relative" key={screen} style={{ animation: "fadein 260ms ease" }}>
          {screen === "login" && <LoginScreen onLogin={() => go("dashboard")} />}
          {screen === "dashboard" && (
            <DashboardScreen
              go={go}
              onSos={() => setSos(true)}
            />
          )}
          {screen === "fleet" && <FleetScreen onBack={() => go("dashboard")} />}
          {screen === "network" && <NetworkScreen onBack={() => go("dashboard")} />}
          {screen === "invest" && <InvestScreen onBack={() => go("dashboard")} />}

          {tabScreens.includes(screen) && <BottomNav screen={screen} go={go} />}
        </div>

        {/* Floating Action Button + Chat Drawer (authenticated screens only) */}
        {isAuthenticated && (
          <>
            <FloatingActionButton />
            <ChatDrawer />
          </>
        )}

        {/* SOS Modal */}
        {sos && (
          <div className="absolute inset-0 z-40 flex items-center justify-center px-8" style={{ background: "rgba(10,9,7,0.88)" }}>
            <div className="w-full rounded-2xl p-6 text-center" style={{ background: colors.surface, border: `1px solid ${colors.accentDanger}` }}>
              <AlertTriangle size={26} color={colors.accentDanger} className="mx-auto" />
              <div style={{ fontFamily: fonts.display, fontSize: 19, color: colors.text, marginTop: 12 }}>
                Экстренная связь
              </div>
              <div style={{ fontFamily: fonts.body, fontSize: 12.5, color: colors.textMuted, marginTop: 6, lineHeight: 1.5 }}>
                Координатор {tenant.brand_name} на площадке свяжется с вами в течение 2 минут.
              </div>
              <a
                href={`tel:${(tenant.contact?.support_phone || "+971500000000").replace(/\s/g, "")}`}
                className="block w-full mt-5 py-3 rounded-xl text-center"
                style={{ background: colors.accentDanger, fontFamily: fonts.body, fontSize: 13.5, color: "#F1EAD9", fontWeight: 600 }}
              >
                Позвонить координатору
              </a>
              <button
                onClick={() => setSos(false)}
                className="w-full mt-2.5 py-2.5"
                style={{ fontFamily: fonts.body, fontSize: 12.5, color: colors.textFaint }}
              >
                Отмена
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
