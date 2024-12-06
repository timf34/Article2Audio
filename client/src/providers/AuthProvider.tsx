'use client'

import { Auth0Provider } from '@auth0/auth0-react';

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const enableAuth = process.env.NEXT_PUBLIC_ENABLE_AUTH === 'true';

    if (!enableAuth) {
        return <>{children}</>;
    }

    return (
        <Auth0Provider
            domain={process.env.NEXT_PUBLIC_AUTH0_DOMAIN || ''}
            clientId={process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID || ''}
            authorizationParams={{
                redirect_uri: typeof window !== 'undefined' ? window.location.origin : '',
                audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
                scope: 'openid profile email',
                response_type: 'token id_token',
            }}
        >
            {children}
        </Auth0Provider>
    );
}