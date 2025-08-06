import React, { useState } from 'react';
import { MessageCircle, Send, Clock, User, Bot } from 'lucide-react';
import { apiService } from '../services/api';
import { LegalQuery, QueryResponse } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

interface QueryHistoryItem extends QueryResponse {
  question: string;
}

const LegalQueryPage: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<QueryHistoryItem[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!question.trim()) {
      setError('Please enter a question.');
      return;
    }

    if (question.length > 1000) {
      setError('Question is too long. Maximum 1000 characters allowed.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const query: LegalQuery = { question: question.trim() };
      const response = await apiService.processLegalQuery(query);
      console.log("Raw response from backend:", response);
      console.log("Parsed keys:", Object.keys(response));
      console.log("Raw answer content:", response.answer);

      
      const historyItem: QueryHistoryItem = {
        ...response,
        question: question.trim(),
      };
      
      setHistory(prev => [historyItem, ...prev]);
      setQuestion('');
    } catch (err: any) {
      console.error("Error in API call:", err);
      const errorMessage = err.response?.data?.detail ||err.message ||'Failed to process query. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const exampleQuestions = [
    "A journalist is arrested for tweeting criticism of a Chief Minister. Does this violate freedom of speech under Article 19(1)(a)?",
    "Police enter a person’s home without a warrant claiming suspicion of illegal activity. Is this a breach of their right to privacy?",
    "A school denies admission to a child because their parents belong to a lower caste. Is this a violation of Article 15?",
    "A Muslim woman challenges a triple talaq divorce issued via WhatsApp. What constitutional rights are involved?",
    "The government shuts down internet services during a protest. Can this be challenged under any fundamental right?",
  ];

  const handleExampleClick = (exampleQuestion: string) => {
    setQuestion(exampleQuestion);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <MessageCircle className="h-12 w-12 text-blue-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900">Legal Query System</h1>
        <p className="text-lg text-gray-600">
          Ask complex legal questions and get detailed, researched answers
        </p>
      </div>

      {/* Query Form */}
      <div className="bg-white rounded-2xl shadow-lg p-8 border border-slate-200">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
              Your Legal Question
            </label>
            <textarea
              id="question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Enter your legal question here..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={4}
              maxLength={1000}
            />
            <div className="flex justify-between items-center mt-2">
              <p className="text-sm text-gray-500">
                {question.length}/1000 characters
              </p>
              <button
                type="submit"
                disabled={loading || !question.trim()}
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span className="ml-2">Processing...</span>
                  </>
                ) : (
                  <>
                    <Send className="h-5 w-5 mr-2" />
                    Submit Query
                  </>
                )}
              </button>
            </div>
          </div>
        </form>

        {error && (
          <div className="mt-4">
            <ErrorMessage message={error} onClose={() => setError(null)} />
          </div>
        )}
      </div>

      {/* Example Questions */}
      {history.length === 0 && (
        <div className="bg-blue-50 rounded-2xl p-8 border border-blue-200">
          <h3 className="text-xl font-bold text-blue-900 mb-4">Example Questions</h3>
          <div className="space-y-2">
            {exampleQuestions.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(example)}
                className="block w-full text-left p-3 text-blue-700 hover:bg-blue-100 rounded-lg transition-colors"
              >
                "{example}"
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Query History */}
      {history.length > 0 && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900">Query History</h2>
          
          {history.map((item, index) => (
            <div key={item.query_id} className="bg-white rounded-2xl shadow-lg border border-slate-200 overflow-hidden">
              {/* Question */}
              <div className="bg-gray-50 p-6 border-b border-gray-200">
                <div className="flex items-start space-x-3">
                  <div className="bg-blue-100 p-2 rounded-lg">
                    <User className="h-5 w-5 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="font-medium text-gray-900">Your Question</span>
                      <span className="text-sm text-gray-500">
                        <Clock className="h-4 w-4 inline mr-1" />
                        {formatTimestamp(item.timestamp)}
                      </span>
                    </div>
                    <p className="text-gray-700">{item.question}</p>
                  </div>
                </div>
              </div>

              {/* Answer */}
              <div className="p-6">
                <div className="flex items-start space-x-3">
                  <div className="bg-green-100 p-2 rounded-lg">
                    <Bot className="h-5 w-5 text-green-600" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-3">
                      <span className="font-medium text-gray-900">Legal Analysis</span>
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                        Query ID: {item.query_id.slice(0, 8)}...
                      </span>
                    </div>
                    <div className="prose prose-sm max-w-none">
                      <p className="text-gray-700 whitespace-pre-wrap">{item.answer}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Instructions */}
      <div className="bg-amber-50 rounded-2xl p-8 border border-amber-200">
        <h3 className="text-xl font-bold text-amber-900 mb-4">Important Notice</h3>
        <div className="space-y-3 text-amber-800">
          <p>
            <strong>For Educational Purposes:</strong> This system provides general legal information for educational purposes only.
          </p>
          <p>
            <strong>Not Legal Advice:</strong> The responses are not intended as legal advice and should not be relied upon for legal decisions.
          </p>
          <p>
            <strong>Consult an Attorney:</strong> For specific legal issues, please consult with a qualified attorney in your jurisdiction.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LegalQueryPage;