import { useRef, useEffect } from 'react'
import { motion, AnimatePresence, useInView } from 'framer-motion'
import { CheckCircle, XCircle, Clock, Globe, Search, Play,
         Monitor, Camera, Cloud, Terminal, ChevronRight, Zap, Cpu } from 'lucide-react'

const ACTION_ICONS = {
  open_website:      Globe,
  search_youtube:    Search,
  click_first_video: Play,
  search_google:     Search,
  open_app:          Monitor,
  close_app:         Monitor,
  open_camera:       Camera,
  click_photo:       Camera,
  get_weather:       Cloud,
  get_news:          Cloud,
  run_command:       Terminal,
  take_screenshot:   Monitor,
  respond:           ChevronRight,
}

const ACTION_LABELS = {
  open_website:      'Open Website',
  search_youtube:    'Search YouTube',
  click_first_video: 'Play Video',
  search_google:     'Search Google',
  open_app:          'Open App',
  close_app:         'Close App',
  open_camera:       'Open Camera',
  click_photo:       'Take Photo',
  get_weather:       'Get Weather',
  get_news:          'Get News',
  run_command:       'Run Command',
  take_screenshot:   'Screenshot',
  respond:           'Response',
}

const STATUS_COLOR = {
  success: '#00ff88',
  error:   '#ff3366',
  running: '#00d4ff',
  pending: '#1a3a5a',
}

/* ── Spinning loader ── */
function SpinLoader() {
  return (
    <div className="relative w-4 h-4">
      <motion.div
        className="absolute inset-0 rounded-full border-t border-jarvis-cyan"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 0.7, ease: 'linear' }}
      />
      <motion.div
        className="absolute inset-0.5 rounded-full border-t border-jarvis-blue/60"
        animate={{ rotate: -360 }}
        transition={{ repeat: Infinity, duration: 1.1, ease: 'linear' }}
      />
    </div>
  )
}

/* ── Typing text output ── */
function TypingText({ text, color }) {
  return (
    <motion.div
      initial={{ width: 0 }} animate={{ width: '100%' }}
      transition={{ duration: Math.min(text.length * 0.02, 1.5), ease: 'linear' }}
      className="overflow-hidden whitespace-nowrap"
    >
      <span className="text-xs font-mono" style={{ color }}>{text.slice(0, 80)}</span>
    </motion.div>
  )
}

