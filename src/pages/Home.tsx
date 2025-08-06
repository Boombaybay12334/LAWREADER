import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, MessageCircle, Scale, ArrowRight, Shield, Zap, Users } from 'lucide-react';

const Home: React.FC = () => {
  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <div className="text-center space-y-6">
        <div className="flex justify-center mb-6">
          <Scale className="h-16 w-16 text-blue-600" />
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight">
          Legal Document Analyzer
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
          Streamline your legal workflow with advanced document analysis and intelligent query processing. 
          Built for legal professionals who demand precision and efficiency.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
          <Link
            to="/pdf-analyzer"
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2 shadow-lg"
          >
            <FileText className="h-5 w-5" />
            <span>Analyze Documents</span>
          </Link>
          <Link
            to="/legal-query"
            className="bg-white text-blue-600 px-8 py-3 rounded-lg font-medium hover:bg-blue-50 transition-colors flex items-center justify-center space-x-2 border-2 border-blue-600"
          >
            <MessageCircle className="h-5 w-5" />
            <span>Ask Legal Questions</span>
          </Link>
        </div>
      </div>

      {/* Features Section */}
      <div className="grid md:grid-cols-2 gap-8">
        {/* PDF Analyzer Card */}
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-slate-200 hover:shadow-xl transition-shadow">
          <div className="flex items-center space-x-3 mb-6">
            <div className="bg-blue-100 p-3 rounded-lg">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">PDF Document Analyzer</h2>
          </div>
          <p className="text-gray-600 mb-6 leading-relaxed">
            Upload your legal documents and get comprehensive analysis with automated processing. 
            Our advanced algorithms extract key information and provide structured insights.
          </p>
          <ul className="space-y-3 mb-6">
            <li className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
              <span className="text-gray-700">Automated document processing</span>
            </li>
            <li className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
              <span className="text-gray-700">Key information extraction</span>
            </li>
            <li className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
              <span className="text-gray-700">Structured analysis reports</span>
            </li>
          </ul>
          <Link
            to="/pdf-analyzer"
            className="inline-flex items-center text-blue-600 font-medium hover:text-blue-700 transition-colors"
          >
            Get Started <ArrowRight className="h-4 w-4 ml-1" />
          </Link>
        </div>

        {/* Legal Query Card */}
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-slate-200 hover:shadow-xl transition-shadow">
          <div className="flex items-center space-x-3 mb-6">
            <div className="bg-green-100 p-3 rounded-lg">
              <MessageCircle className="h-6 w-6 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Legal Query System</h2>
          </div>
          <p className="text-gray-600 mb-6 leading-relaxed">
            Ask complex legal questions and receive detailed, researched answers based on our 
            comprehensive legal knowledge base and case law database.
          </p>
          <ul className="space-y-3 mb-6">
            <li className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-600 rounded-full"></div>
              <span className="text-gray-700">Comprehensive legal database</span>
            </li>
            <li className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-600 rounded-full"></div>
              <span className="text-gray-700">Case law references</span>
            </li>
            <li className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-600 rounded-full"></div>
              <span className="text-gray-700">Instant detailed responses</span>
            </li>
          </ul>
          <Link
            to="/legal-query"
            className="inline-flex items-center text-green-600 font-medium hover:text-green-700 transition-colors"
          >
            Ask a Question <ArrowRight className="h-4 w-4 ml-1" />
          </Link>
        </div>
      </div>

      {/* Benefits Section */}
      <div className="bg-white rounded-2xl shadow-lg p-8 border border-slate-200">
        <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">
          Why Choose Our Platform?
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-blue-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Shield className="h-8 w-8 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Secure & Reliable</h3>
            <p className="text-gray-600">
              Your documents are processed securely with enterprise-grade encryption and automatic cleanup.
            </p>
          </div>
          <div className="text-center">
            <div className="bg-green-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Zap className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Fast Processing</h3>
            <p className="text-gray-600">
              Get results in minutes, not hours. Our optimized processing pipeline ensures quick turnaround.
            </p>
          </div>
          <div className="text-center">
            <div className="bg-purple-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Users className="h-8 w-8 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Expert Support</h3>
            <p className="text-gray-600">
              Built by legal technology experts with deep understanding of legal workflows and requirements.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;