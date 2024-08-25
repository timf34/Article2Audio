import React, { useState } from 'react';
import { TextField, Button, Box, Container, useMediaQuery } from '@mui/material';

interface URLFormProps {
    onSubmit: (url: string) => void;
}

// Constants for element heights
const DESKTOP_HEIGHT = '50px';
const MOBILE_HEIGHT = '36px';

const URLForm: React.FC<URLFormProps> = ({ onSubmit }) => {
    const [url, setUrl] = useState<string>('');
    const isMobile = useMediaQuery('(max-width:600px)');

    const elementHeight = isMobile ? MOBILE_HEIGHT : DESKTOP_HEIGHT;

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        onSubmit(url);
    };

    return (
        <Container maxWidth="sm" sx={{ py: 4 }}>
            <Box
                sx={{
                    background: 'linear-gradient(145deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.9) 100%)',
                    borderRadius: '12px',
                    padding: isMobile ? '16px' : '24px',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)',
                }}
            >
                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <TextField
                        fullWidth
                        variant="outlined"
                        label="Article URL"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="https://example.com/article"
                        sx={{
                            '& .MuiOutlinedInput-root': {
                                height: elementHeight,
                                '& fieldset': {
                                    borderColor: 'rgba(25, 118, 210, 0.3)',
                                },
                                '&:hover fieldset': {
                                    borderColor: 'rgba(25, 118, 210, 0.5)',
                                },
                                '&.Mui-focused fieldset': {
                                    borderColor: '#1976d2',
                                },
                            },
                        }}
                    />
                    <Button
                        type="submit"
                        variant="contained"
                        fullWidth
                        sx={{
                            height: elementHeight,
                            background: 'linear-gradient(145deg, rgba(25, 118, 210, 0.8) 0%, rgba(25, 118, 210, 0.9) 100%)',
                            transition: 'all 0.3s',
                            '&:hover': {
                                background: 'linear-gradient(145deg, rgba(25, 118, 210, 0.9) 0%, rgba(25, 118, 210, 1) 100%)',
                                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                            },
                        }}
                    >
                        Convert to Audio
                    </Button>
                </form>
            </Box>
        </Container>
    );
};

export default URLForm;