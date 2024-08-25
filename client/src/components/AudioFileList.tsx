import React, { useState, useEffect } from 'react';
import { getAudioFiles, downloadFile } from '../api';
import {
  Typography,
  List,
  ListItem,
  ListItemText,
  Button,
  Box,
  Container,
  Paper,
  useMediaQuery
} from '@mui/material';

interface AudioFile {
  id: string;
  file_name: string;
  creation_date: string;
}

const AudioFileList: React.FC = () => {
  const [audioFiles, setAudioFiles] = useState<AudioFile[]>([]);
  const isMobile = useMediaQuery('(max-width:600px)');

  useEffect(() => {
    const fetchAudioFiles = async () => {
      try {
        const files = await getAudioFiles();
        console.log("files", files);
        setAudioFiles(files);
      } catch (error) {
        console.error("Error fetching audio files:", error);
      }
    };
    fetchAudioFiles();
  }, []);

  const handleDownload = async (fileId: string) => {
    try {
      await downloadFile(fileId);
    } catch (error) {
      console.error("Error downloading file:", error);
    }
  };

  return (
      <Container maxWidth="sm" sx={{ py: 4 }}>
        <Paper
            elevation={3}
            sx={{
              background: 'linear-gradient(145deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.9) 100%)',
              borderRadius: '12px',
              padding: isMobile ? '16px' : '24px',
            }}
        >
          <Typography variant="h5" component="h2" gutterBottom>
            Audio Files
          </Typography>
          <List>
            {audioFiles.map((file) => (
                <ListItem
                    key={file.id}
                    sx={{
                      borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
                      '&:last-child': { borderBottom: 'none' },
                    }}
                >
                  <ListItemText
                      primary={file.file_name}
                      secondary={new Date(file.creation_date).toLocaleString()}
                  />
                  <Box>
                    <Button
                        variant="contained"
                        size="small"
                        onClick={() => handleDownload(file.id)}
                        sx={{
                          background: 'linear-gradient(145deg, rgba(25, 118, 210, 0.8) 0%, rgba(25, 118, 210, 0.9) 100%)',
                          transition: 'all 0.3s',
                          '&:hover': {
                            background: 'linear-gradient(145deg, rgba(25, 118, 210, 0.9) 0%, rgba(25, 118, 210, 1) 100%)',
                            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                          },
                        }}
                    >
                      Download
                    </Button>
                  </Box>
                </ListItem>
            ))}
          </List>
        </Paper>
      </Container>
  );
};

export default AudioFileList;