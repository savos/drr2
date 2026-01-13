import { useState, useEffect } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';

function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const [passwordStrength, setPasswordStrength] = useState({
    isValid: false,
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

  // Verify token on mount
  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setTokenValid(false);
        setVerifying(false);
        return;
      }

      try {
        const response = await fetch(`/api/auth/verify-reset-token?token=${encodeURIComponent(token)}`);
        const data = await response.json();
        setTokenValid(data.valid);
      } catch (err) {
        setTokenValid(false);
      } finally {
        setVerifying(false);
      }
    };

    verifyToken();
  }, [token]);

  // Password strength validation
  const checkPasswordStrength = (password) => {
    if (!password) {
      setPasswordStrength({
        isValid: false,
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
    if (passedChecks >= 4 && !isValid) {
      strength = 'medium';
    } else if (isValid) {
      strength = 'strong';
    }

    setPasswordStrength({ isValid, strength, checks });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');

    if (name === 'password') {
      checkPasswordStrength(value);
      if (formData.confirmPassword) {
        setPasswordsMatch(value === formData.confirmPassword);
      }
    } else if (name === 'confirmPassword') {
      setPasswordsMatch(formData.password === value);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!passwordStrength.isValid) {
      setError('Please use a stronger password that meets all requirements');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          password: formData.password
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(true);
      } else {
        setError(data.detail || 'Failed to reset password');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Loading state
  if (verifying) {
    return (
      <div className="login-container">
        <div className="login-card">
          <div className="loading-state">
            <span className="spinner"></span>
            <p>Verifying reset link...</p>
          </div>
        </div>
      </div>
    );
  }

  // Invalid token state
  if (!tokenValid) {
    return (
      <div className="login-container">
        <div className="login-card">
          <div className="error-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
          </div>
          <h1>Invalid or Expired Link</h1>
          <p className="login-subtitle">
            This password reset link is invalid or has expired. Please request a new one.
          </p>
          <div className="form-actions" style={{ marginTop: '1.5rem' }}>
            <Link to="/forgot-password" className="btn btn-primary" style={{ width: '100%', textAlign: 'center' }}>
              Request New Link
            </Link>
          </div>
          <div className="login-footer">
            <p>
              Remember your password?{' '}
              <Link to="/login" className="link">Sign In</Link>
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Success state
  if (success) {
    return (
      <div className="login-container">
        <div className="login-card">
          <div className="success-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h1>Password Reset Successful</h1>
          <p className="login-subtitle">
            Your password has been reset successfully. You can now sign in with your new password.
          </p>
          <div className="form-actions" style={{ marginTop: '1.5rem' }}>
            <Link to="/login" className="btn btn-primary" style={{ width: '100%', textAlign: 'center' }}>
              Sign In
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Reset form
  return (
    <div className="login-container">
      <div className="login-card">
        <h1>Reset Password</h1>
        <p className="login-subtitle">
          Enter your new password below.
        </p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="password">New Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
              autoComplete="new-password"
            />
            <div className="password-strength-container">
              {formData.password && (
                <>
                  <div className={`strength-bar strength-${passwordStrength.strength}`}>
                    <div className="strength-fill"></div>
                  </div>
                  <div className="strength-checklist">
                    <div className={passwordStrength.checks.length ? 'check-passed' : 'check-failed'}>
                      {passwordStrength.checks.length ? '\u2713' : '\u25CB'} At least 8 characters
                    </div>
                    <div className={passwordStrength.checks.uppercase ? 'check-passed' : 'check-failed'}>
                      {passwordStrength.checks.uppercase ? '\u2713' : '\u25CB'} One uppercase letter
                    </div>
                    <div className={passwordStrength.checks.lowercase ? 'check-passed' : 'check-failed'}>
                      {passwordStrength.checks.lowercase ? '\u2713' : '\u25CB'} One lowercase letter
                    </div>
                    <div className={passwordStrength.checks.number ? 'check-passed' : 'check-failed'}>
                      {passwordStrength.checks.number ? '\u2713' : '\u25CB'} One number
                    </div>
                    <div className={passwordStrength.checks.special ? 'check-passed' : 'check-failed'}>
                      {passwordStrength.checks.special ? '\u2713' : '\u25CB'} One special character
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm New Password</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              minLength={8}
              autoComplete="new-password"
              className={passwordsMatch === false ? 'invalid' : passwordsMatch === true ? 'valid' : ''}
            />
            <div className="password-match-container">
              {formData.confirmPassword && (
                <div className={`validation-message ${passwordsMatch ? 'success' : 'error'}`}>
                  {passwordsMatch ? '\u2713 Passwords match' : '\u2717 Passwords do not match'}
                </div>
              )}
            </div>
          </div>

          <div className="form-actions">
            <Link to="/login" className="btn btn-secondary">
              Cancel
            </Link>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !passwordStrength.isValid || !passwordsMatch}
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ResetPassword;