/* ── Step card ── */
function StepCard({ step, index }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true })
  const Icon   = ACTION_ICONS[step.action] || ChevronRight
  const label  = ACTION_LABELS[step.action] || step.action
  const param  = step.params ? Object.values(step.params)[0] : null
  const color  = STATUS_COLOR[step.status] || STATUS_COLOR.pending

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, x: -30, scale: 0.97 }}
      animate={inView ? { opacity: 1, x: 0, scale: 1 } : {}}
      transition={{ type: 'spring', stiffness: 260, damping: 22, delay: index * 0.06 }}
      className="relative rounded-lg hud-corner overflow-hidden"
      style={{
        border:      `1px solid rgba(10,32,64,0.9)`,
        borderLeft:  `2px solid ${color}`,
        background:  step.status === 'running'
          ? 'rgba(0,212,255,0.04)'
          : step.status === 'success'
          ? 'rgba(0,255,136,0.03)'
          : step.status === 'error'
          ? 'rgba(255,51,102,0.03)'
          : 'rgba(4,13,26,0.6)',
      }}
    >
      {/* Running shimmer sweep */}
      {step.status === 'running' && (
        <motion.div
          className="absolute inset-0 pointer-events-none"
          style={{ background: 'linear-gradient(90deg, transparent 0%, rgba(0,212,255,0.08) 50%, transparent 100%)' }}
          animate={{ x: ['-100%', '200%'] }}
          transition={{ repeat: Infinity, duration: 1.4, ease: 'linear' }}
        />
      )}

      {/* Success flash */}
      {step.status === 'success' && (
        <motion.div
          className="absolute inset-0 pointer-events-none rounded-lg"
          initial={{ opacity: 0.4 }}
          animate={{ opacity: 0 }}
          transition={{ duration: 0.8 }}
          style={{ background: 'rgba(0,255,136,0.08)' }}
        />
      )}

      <div className="flex items-center gap-3 px-4 py-3">
        {/* Index */}
        <span className="text-xs font-mono w-5 flex-shrink-0 text-center"
          style={{ color: `${color}66` }}>
          {String(index + 1).padStart(2, '0')}
        </span>

        {/* Icon box */}
        <motion.div
          className="w-7 h-7 rounded flex items-center justify-center flex-shrink-0"
          style={{ background: `${color}11`, border: `1px solid ${color}22` }}
          animate={step.status === 'running' ? { boxShadow: [`0 0 0px ${color}00`, `0 0 10px ${color}44`, `0 0 0px ${color}00`] } : {}}
          transition={{ repeat: Infinity, duration: 1.2 }}
        >
          <Icon size={13} style={{ color }} />
        </motion.div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-jarvis-text">{label}</span>
            <span className="text-xs font-mono text-jarvis-muted/35">{step.action}</span>
          </div>
          {param && (
            <div className="text-xs font-mono text-jarvis-muted/55 truncate mt-0.5">
              "{String(param).slice(0, 55)}"
            </div>
          )}
          {step.output && step.status !== 'running' && (
            <TypingText
              text={step.output}
              color={step.status === 'error' ? '#ff3366' : '#00ff8877'}
            />
          )}
        </div>

        {/* Status icon */}
        <div className="flex-shrink-0 w-5 flex items-center justify-center">
          {step.status === 'success' && (
            <motion.div initial={{ scale: 0, rotate: -90 }} animate={{ scale: 1, rotate: 0 }} transition={{ type: 'spring', stiffness: 400, damping: 15 }}>
              <CheckCircle size={14} style={{ color: '#00ff88', filter: 'drop-shadow(0 0 5px #00ff88)' }} />
            </motion.div>
          )}
          {step.status === 'error' && (
            <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', stiffness: 400 }}>
              <XCircle size={14} style={{ color: '#ff3366', filter: 'drop-shadow(0 0 5px #ff3366)' }} />
            </motion.div>
          )}
          {step.status === 'running' && <SpinLoader />}
          {step.status === 'pending' && (
            <motion.div animate={{ opacity: [0.3, 0.7, 0.3] }} transition={{ repeat: Infinity, duration: 1.5 }}>
              <Clock size={13} style={{ color: '#1a3a5a' }} />
            </motion.div>
          )}
        </div>
      </div>

      {/* Bottom progress line for running */}
      {step.status === 'running' && (
        <motion.div
          className="absolute bottom-0 left-0 h-px"
          animate={{ x: ['-100%', '200%'] }}
          transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
          style={{ width: '60%', background: `linear-gradient(90deg, transparent, ${color}, transparent)` }}
        />
      )}
    </motion.div>
  )
}

