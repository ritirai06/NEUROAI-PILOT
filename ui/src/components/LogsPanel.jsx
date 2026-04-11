import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Activity, Trash2, ChevronRight } from 'lucide-react'

const LOG_STYLE = {
  info:    { color: '#4499ff', prefix: '●', glow: 'rgba(68,153,255,0.15)' },
  success: { color: '#00ff88', prefix: '✓', glow: 'rgba(0,255,136,0.12)' },
  error:   { color: '#ff3366', prefix: '✗', glow: 'rgba(255,51,102,0.12)' },
  warn:    { color: '#ffaa00', prefix: '⚠', glow: 'rgba(255,170,0,0.12)'  },
  plan:    { color: '#00d4ff', prefix: '▶', glow: 'rgba(0,212,255,0.15)'  },
  user:    { color: '#a0c8e8', prefix: '›', glow: 'transparent'           },
  running: { color: '#00d4ff', prefix: '◌', glow: 'rgba(0,212,255,0.08)'  },
  done:    { color: '#00ff88', prefix: '✓', glow: 'rgba(0,255,136,0.12)'  },
  step:    { color: '#00ff88', prefix: '✓', glow: 'rgba(0,255,136,0.08)'  },
}

function LogEntry({ log, index }) {
  const style = LOG_STYLE[log.type] || LOG_STYLE.info

  return (
    <motion.div
      initial={{ opacity: 0, x: 16, height: 0 }}
      animate={{ opacity: 1, x: 0, height: 'auto' }}
      transition={{ duration: 0.18, ease: 'easeOut' }}
      className="group flex items-start gap-1.5 px-2 py-1 rounded transition-all cursor-default"
      style={{ background: 'transparent' }}
      whileHover={{ background: style.glow }}
    >
      <motion.span
        className="text-xs flex-shrink-0 mt-0.5 w-3 text-center font-mono"
        style={{ color: style.color }}
        animate={log.type === 'running' ? { opacity: [1, 0.3, 1] } : {}}
        transition={{ repeat: Infinity, duration: 1 }}
      >
        {style.prefix}
      </motion.span>

      <div className="flex-1 min-w-0">
        <p className="text-xs font-mono leading-relaxed break-words" style={{ color: style.color }}>
          {log.message}
        </p>
        {log.steps && (
          <div className="mt-0.5 space-y-0.5 pl-1 border-l border-jarvis-border/50">
            {log.steps.map((s, j) => (
              <div key={j} className="flex items-center gap-1 text-xs font-mono">
                <span className="text-jarvis-muted/30 w-3">{j + 1}</span>
                <span className="text-jarvis-cyan/50">{s.action}</span>
                {s.params && Object.values(s.params)[0] && (
                  <span className="text-jarvis-muted/35 truncate">
                    → "{String(Object.values(s.params)[0]).slice(0, 22)}"
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <span className="text-xs font-mono text-jarvis-muted/25 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity tabular-nums">
        {log.ts}
      </span>
    </motion.div>
  )
}

export default function LogsPanel({ logs, onClear }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  const errors    = logs.filter(l => l.type === 'error').length
  const successes = logs.filter(l => ['success','done','step'].includes(l.type)).length

  return (
    <div className="w-72 flex flex-col glass border-l border-jarvis-border h-full relative overflow-hidden">
      {/* Data stream background */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-20">
        {[...Array(3)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-px"
            style={{
              left:       `${25 + i * 25}%`,
              background: 'linear-gradient(180deg, transparent, #00d4ff, transparent)',
              height:     '30%',
            }}
            animate={{ y: ['-30%', '130%'] }}
            transition={{ repeat: Infinity, duration: 3 + i, ease: 'linear', delay: i * 1.2 }}
          />
        ))}
      </div>

      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-jarvis-border flex-shrink-0 relative z-10">
        <div className="flex items-center gap-2">
          <motion.div
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ repeat: Infinity, duration: 2 }}
          >
            <Activity size={11} className="text-jarvis-cyan/60" />
          </motion.div>
          <span className="text-xs font-mono text-jarvis-muted tracking-widest">EXECUTION LOGS</span>
        </div>
        <div className="flex items-center gap-2">
          <AnimatePresence>
            {successes > 0 && (
              <motion.span
                initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }}
                className="text-xs font-mono px-1.5 py-0.5 rounded tabular-nums"
                style={{ color: '#00ff88', background: 'rgba(0,255,136,0.08)', border: '1px solid rgba(0,255,136,0.15)' }}
              >
                {successes}✓
              </motion.span>
            )}
            {errors > 0 && (
              <motion.span
                initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }}
                className="text-xs font-mono px-1.5 py-0.5 rounded tabular-nums"
                style={{ color: '#ff3366', background: 'rgba(255,51,102,0.08)', border: '1px solid rgba(255,51,102,0.15)' }}
              >
                {errors}✗
              </motion.span>
            )}
          </AnimatePresence>
          <motion.button
            onClick={onClear}
            whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}
            className="p-1 rounded hover:bg-jarvis-border/50 transition text-jarvis-muted/40 hover:text-jarvis-muted"
          >
            <Trash2 size={11} />
          </motion.button>
        </div>
      </div>

      {/* Entries */}
      <div className="flex-1 overflow-y-auto px-1 py-1 space-y-0 relative z-10">
        {logs.length === 0 && (
          <div className="flex flex-col items-center justify-center h-32 gap-2">
            <motion.div
              animate={{ opacity: [0.2, 0.5, 0.2] }}
              transition={{ repeat: Infinity, duration: 2 }}
            >
              <Activity size={20} className="text-jarvis-muted/20" />
            </motion.div>
            <p className="text-xs font-mono text-jarvis-muted/25">No logs yet</p>
          </div>
        )}
        <AnimatePresence initial={false}>
          {logs.map((log, i) => (
            <LogEntry key={i} log={log} index={i} />
          ))}
        </AnimatePresence>
        <div ref={bottomRef} />
      </div>

      {/* Footer */}
      <div className="px-3 py-1.5 border-t border-jarvis-border flex-shrink-0 relative z-10">
        <div className="flex items-center justify-between text-xs font-mono text-jarvis-muted/30">
          <span>{logs.length} entries</span>
          <motion.span
            animate={{ opacity: [0.4, 0.8, 0.4] }}
            transition={{ repeat: Infinity, duration: 2 }}
          >
            {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </motion.span>
        </div>
      </div>
    </div>
  )
}
