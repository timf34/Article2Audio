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
            <Container maxWidth="md" sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ flex: 1 }}>
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
                <Button
                    color="inherit"
                    onClick={onSignOut}
                    sx={{
                        backgroundColor: 'rgba(255,255,255,0.1)',
                        '&:hover': {
                            backgroundColor: 'rgba(255,255,255,0.2)',
                        },
                    }}
                >
                    Sign Out
                </Button>
            </Container>
        </Box>
    );
};

export default Header;