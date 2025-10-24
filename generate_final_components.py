#!/usr/bin/env python3
"""
Generate final critical components: AI service, React components, and utilities
"""

from pathlib import Path

FINAL_FILES = {
    # AI Service
    "backend/app/services/__init__.py": '''"""Business logic services"""''',
    
    "backend/app/services/ai_service.py": '''"""
AI Service for Feedback Parsing
OpenAI integration for parsing creative feedback
"""
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI

from app.core.config import settings
from app.core.logging_config import logger

client = OpenAI(api_key=settings.OPENAI_API_KEY)

FEEDBACK_PARSING_PROMPT = """
You are an expert at analyzing creative feedback and extracting actionable tasks.

Given the following client feedback, please:
1. Extract specific, actionable tasks
2. Determine the sentiment (positive, neutral, negative)
3. Assign a priority level (low, medium, high, urgent)
4. Provide a clear summary

Feedback: {feedback_text}

Respond in JSON format:
{{
  "summary": "Brief summary of the feedback",
  "sentiment": "positive|neutral|negative",
  "priority": "low|medium|high|urgent",
  "action_items": [
    {{
      "description": "Specific actionable task",
      "priority": 0-3
    }}
  ],
  "key_points": ["point 1", "point 2"]
}}
"""

async def parse_feedback(feedback_text: str) -> Dict[str, Any]:
    """
    Parse feedback using OpenAI GPT-4
    
    Args:
        feedback_text: Raw feedback text from client
        
    Returns:
        Parsed feedback with action items, sentiment, and priority
    """
    try:
        logger.info("Parsing feedback with AI", extra={"text_length": len(feedback_text)})
        
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes creative feedback."},
                {"role": "user", "content": FEEDBACK_PARSING_PROMPT.format(feedback_text=feedback_text)}
            ],
            max_tokens=settings.OPENAI_MAX_TOKENS,
            temperature=settings.OPENAI_TEMPERATURE,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        logger.info("Successfully parsed feedback", extra={"action_items": len(result.get("action_items", []))})
        
        return result
        
    except Exception as e:
        logger.error(f"Error parsing feedback: {str(e)}", exc_info=True)
        raise

def extract_action_items(parsed_feedback: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract action items from parsed feedback"""
    return parsed_feedback.get("action_items", [])

def get_sentiment(parsed_feedback: Dict[str, Any]) -> str:
    """Get sentiment from parsed feedback"""
    return parsed_feedback.get("sentiment", "neutral")

def get_priority(parsed_feedback: Dict[str, Any]) -> str:
    """Get priority from parsed feedback"""
    return parsed_feedback.get("priority", "medium")
''',

    # React Context
    "frontend/src/contexts/AuthContext.tsx": '''import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import * as authService from '../services/auth';

interface User {
  id: string;
  email: string;
  full_name?: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      authService.getCurrentUser()
        .then(setUser)
        .catch(() => localStorage.removeItem('access_token'))
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authService.login(email, password);
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);
    const userData = await authService.getCurrentUser();
    setUser(userData);
    navigate('/');
  };

  const register = async (email: string, password: string, fullName?: string) => {
    await authService.register(email, password, fullName);
    await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
''',

    # API Service
    "frontend/src/services/api.ts": '''import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
''',

    "frontend/src/services/auth.ts": '''import api from './api';

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export const login = async (email: string, password: string): Promise<LoginResponse> => {
  const response = await api.post('/auth/login', { email, password });
  return response.data;
};

export const register = async (email: string, password: string, full_name?: string): Promise<User> => {
  const response = await api.post('/auth/register', { email, password, full_name });
  return response.data;
};

export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get('/auth/me');
  return response.data;
};

export const logout = async (): Promise<void> => {
  await api.post('/auth/logout');
};
''',

    # React Pages
    "frontend/src/pages/Login.tsx": '''import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h2 className="text-3xl font-bold text-center">Sign In</h2>
        {error && <div className="bg-red-100 text-red-700 p-3 rounded">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border rounded-md"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border rounded-md"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700"
          >
            Sign In
          </button>
        </form>
        <p className="text-center">
          Don't have an account? <Link to="/register" className="text-blue-600">Sign Up</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
''',

    "frontend/src/pages/Register.tsx": '''import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const { register } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await register(email, password, fullName);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h2 className="text-3xl font-bold text-center">Sign Up</h2>
        {error && <div className="bg-red-100 text-red-700 p-3 rounded">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border rounded-md"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border rounded-md"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700"
          >
            Sign Up
          </button>
        </form>
        <p className="text-center">
          Already have an account? <Link to="/login" className="text-blue-600">Sign In</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
''',

    "frontend/src/pages/Dashboard.tsx": '''import React from 'react';
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
''',

    "frontend/src/pages/Projects.tsx": '''import React from 'react';

const Projects: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-6">Projects</h1>
      <p>Projects page coming soon...</p>
    </div>
  );
};

export default Projects;
''',

    "frontend/src/components/ProtectedRoute.tsx": '''import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
''',
}

def create_file(filepath: str, content: str):
    """Create a file with the given content"""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        f.write(content.lstrip())
    
    print(f"✓ Created: {filepath}")

def main():
    """Generate all final files"""
    print("Generating final components...")
    print("=" * 60)
    
    for filepath, content in FINAL_FILES.items():
        create_file(filepath, content)
    
    print("=" * 60)
    print(f"✓ Successfully created {len(FINAL_FILES)} files!")

if __name__ == "__main__":
    main()
