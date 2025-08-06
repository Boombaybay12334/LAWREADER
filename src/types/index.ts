export interface LegalQuery {
  question: string;
}

export interface QueryResponse {
  answer: string;
  timestamp: string;
  query_id: string;
}

export interface AnalysisResponse {
  message: string;
  file_id: string;
  timestamp: string;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}