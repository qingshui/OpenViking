import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { resourceService } from '../services/resources'

interface Resource {
  uri: string
  name: string
  type: string
  size: number
  created_at: string
}

const ResourceManagement: React.FC = () => {
  const navigate = useNavigate()
  const [resources, setResources] = useState<Resource[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)
  const [newPath, setNewPath] = useState('')
  const [newParent, setNewParent] = useState('viking://resources/')
  const [newReason, setNewReason] = useState('')

  useEffect(() => {
    loadResources()
  }, [])

  const loadResources = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await resourceService.list()
      setResources(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load resources')
    } finally {
      setLoading(false)
    }
  }

  const handleAddResource = async () => {
    try {
      await resourceService.add(newPath, newParent, newReason)
      setShowAddForm(false)
      setNewPath('')
      setNewReason('')
      loadResources()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add resource')
    }
  }

  const handleDelete = async (uri: string) => {
    if (!window.confirm(`Delete ${uri}?`)) return
    try {
      await resourceService.delete(uri)
      loadResources()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete resource')
    }
  }

  const handleView = (uri: string) => {
    navigate(`/resources/${encodeURIComponent(uri)}`)
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Resource Management</h2>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          {showAddForm ? 'Cancel' : 'Add Resource'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg mb-4">{error}</div>
      )}

      {showAddForm && (
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-6">
          <h3 className="text-lg font-semibold mb-4">Add New Resource</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Path</label>
              <input
                type="text"
                value={newPath}
                onChange={(e) => setNewPath(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="/path/to/file"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Parent URI</label>
              <input
                type="text"
                value={newParent}
                onChange={(e) => setNewParent(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="viking://resources/"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Reason</label>
              <input
                type="text"
                value={newReason}
                onChange={(e) => setNewReason(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="Reason for adding"
              />
            </div>
            <button
              onClick={handleAddResource}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
            >
              Add Resource
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-center py-8">Loading...</div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">URI</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {resources.map((res) => (
                <tr key={res.uri}>
                  <td className="px-6 py-4 text-sm text-gray-900">{res.uri}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{res.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{res.type}</td>
                  <td className="px-6 py-4 text-sm">
                    <button
                      onClick={() => handleView(res.uri)}
                      className="text-blue-600 hover:text-blue-800 mr-3"
                    >
                      View
                    </button>
                    <button
                      onClick={() => handleDelete(res.uri)}
                      className="text-red-600 hover:text-red-800"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default ResourceManagement
