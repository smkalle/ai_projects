import React, { useState } from 'react';
import { SparklesIcon } from '@heroicons/react/24/outline';

const AIInsights = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const quickQuestions = [
    { text: 'Is it safe to exercise outside?', icon: '🏃' },
    { text: 'How is the air quality today?', icon: '🌫️' },
    { text: 'Safe for children to play outside?', icon: '👶' },
    { text: 'Should I open windows today?', icon: '🪟' }
  ];

  const handleSubmit = async (question = query) => {
    if (!question.trim()) return;
    
    setLoading(true);
    setQuery(question);
    
    // Simulate API call
    setTimeout(() => {
      setResponse({
        insight: `Based on current environmental conditions, ${question.toLowerCase().includes('safe') ? 'it is generally safe' : 'conditions are moderate'} for outdoor activities. Air quality index is currently at 45 (Good level).`,
        confidence: 0.85,
        query_type: 'safety',
        recommendations: [
          'Current conditions are suitable for most outdoor activities',
          'Sensitive individuals should monitor air quality throughout the day',
          'Early morning or evening hours are optimal for exercise'
        ]
      });
      setLoading(false);
    }, 1500);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-6">
          <SparklesIcon className="w-8 h-8 text-primary-400" />
          <h1 className="text-3xl font-bold">AI Environmental Insights</h1>
        </div>

        <div className="max-w-4xl">
          <div className="flex gap-4 mb-6">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask about environmental conditions..."
              className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-primary-400 transition-all"
              onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
            />
            <button
              onClick={() => handleSubmit()}
              disabled={loading || !query.trim()}
              className="gradient-primary text-white px-6 py-3 rounded-xl font-medium disabled:opacity-50"
            >
              {loading ? 'Thinking...' : 'Ask AI'}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-8">
            {quickQuestions.map((q, index) => (
              <button
                key={index}
                onClick={() => handleSubmit(q.text)}
                className="glass-button p-4 text-left hover:border-primary-400 transition-all"
              >
                <span className="text-2xl mr-3">{q.icon}</span>
                {q.text}
              </button>
            ))}
          </div>

          {response && (
            <div className="glass-card p-6 animate-fade-in">
              <div className="flex items-center justify-between mb-4">
                <span className="px-3 py-1 bg-primary-500/20 text-primary-400 rounded-full text-sm font-medium">
                  {response.query_type.toUpperCase()}
                </span>
                <span className="text-sm text-gray-400">
                  {Math.round(response.confidence * 100)}% confident
                </span>
              </div>
              
              <p className="text-lg mb-6">{response.insight}</p>
              
              <div>
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <SparklesIcon className="w-5 h-5 text-primary-400" />
                  Recommendations
                </h4>
                <ul className="space-y-2">
                  {response.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <span className="w-2 h-2 bg-primary-400 rounded-full mt-2" />
                      <span className="text-gray-300">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIInsights;