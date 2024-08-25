import React from 'react';
import { Typography, Box, Container } from '@mui/material';
import { SvgIcon } from '@mui/material';

const Header: React.FC = () => {
    return (
        <Box
            sx={{
                background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
                marginBottom: 4,
                padding: 4,
                boxShadow: '0 3px 5px 2px rgba(255, 105, 135, .3)',
            }}
        >
            <Container maxWidth="sm">
                <Box display="flex" alignItems="center" justifyContent="center">
                    <SvgIcon sx={{ fontSize: 40, marginRight: 2 }}>
                        <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z" />
                    </SvgIcon>
                    <Typography variant="h3" component="h1" sx={{
                        fontWeight: 'bold',
                        color: 'white',
                        textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
                    }}>
                        Article to Audio
                    </Typography>
                </Box>
                <Typography variant="subtitle1" align="center" sx={{ mt: 2, color: 'white' }}>
                    Convert your favorite articles into audio files
                </Typography>
            </Container>
        </Box>
    );
};

export default Header;