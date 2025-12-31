/**
 * LoginScreen - Handles user authentication (login/signup)
 */
class LoginScreen {
    constructor(onAuthenticated) {
        this.onAuthenticated = onAuthenticated; // Callback when auth succeeds
        this.container = null;
        this.showingSignup = false;
    }

    /**
     * Render the login screen
     */
    render(parentElement) {
        this.container = document.createElement('div');
        this.container.id = 'login-screen';
        this.container.className = 'screen';

        this.container.innerHTML = `
            <div class="login-container">
                <div class="login-header">
                    <h1>⭐ STARWEB ⭐</h1>
                    <p class="tagline">Conquer the Galaxy</p>
                </div>

                <div class="login-form-container">
                    <!-- Login Form -->
                    <div id="login-form" class="auth-form">
                        <h2>Login</h2>
                        <div class="form-group">
                            <label for="login-username">Username</label>
                            <input type="text" id="login-username" class="form-input" autocomplete="username" autofocus>
                        </div>
                        <div class="form-group">
                            <label for="login-password">Password</label>
                            <input type="password" id="login-password" class="form-input" autocomplete="current-password">
                        </div>
                        <div class="form-error" id="login-error"></div>
                        <button id="login-submit-btn" class="btn btn-primary">Login</button>
                        <div class="form-footer">
                            <a href="#" id="show-signup-link">Don't have an account? Sign up</a>
                        </div>
                    </div>

                    <!-- Signup Form -->
                    <div id="signup-form" class="auth-form" style="display: none;">
                        <h2>Sign Up</h2>
                        <div class="form-group">
                            <label for="signup-username">Username</label>
                            <input type="text" id="signup-username" class="form-input" autocomplete="username">
                            <small>3-20 characters, letters, numbers, and underscores</small>
                        </div>
                        <div class="form-group">
                            <label for="signup-password">Password</label>
                            <input type="password" id="signup-password" class="form-input" autocomplete="new-password">
                            <small>At least 8 characters, must include letters and numbers</small>
                        </div>
                        <div class="form-group">
                            <label for="signup-password-confirm">Confirm Password</label>
                            <input type="password" id="signup-password-confirm" class="form-input" autocomplete="new-password">
                        </div>
                        <div class="form-group">
                            <label for="signup-email">Email (optional)</label>
                            <input type="email" id="signup-email" class="form-input" autocomplete="email">
                        </div>
                        <div class="form-error" id="signup-error"></div>
                        <button id="signup-submit-btn" class="btn btn-primary">Create Account</button>
                        <div class="form-footer">
                            <a href="#" id="show-login-link">Already have an account? Login</a>
                        </div>
                    </div>
                </div>

                <div class="login-footer">
                    <p>A strategic space conquest game</p>
                </div>
            </div>
        `;

        parentElement.appendChild(this.container);
        this.attachEventListeners();
    }