/* ── Idle hologram ── */
function IdleHologram() {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-8 py-8 select-none">
      {/* Main arc reactor */}
      <div className="relative w-32 h-32 flex items-center justify-center">
        {/* Outer rings */}
        {[0, 1, 2, 3].map(i => (
          <motion.div
            key={i}
            className="absolute rounded-full border"
            style={{
              inset:       `${i * 10}px`,
              borderColor: `rgba(0,212,255,${0.08 + i * 0.06})`,
            }}
            animate={{ rotate: i % 2 === 0 ? 360 : -360 }}
            transition={{ repeat: Infinity, duration: 6 + i * 3, ease: 'linear' }}
          />
        ))}

        {/* Orbiting dot */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 3, ease: 'linear' }}
          style={{
            transformOrigin: '4px 50px',
            background: '#00d4ff',
            boxShadow: '0 0 8px #00d4ff',
            width: 6, height: 6,
            borderRadius: '50%',
            position: 'absolute',
            top: '50%', left: '50%',
          }}
        />

        {/* Core */}
        <motion.div
          className="relative z-10 w-12 h-12 rounded-full flex items-center justify-center"
          style={{ background: 'radial-gradient(circle, rgba(0,212,255,0.15), rgba(0,100,200,0.05))' }}
          animate={{ boxShadow: ['0 0 10px rgba(0,212,255,0.2)', '0 0 30px rgba(0,212,255,0.5)', '0 0 10px rgba(0,212,255,0.2)'] }}
          transition={{ repeat: Infinity, duration: 2.5 }}
        >
          <motion.div
            animate={{ scale: [1, 1.15, 1], opacity: [0.7, 1, 0.7] }}
            transition={{ repeat: Infinity, duration: 2 }}
          >
            <Zap size={22} className="neon-cyan" />
          </motion.div>
        </motion.div>
      </div>

      {/* Text */}
      <div className="text-center space-y-2">
        <motion.p
          className="text-base font-mono tracking-[0.3em] holo-text"
          animate={{ opacity: [0.7, 1, 0.7] }}
          transition={{ repeat: Infinity, duration: 3 }}
        >
          JARVIS READY
        </motion.p>
        <motion.p
          className="text-xs font-mono text-jarvis-muted/50 tracking-widest cursor-blink"
          animate={{ opacity: [0.4, 0.8, 0.4] }}
          transition={{ repeat: Infinity, duration: 2, delay: 0.5 }}
        >
          AWAITING COMMAND
        </motion.p>
      </div>

      {/* System stats row */}
      <div className="flex items-center gap-6 text-xs font-mono text-jarvis-muted/40">
        {[['CPU', '12%'], ['MEM', '2.3GB'], ['NET', 'OK']].map(([k, v]) => (
          <div key={k} className="flex items-center gap-1.5">
            <motion.span
              className="w-1 h-1 rounded-full bg-jarvis-cyan/40"
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ repeat: Infinity, duration: 1.5, delay: Math.random() }}
            />
            <span>{k}</span>
            <span style={{ color: '#00d4ff66' }}>{v}</span>
          </div>
        ))}
      </div>

      {/* Quick command hints */}
      <div className="grid grid-cols-2 gap-2 max-w-sm w-full">
        {['Open Chrome and play Arijit Singh', 'Weather in London', 'Open camera and take photo', 'Search Python tutorials'].map((c, i) => (
          <motion.div
            key={c}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + i * 0.1 }}
            className="text-xs font-mono text-jarvis-muted/40 px-3 py-2 rounded border border-jarvis-border/50 text-center hud-corner hover:border-jarvis-cyan/20 hover:text-jarvis-muted/70 transition-all cursor-default"
          >
            {c}
          </motion.div>
        ))}
      </div>
    </div>
  )
}

