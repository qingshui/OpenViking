import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { resourceService } from '../services/resources'

const ResourceDetail: React.FC = () => {
  const { uri } = useParams()
  const navigate = useNavigate()
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [metadata, setMetadata] = useState<any>(null)

  useEffect(() => {
    if (uri) {
      loadResource()
    }
  }, [uri])

  const loadResource = async () => {
    try {
      setLoading(true)
      setError('')
      if (uri) {
        const decodedUri = decodeURIComponent(uri)
        const data = await resourceService.getAbstract(decodedUri)
        // Backend returns string directly, not {content, metadata}
        setContent(typeof data === 'string' ? data : data?.content || '')
        // Metadata is not available from abstract endpoint
        setMetadata({})
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load resource')
    } finally {
      setLoading(false)
    }
  }

  if (!uri) {
    return <div className="text-center py-8">Invalid resource URI</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Resource Details</h2>
        <button
          onClick={() => navigate('/resources')}
          className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
        >
          Back to Resources
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg mb-4">{error}</div>
      )}

      {loading ? (
        <div className="text-center py-8">Loading...</div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <div className="bg-gray-50 px-6 py-4 border-b">
            <h3 className="text-lg font-semibold text-gray-900">{uri}</h3>
            {metadata && (
              <div className="mt-2 text-sm text-gray-600">
                {metadata.size && <span>Size: {metadata.size} bytes</span>}
                {metadata.modTime && <span> | Modified: {new Date(metadata.modTime).toLocaleString()}</span>}
              </div>
            )}
          </div>
          <div className="p-6">
            <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm whitespace-pre-wrap">
              {content || 'No content available'}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}

export default ResourceDetail