    /**
     * Attach event listeners to form elements
     */
    attachEventListeners() {
        // Login form submit
        const loginBtn = document.getElementById('login-submit-btn');
        loginBtn.addEventListener('click', () => this.handleLogin());

        const loginUsername = document.getElementById('login-username');
        const loginPassword = document.getElementById('login-password');

        loginUsername.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleLogin();
        });
        loginPassword.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleLogin();
        });

        // Signup form submit
        const signupBtn = document.getElementById('signup-submit-btn');
        signupBtn.addEventListener('click', () => this.handleSignup());

        const signupInputs = [
            document.getElementById('signup-username'),
            document.getElementById('signup-password'),
            document.getElementById('signup-password-confirm'),
            document.getElementById('signup-email')
        ];

        signupInputs.forEach(input => {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.handleSignup();
            });
        });

        // Toggle between login and signup
        document.getElementById('show-signup-link').addEventListener('click', (e) => {
            e.preventDefault();
            this.showSignupForm();
        });

        document.getElementById('show-login-link').addEventListener('click', (e) => {
            e.preventDefault();
            this.showLoginForm();
        });
    }

    /**
     * Show the signup form
     */
    showSignupForm() {
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('signup-form').style.display = 'block';
        document.getElementById('signup-username').focus();
        this.clearErrors();
        this.showingSignup = true;
    }

    /**
     * Show the login form
     */
    showLoginForm() {
        document.getElementById('signup-form').style.display = 'none';
        document.getElementById('login-form').style.display = 'block';
        document.getElementById('login-username').focus();
        this.clearErrors();
        this.showingSignup = false;
    }

    /**
     * Clear error messages
     */
    clearErrors() {
        document.getElementById('login-error').textContent = '';
        document.getElementById('signup-error').textContent = '';
    }

    /**
     * Handle login submission
     */
    async handleLogin() {
        this.clearErrors();

        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;

        if (!username || !password) {
            this.showError('login', 'Please enter both username and password');
            return;
        }

        // Disable button during request
        const btn = document.getElementById('login-submit-btn');
        btn.disabled = true;
        btn.textContent = 'Logging in...';

        try {
            // Send LOGIN message to server
            const message = {
                type: 'LOGIN',
                username: username,
                password: password
            };

            window.ws.send(JSON.stringify(message));

            // Response will be handled by message handler in main.js
        } catch (error) {
            this.showError('login', 'Connection error. Please try again.');
            btn.disabled = false;
            btn.textContent = 'Login';
        }
    }

    /**
     * Handle signup submission
     */
    async handleSignup() {
        this.clearErrors();

        const username = document.getElementById('signup-username').value.trim();
        const password = document.getElementById('signup-password').value;
        const passwordConfirm = document.getElementById('signup-password-confirm').value;
        const email = document.getElementById('signup-email').value.trim();

        // Validation
        if (!username || !password) {
            this.showError('signup', 'Please enter username and password');
            return;
        }

        if (password !== passwordConfirm) {
            this.showError('signup', 'Passwords do not match');
            return;
        }

        if (password.length < 8) {
            this.showError('signup', 'Password must be at least 8 characters');
            return;
        }

        if (!/[a-zA-Z]/.test(password) || !/\d/.test(password)) {
            this.showError('signup', 'Password must contain both letters and numbers');
            return;
        }

        // Disable button during request
        const btn = document.getElementById('signup-submit-btn');
        btn.disabled = true;
        btn.textContent = 'Creating account...';

        try {
            // Send SIGNUP message to server
            const message = {
                type: 'SIGNUP',
                username: username,
                password: password,
                email: email || undefined
            };

            window.ws.send(JSON.stringify(message));

            // Response will be handled by message handler in main.js
        } catch (error) {
            this.showError('signup', 'Connection error. Please try again.');
            btn.disabled = false;
            btn.textContent = 'Create Account';
        }
    }

    /**
     * Show error message
     */
    showError(formType, message) {
        const errorElement = document.getElementById(`${formType}-error`);
        errorElement.textContent = message;
    }

    /**
     * Handle authentication success
     */
    handleAuthSuccess(data) {
        // Store auth data in localStorage
        localStorage.setItem('starweb_token', data.token);
        localStorage.setItem('starweb_player_id', data.player_id);
        localStorage.setItem('starweb_username', data.username);

        // Call callback to transition to lobby
        if (this.onAuthenticated) {
            this.onAuthenticated(data);
        }
    }

    /**
     * Handle authentication error
     */
    handleAuthError(message) {
        const formType = this.showingSignup ? 'signup' : 'login';
        this.showError(formType, message);

        // Re-enable button
        const btnId = this.showingSignup ? 'signup-submit-btn' : 'login-submit-btn';
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.disabled = false;
            btn.textContent = this.showingSignup ? 'Create Account' : 'Login';
        }
    }

    /**
     * Remove the screen from DOM
     */
    destroy() {
        if (this.container && this.container.parentElement) {
            this.container.parentElement.removeChild(this.container);
        }
        this.container = null;
    }

    /**
     * Check if user has saved session
     */
    static hasSavedSession() {
        return !!localStorage.getItem('starweb_token');
    }

    /**
     * Get saved session data
     */
    static getSavedSession() {
        return {
            token: localStorage.getItem('starweb_token'),
            player_id: localStorage.getItem('starweb_player_id'),
            username: localStorage.getItem('starweb_username')
        };
    }

    /**
     * Clear saved session
     */
    static clearSavedSession() {
        localStorage.removeItem('starweb_token');
        localStorage.removeItem('starweb_player_id');
        localStorage.removeItem('starweb_username');
    }
}
