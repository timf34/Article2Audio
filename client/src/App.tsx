import React, { useState, useEffect } from 'react';
import { Container, Typography, Box } from '@mui/material';
import URLForm from './components/URLForm';
import StatusDisplay from './components/StatusDisplay';
import AudioFileList from './components/AudioFileList';
import { processArticle, getStatus } from './api';

const App: React.FC = () => {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('');
  const [estimatedTime, setEstimatedTime] = useState<number>(0);

  useEffect(() => {
    if (taskId) {
      const interval = setInterval(async () => {
        try {
          const statusResponse = await getStatus(taskId);
          setStatus(statusResponse.status);
          if (statusResponse.status === 'completed') {
            clearInterval(interval);
          }
        } catch (error) {
          console.error("Error fetching status:", error);
          clearInterval(interval);
        }
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [taskId]);

  const handleSubmit = async (url: string) => {
    setStatus('Submitting...');
    try {
      const response = await processArticle(url);
      setTaskId(response.task_id);
      setEstimatedTime(response.estimated_time);
      setStatus('Processing...');
    } catch (error) {
      console.error("Error in handleSubmit:", error);
      setStatus('Failed to submit URL.');
    }
  };

  return (
    <Container maxWidth="md">
      <Box my={4}>
        <Typography variant="h3" component="h1" gutterBottom>
          Article to Audio Converter
        </Typography>
        <URLForm onSubmit={handleSubmit} />
        <StatusDisplay status={status} estimatedTime={estimatedTime} />
        <AudioFileList />
      </Box>
    </Container>
  );
};

export default App;