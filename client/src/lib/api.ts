import { useAuth0 } from '@auth0/auth0-react';

export function useApi() {
    const { getAccessTokenSilently } = useAuth0();
    const enableAuth = process.env.NEXT_PUBLIC_ENABLE_AUTH === 'true';

    const getHeaders = async () => {
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
        };

        if (enableAuth) {
            try {
                // Get the access token specifically
                const token = await getAccessTokenSilently({
                    authorizationParams: {
                        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
                    },
                });
                console.log('Token:', token);
                headers['Authorization'] = `Bearer ${token}`;
            } catch (error) {
                console.error('Error getting token:', error);
            }
        }

        return headers;
    };

    const convertArticle = async (url: string) => {
        const headers = await getHeaders();
        const response = await fetch('http://localhost:8080/convert', {
            method: 'POST',
            headers,
            body: JSON.stringify({ url }),
        });
        return response.json();
    };

    const listAudioFiles = async () => {
        const headers = await getHeaders();
        const response = await fetch('http://localhost:8080/audio-files', {
            headers,
        });
        return response.json();
    };

    return {
        convertArticle,
        listAudioFiles,
    };
}