export default function StepTracker({ steps, summary, result, loading }) {
  const done   = steps.filter(s => s.status === 'success').length
  const failed = steps.filter(s => s.status === 'error').length
  const total  = steps.length

  if (!total && !loading && !result) return <IdleHologram />

  if (loading && !total && !result) return (
    <div className="flex flex-col items-center justify-center h-full gap-6">
      <div className="relative w-20 h-20 flex items-center justify-center">
        {[0, 1, 2].map(i => (
          <motion.div
            key={i}
            className="absolute rounded-full border border-jarvis-cyan"
            style={{ inset: `${i * 8}px`, opacity: 0.2 + i * 0.2 }}
            animate={{ rotate: i % 2 === 0 ? 360 : -360 }}
            transition={{ repeat: Infinity, duration: 2 + i, ease: 'linear' }}
          />
        ))}
        <motion.div
          animate={{ scale: [1, 1.2, 1], opacity: [0.6, 1, 0.6] }}
          transition={{ repeat: Infinity, duration: 1 }}
        >
          <Cpu size={20} className="neon-cyan" />
        </motion.div>
      </div>
      <motion.p
        className="text-sm font-mono tracking-widest"
        style={{ color: '#00d4ff' }}
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ repeat: Infinity, duration: 1.2 }}
      >
        PLANNING...
      </motion.p>
    </div>
  )

  return (
    <div className="space-y-3 max-w-2xl mx-auto w-full pb-4">

      {/* Plan header */}
      <AnimatePresence>
        {summary && (
          <motion.div
            initial={{ opacity: 0, y: -15, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ type: 'spring', stiffness: 260, damping: 22 }}
            className="flex items-center justify-between px-4 py-2.5 rounded-lg glass-bright hud-corner relative overflow-hidden"
          >
            {/* Shimmer */}
            <motion.div
              className="absolute inset-0 pointer-events-none"
              style={{ background: 'linear-gradient(90deg, transparent, rgba(0,212,255,0.05), transparent)' }}
              animate={{ x: ['-100%', '200%'] }}
              transition={{ repeat: Infinity, duration: 3, ease: 'linear', repeatDelay: 2 }}
            />
            <div className="flex items-center gap-2">
              <motion.div animate={{ rotate: [0, 90, 0] }} transition={{ repeat: Infinity, duration: 4 }}>
                <ChevronRight size={12} className="text-jarvis-cyan/50" />
              </motion.div>
              <span className="text-xs font-mono text-jarvis-muted tracking-widest">EXECUTING PLAN</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm font-mono text-jarvis-text">{summary}</span>
              {total > 0 && (
                <div className="flex items-center gap-1.5 text-xs font-mono">
                  <motion.span
                    style={{ color: '#00ff88' }}
                    animate={{ opacity: done === total ? 1 : [0.6, 1, 0.6] }}
                    transition={{ repeat: done === total ? 0 : Infinity, duration: 1 }}
                  >
                    {done}/{total}
                  </motion.span>
                  {failed > 0 && <span style={{ color: '#ff3366' }}>{failed}✗</span>}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Progress bar */}
      {total > 0 && (
        <div className="relative h-1 bg-jarvis-border rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{ background: failed > 0 ? 'linear-gradient(90deg,#ff3366,#ff6688)' : 'linear-gradient(90deg,#0066ff,#00d4ff)' }}
            initial={{ width: 0 }}
            animate={{ width: `${(done / total) * 100}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
          {/* Glow on progress bar */}
          <motion.div
            className="absolute top-0 h-full w-8 rounded-full"
            style={{ background: 'linear-gradient(90deg, transparent, rgba(0,212,255,0.6), transparent)', right: `${100 - (done / total) * 100}%` }}
            animate={{ opacity: [0, 1, 0] }}
            transition={{ repeat: Infinity, duration: 1 }}
          />
        </div>
      )}

      {/* Steps */}
      <div className="space-y-2">
        <AnimatePresence>
          {steps.map((step, i) => (
            <StepCard key={`${step.action}-${i}`} step={step} index={i} />
          ))}
        </AnimatePresence>
      </div>

      {/* Result */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 15, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.97 }}
            transition={{ type: 'spring', stiffness: 260, damping: 22 }}
            className="px-4 py-3 rounded-lg hud-corner relative overflow-hidden"
            style={{ background: 'rgba(0,255,136,0.04)', border: '1px solid rgba(0,255,136,0.15)' }}
          >
            {/* Success shimmer */}
            <motion.div
              className="absolute inset-0 pointer-events-none"
              style={{ background: 'linear-gradient(90deg, transparent, rgba(0,255,136,0.06), transparent)' }}
              animate={{ x: ['-100%', '200%'] }}
              transition={{ repeat: Infinity, duration: 3, ease: 'linear', repeatDelay: 1 }}
            />
            <div className="flex items-center gap-2 mb-2">
              <motion.div
                initial={{ scale: 0, rotate: -180 }} animate={{ scale: 1, rotate: 0 }}
                transition={{ type: 'spring', stiffness: 400, damping: 15 }}
              >
                <CheckCircle size={12} style={{ color: '#00ff88', filter: 'drop-shadow(0 0 4px #00ff88)' }} />
              </motion.div>
              <span className="text-xs font-mono text-jarvis-muted tracking-widest">RESULT</span>
            </div>
            <motion.p
              className="text-sm font-mono text-jarvis-text whitespace-pre-wrap"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
            >
              {result}
            </motion.p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
