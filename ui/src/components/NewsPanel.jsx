import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Newspaper, RefreshCw, ExternalLink, X, ChevronRight, Zap } from 'lucide-react'

const CATEGORIES = [
  { id: 'technology',    label: 'TECH',    color: '#00d4ff' },
  { id: 'health',        label: 'HEALTH',  color: '#00ff88' },
  { id: 'finance',       label: 'FINANCE', color: '#ffaa00' },
  { id: 'law',           label: 'LAW',     color: '#ff6688' },
  { id: 'education',     label: 'EDU',     color: '#aa88ff' },
  { id: 'science',       label: 'SCIENCE', color: '#00ffcc' },
  { id: 'sports',        label: 'SPORTS',  color: '#ff8844' },
  { id: 'politics',      label: 'POLITICS',color: '#ff4466' },
  { id: 'business',      label: 'BIZ',     color: '#44ddff' },
  { id: 'entertainment', label: 'ENTMT',   color: '#ff44aa' },
  { id: 'world',         label: 'WORLD',   color: '#88aaff' },
  { id: 'india',         label: 'INDIA',   color: '#ff9933' },
]

function ArticleCard({ article, color, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05, type: 'spring', stiffness: 260, damping: 22 }}
      className="group relative rounded-lg border border-jarvis-border hover:border-opacity-60 transition-all overflow-hidden"
      style={{ background: 'rgba(4,13,26,0.7)', borderLeftWidth: 2, borderLeftColor: color }}
    >
      {/* hover shimmer */}
      <motion.div
        className="absolute inset-0 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity"
        style={{ background: `linear-gradient(90deg, transparent, ${color}08, transparent)` }}
      />
      <div className="px-3 py-2.5">
        <p className="text-xs font-mono text-jarvis-text leading-relaxed line-clamp-2 group-hover:text-white transition-colors">
          {article.title}
        </p>
        <div className="flex items-center justify-between mt-1.5">
          <span className="text-xs font-mono text-jarvis-muted/40 truncate max-w-[140px]">
            {article.source}
          </span>
          {article.link && (
            <a
              href={article.link}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs font-mono transition-colors"
              style={{ color: `${color}88` }}
              onMouseEnter={e => e.currentTarget.style.color = color}
              onMouseLeave={e => e.currentTarget.style.color = `${color}88`}
            >
              <ExternalLink size={9} />
              <span>READ</span>
            </a>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export default function NewsPanel({ onClose }) {
  const [activeTab,  setActiveTab]  = useState('technology')
  const [articles,   setArticles]   = useState({})
  const [loading,    setLoading]    = useState(false)
  const [lastUpdate, setLastUpdate] = useState(null)

  const activeColor = CATEGORIES.find(c => c.id === activeTab)?.color || '#00d4ff'

  const fetchCategory = useCallback(async (cat) => {
    if (articles[cat]) return
    setLoading(true)
    try {
      const r = await fetch(`/news/${cat}?limit=8`)
      const d = await r.json()
      setArticles(p => ({ ...p, [cat]: d.articles || [] }))
      setLastUpdate(new Date().toLocaleTimeString())
    } catch {
      setArticles(p => ({ ...p, [cat]: [] }))
    } finally {
      setLoading(false)
    }
  }, [articles])

  const refresh = useCallback(async () => {
    setLoading(true)
    setArticles(p => ({ ...p, [activeTab]: undefined }))
    setTimeout(() => fetchCategory(activeTab), 100)
  }, [activeTab, fetchCategory])

  useEffect(() => { fetchCategory(activeTab) }, [activeTab, fetchCategory])

  const currentArticles = articles[activeTab] || []

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.97 }}
      transition={{ type: 'spring', stiffness: 260, damping: 24 }}
      className="flex flex-col glass border border-jarvis-border rounded-xl overflow-hidden"
      style={{ width: 420, maxHeight: '80vh', minHeight: 400 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-jarvis-border flex-shrink-0">
        <div className="flex items-center gap-2">
          <motion.div animate={{ rotate: [0, 15, -15, 0] }} transition={{ repeat: Infinity, duration: 4 }}>
            <Newspaper size={14} className="neon-cyan" />
          </motion.div>
          <span className="text-xs font-mono neon-cyan tracking-widest">LIVE NEWS FEED</span>
          {lastUpdate && (
            <span className="text-xs font-mono text-jarvis-muted/40">· {lastUpdate}</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <motion.button
            onClick={refresh}
            whileTap={{ scale: 0.9 }}
            className="p-1.5 rounded border border-jarvis-border hover:border-jarvis-cyan/30 transition"
          >
            <motion.div animate={loading ? { rotate: 360 } : {}} transition={{ repeat: loading ? Infinity : 0, duration: 0.8, ease: 'linear' }}>
              <RefreshCw size={11} className="text-jarvis-muted/50" />
            </motion.div>
          </motion.button>
          <motion.button
            onClick={onClose}
            whileTap={{ scale: 0.9 }}
            className="p-1.5 rounded border border-jarvis-border hover:border-red-500/30 transition"
          >
            <X size={11} className="text-jarvis-muted/50" />
          </motion.button>
        </div>
      </div>

      {/* Category tabs — scrollable */}
      <div className="flex gap-1 px-3 py-2 border-b border-jarvis-border overflow-x-auto flex-shrink-0 scrollbar-hide">
        {CATEGORIES.map(cat => (
          <button
            key={cat.id}
            onClick={() => setActiveTab(cat.id)}
            className="flex-shrink-0 px-2.5 py-1 rounded text-xs font-mono transition-all"
            style={{
              color:      activeTab === cat.id ? cat.color : '#3a5a7a',
              background: activeTab === cat.id ? `${cat.color}15` : 'transparent',
              border:     `1px solid ${activeTab === cat.id ? `${cat.color}40` : 'transparent'}`,
            }}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Articles */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {loading && !currentArticles.length ? (
          <div className="flex flex-col items-center justify-center py-12 gap-3">
            <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}>
              <RefreshCw size={18} style={{ color: activeColor }} />
            </motion.div>
            <span className="text-xs font-mono text-jarvis-muted/40">Fetching {activeTab} news...</span>
          </div>
        ) : currentArticles.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 gap-2">
            <Newspaper size={24} className="text-jarvis-muted/20" />
            <span className="text-xs font-mono text-jarvis-muted/40">No articles found</span>
            <button onClick={refresh} className="text-xs font-mono text-jarvis-cyan/50 hover:text-jarvis-cyan transition">
              Try again
            </button>
          </div>
        ) : (
          <AnimatePresence mode="wait">
            <motion.div key={activeTab} className="space-y-2">
              {/* Category header */}
              <div className="flex items-center gap-2 px-1 mb-3">
                <motion.div
                  className="w-1.5 h-1.5 rounded-full"
                  style={{ background: activeColor, boxShadow: `0 0 6px ${activeColor}` }}
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ repeat: Infinity, duration: 1.5 }}
                />
                <span className="text-xs font-mono tracking-widest" style={{ color: activeColor }}>
                  {CATEGORIES.find(c => c.id === activeTab)?.label} — {currentArticles.length} ARTICLES
                </span>
              </div>
              {currentArticles.map((a, i) => (
                <ArticleCard key={i} article={a} color={activeColor} index={i} />
              ))}
            </motion.div>
          </AnimatePresence>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t border-jarvis-border flex items-center justify-between flex-shrink-0">
        <span className="text-xs font-mono text-jarvis-muted/30">Powered by Google News RSS</span>
        <motion.div
          className="flex items-center gap-1 text-xs font-mono"
          style={{ color: `${activeColor}60` }}
          animate={{ opacity: [0.4, 0.8, 0.4] }}
          transition={{ repeat: Infinity, duration: 2 }}
        >
          <Zap size={9} />
          <span>LIVE</span>
        </motion.div>
      </div>
    </motion.div>
  )
}
