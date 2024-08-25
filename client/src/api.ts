import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

interface ProcessArticleResponse {
  task_id: string;
  estimated_time: number;
}

interface StatusResponse {
  status: string;
}

interface AudioFile {
  id: string;
  file_name: string;
  creation_date: string;
}

export const processArticle = async (url: string): Promise<ProcessArticleResponse> => {
  const response = await axios.post(`${API_URL}/process_article`, { url });
  return response.data;
};

export const getStatus = async (taskId: string): Promise<StatusResponse> => {
  const response = await axios.get(`${API_URL}/status/${taskId}`);
  return response.data;
};

export const downloadFile = async (taskId: string): Promise<void> => {
  // ... (same as before)
};

export const getAudioFiles = async (): Promise<AudioFile[]> => {
  const response = await axios.get(`${API_URL}/audio_files`);
  return response.data;
};