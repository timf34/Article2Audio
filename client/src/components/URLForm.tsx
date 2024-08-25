import React, { useState } from 'react';
import { TextField, Button, Box } from '@mui/material';

interface URLFormProps {
    onSubmit: (url: string) => void;
}

const FORM_ELEMENT_HEIGHT = '36px';

const URLForm: React.FC<URLFormProps> = ({ onSubmit }) => {
    const [url, setUrl] = useState<string>('');

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        onSubmit(url);
    };

    return (
        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', gap: 2, maxWidth: '600px' }}>
            <TextField
                variant="outlined"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter URL"
                required
                fullWidth
                size="small"
                sx={{
                    flexGrow: 1,
                    '& .MuiOutlinedInput-root': {
                        height: FORM_ELEMENT_HEIGHT,
                    }
                }}
            />
            <Button
                type="submit"
                variant="contained"
                color="primary"
                sx={{ height: FORM_ELEMENT_HEIGHT, minWidth: '80px' }}
            >
                Submit
            </Button>
        </Box>
    );
};

export default URLForm;