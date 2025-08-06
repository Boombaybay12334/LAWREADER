import React from 'react';
import { CheckCircle, X } from 'lucide-react';

interface SuccessMessageProps {
  message: string;
  onClose?: () => void;
}

const SuccessMessage: React.FC<SuccessMessageProps> = ({ message, onClose }) => {
  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
      <div className="flex items-start">
        <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
        <div className="flex-1">
          <h3 className="text-sm font-medium text-green-800 mb-1">Success</h3>
          <p className="text-sm text-green-700">{message}</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-2 text-green-500 hover:text-green-700 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export default SuccessMessage;