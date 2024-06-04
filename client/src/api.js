// src/api.js
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

export const processArticle = async (url) => {
  const response = await axios.post(`${API_URL}/process_article`, { url });
  return response.data;
};

export const getStatus = async (taskId) => {
  const response = await axios.get(`${API_URL}/status/${taskId}`);
  return response.data;
};

export const downloadFile = async (taskId) => {
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


