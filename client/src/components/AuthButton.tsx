import { useAuth0 } from '@auth0/auth0-react';
import styles from './AuthButton.module.css';


export function AuthButton() {
    const { isAuthenticated, loginWithRedirect, logout, user } = useAuth0();
    const enableAuth = process.env.NEXT_PUBLIC_ENABLE_AUTH === 'true';

    if (!enableAuth) return null;

    if (isAuthenticated) {
        return (
            <div className={styles.authenticatedContainer}>
                <span className={styles.userInfo}>
                    {user?.name || user?.email}
                </span>
                <button
                    onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
                    className={styles.authButton} // Use scoped class name
                >
                    Logout
                </button>
            </div>
        );
    }

    return (
        <button
            onClick={() => loginWithRedirect()}
            className={styles.authButton} // Use scoped class name
        >
            Login
        </button>
    );
}
