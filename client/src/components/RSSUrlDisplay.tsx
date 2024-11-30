import React, { useState, useEffect } from 'react';
import { getFeedUrl } from '../api'; // Adjust the import path based on your project structure
import { Button, TextField, Box } from '@mui/material'; // Assuming you're using Material-UI

const RSSUrlDisplay: React.FC = () => {
  const [rssUrl, setRssUrl] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const fetchRssUrl = async () => {
      try {
        const response = await getFeedUrl();
        setRssUrl(response.feed_url);
      } catch (error) {
        console.error('Error fetching RSS feed URL:', error);
      }
    };
    fetchRssUrl();
  }, []);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(rssUrl).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <Box sx={{ mt: 4 }}>
      <p>Your RSS Feed URL:</p>
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <TextField
          value={rssUrl}
          variant="outlined"
          fullWidth
          InputProps={{
            readOnly: true,
          }}
        />
        <Button
          onClick={copyToClipboard}
          variant="contained"
          color="primary"
          sx={{ ml: 2 }}
        >
          {copied ? 'Copied!' : 'Copy'}
        </Button>
      </Box>
    </Box>
  );
};

export default RSSUrlDisplay;
