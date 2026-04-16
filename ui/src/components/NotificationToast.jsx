import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, ExternalLink, Bell, Newspaper } from 'lucide-react'

const CAT_COLORS = {
  technology: '#00d4ff', health: '#00ff88', finance: '#ffaa00',
  law: '#ff6688', education: '#aa88ff', science: '#00ffcc',
  sports: '#ff8844', politics: '#ff4466', business: '#44ddff',
  entertainment: '#ff44aa', world: '#88aaff', india: '#ff9933',
}

function Toast({ notif, onDismiss }) {
  const color = CAT_COLORS[notif.category] || '#00d4ff'
  const article = notif.articles?.[0]

  useEffect(() => {
    const t = setTimeout(() => onDismiss(notif.id), 8000)
    return () => clearTimeout(t)
  }, [notif.id, onDismiss])

  if (!article) return null

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 340, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 340, scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 300, damping: 28 }}
      className="relative rounded-xl overflow-hidden shadow-2xl"
      style={{
        width: 320,
        background: 'rgba(4,13,26,0.96)',
        border: `1px solid ${color}30`,
        boxShadow: `0 0 20px ${color}15`,
      }}
    >
      {/* Top accent line */}
      <motion.div
        className="absolute top-0 left-0 right-0 h-px"
        style={{ background: `linear-gradient(90deg, transparent, ${color}, transparent)` }}
        animate={{ opacity: [0.4, 1, 0.4] }}
        transition={{ repeat: Infinity, duration: 2 }}
      />

      {/* Auto-dismiss progress bar */}
      <motion.div
        className="absolute bottom-0 left-0 h-0.5 rounded-full"
        style={{ background: color }}
        initial={{ width: '100%' }}
        animate={{ width: '0%' }}
        transition={{ duration: 8, ease: 'linear' }}
      />

      <div className="px-4 py-3">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <motion.div
              className="w-1.5 h-1.5 rounded-full"
              style={{ background: color, boxShadow: `0 0 6px ${color}` }}
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ repeat: Infinity, duration: 1 }}
            />
            <span className="text-xs font-mono tracking-widest" style={{ color }}>
              {notif.category?.toUpperCase()} NEWS
            </span>
          </div>
          <button
            onClick={() => onDismiss(notif.id)}
            className="p-0.5 rounded hover:bg-white/5 transition"
          >
            <X size={10} className="text-jarvis-muted/50" />
          </button>
        </div>

        {/* Article */}
        <p className="text-xs font-mono text-jarvis-text leading-relaxed line-clamp-2 mb-2">
          {article.title}
        </p>

        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-jarvis-muted/40 truncate max-w-[180px]">
            {article.source}
          </span>
          {article.link && (
            <a
              href={article.link}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs font-mono transition-colors"
              style={{ color: `${color}80` }}
            >
              <ExternalLink size={9} />
              <span>READ</span>
            </a>
          )}
        </div>

        {/* More articles count */}
        {notif.articles?.length > 1 && (
          <p className="text-xs font-mono text-jarvis-muted/30 mt-1.5">
            +{notif.articles.length - 1} more {notif.category} articles
          </p>
        )}
      </div>
    </motion.div>
  )
}

export default function NotificationToast({ notifications, onDismiss, onDismissAll }) {
  if (!notifications.length) return null

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 items-end">
      <AnimatePresence>
        {notifications.slice(0, 4).map(n => (
          <Toast key={n.id} notif={n} onDismiss={onDismiss} />
        ))}
      </AnimatePresence>
      {notifications.length > 1 && (
        <motion.button
          initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          onClick={onDismissAll}
          className="text-xs font-mono text-jarvis-muted/40 hover:text-jarvis-muted/70 transition px-3 py-1 rounded border border-jarvis-border hover:border-jarvis-cyan/20"
        >
          Dismiss all ({notifications.length})
        </motion.button>
      )}
    </div>
  )
}
