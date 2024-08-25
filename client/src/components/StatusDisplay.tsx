import React, { useState, useEffect } from 'react';
import { Box, Typography, LinearProgress, Paper, Container } from '@mui/material';

interface StatusDisplayProps {
    status: string;
    estimatedTime: number;
}

const StatusDisplay: React.FC<StatusDisplayProps> = ({ status, estimatedTime }) => {
    const [displayTime, setDisplayTime] = useState<number>(estimatedTime);

    useEffect(() => {
        if ((status === 'Creating audio file...') && estimatedTime > 0) {
            setDisplayTime(estimatedTime);
            const countdown = setInterval(() => {
                setDisplayTime((prevTime) => prevTime > 1 ? prevTime - 1 : 0);
            }, 1000);
            return () => clearInterval(countdown);
        }
    }, [status, estimatedTime]);

    const getStatusColor = () => {
        switch (status) {
            case 'Submitting...': return 'info.main';
            case 'Processing...':
            case 'Creating audio file...': return 'warning.main';
            case 'completed': return 'success.main';
            default: return 'text.primary';
        }
    };

    return (
        <Container maxWidth="sm">
            <Paper
                elevation={3}
                sx={{
                    mt: 2,
                    mb: 2,
                    p: 2,
                    borderRadius: '12px',
                    boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .1)',
                    maxWidth: '600px',
                    margin: '0 auto',
                }}
            >
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Typography variant="body1" color={getStatusColor()} sx={{ fontWeight: 'medium' }}>
                        Status: {status}
                    </Typography>
                    {(status === 'Creating audio file...') && (
                        <Typography variant="body2" color="text.secondary">
                            {displayTime > 0 ? `${displayTime}s` : 'Almost done!'}
                        </Typography>
                    )}
                </Box>
                {(status === 'Creating audio file...') && (
                    <LinearProgress
                        variant="determinate"
                        value={((estimatedTime - displayTime) / estimatedTime) * 100}
                        sx={{ mt: 1, height: 4, borderRadius: 2 }}
                    />
                )}
            </Paper>
        </Container>
    );
};

export default StatusDisplay;