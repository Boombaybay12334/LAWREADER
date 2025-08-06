import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Scale, FileText, MessageCircle, Home } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <nav className="bg-white shadow-lg border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-3">
              <Scale className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">
                Legal Document Analyzer
              </span>
            </Link>

            <div className="flex space-x-1">
              <Link
                to="/"
                className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition-all duration-200 ${
                  isActive('/')
                    ? 'bg-blue-100 text-blue-700 font-medium'
                    : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
                }`}
              >
                <Home className="h-4 w-4" />
                <span>Home</span>
              </Link>

              <Link
                to="/pdf-analyzer"
                className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition-all duration-200 ${
                  isActive('/pdf-analyzer')
                    ? 'bg-blue-100 text-blue-700 font-medium'
                    : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
                }`}
              >
                <FileText className="h-4 w-4" />
                <span>PDF Analyzer</span>
              </Link>

              <Link
                to="/legal-query"
                className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition-all duration-200 ${
                  isActive('/legal-query')
                    ? 'bg-blue-100 text-blue-700 font-medium'
                    : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
                }`}
              >
                <MessageCircle className="h-4 w-4" />
                <span>Legal Query</span>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      <footer className="bg-white border-t border-slate-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Scale className="h-6 w-6 text-blue-600" />
              <span className="text-gray-600">Legal Document Analyzer</span>
            </div>
            <div className="text-sm text-gray-500">
              © 2024 Legal Document Analyzer. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;