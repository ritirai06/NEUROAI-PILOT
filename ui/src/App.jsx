import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { motion, AnimatePresence, useMotionValue, useSpring } from 'framer-motion'
import { Brain, Cpu, Activity, Zap, Wifi, WifiOff, Newspaper, Bell, BellOff } from 'lucide-react'
import CommandInput, { speakText } from './components/CommandInput'
import StepTracker   from './components/StepTracker'
import LogsPanel     from './components/LogsPanel'
import Sidebar       from './components/Sidebar'
import NewsPanel     from './components/NewsPanel'
import NotificationToast from './components/NotificationToast'

const WS_URL = 'ws://localhost:8000/ws'
const ts = () => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })

/* ── Floating particles ── */
function Particles() {
  const particles = useMemo(() => Array.from({ length: 18 }, (_, i) => ({
    id: i,
    left:     `${Math.random() * 100}%`,
    size:     Math.random() * 3 + 1,
    duration: Math.random() * 12 + 8,
    delay:    Math.random() * 10,
    color:    i % 3 === 0 ? '#00d4ff' : i % 3 === 1 ? '#0066ff' : '#00ff88',
  })), [])

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
      {particles.map(p => (
        <div
          key={p.id}
          className="particle"
          style={{
            left:            p.left,
            width:           p.size,
            height:          p.size,
            background:      p.color,
            boxShadow:       `0 0 ${p.size * 3}px ${p.color}`,
            animationDuration: `${p.duration}s`,
            animationDelay:  `${p.delay}s`,
            bottom:          0,
          }}
        />
      ))}
    </div>
  )
}

/* ── Cursor follower ── */
function CursorGlow() {
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const sx = useSpring(x, { stiffness: 80, damping: 20 })
  const sy = useSpring(y, { stiffness: 80, damping: 20 })

  useEffect(() => {
    const move = (e) => { x.set(e.clientX); y.set(e.clientY) }
    window.addEventListener('mousemove', move)
    return () => window.removeEventListener('mousemove', move)
  }, [x, y])

  return (
    <motion.div
      className="fixed pointer-events-none z-50"
      style={{
        left: sx, top: sy,
        width: 300, height: 300,
        x: '-50%', y: '-50%',
        background: 'radial-gradient(circle, rgba(0,212,255,0.04) 0%, transparent 70%)',
        borderRadius: '50%',
      }}
    />
  )
}

/* ── Arc reactor header logo ── */
function ArcReactor({ loading }) {
  return (
    <div className="relative w-10 h-10 flex items-center justify-center flex-shrink-0">
      {/* Outer ring */}
      <motion.div
        className="absolute inset-0 rounded-full border border-jarvis-cyan/25"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 10, ease: 'linear' }}
      />
      {/* Middle ring */}
      <motion.div
        className="absolute inset-1.5 rounded-full border border-jarvis-blue/35"
        animate={{ rotate: -360 }}
        transition={{ repeat: Infinity, duration: 6, ease: 'linear' }}
      />
      {/* Inner ring */}
      <motion.div
        className="absolute inset-3 rounded-full border border-jarvis-cyan/40"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 3, ease: 'linear' }}
      />
      {/* Core glow */}
      <motion.div
        className="absolute inset-3 rounded-full"
        animate={{ opacity: loading ? [0.4, 1, 0.4] : [0.2, 0.5, 0.2] }}
        transition={{ repeat: Infinity, duration: loading ? 0.8 : 2 }}
        style={{ background: 'radial-gradient(circle, rgba(0,212,255,0.6), transparent)' }}
      />
      <Brain size={13} className="neon-cyan relative z-10" />
    </div>
  )
}

