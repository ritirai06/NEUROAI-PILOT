import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { History, Wrench, Clock, ChevronRight, Globe, Monitor,
         Camera, Cloud, Terminal, Search, Play, Zap } from 'lucide-react'

const TABS = [
  { id: 'history', label: 'HISTORY', icon: History },
  { id: 'tools',   label: 'TOOLS',   icon: Wrench },
  { id: 'schedule',label: 'SCHEDULE',icon: Clock },
]

const TOOLS = [
  { group: 'BROWSER',  icon: Globe,    items: ['open_website','search_youtube','click_first_video','search_google','send_email'] },
  { group: 'SYSTEM',   icon: Monitor,  items: ['open_app','close_app','run_command','take_screenshot'] },
  { group: 'CAMERA',   icon: Camera,   items: ['open_camera','click_photo','close_camera'] },
  { group: 'API',      icon: Cloud,    items: ['get_weather','get_news'] },
]

export default function Sidebar({ history, context, onCommand }) {
  const [tab, setTab] = useState('history')
  const [scheduleCmd, setScheduleCmd] = useState('')
  const [scheduleCron, setScheduleCron] = useState('09:00')
  const [schedules, setSchedules] = useState([])

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
