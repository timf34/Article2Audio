// src/components/Header.tsx
import React from 'react';
import { Typography, Box, Container } from '@mui/material';

const Header: React.FC = () => {
    return (
        <Box
            sx={{
                background: 'linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%)',
                marginBottom: 2,
                padding: 2,
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            }}
        >
            <Container maxWidth="sm">
                <Typography variant="h4" component="h1" sx={{
                    fontWeight: 'bold',
                    color: 'white',
                    textAlign: 'center',
                    textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
                }}>
                    Article to Audio
                </Typography>
                <Typography variant="subtitle2" sx={{
                    color: 'rgba(255,255,255,0.9)',
                    textAlign: 'center',
                    mt: 1,
                    fontSize: '0.9rem',
                    letterSpacing: '0.5px',
                }}>
                    URL → audio file → podcast app!
                </Typography>
            </Container>
        </Box>
    );
};

export default Header;