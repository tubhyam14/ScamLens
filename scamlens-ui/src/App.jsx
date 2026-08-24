import { useState } from 'react';

function App() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error('Failed to connect to ScamLens backend API.');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center py-10 px-4">
      {/* Header */}
      <header className="max-w-3xl w-full text-center mb-10">
        <h1 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-orange-400">
          ScamLens AI
        </h1>
        <p className="text-slate-400 mt-2">
          Detect phishing messages, job scams, and fraud patterns instantly.
        </p>
      </header>

      {/* Main Container */}
      <main className="max-w-3xl w-full bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
        <form onSubmit={handleAnalyze} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Paste suspicious message or email text:
            </label>
            <textarea
              rows="5"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="e.g. Congratulations! You have been selected for a remote data entry job. Click here to send your registration fee..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-slate-100 focus:outline-none focus:ring-2 focus:ring-orange-500 text-sm"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-red-600 to-orange-500 hover:from-red-500 hover:to-orange-400 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 shadow-lg disabled:opacity-50"
          >
            {loading ? 'Analyzing Pattern...' : 'Scan for Scam'}
          </button>
        </form>

        {/* Error State */}
        {error && (
          <div className="mt-6 bg-red-950/50 border border-red-800 text-red-200 p-4 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Results Box */}
        {result && (
          <div className="mt-8 space-y-6 border-t border-slate-800 pt-6">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs uppercase tracking-wider text-slate-400">Verdict</span>
                <h2 className="text-2xl font-bold mt-0.5">
		{result.risk_level && result.risk_level !== 'LOW' && result.risk_level !== 'SAFE' ? (
 			 <span className="text-red-400">🚨 Scam Detected</span>
		) : (
 			 <span className="text-emerald-400">✅ Safe / Low Risk</span>
		)}
                </h2>
              </div>
              <div className="text-right">
                <span className="text-xs uppercase tracking-wider text-slate-400">Risk Level</span>
                <p className="text-lg font-semibold uppercase text-orange-400">
                  {result.risk_level}
                </p>
              </div>
            </div>

            {/* AI Explanation */}
            <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-slate-300 mb-1">AI Explanation</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                {result.ai_explanation}
              </p>
            </div>

            {/* Triggers & Actions Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-slate-300 mb-2">Detected Triggers</h3>
                {result.detected_triggers && result.detected_triggers.length > 0 ? (
                  <ul className="list-disc list-inside text-sm text-slate-400 space-y-1">
                    {result.detected_triggers.map((trigger, idx) => (
                      <li key={idx}>{trigger}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-slate-500">No specific flags triggered.</p>
                )}
              </div>

              <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-slate-300 mb-1">Recommended Action</h3>
                <p className="text-sm text-slate-400">
                  {result.recommended_action || 'Proceed with normal caution.'}
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
