import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { History, Wrench, Clock, ChevronRight, Globe, Monitor,
         Camera, Cloud, Zap, BarChart2, Newspaper, Bell } from 'lucide-react'

const TABS = [
  { id: 'history', label: 'HISTORY',  icon: History },
  { id: 'tools',   label: 'TOOLS',    icon: Wrench },
  { id: 'news',    label: 'NEWS',     icon: Newspaper },
  { id: 'stats',   label: 'STATS',    icon: BarChart2 },
  { id: 'schedule',label: 'SCHED',    icon: Clock },
]

const TOOLS = [
  { group: 'BROWSER',  icon: Globe,    items: ['open_website','search_youtube','click_first_video','search_google','send_email'] },
  { group: 'SYSTEM',   icon: Monitor,  items: ['open_app','close_app','run_command','take_screenshot'] },
  { group: 'CAMERA',   icon: Camera,   items: ['open_camera','click_photo','close_camera'] },
  { group: 'API',      icon: Cloud,    items: ['get_weather','get_news'] },
]

const NEWS_CATS = [
  { id: 'technology',    label: 'Technology',    color: '#00d4ff' },
  { id: 'health',        label: 'Health',        color: '#00ff88' },
  { id: 'finance',       label: 'Finance',       color: '#ffaa00' },
  { id: 'law',           label: 'Law & Legal',   color: '#ff6688' },
  { id: 'education',     label: 'Education',     color: '#aa88ff' },
  { id: 'science',       label: 'Science',       color: '#00ffcc' },
  { id: 'sports',        label: 'Sports',        color: '#ff8844' },
  { id: 'politics',      label: 'Politics',      color: '#ff4466' },
  { id: 'business',      label: 'Business',      color: '#44ddff' },
  { id: 'entertainment', label: 'Entertainment', color: '#ff44aa' },
  { id: 'world',         label: 'World',         color: '#88aaff' },
  { id: 'india',         label: 'India',         color: '#ff9933' },
]

