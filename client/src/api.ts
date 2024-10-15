import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const apiClient = axios.create({
  baseURL: API_URL,
});

apiClient.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
);

export default apiClient;

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
  const response = await apiClient.post('/process_article', { url });
  return response.data;
};

export const getStatus = async (taskId: string): Promise<StatusResponse> => {
  const response = await apiClient.get(`/status/${taskId}`);
  return response.data;
};

export const getAudioFiles = async (): Promise<AudioFile[]> => {
  const response = await apiClient.get('/audio_files');
  return response.data;
};

export const getFeedUrl = async () => {
  const response = await apiClient.get('/get_feed_url');
  return response.data;
};

export const downloadFile = async (taskId: string) => {
    try {
        const response = await axios.get(`${API_URL}/download/${taskId}`, {
            responseType: 'blob',
        });
        console.log("response", response);

        const fileName = response.headers['content-disposition']
            .split('filename=')[1]
            .replace(/"/g, '');

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', fileName);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (error) {
        console.error("Error in downloadFile:", error);
        throw error;
    }
};


export const verifyToken = async (token: string) => {
  const response = await apiClient.post('/verify_token', { token });
  if (response.status !== 200) {
    throw new Error('Failed to verify token');
  }
  return response.data;
};
