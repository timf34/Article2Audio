import { useAuth0 } from '@auth0/auth0-react';

export function AuthButton() {
    const { isAuthenticated, loginWithRedirect, logout, user } = useAuth0();
    const enableAuth = process.env.NEXT_PUBLIC_ENABLE_AUTH === 'true';

    if (!enableAuth) return null;

    if (isAuthenticated) {
        return (
            <div className="flex items-center gap-4">
                <span className="text-sm text-gray-700 font-semibold">
                    {user?.name || user?.email}
                </span>
                <button
                    onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
                    className="px-4 py-2 text-sm bg-red-500 text-white rounded hover:bg-red-600"
                >
                    Logout
                </button>
            </div>
        );
    }

    return (
        <button
            onClick={() => loginWithRedirect()}
            className="px-4 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
        >
            Login
        </button>
    );
}