export default function App() {
  const [wsStatus,    setWsStatus]    = useState('connecting')
  const [temporal,    setTemporal]    = useState(false)
  const [loading,     setLoading]     = useState(false)
  const [showLogs,    setShowLogs]    = useState(true)
  const [showSidebar, setShowSidebar] = useState(true)
  const [showNews,    setShowNews]    = useState(false)
  const [logs,        setLogs]        = useState([])
  const [steps,       setSteps]       = useState([])
  const [summary,     setSummary]     = useState('')
  const [result,      setResult]      = useState(null)
  const [history,     setHistory]     = useState([])
  const [context,     setContext]     = useState({})
  const [time,        setTime]        = useState(new Date())
  const [cmdCount,    setCmdCount]    = useState(0)
  const [stats,       setStats]       = useState(null)
  const [notifications, setNotifications] = useState([])
  const [notifEnabled,  setNotifEnabled]  = useState(() => localStorage.getItem('neuro-notif') !== 'off')
  const wsRef = useRef(null)

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  useEffect(() => {
    const poll = () => fetch('/status').then(r => r.json()).then(d => setTemporal(d.temporal)).catch(() => {})
    poll()
    const t = setInterval(poll, 10000)
    return () => clearInterval(t)
  }, [])

  useEffect(() => {
    const pollStats = () => fetch('/stats').then(r => r.json()).then(setStats).catch(() => {})
    pollStats()
    const t = setInterval(pollStats, 3000)
    return () => clearInterval(t)
  }, [])

  const addLog = useCallback((log) => {
    setLogs(p => [...p.slice(-499), { ...log, ts: ts() }])
  }, [])

  const connectWS = useCallback(() => {
    setWsStatus('connecting')
    const ws = new WebSocket(WS_URL)
    ws.onopen  = () => { setWsStatus('connected'); addLog({ type: 'info', message: 'Connected to NeuroAI backend' }) }
    ws.onclose = () => { setWsStatus('disconnected'); addLog({ type: 'warn', message: 'Disconnected — retrying...' }); setTimeout(connectWS, 3000) }
    ws.onerror = () => setWsStatus('disconnected')
    ws.onmessage = (e) => {
      const d = JSON.parse(e.data)
      if (d.type === 'status') {
        addLog({ type: 'info', message: d.message })
      } else if (d.type === 'plan') {
        setSummary(d.data.summary || '')
        setResult(null)
        setSteps(d.data.steps.map((s, i) => ({ ...s, index: i, status: 'pending', output: '' })))
        addLog({ type: 'plan', message: `Plan: ${d.data.summary}`, steps: d.data.steps })
      } else if (d.type === 'step') {
        const { index, status, output, action } = d.data
        setSteps(p => p.map((s, i) => i === index ? { ...s, status, output: output || '' } : s))
        addLog({ type: status === 'error' ? 'error' : status === 'running' ? 'running' : 'success', message: `${action}: ${output || status}` })
        fetch('/context').then(r => r.json()).then(setContext).catch(() => {})
      } else if (d.type === 'done') {
        setLoading(false)
        setResult(d.message)
        setCmdCount(c => c + 1)
        addLog({ type: 'done', message: 'Task completed' })
        setHistory(p => [{ text: d._input || '', result: d.message, ts: ts() }, ...p.slice(0, 49)])
        fetch('/context').then(r => r.json()).then(setContext).catch(() => {})
        if (localStorage.getItem('neuro-tts') !== 'off' && d.message) speakText(d.message)
      } else if (d.type === 'news_notification') {
        if (notifEnabled) {
          const notif = { id: Date.now() + Math.random(), ...d }
          setNotifications(p => [notif, ...p.slice(0, 7)])
          addLog({ type: 'info', message: `📰 News: ${d.articles?.[0]?.title?.slice(0, 60)}` })
        }
      }
    }
    wsRef.current = ws
  }, [addLog])

  useEffect(() => { connectWS() }, [connectWS])

  const runCommand = useCallback((text) => {
    const msg = text.trim()
    if (!msg || loading) return
    setLoading(true)
    setSteps([])
    setResult(null)
    setSummary('')
    addLog({ type: 'user', message: `→ ${msg}` })
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ message: msg }))
    } else {
      fetch('/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: msg }) })
        .then(r => r.json())
        .then(d => {
          setResult(d.response)
          if (d.plan?.steps) { setSteps(d.plan.steps.map((s, i) => ({ ...s, index: i, status: 'success', output: '' }))); setSummary(d.plan.summary || '') }
        })
        .catch(() => setResult('Backend offline. Run python main.py first.'))
        .finally(() => setLoading(false))
    }
  }, [loading, addLog])

  const wsColor = wsStatus === 'connected' ? '#00ff88' : wsStatus === 'connecting' ? '#ffaa00' : '#ff3366'

  return (
    <div className="flex h-screen overflow-hidden bg-jarvis-bg relative">
      {/* Layered backgrounds */}
      <div className="absolute inset-0 grid-bg opacity-50 pointer-events-none z-0" />
      <div className="absolute inset-0 hex-bg opacity-30 pointer-events-none z-0" />
      <div className="absolute inset-0 scanlines pointer-events-none z-0" />
      <div className="absolute inset-0 scan-beam pointer-events-none z-0" />
      <Particles />
      <CursorGlow />

      {/* News Panel overlay */}
      <AnimatePresence>
        {showNews && (
          <div className="fixed inset-0 z-40 flex items-center justify-center" style={{ background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(4px)' }}
            onClick={e => { if (e.target === e.currentTarget) setShowNews(false) }}
          >
            <NewsPanel onClose={() => setShowNews(false)} />
          </div>
        )}
      </AnimatePresence>

      {/* Notification toasts */}
      <NotificationToast
        notifications={notifications}
        onDismiss={id => setNotifications(p => p.filter(n => n.id !== id))}
        onDismissAll={() => setNotifications([])}
      />

      {/* Sidebar */}
      <AnimatePresence>
        {showSidebar && (
          <motion.div
            initial={{ x: -280, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -280, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 280, damping: 28 }}
            className="relative z-10 flex-shrink-0"
          >
            <Sidebar history={history} context={context} onCommand={runCommand} stats={stats} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main */}
      <div className="flex flex-col flex-1 min-w-0 relative z-10">

        {/* ── HUD HEADER ── */}
        <motion.header
          initial={{ y: -60, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 25, delay: 0.1 }}
          className="flex items-center justify-between px-4 py-2 border-b border-jarvis-border glass flex-shrink-0 relative overflow-hidden"
        >
          {/* Header shimmer line */}
          <motion.div
            className="absolute bottom-0 left-0 h-px"
            animate={{ x: ['-100%', '200%'] }}
            transition={{ repeat: Infinity, duration: 4, ease: 'linear', repeatDelay: 3 }}
            style={{ width: '40%', bottom: 0, background: 'linear-gradient(90deg, transparent, #00d4ff, transparent)' }}
          />

          {/* Left */}
          <div className="flex items-center gap-3">
            <motion.button
              onClick={() => setShowSidebar(v => !v)}
              whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
              className="btn-jarvis p-1.5 rounded border border-jarvis-border"
            >
              <div className="w-4 h-3 flex flex-col justify-between">
                <motion.span className="block h-px bg-jarvis-cyan" animate={{ width: showSidebar ? '100%' : '75%' }} />
                <span className="block h-px bg-jarvis-cyan w-3/4" />
                <motion.span className="block h-px bg-jarvis-cyan" animate={{ width: showSidebar ? '75%' : '100%' }} />
              </div>
            </motion.button>

            <ArcReactor loading={loading} />

            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm tracking-widest holo-text font-mono">NEUROAI</span>
                <span className="text-xs px-1.5 py-0.5 rounded font-mono border border-jarvis-cyan/20 text-jarvis-cyan/60">v3.0</span>
                <AnimatePresence>
                  {loading && (
                    <motion.span
                      initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: [1,0.4,1], scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      transition={{ opacity: { repeat: Infinity, duration: 0.8 }, scale: { duration: 0.2 } }}
                      className="text-xs px-1.5 py-0.5 rounded font-mono border border-jarvis-warn/30 text-jarvis-warn"
                    >
                      EXECUTING
                    </motion.span>
                  )}
                </AnimatePresence>
              </div>
              <div className="flex items-center gap-1.5 mt-0.5">
                <motion.span
                  className="w-1.5 h-1.5 rounded-full status-dot"
                  style={{ background: wsColor, color: wsColor }}
                />
                <span className="text-xs font-mono text-jarvis-muted">
                  {wsStatus === 'connected' ? 'ONLINE' : wsStatus === 'connecting' ? 'CONNECTING' : 'OFFLINE'}
                </span>
              </div>
            </div>
          </div>

          {/* Center: context flow */}
          <AnimatePresence>
            {(context.current_app || context.current_url) && (
              <motion.div
                initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
                className="hidden lg:flex items-center gap-2 text-xs font-mono"
              >
                {context.current_app && (
                  <motion.span
                    initial={{ scale: 0.8 }} animate={{ scale: 1 }}
                    className="px-2 py-1 rounded border border-jarvis-cyan/20 text-jarvis-cyan/70 glass-bright"
                  >
                    {context.current_app.toUpperCase()}
                  </motion.span>
                )}
                {context.current_app && context.current_url && (
                  <motion.span
                    animate={{ x: [0, 3, 0] }} transition={{ repeat: Infinity, duration: 1.5 }}
                    className="text-jarvis-muted"
                  >→</motion.span>
                )}
                {context.current_url && (
                  <span className="px-2 py-1 rounded border border-jarvis-blue/20 text-jarvis-text/60 glass-bright max-w-[200px] truncate">
                    {context.current_url}
                  </span>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Right */}
          <div className="flex items-center gap-3">
            {/* Stats */}
            <div className="hidden md:flex items-center gap-1 text-xs font-mono text-jarvis-muted/40">
              <span>{cmdCount}</span>
              <span>cmds</span>
            </div>

            {/* Temporal */}
            <motion.div
              className="hidden sm:flex items-center gap-1.5 text-xs font-mono"
              animate={{ opacity: [0.7, 1, 0.7] }} transition={{ repeat: Infinity, duration: 3 }}
            >
              <Zap size={10} style={{ color: temporal ? '#00ff88' : '#ff3366' }} />
              <span style={{ color: temporal ? '#00ff88' : '#ff3366' }}>{temporal ? 'TEMPORAL' : 'DIRECT'}</span>
            </motion.div>

            {/* Ollama */}
            <div className="hidden sm:flex items-center gap-1.5 text-xs font-mono text-jarvis-cyan/50">
              <Cpu size={10} />
              <span>OLLAMA</span>
            </div>

            {/* Clock */}
            <motion.div
              className="text-xs font-mono tabular-nums"
              style={{ color: '#00d4ff88' }}
              animate={{ opacity: [0.6, 1, 0.6] }} transition={{ repeat: Infinity, duration: 2 }}
            >
              {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </motion.div>

            {/* Logs toggle */}
            <motion.button
              onClick={() => setShowLogs(v => !v)}
              whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
              className="btn-jarvis flex items-center gap-1.5 text-xs font-mono px-2.5 py-1.5 rounded border border-jarvis-border text-jarvis-muted hover:text-jarvis-cyan transition"
            >
              <Activity size={11} />
              LOGS
            </motion.button>

            {/* News toggle */}
            <motion.button
              onClick={() => setShowNews(v => !v)}
              whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
              className="btn-jarvis flex items-center gap-1.5 text-xs font-mono px-2.5 py-1.5 rounded border transition"
              style={{
                borderColor: showNews ? 'rgba(0,212,255,0.4)' : 'rgba(10,32,64,1)',
                color: showNews ? '#00d4ff' : '#3a5a7a',
                background: showNews ? 'rgba(0,212,255,0.06)' : 'transparent',
              }}
            >
              <Newspaper size={11} />
              NEWS
            </motion.button>

            {/* Notification bell */}
            <motion.button
              onClick={() => {
                const next = !notifEnabled
                setNotifEnabled(next)
                localStorage.setItem('neuro-notif', next ? 'on' : 'off')
                fetch('/notifications/settings', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ enabled: next }) })
              }}
              whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
              className="relative btn-jarvis p-1.5 rounded border border-jarvis-border transition"
            >
              {notifEnabled
                ? <Bell size={13} style={{ color: '#00ff88' }} />
                : <BellOff size={13} style={{ color: '#3a5a7a' }} />
              }
              {notifications.length > 0 && notifEnabled && (
                <motion.span
                  initial={{ scale: 0 }} animate={{ scale: 1 }}
                  className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full text-xs flex items-center justify-center font-mono"
                  style={{ background: '#ff3366', fontSize: 8 }}
                >
                  {notifications.length}
                </motion.span>
              )}
            </motion.button>
          </div>
        </motion.header>

        {/* ── MAIN CONTENT ── */}
        <div className="flex flex-1 overflow-hidden">
          <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
            {/* Stats bar */}
            {stats && (
              <motion.div
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="flex items-center gap-4 px-4 py-1 border-b border-jarvis-border/50 text-xs font-mono text-jarvis-muted/50 flex-shrink-0 overflow-x-auto"
              >
                <span className="flex items-center gap-1.5 flex-shrink-0">
                  <span className="text-jarvis-cyan/40">CPU</span>
                  <span style={{ color: stats.cpu > 80 ? '#ff3366' : stats.cpu > 50 ? '#ffaa00' : '#00ff88' }}>{stats.cpu}%</span>
                  <div className="w-12 h-1 rounded-full bg-jarvis-border overflow-hidden">
                    <motion.div className="h-full rounded-full" animate={{ width: `${stats.cpu}%` }}
                      style={{ background: stats.cpu > 80 ? '#ff3366' : stats.cpu > 50 ? '#ffaa00' : '#00ff88' }} />
                  </div>
                </span>
                <span className="flex items-center gap-1.5 flex-shrink-0">
                  <span className="text-jarvis-cyan/40">RAM</span>
                  <span style={{ color: stats.ram > 85 ? '#ff3366' : stats.ram > 60 ? '#ffaa00' : '#00d4ff' }}>{stats.ram}%</span>
                  <div className="w-12 h-1 rounded-full bg-jarvis-border overflow-hidden">
                    <motion.div className="h-full rounded-full bg-jarvis-cyan" animate={{ width: `${stats.ram}%` }} />
                  </div>
                </span>
                {stats.battery !== null && (
                  <span className="flex items-center gap-1.5 flex-shrink-0">
                    <span className="text-jarvis-cyan/40">{stats.charging ? '⚡' : '🔋'}</span>
                    <span style={{ color: stats.battery < 20 ? '#ff3366' : '#00ff88' }}>{stats.battery}%</span>
                  </span>
                )}
                <span className="flex items-center gap-1.5 flex-shrink-0">
                  <span className="text-jarvis-cyan/40">↑</span>
                  <span>{stats.net_sent_mb}MB</span>
                  <span className="text-jarvis-cyan/40">↓</span>
                  <span>{stats.net_recv_mb}MB</span>
                </span>
              </motion.div>
            )}
            <CommandInput onRun={runCommand} loading={loading} />
            <div className="flex-1 overflow-y-auto px-4 py-3">
              <StepTracker steps={steps} summary={summary} result={result} loading={loading} />
            </div>
          </div>

          <AnimatePresence>
            {showLogs && (
              <motion.div
                initial={{ x: 300, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: 300, opacity: 0 }}
                transition={{ type: 'spring', stiffness: 280, damping: 28 }}
                className="flex-shrink-0"
              >
                <LogsPanel logs={logs} onClear={() => setLogs([])} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
