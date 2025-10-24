import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Freelancer Feedback Assistant</h1>
          <div className="flex items-center gap-4">
            <span>{user?.email}</span>
            <button
              onClick={logout}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 py-8">
        <h2 className="text-3xl font-bold mb-6">Welcome, {user?.full_name || user?.email}!</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-2">Projects</h3>
            <p className="text-gray-600">Manage your projects</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-2">Feedback</h3>
            <p className="text-gray-600">Parse client feedback</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold mb-2">Revisions</h3>
            <p className="text-gray-600">Track version history</p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
