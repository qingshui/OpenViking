import React, { useState, useEffect } from 'react'
import { filesystemService } from '../services/filesystem'
import apiClient from '../services/api'

interface FileNode {
  uri: string
  name: string
  type: 'file' | 'directory'
}

const FileExplorer: React.FC = () => {
  const [currentUri, setCurrentUri] = useState('viking://resources/')
  const [files, setFiles] = useState<FileNode[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [content, setContent] = useState<string>('')
  const [showContent, setShowContent] = useState(false)
  const [contentLevel, setContentLevel] = useState<'l0' | 'l1' | 'l2'>('l0')

  useEffect(() => {
    loadFiles()
  }, [currentUri])

  const loadFiles = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await filesystemService.list(currentUri)
      setFiles(data)
      setContent('')
      setShowContent(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load files')
    } finally {
      setLoading(false)
    }
  }

  const handleLoadContent = async (uri: string, level: 'l0' | 'l1' | 'l2') => {
    try {
      setContentLevel(level)
      let content: string = ''

      if (level === 'l0') {
        // L0: Abstract
        const response = await apiClient.post('', {
          method: 'GET',
          path: '/api/v1/content/abstract',
          query: { uri }
        })
        const data = response.data?.result
        content = typeof data === 'string' ? data : data?.content || ''
      } else if (level === 'l1') {
        // L1: Overview
        const response = await apiClient.post('', {
          method: 'GET',
          path: '/api/v1/content/overview',
          query: { uri }
        })
        const data = response.data?.result
        content = typeof data === 'string' ? data : data?.content || ''
      } else {
        // L2: Full content
        const response = await apiClient.post('', {
          method: 'GET',
          path: '/api/v1/content/read',
          query: { uri, offset: 0, limit: -1 }
        })
        const data = response.data?.result
        content = typeof data === 'string' ? data : data?.content || ''
      }

      setContent(content)
      setShowContent(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load content')
    }
  }

  const handleMkdir = async () => {
    const name = prompt('Enter directory name:')
    if (!name) return
    try {
      const newUri = `${currentUri}${name}/`
      await filesystemService.mkdir(newUri)
      loadFiles()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create directory')
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-4">
          <input
            type="text"
            value={currentUri}
            onChange={(e) => setCurrentUri(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg w-96"
          />
          <button
            onClick={loadFiles}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Load
          </button>
          <button
            onClick={handleMkdir}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
          >
            Create Directory
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg mb-4">{error}</div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <div className="p-4 border-b">
            <h3 className="font-semibold">Files</h3>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center text-gray-500">Loading...</div>
            ) : files.length === 0 ? (
              <div className="p-4 text-center text-gray-500">No files</div>
            ) : (
              files.map((file) => (
                <div
                  key={file.uri}
                  className="p-4 border-b hover:bg-gray-50"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{file.name}</div>
                      <div className="text-xs text-gray-500">{file.uri}</div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleLoadContent(file.uri, 'l0')}
                        className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
                      >
                        L0
                      </button>
                      <button
                        onClick={() => handleLoadContent(file.uri, 'l1')}
                        className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200"
                      >
                        L1
                      </button>
                      <button
                        onClick={() => handleLoadContent(file.uri, 'l2')}
                        className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded hover:bg-purple-200"
                      >
                        L2
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <div className="p-4 border-b flex justify-between items-center">
            <h3 className="font-semibold">Content ({contentLevel.toUpperCase()})</h3>
            <button
              onClick={() => setShowContent(false)}
              className="text-sm text-gray-600 hover:text-gray-800"
            >
              Close
            </button>
          </div>
          <div className="max-h-96 overflow-y-auto p-4">
            {showContent ? (
              <pre className="whitespace-pre-wrap text-sm text-gray-900">{content}</pre>
            ) : (
              <div className="text-center text-gray-500 py-8">
                Select a file and click L0/L1/L2 to view content
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default FileExplorer
