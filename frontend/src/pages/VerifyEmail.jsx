import { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

function VerifyEmail({ onAuthSuccess }) {
  const [status, setStatus] = useState('verifying'); // 'verifying', 'set_password', 'success', 'error'
  const [message, setMessage] = useState('');
  const [verificationToken, setVerificationToken] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordStrength, setPasswordStrength] = useState('');
  const [passwordChecks, setPasswordChecks] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    number: false,
    special: false
  });
  const [passwordError, setPasswordError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const hasVerified = useRef(false); // Prevent duplicate verification calls

  useEffect(() => {
    const verifyEmail = async () => {
      // Prevent duplicate calls (React strict mode or re-renders)
      if (hasVerified.current) {
        return;
      }
      hasVerified.current = true;

      // Get token from URL hash params (avoid query string tokens)
      const hashParams = new URLSearchParams(location.hash.replace(/^#/, ''));
      let token = hashParams.get('token');
      if (!token) {
        const searchParams = new URLSearchParams(location.search);
        token = searchParams.get('token');
      }

      if (!token) {
        setStatus('error');
        setMessage('Invalid verification link. No token provided.');
        return;
      }

      try {
        const response = await fetch('/api/auth/verify-email', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token }),
        });
        const data = await response.json();

        if (response.ok) {
          if (data.needs_password) {
            // User needs to set password
            setStatus('set_password');
            setVerificationToken(data.verification_token);
            setMessage('Welcome! Please create your password to continue.');
          } else {
            // Email verified, user already has password
            setStatus('success');
            setMessage(data.message || 'Your email has been verified successfully!');
            // Redirect to login after 3 seconds
            setTimeout(() => {
              navigate('/login');
            }, 3000);
          }
        } else {
          setStatus('error');
          setMessage(data.detail || 'Verification failed. The link may be invalid or expired.');
        }
      } catch (err) {
        setStatus('error');
        setMessage('An error occurred while verifying your email. Please try again.');
        console.error('Error:', err);
      }
    };

    verifyEmail();
  }, [location.hash, location.search, navigate]);

  // Validate password strength
  const validatePassword = (pwd) => {
    const checks = {
      length: pwd.length >= 8,
      uppercase: /[A-Z]/.test(pwd),
      lowercase: /[a-z]/.test(pwd),
      number: /[0-9]/.test(pwd),
      special: /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(pwd)
    };

    setPasswordChecks(checks);

    if (!checks.length) {
      setPasswordStrength('');
      setPasswordError('Password must be at least 8 characters long');
      return false;
    }

    const passedChecks = Object.values(checks).filter(Boolean).length;
    const allValid = Object.values(checks).every(Boolean);

    if (!allValid) {
      setPasswordStrength('weak');
      setPasswordError('Password must contain uppercase, lowercase, number, and special character');
      return false;
    }

    setPasswordStrength('strong');
    setPasswordError('');
    return true;
  };

  const handlePasswordChange = (e) => {
    const pwd = e.target.value;
    setPassword(pwd);
    if (pwd) {
      validatePassword(pwd);
    } else {
      setPasswordStrength('');
      setPasswordError('');
      setPasswordChecks({
        length: false,
        uppercase: false,
        lowercase: false,
        number: false,
        special: false
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setPasswordError('');

    if (!validatePassword(password)) {
      return;
    }

    if (password !== confirmPassword) {
      setPasswordError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/auth/set-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          token: verificationToken,
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Password set successfully, auto-login via HttpOnly cookie
        localStorage.setItem('user', JSON.stringify(data.user));

        // Call onAuthSuccess if provided
        if (onAuthSuccess) {
          onAuthSuccess(data.user);
        }

        setStatus('success');
        setMessage('Password created successfully! Redirecting to dashboard...');

        setTimeout(() => {
          navigate('/dashboard');
        }, 1500);
      } else {
        setPasswordError(data.detail || 'Failed to set password. Please try again.');
      }
    } catch (err) {
      setPasswordError('An error occurred. Please try again.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '1rem'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '2rem',
        maxWidth: '500px',
        width: '100%',
        textAlign: 'center',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
      }}>
        {status === 'verifying' && (
          <>
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              backgroundColor: '#f3f4f6',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.5rem'
            }}>
              <div className="spinner" style={{ width: '32px', height: '32px' }}></div>
            </div>
            <h2 style={{ margin: '0 0 0.5rem', fontSize: '1.5rem', fontWeight: '600', color: '#1f2937' }}>
              Verifying Your Email
            </h2>
            <p style={{ margin: 0, color: '#6b7280', fontSize: '1rem' }}>
              Please wait while we verify your email address...
            </p>
          </>
        )}

        {status === 'set_password' && (
          <>
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              backgroundColor: '#dbeafe',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.5rem'
            }}>
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
              </svg>
            </div>
            <h2 style={{ margin: '0 0 0.5rem', fontSize: '1.5rem', fontWeight: '600', color: '#1f2937' }}>
              Create Your Password
            </h2>
            <p style={{ margin: '0 0 1.5rem', color: '#6b7280', fontSize: '0.875rem' }}>
              {message}
            </p>

            <form onSubmit={handleSubmit} style={{ textAlign: 'left' }}>
              <div className="form-group" style={{ marginBottom: '1rem' }}>
                <label htmlFor="password" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', fontSize: '0.875rem' }}>
                  Password *
                </label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={handlePasswordChange}
                  required
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '1rem'
                  }}
                  placeholder="Enter your password"
                />
                {passwordStrength && (
                  <div style={{
                    marginTop: '0.5rem',
                    fontSize: '0.75rem',
                    color: passwordStrength === 'strong' ? '#22c55e' : passwordStrength === 'medium' ? '#f59e0b' : '#dc2626'
                  }}>
                    Password strength: {passwordStrength}
                  </div>
                )}
              </div>

              <div className="form-group" style={{ marginBottom: '1rem' }}>
                <label htmlFor="confirmPassword" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', fontSize: '0.875rem' }}>
                  Confirm Password *
                </label>
                <input
                  type="password"
                  id="confirmPassword"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '1rem'
                  }}
                  placeholder="Confirm your password"
                />
              </div>

              {passwordError && (
                <div style={{
                  marginBottom: '1rem',
                  padding: '0.75rem',
                  backgroundColor: '#fef2f2',
                  border: '1px solid #fecaca',
                  borderRadius: '6px',
                  color: '#dc2626',
                  fontSize: '0.875rem'
                }}>
                  {passwordError}
                </div>
              )}

              <div style={{ fontSize: '0.75rem', marginBottom: '1rem' }}>
                <div style={{ marginBottom: '0.5rem', color: '#6b7280', fontWeight: '500' }}>
                  Password must contain:
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  <div style={{
                    color: passwordChecks.length ? '#22c55e' : '#6b7280',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <span style={{ fontWeight: '600', minWidth: '1.5rem' }}>
                      {passwordChecks.length ? '✓' : '○'}
                    </span>
                    At least 8 characters
                  </div>
                  <div style={{
                    color: passwordChecks.uppercase ? '#22c55e' : '#6b7280',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <span style={{ fontWeight: '600', minWidth: '1.5rem' }}>
                      {passwordChecks.uppercase ? '✓' : '○'}
                    </span>
                    1 uppercase letter
                  </div>
                  <div style={{
                    color: passwordChecks.lowercase ? '#22c55e' : '#6b7280',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <span style={{ fontWeight: '600', minWidth: '1.5rem' }}>
                      {passwordChecks.lowercase ? '✓' : '○'}
                    </span>
                    1 lowercase letter
                  </div>
                  <div style={{
                    color: passwordChecks.number ? '#22c55e' : '#6b7280',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <span style={{ fontWeight: '600', minWidth: '1.5rem' }}>
                      {passwordChecks.number ? '✓' : '○'}
                    </span>
                    1 number
                  </div>
                  <div style={{
                    color: passwordChecks.special ? '#22c55e' : '#6b7280',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <span style={{ fontWeight: '600', minWidth: '1.5rem' }}>
                      {passwordChecks.special ? '✓' : '○'}
                    </span>
                    1 special character (!@#$%^&*)
                  </div>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading || !password || !confirmPassword || passwordStrength === 'weak'}
                className="btn btn-primary"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  fontSize: '1rem',
                  opacity: (loading || !password || !confirmPassword || passwordStrength === 'weak') ? 0.6 : 1,
                  cursor: (loading || !password || !confirmPassword || passwordStrength === 'weak') ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? 'Creating Password...' : 'Create Password'}
              </button>
            </form>
          </>
        )}

        {status === 'success' && (
          <>
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              backgroundColor: '#d1fae5',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.5rem'
            }}>
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
            </div>
            <h2 style={{ margin: '0 0 0.5rem', fontSize: '1.5rem', fontWeight: '600', color: '#1f2937' }}>
              Success!
            </h2>
            <p style={{ margin: '0 0 1.5rem', color: '#6b7280', fontSize: '1rem' }}>
              {message}
            </p>
            <p style={{ margin: 0, color: '#6b7280', fontSize: '0.875rem' }}>
              Redirecting...
            </p>
          </>
        )}

        {status === 'error' && (
          <>
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              backgroundColor: '#fee2e2',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.5rem'
            }}>
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#dc2626" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
              </svg>
            </div>
            <h2 style={{ margin: '0 0 0.5rem', fontSize: '1.5rem', fontWeight: '600', color: '#1f2937' }}>
              Verification Failed
            </h2>
            <p style={{ margin: '0 0 1.5rem', color: '#6b7280', fontSize: '1rem' }}>
              {message}
            </p>
            <button
              onClick={() => navigate('/login')}
              className="btn btn-primary"
            >
              Go to Login
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default VerifyEmail;
