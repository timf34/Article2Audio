import React from 'react';
import { Typography, Box, Container, Button } from '@mui/material';

interface HeaderProps {
    onSignOut: () => void;
}

const Header: React.FC<HeaderProps> = ({ onSignOut }) => {
    return (
        <Box
            sx={{
                background: 'linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%)',
                marginBottom: 2,
                padding: 2,
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            }}
        >
            <Container maxWidth="md">
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{ flex: 1 }} /> {/* Left spacer */}
                    <Box sx={{ flex: 2, textAlign: 'center' }}> {/* Centered content */}
                        <Typography variant="h4" component="h1" sx={{
                            fontWeight: 'bold',
                            color: 'white',
                            textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
                        }}>
                            Article to Audio
                        </Typography>
                        <Typography variant="subtitle2" sx={{
                            color: 'rgba(255,255,255,0.9)',
                            mt: 1,
                            fontSize: '0.9rem',
                            letterSpacing: '0.5px',
                        }}>
                            URL → audio file → podcast app!
                        </Typography>
                    </Box>
                    <Box sx={{ flex: 1, display: 'flex', justifyContent: 'flex-end' }}> {/* Right-aligned button */}
                        <Button
                            color="inherit"
                            onClick={onSignOut}
                            sx={{
                                backgroundColor: 'rgba(255,255,255,0.4)',
                                '&:hover': {
                                    backgroundColor: 'rgba(255,255,255,0.7)',
                                },
                            }}
                        >
                            Sign Out
                        </Button>
                    </Box>
                </Box>
            </Container>
        </Box>
    );
};

export default Header;