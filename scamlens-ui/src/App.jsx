import { useState } from 'react'

function App() {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleScan = async (e) => {
    e.preventDefault()
    if (!text.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      })

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message || 'Failed to connect to ScamLens API. Ensure backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const getRiskBadge = (risk) => {
    switch (risk) {
      case 'HIGH':
        return 'bg-red-500/20 text-red-400 border-red-500/30'
      case 'MEDIUM':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30'
      default:
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 selection:bg-orange-500 selection:text-white">
      <div className="w-full max-w-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl rounded-2xl shadow-2xl p-8 transition-all">
        
        {/* Header */}
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 bg-gradient-to-tr from-orange-500 to-amber-500 rounded-xl shadow-lg shadow-orange-500/20 text-2xl">
            🛡️
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
              ScamLens AI
            </h1>
            <p className="text-sm text-slate-400">Multi-Model Phishing & SMS Scam Detector</p>
          </div>
        </div>

        {/* Input Form */}
        <form onSubmit={handleScan} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Message Content / URLs
            </label>
            <textarea
              rows={4}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste suspicious text or links here (e.g., 'URGENT: Click http://secure-login.com to verify your account')..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all resize-none text-sm leading-relaxed"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !text.trim()}
            className="w-full bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white font-semibold py-3 px-6 rounded-xl shadow-lg shadow-orange-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <span>Analyzing ML & URL Models...</span>
              </>
            ) : (
              <span>Analyze Message</span>
            )}
          </button>
        </form>

        {/* Error Alert */}
        {error && (
          <div className="mt-6 p-4 bg-red-950/40 border border-red-800/50 rounded-xl text-red-300 text-sm flex items-center space-x-2">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {/* Analysis Results */}
        {result && (
          <div className="mt-8 pt-6 border-t border-slate-800 space-y-6">
            
            {/* Verdict Box */}
            <div className="flex items-center justify-between p-4 bg-slate-950 border border-slate-800/80 rounded-xl">
              <div>
                <span className="text-xs uppercase tracking-wider text-slate-500 font-bold">Overall Verdict</span>
                <h2 className="text-xl font-bold mt-0.5">
                  {result.risk_level === 'HIGH' && <span className="text-red-400">🚨 Scam Detected</span>}
                  {result.risk_level === 'MEDIUM' && <span className="text-amber-400">⚠️ Suspicious Content</span>}
                  {result.risk_level === 'LOW' && <span className="text-emerald-400">✅ Low Risk / Safe</span>}
                </h2>
              </div>
              <div className="text-right">
                <span className="text-xs uppercase tracking-wider text-slate-500 font-bold">Combined Score</span>
                <div className={`mt-1 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getRiskBadge(result.risk_level)}`}>
                  {result.score % 1 === 0 ? Math.round(result.score) : result.score} / 100 ({result.risk_level})
                </div>
              </div>
            </div>

            {/* Explanation & Action */}
            <div className="bg-slate-950/60 border border-slate-800/60 rounded-xl p-4 space-y-3">
              <div>
                <h3 className="text-xs uppercase tracking-wider text-slate-400 font-bold mb-1">AI Explanation</h3>
                <p className="text-sm text-slate-300 leading-relaxed">{result.ai_explanation}</p>
              </div>
              <div>
                <h3 className="text-xs uppercase tracking-wider text-slate-400 font-bold mb-1">Recommended Action</h3>
                <p className="text-sm text-amber-300/90 leading-relaxed font-medium">{result.recommended_action}</p>
              </div>
            </div>

            {/* Triggers */}
            {result.detected_triggers && result.detected_triggers.length > 0 && (
              <div>
                <h3 className="text-xs uppercase tracking-wider text-slate-400 font-bold mb-2">Detected Risk Indicators</h3>
                <ul className="space-y-1.5">
                  {result.detected_triggers.map((trigger, idx) => (
                    <li key={idx} className="text-xs bg-red-950/30 border border-red-900/30 text-red-300 px-3 py-2 rounded-lg flex items-center space-x-2">
                      <span>•</span>
                      <span>{trigger}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* URL Breakdown */}
            {result.urls_found && result.urls_found.length > 0 && (
              <div>
                <h3 className="text-xs uppercase tracking-wider text-slate-400 font-bold mb-2">Extracted URL Analysis</h3>
                <div className="space-y-2">
                  {result.urls_found.map((urlItem, idx) => (
                    <div key={idx} className="bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs space-y-1">
                      <div className="flex justify-between items-center">
                        <span className="font-mono text-slate-300 break-all">{urlItem.original_url}</span>
                        <span className={`px-2 py-0.5 rounded border text-[10px] font-bold ${getRiskBadge(urlItem.risk)}`}>
                          {urlItem.risk} ({urlItem.score}/100)
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        )}

      </div>
    </div>
  )
}

export default App
