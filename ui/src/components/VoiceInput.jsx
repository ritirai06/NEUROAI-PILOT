/**
 * VoiceInput — Real-time Speech-to-Text using Web Speech API
 *
 * Features:
 *  • Interim results → text appears live as you speak
 *  • Continuous mode → keeps listening until you stop
 *  • Hindi + English support
 *  • Auto-send option
 *  • Animated waveform
 *  • Full error handling
 */
import { useState, useRef, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Mic, MicOff, X, Languages } from 'lucide-react'

const LANGS = [
  { code: 'en-IN', label: 'EN' },
  { code: 'hi-IN', label: 'HI' },
  { code: 'en-US', label: 'US' },
]

const ERROR_MESSAGES = {
  'not-allowed':      'Microphone access denied. Click the 🔒 icon in your browser address bar and allow microphone.',
  'no-speech':        'No speech detected. Please speak clearly.',
  'network':          'Network error. Check your internet connection.',
  'audio-capture':    'No microphone found. Please connect a microphone.',
  'service-not-allowed': 'Speech service blocked. Try Chrome or Edge.',
  'aborted':          null, // user stopped — not an error
}

export default function VoiceInput({ onTranscript, onSubmit, disabled }) {
  const [listening,    setListening]    = useState(false)
  const [interim,      setInterim]      = useState('')   // live partial text
  const [final,        setFinal]        = useState('')   // confirmed text
  const [error,        setError]        = useState(null)
  const [langIdx,      setLangIdx]      = useState(0)
  const [autoSend,     setAutoSend]     = useState(false)
  const [supported,    setSupported]    = useState(true)
  const [levels,       setLevels]       = useState(Array(12).fill(2)) // waveform bar heights

  const recogRef     = useRef(null)
  const audioCtxRef  = useRef(null)
  const analyserRef  = useRef(null)
  const animFrameRef = useRef(null)
  const streamRef    = useRef(null)

  // Check browser support
  useEffect(() => {
    const ok = 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window
    setSupported(ok)
  }, [])

  // Waveform animation via Web Audio API
  const startWaveform = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      const ctx      = new (window.AudioContext || window.webkitAudioContext)()
      const analyser = ctx.createAnalyser()
      analyser.fftSize = 64
      ctx.createMediaStreamSource(stream).connect(analyser)
      audioCtxRef.current  = ctx
      analyserRef.current  = analyser

      const data = new Uint8Array(analyser.frequencyBinCount)
      const tick = () => {
        analyser.getByteFrequencyData(data)
        const bars = Array.from({ length: 12 }, (_, i) => {
          const val = data[Math.floor(i * data.length / 12)] || 0
          return Math.max(2, Math.round((val / 255) * 28))
        })
        setLevels(bars)
        animFrameRef.current = requestAnimationFrame(tick)
      }
      tick()
    } catch {
      // Waveform optional — speech still works without it
    }
  }, [])

  const stopWaveform = useCallback(() => {
    cancelAnimationFrame(animFrameRef.current)
    streamRef.current?.getTracks().forEach(t => t.stop())
    audioCtxRef.current?.close().catch(() => {})
    audioCtxRef.current = null
    analyserRef.current = null
    setLevels(Array(12).fill(2))
  }, [])

  const stop = useCallback(() => {
    recogRef.current?.stop()
    recogRef.current = null
    stopWaveform()
    setListening(false)
    setInterim('')
  }, [stopWaveform])

  const start = useCallback(() => {
    if (!supported) {
      setError('Speech recognition not supported. Use Chrome or Edge.')
      return
    }
    setError(null)
    setFinal('')
    setInterim('')

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    const r  = new SR()

    r.lang            = LANGS[langIdx].code
    r.continuous      = true      // keep listening
    r.interimResults  = true      // get partial results live
    r.maxAlternatives = 1

    r.onstart = () => {
      setListening(true)
      startWaveform()
    }

    r.onresult = (e) => {
      let interimText = ''
      let finalText   = ''

      for (let i = e.resultIndex; i < e.results.length; i++) {
        const t = e.results[i][0].transcript
        if (e.results[i].isFinal) {
          finalText += t + ' '
        } else {
          interimText += t
        }
      }

      if (finalText) {
        setFinal(prev => {
          const updated = (prev + finalText).trim()
          onTranscript(updated)          // push to input box live
          return updated
        })
      }
      setInterim(interimText)
      if (finalText) onTranscript((final + finalText).trim())
    }

    r.onerror = (e) => {
      const msg = ERROR_MESSAGES[e.error]
      if (msg !== null) setError(msg || `Error: ${e.error}`)
      stop()
    }

    r.onend = () => {
      setListening(false)
      stopWaveform()
      setInterim('')
      // Auto-send if enabled and we have text
      if (autoSend && final.trim()) {
        setTimeout(() => {
          onSubmit(final.trim())
          setFinal('')
        }, 300)
      }
    }

    recogRef.current = r
    try {
      r.start()
    } catch (e) {
      setError('Could not start microphone. Try again.')
    }
  }, [supported, langIdx, startWaveform, stopWaveform, stop, autoSend, final, onTranscript, onSubmit])

  const toggle = useCallback(() => {
    if (listening) stop()
    else start()
  }, [listening, start, stop])

  const cycleLang = useCallback(() => {
    if (listening) stop()
    setLangIdx(i => (i + 1) % LANGS.length)
    setError(null)
  }, [listening, stop])

  // Cleanup on unmount
  useEffect(() => () => stop(), [stop])

  if (!supported) return null

  return (
    <div className="flex flex-col gap-1">
      {/* Controls row */}
      <div className="flex items-center gap-1.5">

        {/* Language toggle */}
        <motion.button
          onClick={cycleLang}
          whileTap={{ scale: 0.9 }}
          title="Switch language"
          className="flex items-center gap-1 text-xs font-mono px-1.5 py-1 rounded border transition-all"
          style={{
            borderColor: 'rgba(0,212,255,0.15)',
            color:       '#00d4ff88',
            background:  'transparent',
          }}
        >
          <Languages size={9} />
          <span>{LANGS[langIdx].label}</span>
        </motion.button>

        {/* Auto-send toggle */}
        <motion.button
          onClick={() => setAutoSend(v => !v)}
          whileTap={{ scale: 0.9 }}
          title="Auto-send when speech ends"
          className="text-xs font-mono px-1.5 py-1 rounded border transition-all"
          style={{
            borderColor: autoSend ? 'rgba(0,255,136,0.3)' : 'rgba(10,32,64,1)',
            color:       autoSend ? '#00ff88' : '#3a5a7a',
            background:  autoSend ? 'rgba(0,255,136,0.06)' : 'transparent',
          }}
        >
          AUTO
        </motion.button>

        {/* Main mic button */}
        <motion.button
          onClick={toggle}
          disabled={disabled}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.88 }}
          className="relative flex items-center justify-center rounded-lg border transition-all"
          style={{
            width:       listening ? 80 : 32,
            height:      32,
            borderColor: listening ? 'rgba(255,51,102,0.7)' : 'rgba(0,212,255,0.25)',
            background:  listening
              ? 'rgba(255,51,102,0.12)'
              : 'rgba(0,212,255,0.05)',
            boxShadow:   listening
              ? '0 0 20px rgba(255,51,102,0.35), inset 0 0 10px rgba(255,51,102,0.1)'
              : '0 0 8px rgba(0,212,255,0.1)',
          }}
        >
          {/* Pulse rings when listening */}
          {listening && (
            <>
              <motion.span
                className="absolute inset-0 rounded-lg border border-red-500/30"
                animate={{ scale: [1, 1.4], opacity: [0.5, 0] }}
                transition={{ repeat: Infinity, duration: 1, ease: 'easeOut' }}
              />
              <motion.span
                className="absolute inset-0 rounded-lg border border-red-500/20"
                animate={{ scale: [1, 1.7], opacity: [0.3, 0] }}
                transition={{ repeat: Infinity, duration: 1, delay: 0.3, ease: 'easeOut' }}
              />
            </>
          )}

          <AnimatePresence mode="wait">
            {listening ? (
              <motion.div
                key="listening"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="flex items-center gap-1.5 px-2"
              >
                {/* Live waveform */}
                <div className="flex items-center gap-px">
                  {levels.slice(0, 6).map((h, i) => (
                    <motion.div
                      key={i}
                      className="w-0.5 rounded-full"
                      style={{ background: '#ff3366', height: h }}
                      transition={{ duration: 0.05 }}
                    />
                  ))}
                </div>
                <MicOff size={11} style={{ color: '#ff3366' }} />
              </motion.div>
            ) : (
              <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <Mic size={13} style={{ color: '#00d4ff99' }} />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.button>

        {/* Clear interim */}
        <AnimatePresence>
          {(interim || final) && (
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.8 }}
              onClick={() => { setFinal(''); setInterim(''); onTranscript('') }}
              className="w-6 h-6 rounded flex items-center justify-center border border-jarvis-border text-jarvis-muted/40 hover:text-jarvis-muted transition"
            >
              <X size={9} />
            </motion.button>
          )}
        </AnimatePresence>
      </div>

      {/* Live status bar */}
      <AnimatePresence>
        {listening && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="flex items-center gap-2 px-1 py-0.5">
              {/* Full waveform */}
              <div className="flex items-end gap-px h-5">
                {levels.map((h, i) => (
                  <motion.div
                    key={i}
                    className="w-0.5 rounded-full"
                    style={{ background: `rgba(255,51,102,${0.4 + (h / 28) * 0.6})` }}
                    animate={{ height: h }}
                    transition={{ duration: 0.05 }}
                  />
                ))}
              </div>

              <span className="text-xs font-mono" style={{ color: '#ff3366' }}>
                LISTENING
              </span>

              {/* Interim text preview */}
              {interim && (
                <motion.span
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                  className="text-xs font-mono text-jarvis-muted/60 truncate max-w-[180px] italic"
                >
                  {interim}
                </motion.span>
              )}

              <span className="text-xs font-mono text-jarvis-muted/30 ml-auto">
                {LANGS[langIdx].code} · click mic to stop
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="flex items-start gap-2 px-2 py-1.5 rounded border text-xs font-mono"
            style={{ borderColor: 'rgba(255,51,102,0.2)', background: 'rgba(255,51,102,0.06)', color: '#ff3366' }}
          >
            <span className="flex-1">{error}</span>
            <button onClick={() => setError(null)} className="opacity-60 hover:opacity-100">
              <X size={10} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
