'use client'

import { useAuth0 } from '@auth0/auth0-react'
import { AuthButton } from './AuthButton'
import styles from './NavBar.module.css'

export function NavBar() {
    const { isAuthenticated } = useAuth0()

    return (
        <nav className={styles.navbar}>
            <div className={styles.logo}>article2audio</div>
            {isAuthenticated && (
                <div className={styles.authContainer}>
                    <AuthButton />
                </div>
            )}
        </nav>
    )
}