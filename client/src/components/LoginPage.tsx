import React from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { Typography, Box, Container, Paper } from '@mui/material';

interface LoginPageProps {
    onLogin: (credentialResponse: any) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
    return (
        <Box
            sx={{
                minHeight: '100vh',
                display: 'flex',
                flexDirection: 'column',
                background: 'linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%)',
            }}
        >
            <Container maxWidth="sm" sx={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <Paper elevation={6} sx={{ padding: 4, borderRadius: 2 }}>
                    <Box sx={{ textAlign: 'center', mb: 4 }}>
                        <img src="/article2audio_logo.png" alt="Article2Audio Logo" style={{ width: '80px', height: '80px', marginBottom: '16px' }} />
                        <Typography variant="h4" component="h1" sx={{
                            fontWeight: 'bold',
                            color: '#3a7bd5',
                            textShadow: '1px 1px 2px rgba(0,0,0,0.1)',
                        }}>
                            Article to Audio
                        </Typography>
                        <Typography variant="subtitle1" sx={{
                            color: 'rgba(0,0,0,0.6)',
                            mt: 1,
                            letterSpacing: '0.5px',
                        }}>
                            URL → audio file → podcast app!
                        </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
                        <GoogleLogin
                            onSuccess={onLogin}
                            onError={() => console.log('Login Failed')}
                            useOneTap
                            shape="rectangular"
                            theme="filled_blue"
                            size="large"
                            text="continue_with"
                            width="100%"
                        />
                    </Box>

                    <Typography variant="body2" align="center" color="textSecondary">
                        By logging in, you agree to our{' '}
                        <a href="/terms-of-service.html" style={{ color: '#3a7bd5' }}>Terms of Service</a>
                        {' '}and{' '}
                        <a href="/privacy-policy.html" style={{ color: '#3a7bd5' }}>Privacy Policy</a>.
                    </Typography>
                </Paper>
            </Container>
        </Box>
    );
};

export default LoginPage;