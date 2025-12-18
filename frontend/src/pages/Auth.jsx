import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Auth.css';

function Auth() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    firstname: '',
    lastname: '',
    companyName: '',
    email: '',
    password: '',
    repeatPassword: ''
  });

  const [emailValid, setEmailValid] = useState(null);
  const [passwordStrength, setPasswordStrength] = useState({
    isValid: false,
    message: '',
    strength: 'weak',
    checks: {
      length: false,
      uppercase: false,
      lowercase: false,
      number: false,
      special: false
    }
  });
  const [passwordsMatch, setPasswordsMatch] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Email validation - string@string.string
  const validateEmail = (email) => {
    if (!email) {
      setEmailValid(null);
      return false;
    }

    // Check format: has @, has string after @, has at least one dot after @, has string after dot
    const parts = email.split('@');
    if (parts.length !== 2 || !parts[0] || !parts[1]) {
      setEmailValid(false);
      return false;
    }

    const afterAt = parts[1];
    const dotParts = afterAt.split('.');
    if (dotParts.length < 2 || !dotParts[0] || !dotParts[dotParts.length - 1]) {
      setEmailValid(false);
      return false;
    }

    setEmailValid(true);
    return true;
  };

  // Password strength validation
  const checkPasswordStrength = (password) => {
    if (!password) {
      setPasswordStrength({
        isValid: false,
        message: '',
        strength: 'weak',
        checks: {
          length: false,
          uppercase: false,
          lowercase: false,
          number: false,
          special: false
        }
      });
      return;
    }

    const checks = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /[0-9]/.test(password),
      special: /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)
    };

    const passedChecks = Object.values(checks).filter(Boolean).length;
    const isValid = Object.values(checks).every(Boolean);

    let strength = 'weak';
    let message = '';

    if (!checks.length) {
      message = 'Password must be at least 8 characters long';
    } else if (!checks.uppercase) {
      message = 'Password must contain at least 1 uppercase letter (A-Z)';
    } else if (!checks.lowercase) {
      message = 'Password must contain at least 1 lowercase letter (a-z)';
    } else if (!checks.number) {
      message = 'Password must contain at least 1 number (0-9)';
    } else if (!checks.special) {
      message = 'Password must contain at least 1 special character (!@#$%^&*()_+-=[]{}|;:,.<>?)';
    } else {
      message = 'Strong password!';
      strength = 'strong';
    }

    if (passedChecks >= 4 && !isValid) {
      strength = 'medium';
    }

    setPasswordStrength({
      isValid,
      message,
      strength,
      checks
    });
  };

  // Password match validation
  const checkPasswordsMatch = (password, repeatPassword) => {
    if (!repeatPassword) {
      setPasswordsMatch(null);
      return false;
    }

    const match = password === repeatPassword;
    setPasswordsMatch(match);
    return match;
  };

  // Handle form field changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    // Real-time validation
    if (name === 'email') {
      validateEmail(value);
    } else if (name === 'password') {
      checkPasswordStrength(value);
      if (formData.repeatPassword) {
        checkPasswordsMatch(value, formData.repeatPassword);
      }
    } else if (name === 'repeatPassword') {
      checkPasswordsMatch(formData.password, value);
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate email
    if (!validateEmail(formData.email)) {
      setError('Please enter a valid email address');
      return;
    }

    // Validate password strength
    if (!passwordStrength.isValid) {
      setError('Please use a stronger password that meets all requirements');
      return;
    }

    // Validate passwords match
    if (!checkPasswordsMatch(formData.password, formData.repeatPassword)) {
      setError('Passwords do not match');
      return;
    }

    // Validate required fields
    if (!formData.firstname || !formData.lastname || !formData.companyName) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          firstname: formData.firstname,
          lastname: formData.lastname,
          email: formData.email,
          password: formData.password,
          company_name: formData.companyName
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed');
      }

      // Store token and user data
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      // Redirect to dashboard
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle cancel
  const handleCancel = () => {
    navigate(-1); // Go back to previous route
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Sign Up</h1>
        <p className="auth-subtitle">Create your account to get started</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="firstname">First Name *</label>
              <input
                type="text"
                id="firstname"
                name="firstname"
                value={formData.firstname}
                onChange={handleChange}
                required
                maxLength={64}
              />
            </div>

            <div className="form-group">
              <label htmlFor="lastname">Last Name *</label>
              <input
                type="text"
                id="lastname"
                name="lastname"
                value={formData.lastname}
                onChange={handleChange}
                required
                maxLength={64}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="companyName">Company Name *</label>
            <input
              type="text"
              id="companyName"
              name="companyName"
              value={formData.companyName}
              onChange={handleChange}
              required
              maxLength={255}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              maxLength={64}
              className={emailValid === false ? 'invalid' : emailValid === true ? 'valid' : ''}
            />
            {emailValid === false && (
              <div className="validation-message error">
                Invalid email format. Use: yourname@example.com
              </div>
            )}
            {emailValid === true && (
              <div className="validation-message success">
                ✓ Valid email format
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="password">Password *</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
            />
            {/* Reserved space for password strength indicator */}
            <div className="password-strength-container">
              {formData.password && (
                <>
                  <div className={`strength-bar strength-${passwordStrength.strength}`}>
                    <div className="strength-fill"></div>
                  </div>
                  <div className="strength-checklist">
                    <div className={passwordStrength.checks.length ? 'check-passed' : 'check-failed'}>
                      {passwordStrength.checks.length ? '✓' : '○'} At least 8 characters
                    </div>
                    <div className={passwordStrength.checks.uppercase ? 'check-passed' : 'check-failed'}>
                      {passwordStrength.checks.uppercase ? '✓' : '○'} One uppercase letter
                    </div>
                    <div className={passwordStrength.checks.lowercase ? 'check-passed' : 'check-failed'}>
                      {passwordStrength.checks.lowercase ? '✓' : '○'} One lowercase letter
                    </div>
                    <div className={passwordStrength.checks.number ? 'check-passed' : 'check-failed'}>
                      {passwordStrength.checks.number ? '✓' : '○'} One number
                    </div>
                    <div className={passwordStrength.checks.special ? 'check-passed' : 'check-failed'}>
                      {passwordStrength.checks.special ? '✓' : '○'} One special character
                    </div>
                  </div>
                </>
              )}
              {!formData.password && (
                <div className="strength-placeholder">
                  Password strength will be displayed here
                </div>
              )}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="repeatPassword">Repeat Password *</label>
            <input
              type="password"
              id="repeatPassword"
              name="repeatPassword"
              value={formData.repeatPassword}
              onChange={handleChange}
              required
              minLength={8}
              className={passwordsMatch === false ? 'invalid' : passwordsMatch === true ? 'valid' : ''}
            />
            {/* Reserved space for password match indicator */}
            <div className="password-match-container">
              {formData.repeatPassword && (
                <div className={`validation-message ${passwordsMatch ? 'success' : 'error'}`}>
                  {passwordsMatch ? '✓ Passwords match' : '✗ Passwords do not match'}
                </div>
              )}
              {!formData.repeatPassword && (
                <div className="match-placeholder">
                  Password match status will be displayed here
                </div>
              )}
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={handleCancel}
              className="btn btn-secondary"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !emailValid || !passwordStrength.isValid || !passwordsMatch}
            >
              {loading ? 'Signing Up...' : 'Sign Up'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Auth;
