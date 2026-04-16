import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, ChevronRight, Volume2 } from 'lucide-react'
import VoiceInput from './VoiceInput'

const QUICK = [
  'Open Chrome and play Arijit Singh',
  'Open camera and take photo',
  'Weather in London',
  'Search Python tutorials',
  'Open VS Code',
  'Take a screenshot',
  'Get latest tech news',
  'Run command: ipconfig',
]

// ── Browser TTS ───────────────────────────────────────────────────────────────
export function speakText(text) {
  if (!text || !window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const utt = new SpeechSynthesisUtterance(text.replace(/[^\x00-\x7F]/g, ''))
  utt.rate = 1.0; utt.pitch = 1.0; utt.volume = 1.0
  const voices = window.speechSynthesis.getVoices()
  const preferred = voices.find(v =>
    v.name.includes('Zira') || v.name.includes('Google') || v.name.includes('Natural')
  )
  if (preferred) utt.voice = preferred
  window.speechSynthesis.speak(utt)
}

export default function CommandInput({ onRun, loading }) {
  const [value,   setValue]   = useState('')
  const [focused, setFocused] = useState(false)
  const [ttsOn,   setTtsOn]   = useState(() => localStorage.getItem('neuro-tts') !== 'off')
  const inputRef = useRef(null)

  useEffect(() => {
    localStorage.setItem('neuro-tts', ttsOn ? 'on' : 'off')
  }, [ttsOn])

  // Called by VoiceInput with live transcript — updates textarea in real-time
  const handleTranscript = useCallback((text) => {
    setValue(text)
    // Auto-resize textarea
    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
      inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 80) + 'px'
    }
  }, [])

  // Called by VoiceInput auto-send OR user clicks Send
  const handleSubmit = useCallback((text) => {
    const msg = (text || value).trim()
    if (!msg || loading) return
    onRun(msg)
    setValue('')
    if (inputRef.current) inputRef.current.style.height = 'auto'
  }, [value, loading, onRun])

  const submit = () => handleSubmit(value)

  return (
    <div className="px-4 pt-3 pb-2 border-b border-jarvis-border flex-shrink-0">

      {/* ── Label row ── */}
      <div className="flex items-center gap-2 mb-2">
        <ChevronRight size={10} className="text-jarvis-cyan/50" />
        <span className="text-xs font-mono text-jarvis-muted tracking-widest">COMMAND INPUT</span>
        <div className="flex-1 h-px bg-jarvis-border" />
        <button
          onClick={() => setTtsOn(v => !v)}
          className="flex items-center gap-1 text-xs font-mono px-2 py-0.5 rounded border transition-all"
          style={{
            borderColor: ttsOn ? 'rgba(0,212,255,0.3)' : 'rgba(10,32,64,1)',
            color:       ttsOn ? '#00d4ff' : '#3a5a7a',
            background:  ttsOn ? 'rgba(0,212,255,0.06)' : 'transparent',
          }}
        >
          <Volume2 size={9} />
          <span>TTS {ttsOn ? 'ON' : 'OFF'}</span>
        </button>
      </div>

      {/* ── Main input box ── */}
      <div className="relative">
        {focused && (
          <motion.div
            className="absolute inset-0 rounded-lg pointer-events-none"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            style={{ boxShadow: '0 0 0 1px rgba(0,212,255,0.4), 0 0 20px rgba(0,212,255,0.08)' }}
          />
        )}

        <div
          className="flex items-start gap-2 glass rounded-lg border px-3 py-2.5 transition-colors"
          style={{ borderColor: focused ? 'rgba(0,212,255,0.3)' : 'rgba(10,32,64,1)' }}
        >
          <span className="text-jarvis-cyan/50 font-mono text-sm select-none flex-shrink-0 mt-0.5">›</span>

          <textarea
            ref={inputRef}
            value={value}
            onChange={e => setValue(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit() }
            }}
            placeholder="Tell Neuro what to do...  or click Mic and speak"
            rows={1}
            disabled={loading}
            className="flex-1 bg-transparent text-jarvis-text placeholder-jarvis-muted/40 text-sm font-mono resize-none outline-none leading-relaxed"
            style={{ minHeight: '24px', maxHeight: '80px' }}
          />

          {/* Send button */}
          <motion.button
            onClick={submit}
            disabled={loading || !value.trim()}
            whileTap={{ scale: 0.9 }}
            className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center border transition-all mt-0.5"
            style={{
              borderColor: value.trim() && !loading ? 'rgba(0,212,255,0.5)' : 'rgba(10,32,64,1)',
              background:  value.trim() && !loading ? 'rgba(0,212,255,0.1)' : 'transparent',
              boxShadow:   value.trim() && !loading ? '0 0 10px rgba(0,212,255,0.2)' : 'none',
            }}
          >
            {loading
              ? <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}>
                  <SpinIcon size={13} />
                </motion.div>
              : <Send size={13} style={{ color: value.trim() ? '#00d4ff' : '#3a5a7a' }} />
            }
          </motion.button>
        </div>
      </div>

      {/* ── Voice input (real-time STT) ── */}
      <div className="mt-2">
        <VoiceInput
          onTranscript={handleTranscript}
          onSubmit={handleSubmit}
          disabled={loading}
        />
      </div>

      {/* ── Quick commands ── */}
      <div className="flex flex-wrap gap-1.5 mt-2">
        {QUICK.map(q => (
          <motion.button
            key={q}
            onClick={() => { setValue(q); inputRef.current?.focus() }}
            disabled={loading}
            whileHover={{ borderColor: 'rgba(0,212,255,0.3)', color: 'rgba(0,212,255,0.8)' }}
            className="text-xs font-mono px-2 py-0.5 rounded border border-jarvis-border text-jarvis-muted transition-all"
          >
            {q}
          </motion.button>
        ))}
      </div>

      {/* ── Hints ── */}
      <div className="flex items-center gap-3 mt-1.5 text-xs font-mono text-jarvis-muted/35">
        <span><kbd className="px-1 rounded border border-jarvis-border">Enter</kbd> run</span>
        <span><kbd className="px-1 rounded border border-jarvis-border">Shift+Enter</kbd> newline</span>
        <span className="ml-auto opacity-60">🎤 speak → text appears live</span>
      </div>
    </div>
  )
}

function SpinIcon({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="#00d4ff" strokeWidth="2">
      <path d="M21 12a9 9 0 1 1-6.219-8.56" />
    </svg>
  )
}