export default function Sidebar({ history, context, onCommand, stats }) {
  const [tab, setTab] = useState('history')
  const [scheduleCmd, setScheduleCmd] = useState('')
  const [scheduleCron, setScheduleCron] = useState('09:00')
  const [schedules, setSchedules] = useState([])
  const [notifSettings, setNotifSettings] = useState({
    enabled: true, popup: true, interval_minutes: 30,
    categories: ['technology','health','finance','world','india'],
  })

  useEffect(() => {
    fetch('/notifications/settings').then(r => r.json()).then(setNotifSettings).catch(() => {})
  }, [])

  const updateNotif = (patch) => {
    const next = { ...notifSettings, ...patch }
    setNotifSettings(next)
    fetch('/notifications/settings', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(next) })
  }

  const toggleCategory = (id) => {
    const cats = notifSettings.categories.includes(id)
      ? notifSettings.categories.filter(c => c !== id)
      : [...notifSettings.categories, id]
    updateNotif({ categories: cats })
  }

  const addSchedule = () => {
    if (!scheduleCmd.trim()) return
    fetch('/schedule', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: scheduleCmd, cron: scheduleCron })
    }).then(() => {
      setSchedules(p => [...p, { command: scheduleCmd, cron: scheduleCron }])
      setScheduleCmd('')
    })
  }

  return (
    <div className="w-64 flex flex-col glass border-r border-jarvis-border h-full">
      {/* Logo area */}
      <div className="px-4 py-3 border-b border-jarvis-border">
        <div className="flex items-center gap-2">
          <div className="relative w-6 h-6 flex items-center justify-center">
            <motion.div
              className="absolute inset-0 rounded-full border border-jarvis-cyan/20"
              animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 6, ease: 'linear' }}
            />
            <Zap size={10} className="neon-cyan" />
          </div>
          <span className="text-xs font-mono neon-cyan tracking-widest">COMMAND DASHBOARD</span>
        </div>

        {/* Context display */}
        {(context?.current_app || context?.current_url) && (
          <div className="mt-2 px-2 py-1.5 rounded glass-bright text-xs font-mono space-y-0.5">
            {context.current_app && (
              <div className="flex items-center gap-1.5">
                <Monitor size={9} className="text-jarvis-cyan/50" />
                <span className="text-jarvis-cyan/70">{context.current_app}</span>
              </div>
            )}
            {context.current_url && (
              <div className="flex items-center gap-1.5">
                <Globe size={9} className="text-jarvis-cyan/50" />
                <span className="text-jarvis-muted/60 truncate">{context.current_url}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex border-b border-jarvis-border">
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className="flex-1 flex flex-col items-center gap-0.5 py-2 text-xs font-mono transition-all"
            style={{
              color:       tab === t.id ? '#00d4ff' : '#3a5a7a',
              borderBottom: tab === t.id ? '1px solid #00d4ff' : '1px solid transparent',
              background:  tab === t.id ? 'rgba(0,212,255,0.04)' : 'transparent',
            }}
          >
            <t.icon size={11} />
            <span className="text-xs">{t.label}</span>
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-y-auto">
        <AnimatePresence mode="wait">
          {tab === 'history' && (
            <motion.div key="history" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="p-2 space-y-1">
              {history.length === 0 ? (
                <p className="text-xs font-mono text-jarvis-muted/40 text-center py-8">No commands yet</p>
              ) : history.map((h, i) => (
                <button
                  key={i}
                  onClick={() => onCommand(h.text)}
                  className="w-full text-left px-2.5 py-2 rounded border border-jarvis-border hover:border-jarvis-cyan/20 hover:bg-jarvis-cyan/5 transition group"
                >
                  <div className="flex items-start gap-1.5">
                    <ChevronRight size={9} className="text-jarvis-cyan/30 mt-0.5 flex-shrink-0 group-hover:text-jarvis-cyan/60" />
                    <div className="min-w-0">
                      <p className="text-xs font-mono text-jarvis-text truncate">{h.text}</p>
                      <p className="text-xs font-mono text-jarvis-muted/40 mt-0.5">{h.ts}</p>
                    </div>
                  </div>
                </button>
              ))}
            </motion.div>
          )}

          {tab === 'tools' && (
            <motion.div key="tools" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="p-2 space-y-3">
              {TOOLS.map(group => (
                <div key={group.group}>
                  <div className="flex items-center gap-1.5 px-1 mb-1.5">
                    <group.icon size={9} className="text-jarvis-cyan/40" />
                    <span className="text-xs font-mono text-jarvis-muted/50 tracking-widest">{group.group}</span>
                  </div>
                  <div className="space-y-0.5">
                    {group.items.map(item => (
                      <div key={item} className="flex items-center gap-2 px-2.5 py-1.5 rounded border border-jarvis-border/50">
                        <span className="w-1.5 h-1.5 rounded-full bg-jarvis-cyan/30 flex-shrink-0" />
                        <span className="text-xs font-mono text-jarvis-muted/60">{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </motion.div>
          )}

          {tab === 'news' && (
            <motion.div key="news" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="p-3 space-y-4">
              {/* Master toggle */}
              <div className="flex items-center justify-between px-2.5 py-2 rounded border border-jarvis-border">
                <div className="flex items-center gap-2">
                  <Bell size={10} className="text-jarvis-cyan/50" />
                  <span className="text-xs font-mono text-jarvis-muted/60">Notifications</span>
                </div>
                <button
                  onClick={() => updateNotif({ enabled: !notifSettings.enabled })}
                  className="w-8 h-4 rounded-full transition-all relative"
                  style={{ background: notifSettings.enabled ? 'rgba(0,212,255,0.3)' : 'rgba(10,32,64,1)', border: '1px solid rgba(0,212,255,0.2)' }}
                >
                  <motion.div
                    className="absolute top-0.5 w-3 h-3 rounded-full"
                    animate={{ left: notifSettings.enabled ? '17px' : '1px', background: notifSettings.enabled ? '#00d4ff' : '#3a5a7a' }}
                    transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                  />
                </button>
              </div>

              {/* Popup toggle */}
              <div className="flex items-center justify-between px-2.5 py-2 rounded border border-jarvis-border">
                <span className="text-xs font-mono text-jarvis-muted/60">Popup alerts</span>
                <button
                  onClick={() => updateNotif({ popup: !notifSettings.popup })}
                  className="w-8 h-4 rounded-full transition-all relative"
                  style={{ background: notifSettings.popup ? 'rgba(0,255,136,0.3)' : 'rgba(10,32,64,1)', border: '1px solid rgba(0,255,136,0.2)' }}
                >
                  <motion.div
                    className="absolute top-0.5 w-3 h-3 rounded-full"
                    animate={{ left: notifSettings.popup ? '17px' : '1px', background: notifSettings.popup ? '#00ff88' : '#3a5a7a' }}
                    transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                  />
                </button>
              </div>

              {/* Interval */}
              <div className="space-y-1.5">
                <span className="text-xs font-mono text-jarvis-muted/40 tracking-widest">UPDATE INTERVAL</span>
                <div className="flex gap-1.5">
                  {[15, 30, 60].map(m => (
                    <button key={m}
                      onClick={() => updateNotif({ interval_minutes: m })}
                      className="flex-1 py-1 rounded text-xs font-mono transition-all"
                      style={{
                        background: notifSettings.interval_minutes === m ? 'rgba(0,212,255,0.1)' : 'transparent',
                        border: `1px solid ${notifSettings.interval_minutes === m ? 'rgba(0,212,255,0.4)' : 'rgba(10,32,64,1)'}`,
                        color: notifSettings.interval_minutes === m ? '#00d4ff' : '#3a5a7a',
                      }}
                    >{m}m</button>
                  ))}
                </div>
              </div>

              {/* Category toggles */}
              <div className="space-y-1.5">
                <span className="text-xs font-mono text-jarvis-muted/40 tracking-widest">CATEGORIES</span>
                <div className="space-y-1">
                  {NEWS_CATS.map(cat => {
                    const active = notifSettings.categories.includes(cat.id)
                    return (
                      <button key={cat.id}
                        onClick={() => toggleCategory(cat.id)}
                        className="w-full flex items-center justify-between px-2.5 py-1.5 rounded border transition-all"
                        style={{
                          borderColor: active ? `${cat.color}30` : 'rgba(10,32,64,1)',
                          background: active ? `${cat.color}08` : 'transparent',
                        }}
                      >
                        <div className="flex items-center gap-2">
                          <motion.div
                            className="w-1.5 h-1.5 rounded-full"
                            animate={{ opacity: active ? 1 : 0.2 }}
                            style={{ background: cat.color, boxShadow: active ? `0 0 4px ${cat.color}` : 'none' }}
                          />
                          <span className="text-xs font-mono" style={{ color: active ? cat.color : '#3a5a7a' }}>
                            {cat.label}
                          </span>
                        </div>
                        <span className="text-xs font-mono" style={{ color: active ? cat.color : '#1a3a5a' }}>
                          {active ? 'ON' : 'OFF'}
                        </span>
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Manual push */}
              <button
                onClick={() => fetch('/notifications/push', { method: 'POST' })}
                className="w-full py-2 rounded border border-jarvis-cyan/20 text-xs font-mono text-jarvis-cyan/60 hover:bg-jarvis-cyan/5 hover:border-jarvis-cyan/40 transition"
              >
                📰 Push News Now
              </button>
            </motion.div>
          )}

          {tab === 'stats' && (
            <motion.div key="stats" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="p-3 space-y-4">
              {!stats ? (
                <p className="text-xs font-mono text-jarvis-muted/40 text-center py-8">Loading stats...</p>
              ) : (
                <>
                  {/* CPU */}
                  <div>
                    <div className="flex justify-between text-xs font-mono mb-1">
                      <span className="text-jarvis-muted/50">CPU</span>
                      <span style={{ color: stats.cpu > 80 ? '#ff3366' : stats.cpu > 50 ? '#ffaa00' : '#00ff88' }}>{stats.cpu}%</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-jarvis-border overflow-hidden">
                      <motion.div className="h-full rounded-full" animate={{ width: `${stats.cpu}%` }}
                        style={{ background: stats.cpu > 80 ? '#ff3366' : stats.cpu > 50 ? '#ffaa00' : '#00ff88' }} />
                    </div>
                  </div>
                  {/* RAM */}
                  <div>
                    <div className="flex justify-between text-xs font-mono mb-1">
                      <span className="text-jarvis-muted/50">RAM</span>
                      <span className="text-jarvis-cyan/70">{stats.ram_used_mb}MB / {stats.ram_total_mb}MB</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-jarvis-border overflow-hidden">
                      <motion.div className="h-full rounded-full bg-jarvis-cyan" animate={{ width: `${stats.ram}%` }} />
                    </div>
                  </div>
                  {/* Battery */}
                  {stats.battery !== null && (
                    <div>
                      <div className="flex justify-between text-xs font-mono mb-1">
                        <span className="text-jarvis-muted/50">BATTERY {stats.charging ? '⚡' : ''}</span>
                        <span style={{ color: stats.battery < 20 ? '#ff3366' : '#00ff88' }}>{stats.battery}%</span>
                      </div>
                      <div className="w-full h-1.5 rounded-full bg-jarvis-border overflow-hidden">
                        <motion.div className="h-full rounded-full" animate={{ width: `${stats.battery}%` }}
                          style={{ background: stats.battery < 20 ? '#ff3366' : '#00ff88' }} />
                      </div>
                    </div>
                  )}
                  {/* Network */}
                  <div className="px-2.5 py-2 rounded border border-jarvis-border/50 space-y-1">
                    <p className="text-xs font-mono text-jarvis-muted/40 tracking-widest">NETWORK</p>
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-jarvis-muted/50">↑ Sent</span>
                      <span className="text-jarvis-cyan/60">{stats.net_sent_mb} MB</span>
                    </div>
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-jarvis-muted/50">↓ Recv</span>
                      <span className="text-jarvis-cyan/60">{stats.net_recv_mb} MB</span>
                    </div>
                  </div>
                  {/* Quick commands */}
                  <div className="space-y-1">
                    <p className="text-xs font-mono text-jarvis-muted/40 tracking-widest">QUICK ACTIONS</p>
                    {['get system info','get battery','get wifi info','get cpu usage','get ram usage'].map(cmd => (
                      <button key={cmd} onClick={() => onCommand(cmd)}
                        className="w-full text-left px-2.5 py-1.5 rounded border border-jarvis-border/50 hover:border-jarvis-cyan/20 hover:bg-jarvis-cyan/5 text-xs font-mono text-jarvis-muted/60 hover:text-jarvis-cyan/70 transition">
                        {cmd}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </motion.div>
          )}

          {tab === 'schedule' && (
            <motion.div key="schedule" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="p-3 space-y-3">
              <div className="space-y-2">
                <label className="text-xs font-mono text-jarvis-muted/50 tracking-widest">COMMAND</label>
                <input
                  value={scheduleCmd}
                  onChange={e => setScheduleCmd(e.target.value)}
                  placeholder="e.g. Get latest tech news"
                  className="w-full bg-transparent border border-jarvis-border rounded px-2.5 py-1.5 text-xs font-mono text-jarvis-text placeholder-jarvis-muted/30 outline-none focus:border-jarvis-cyan/30"
                />
                <label className="text-xs font-mono text-jarvis-muted/50 tracking-widest">TIME (HH:MM)</label>
                <input
                  type="time"
                  value={scheduleCron}
                  onChange={e => setScheduleCron(e.target.value)}
                  className="w-full bg-transparent border border-jarvis-border rounded px-2.5 py-1.5 text-xs font-mono text-jarvis-text outline-none focus:border-jarvis-cyan/30"
                />
                <button
                  onClick={addSchedule}
                  className="w-full py-1.5 rounded border border-jarvis-cyan/20 text-xs font-mono text-jarvis-cyan/70 hover:bg-jarvis-cyan/5 hover:border-jarvis-cyan/40 transition"
                >
                  + SCHEDULE
                </button>
              </div>
              {schedules.length > 0 && (
                <div className="space-y-1">
                  <span className="text-xs font-mono text-jarvis-muted/40 tracking-widest">SCHEDULED</span>
                  {schedules.map((s, i) => (
                    <div key={i} className="px-2.5 py-1.5 rounded border border-jarvis-border text-xs font-mono">
                      <span className="text-jarvis-cyan/60">{s.cron}</span>
                      <span className="text-jarvis-muted/50 ml-2">{s.command}</span>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
