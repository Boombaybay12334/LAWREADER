import React, { useState, useCallback } from 'react';
import { Upload, FileText, Download, X, CheckCircle } from 'lucide-react';
import { apiService } from '../services/api';
import { AnalysisResponse } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import SuccessMessage from '../components/SuccessMessage';

const PDFAnalyzer: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    setError(null);
    setSuccess(null);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'application/pdf') {
        setFile(droppedFile);
      } else {
        setError('Please upload a PDF file.');
      }
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    setSuccess(null);
    
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
      } else {
        setError('Please upload a PDF file.');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    setSuccess(null);
    setUploadProgress(0);

    try {
      const response = await apiService.uploadPDF(file, (progress) => {
        setUploadProgress(progress);
      });

      setResult(response);
      setSuccess('PDF processed successfully! You can now download the processed document.');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to process PDF. Please try again.';
      setError(errorMessage);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDownload = async () => {
    if (!result) return;

    try {
      const blob = await apiService.downloadProcessedFile(result.file_id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `processed_${result.file_id}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to download processed file.';
      setError(errorMessage);
    }
  };

  const clearFile = () => {
    setFile(null);
    setResult(null);
    setError(null);
    setSuccess(null);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <FileText className="h-12 w-12 text-blue-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900">PDF Document Analyzer</h1>
        <p className="text-lg text-gray-600">
          Upload your legal documents for comprehensive analysis and processing
        </p>
      </div>

      {/* Messages */}
      {error && <ErrorMessage message={error} onClose={() => setError(null)} />}
      {success && <SuccessMessage message={success} onClose={() => setSuccess(null)} />}

      {/* Upload Area */}
      <div className="bg-white rounded-2xl shadow-lg p-8 border border-slate-200">
        <div
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ${
            dragActive
              ? 'border-blue-400 bg-blue-50'
              : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {!file ? (
            <div className="space-y-4">
              <Upload className="h-12 w-12 text-gray-400 mx-auto" />
              <div>
                <p className="text-lg font-medium text-gray-900">Drop your PDF here</p>
                <p className="text-gray-600">or click to browse files</p>
              </div>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 cursor-pointer transition-colors"
              >
                Choose File
              </label>
              <p className="text-sm text-gray-500">Maximum file size: 10MB</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-center space-x-3">
                <FileText className="h-8 w-8 text-blue-600" />
                <div className="text-left">
                  <p className="font-medium text-gray-900">{file.name}</p>
                  <p className="text-sm text-gray-600">{formatFileSize(file.size)}</p>
                </div>
                <button
                  onClick={clearFile}
                  className="text-gray-400 hover:text-red-500 transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              {uploading ? (
                <div className="space-y-4">
                  <LoadingSpinner message="Processing your document..." />
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-gray-600">{uploadProgress}% uploaded</p>
                </div>
              ) : (
                <button
                  onClick={handleUpload}
                  className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                >
                  <Upload className="h-5 w-5 mr-2" />
                  Process Document
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-slate-200">
          <div className="flex items-center space-x-3 mb-6">
            <CheckCircle className="h-8 w-8 text-green-600" />
            <h2 className="text-2xl font-bold text-gray-900">Analysis Complete</h2>
          </div>
          
          <div className="space-y-4">
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-green-800 font-medium">{result.message}</p>
              <p className="text-green-600 text-sm mt-1">
                Processed at: {new Date(result.timestamp).toLocaleString()}
              </p>
            </div>
            
            <div className="flex justify-center">
              <button
                onClick={handleDownload}
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-green-600 hover:bg-green-700 transition-colors"
              >
                <Download className="h-5 w-5 mr-2" />
                Download Processed Document
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-blue-50 rounded-2xl p-8 border border-blue-200">
        <h3 className="text-xl font-bold text-blue-900 mb-4">How it works</h3>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="flex items-start space-x-3">
            <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold text-sm">
              1
            </div>
            <div>
              <h4 className="font-semibold text-blue-900">Upload Document</h4>
              <p className="text-blue-700 text-sm">Select or drag & drop your PDF document</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold text-sm">
              2
            </div>
            <div>
              <h4 className="font-semibold text-blue-900">Process & Analyze</h4>
              <p className="text-blue-700 text-sm">Our AI analyzes and processes your document</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold text-sm">
              3
            </div>
            <div>
              <h4 className="font-semibold text-blue-900">Download Results</h4>
              <p className="text-blue-700 text-sm">Get your processed document with insights</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PDFAnalyzer;