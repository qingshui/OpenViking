import React, { useState } from 'react'
import { searchService } from '../services/search'

interface SearchResult {
  uri: string
  context_type: string
  level: number
  abstract: string
  score: number
}

const SemanticSearch: React.FC = () => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [targetUri, setTargetUri] = useState('')
  const [limit, setLimit] = useState(10)
  const [activeTab, setActiveTab] = useState<'semantic' | 'content'>('semantic')
  const [grepPattern, setGrepPattern] = useState('')

  const handleSemanticSearch = async () => {
    if (!query.trim()) return
    try {
      setLoading(true)
      setError('')
      const data = await searchService.find(query, limit, targetUri || undefined)
      setResults(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  const handleContentSearch = async () => {
    if (!grepPattern.trim() || !targetUri) return
    try {
      setLoading(true)
      setError('')
      const data = await searchService.grep(targetUri, grepPattern)
      setResults(data || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="mb-6">
        <div className="border-b">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('semantic')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'semantic'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Semantic Search
            </button>
            <button
              onClick={() => setActiveTab('content')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'content'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Content Search
            </button>
          </nav>
        </div>
      </div>

      {activeTab === 'semantic' ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Query</label>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSemanticSearch()}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              placeholder="Enter search query..."
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Target URI (optional)</label>
              <input
                type="text"
                value={targetUri}
                onChange={(e) => setTargetUri(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                placeholder="viking://resources/"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Limit</label>
              <input
                type="number"
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                min="1"
                max="50"
              />
            </div>
          </div>
          <button
            onClick={handleSemanticSearch}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Search
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target URI</label>
            <input
              type="text"
              value={targetUri}
              onChange={(e) => setTargetUri(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              placeholder="viking://resources/"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Pattern</label>
            <input
              type="text"
              value={grepPattern}
              onChange={(e) => setGrepPattern(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleContentSearch()}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              placeholder="Enter search pattern..."
            />
          </div>
          <button
            onClick={handleContentSearch}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Search
          </button>
        </div>
      )}

      {error && (
        <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg mt-4">{error}</div>
      )}

      {loading && (
        <div className="text-center py-8 text-gray-600">Searching...</div>
      )}

      {results.length > 0 && (
        <div className="mt-6 space-y-4">
          <h3 className="font-semibold text-gray-700">Results ({results.length})</h3>
          {results.map((result, index) => (
            <div key={index} className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-semibold text-gray-900">{result.uri}</h4>
                <span className="text-sm text-green-600">Score: {result.score.toFixed(2)}</span>
              </div>
              <div className="text-sm text-gray-500 mb-2">
                Type: {result.context_type} | Level: {result.level}
              </div>
              <p className="text-gray-700">{result.abstract}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SemanticSearch
