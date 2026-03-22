import { AnimatePresence, motion } from "framer-motion";
import { AlertCircle, BarChart2, CheckSquare, Layers } from "lucide-react";
import { useMemo, useState } from "react";

import PAIN_RAW from "@/data/pain.json";
import PROJECT from "@/data/project.json";
import STAGES_RAW from "@/data/stages.json";
import STATS_RAW from "@/data/stats.json";
import TASKS_RAW from "@/data/tasks.json";

type Lang = "ua" | "en" | "pt";
type TaskStatus = "ready" | "in_progress" | "pending" | "blocked";

// ─── helpers ────────────────────────────────────────────────────────────────

function daysUntil(dateStr: string): number {
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  const target = new Date(dateStr);
  return Math.ceil((target.getTime() - now.getTime()) / 86_400_000);
}

function StatusBadge({ status, lang }: { status: TaskStatus; lang: Lang }) {
  const ui = PROJECT.ui[lang];
  const map: Record<TaskStatus, { label: string; color: string; dot: string }> =
    {
      ready: {
        label: ui.statusReady,
        color: "bg-emerald-100 text-emerald-800",
        dot: "bg-emerald-500",
      },
      in_progress: {
        label: ui.statusInProgress,
        color: "bg-amber-100 text-amber-800",
        dot: "bg-amber-400",
      },
      pending: {
        label: ui.statusPending,
        color: "bg-zinc-100 text-zinc-600",
        dot: "bg-zinc-400",
      },
      blocked: {
        label: ui.statusBlocked,
        color: "bg-red-100 text-red-700",
        dot: "bg-red-500",
      },
    };
  const { label, color, dot } = map[status] ?? map.pending;
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${color}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${dot}`} />
      {label}
    </span>
  );
}

// ─── sections ────────────────────────────────────────────────────────────────

function PainSection({ lang }: { lang: Lang }) {
  const impactBorder: Record<string, string> = {
    high: "border-l-red-500",
    medium: "border-l-amber-400",
    low: "border-l-green-500",
  };
  return (
    <div className="space-y-3 px-4 pb-8 pt-4">
      {PAIN_RAW.items.map((item, i) => {
        const t = item[lang] as { title: string; description: string };
        return (
          <div
            key={i}
            className={`rounded-xl border border-zinc-200 border-l-4 ${impactBorder[item.impact] ?? "border-l-zinc-300"} bg-white p-4 shadow-sm`}
          >
            <div className="flex items-start gap-3">
              <span className="text-xl leading-none">{item.icon}</span>
              <div>
                <p className="font-semibold text-zinc-900 text-sm leading-snug">
                  {t.title}
                </p>
                <p className="mt-1 text-xs text-zinc-500">{t.description}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function TasksSection({ lang }: { lang: Lang }) {
  const ui = PROJECT.ui[lang];
  const allCategories = Object.keys(TASKS_RAW.categories[lang]);
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    return TASKS_RAW.items.filter((t) => {
      const matchCat =
        activeCategory === "all" || t.category === activeCategory;
      const text = (t[lang as keyof typeof t] as string | undefined) ?? "";
      const matchSearch =
        !search || text.toLowerCase().includes(search.toLowerCase());
      return matchCat && matchSearch;
    });
  }, [activeCategory, search, lang]);

  return (
    <div className="pb-8">
      {/* search */}
      <div className="px-4 pt-4 pb-3">
        <input
          type="text"
          placeholder={ui.search}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:border-zinc-400"
        />
      </div>

      {/* category filter */}
      <div className="flex gap-2 overflow-x-auto px-4 pb-3 no-scrollbar">
        <button
          onClick={() => setActiveCategory("all")}
          className={`shrink-0 rounded-full px-3 py-1 text-xs font-medium transition-colors ${
            activeCategory === "all"
              ? "bg-zinc-900 text-white"
              : "bg-zinc-100 text-zinc-600"
          }`}
        >
          {ui.filterAll}
        </button>
        {allCategories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`shrink-0 rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              activeCategory === cat
                ? "bg-zinc-900 text-white"
                : "bg-zinc-100 text-zinc-600"
            }`}
          >
            {(TASKS_RAW.categories[lang] as Record<string, string>)[cat]}
          </button>
        ))}
      </div>

      {/* task list */}
      <div className="space-y-2 px-4">
        {filtered.map((task) => {
          const days =
            "deadline" in task && task.deadline
              ? daysUntil(task.deadline as string)
              : null;
          const urgent = days !== null && days <= 7;
          const title =
            (task[lang as keyof typeof task] as string | undefined) ?? "";
          const catLabel =
            (TASKS_RAW.categories[lang] as Record<string, string>)[
              task.category
            ] ?? task.category;
          return (
            <div
              key={task.id}
              className="rounded-xl border border-zinc-200 bg-white p-3 shadow-sm"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-zinc-900 leading-snug">
                    {title}
                  </p>
                  <p className="mt-0.5 text-[10px] text-zinc-400">
                    {task.gh ? `#${task.gh} · ` : ""}
                    {catLabel}
                  </p>
                </div>
                <StatusBadge
                  status={task.status as TaskStatus}
                  lang={lang}
                />
              </div>
              {days !== null && (
                <p
                  className={`mt-2 text-xs font-medium ${urgent ? "text-red-600" : "text-zinc-500"}`}
                >
                  {days > 0
                    ? `${days} ${ui.days} ${ui.deadlineIn}`
                    : days === 0
                      ? "🔔 Today!"
                      : `⚠️ ${Math.abs(days)} ${ui.days} overdue`}
                </p>
              )}
            </div>
          );
        })}
        {filtered.length === 0 && (
          <p className="py-8 text-center text-sm text-zinc-400">
            No tasks found
          </p>
        )}
      </div>
    </div>
  );
}

function StagesSection({ lang }: { lang: Lang }) {
  const stageColor: Record<string, string> = {
    completed: "border-emerald-500 bg-emerald-50",
    active: "border-amber-400 bg-amber-50",
    upcoming: "border-zinc-200 bg-white",
  };
  const dotColor: Record<string, string> = {
    completed: "bg-emerald-500",
    active: "bg-amber-400",
    upcoming: "bg-zinc-300",
  };
  const labelColor: Record<string, string> = {
    completed: "text-emerald-700",
    active: "text-amber-700",
    upcoming: "text-zinc-400",
  };
  const labelText: Record<string, Record<Lang, string>> = {
    completed: { ua: "✅ Завершено", en: "✅ Completed", pt: "✅ Concluído" },
    active: { ua: "🔄 В роботі", en: "🔄 Active", pt: "🔄 Em andamento" },
    upcoming: { ua: "⏳ Очікує", en: "⏳ Upcoming", pt: "⏳ Em breve" },
  };

  return (
    <div className="space-y-4 px-4 pb-8 pt-4">
      {STAGES_RAW.stages.map((stage) => {
        const data = stage[lang] as { title: string; deliverables: string[] };
        return (
          <div
            key={stage.id}
            className={`rounded-xl border-2 p-4 ${stageColor[stage.status] ?? stageColor.upcoming}`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span
                  className={`h-2.5 w-2.5 rounded-full ${dotColor[stage.status]} ${stage.status === "active" ? "animate-pulse" : ""}`}
                />
                <span className="font-bold text-zinc-900 text-sm">
                  {data.title}
                </span>
              </div>
              <span
                className={`text-xs font-medium ${labelColor[stage.status]}`}
              >
                {labelText[stage.status]?.[lang]}
              </span>
            </div>
            <p className="text-xs text-zinc-500 mb-3">{stage.dateRange}</p>
            <ul className="space-y-1.5">
              {data.deliverables.map((d, i) => (
                <li
                  key={i}
                  className="flex items-center gap-2 text-xs text-zinc-700"
                >
                  <span className="text-zinc-400">—</span>
                  {d}
                </li>
              ))}
            </ul>
          </div>
        );
      })}
    </div>
  );
}

function StatsSection({ lang }: { lang: Lang }) {
  type StatItem = {
    label_ua: string;
    label_en: string;
    label_pt: string;
    value: string;
    sub_ua: string;
    sub_en: string;
    sub_pt: string;
  };
  return (
    <div className="grid grid-cols-2 gap-3 px-4 pb-8 pt-4">
      {(STATS_RAW as StatItem[]).map((stat, i) => (
        <div
          key={i}
          className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm"
        >
          <p className="text-2xl font-bold text-zinc-900">{stat.value}</p>
          <p className="mt-1 text-xs font-medium text-zinc-700">
            {stat[`label_${lang}`]}
          </p>
          <p className="text-[11px] text-zinc-400">{stat[`sub_${lang}`]}</p>
        </div>
      ))}
    </div>
  );
}

// ─── main page ────────────────────────────────────────────────────────────────

const TABS = [
  { id: "pain", icon: AlertCircle },
  { id: "tasks", icon: CheckSquare },
  { id: "stages", icon: Layers },
  { id: "metrics", icon: BarChart2 },
] as const;

type TabId = (typeof TABS)[number]["id"];

export default function Home() {
  const [lang, setLang] = useState<Lang>(PROJECT.defaultLang as Lang);
  const [activeTab, setActiveTab] = useState<TabId>("tasks");
  const ui = PROJECT.ui[lang];

  const tabLabel: Record<TabId, string> = {
    pain: ui.pain,
    tasks: ui.tasks,
    stages: ui.stages,
    metrics: ui.metrics,
  };

  const langFlags: Record<Lang, string> = { ua: "🇺🇦", en: "🇬🇧", pt: "🇵🇹" };

  return (
    <div className="flex min-h-screen flex-col bg-zinc-50">
      {/* header */}
      <header className="sticky top-0 z-30 bg-zinc-900 text-white shadow-lg">
        <div className="flex items-center justify-between px-4 py-3">
          <div>
            <p className="text-[10px] font-mono tracking-widest text-zinc-400">
              {PROJECT.projectCode}
            </p>
            <p className="text-sm font-bold leading-tight">
              {PROJECT.clientName}
            </p>
          </div>
          {/* language switcher */}
          <div className="flex gap-1">
            {(["ua", "en", "pt"] as Lang[]).map((l) => (
              <button
                key={l}
                onClick={() => setLang(l)}
                className={`rounded-lg px-2 py-1 text-base transition-colors ${
                  lang === l ? "bg-white/20" : "opacity-50 hover:opacity-80"
                }`}
                title={l.toUpperCase()}
              >
                {langFlags[l]}
              </button>
            ))}
          </div>
        </div>
        {/* tags */}
        <div className="flex gap-2 overflow-x-auto px-4 pb-3 no-scrollbar">
          {PROJECT.tags.map((tag) => (
            <span
              key={tag}
              className="shrink-0 rounded-full bg-white/10 px-2.5 py-0.5 text-[11px] font-medium text-zinc-300"
            >
              {tag}
            </span>
          ))}
          <span className="shrink-0 rounded-full bg-white/10 px-2.5 py-0.5 text-[11px] text-zinc-400">
            {ui.updated}: {PROJECT.updatedAt}
          </span>
        </div>
      </header>

      {/* content */}
      <main className="flex-1 overflow-y-auto">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.18 }}
          >
            {activeTab === "pain" && <PainSection lang={lang} />}
            {activeTab === "tasks" && <TasksSection lang={lang} />}
            {activeTab === "stages" && <StagesSection lang={lang} />}
            {activeTab === "metrics" && <StatsSection lang={lang} />}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* bottom nav */}
      <nav className="sticky bottom-0 z-30 border-t border-zinc-200 bg-white">
        <div className="grid grid-cols-4">
          {TABS.map(({ id, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`flex flex-col items-center gap-1 py-3 text-[10px] font-medium transition-colors ${
                activeTab === id
                  ? "text-zinc-900"
                  : "text-zinc-400 hover:text-zinc-600"
              }`}
            >
              <Icon size={20} strokeWidth={activeTab === id ? 2.5 : 1.5} />
              {tabLabel[id]}
            </button>
          ))}
        </div>
      </nav>
    </div>
  );
}
