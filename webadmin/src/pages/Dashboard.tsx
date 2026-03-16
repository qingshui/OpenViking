import React from 'react'

const Dashboard: React.FC = () => {
  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Resources</h3>
          <p className="text-gray-600">Manage your stored resources</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Sessions</h3>
          <p className="text-gray-600">View and manage conversation sessions</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">File System</h3>
          <p className="text-gray-600">Browse viking:// file system</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Search</h3>
          <p className="text-gray-600">Semantic and content search</p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
