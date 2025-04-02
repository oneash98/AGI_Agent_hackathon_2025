export interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  files?: File[];
}

export interface AnalysisFile {
  id: number;
  name: string;
  size: number;
  type: string;
  uploadedAt: Date;
}

export interface DummyResponse {
  question: string;
  response: string;
} 