import React, { useState, useEffect } from 'react';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { ThemeProvider, createTheme, CssBaseline, Container, Box } from '@mui/material';
import URLForm from './components/URLForm';
import StatusDisplay from './components/StatusDisplay';
import AudioFileList from './components/AudioFileList';
import Header from './components/Header';
import LoginPage from './components/LoginPage';
import { processArticle, getStatus, verifyToken } from './api';

const theme = createTheme({
  palette: {
    primary: {
      main: '#3a7bd5',
    },
    secondary: {
      main: '#00d2ff',
    },
  },
});

const App: React.FC = () => {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('');
  const [estimatedTime, setEstimatedTime] = useState<number>(0);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      verifyToken(token).then(setUser).catch(() => localStorage.removeItem('token'));
    }
  }, []);

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

  const handleLogin = async (credentialResponse: any) => {
    try {
      if (credentialResponse.credential) {
        const response = await verifyToken(credentialResponse.credential);
        setUser(response);
        localStorage.setItem('token', credentialResponse.credential);
      } else {
        console.error("No credential in the response");
      }
    } catch (error) {
      console.error("Error verifying token:", error);
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('token');
  };

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
      <GoogleOAuthProvider clientId="213491127239-lssh5snpejuob32apcpjecnvf1i7ceng.apps.googleusercontent.com">
        <ThemeProvider theme={theme}>
          <CssBaseline />
          {user ? (
              <Box sx={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
                <Header onSignOut={handleLogout} />
                <Container maxWidth="md" sx={{ pt: 4, pb: 4 }}>
                  <URLForm onSubmit={handleSubmit} />
                  <StatusDisplay status={status} estimatedTime={estimatedTime} />
                  <AudioFileList />
                </Container>
              </Box>
          ) : (
              <LoginPage onLogin={handleLogin} />
          )}
        </ThemeProvider>
      </GoogleOAuthProvider>
  );
};

export default App;