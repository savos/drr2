/**
 * API utility for making authenticated requests with automatic token expiration handling
 */

/**
 * Handle logout and redirect to sign-in page
 */
const handleLogout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  window.location.href = '/login';
};

/**
 * Make an authenticated API request
 * Automatically redirects to login if token is expired (401 response)
 *
 * @param {string} url - The API endpoint URL
 * @param {object} options - Fetch options (method, headers, body, etc.)
 * @returns {Promise<Response>} - The fetch response
 */
export const authenticatedFetch = async (url, options = {}) => {
  const token = localStorage.getItem('access_token');

  // Add authorization header if token exists
  const headers = {
    ...options.headers,
    ...(token && { 'Authorization': `Bearer ${token}` })
  };

  const response = await fetch(url, {
    ...options,
    headers
  });

  // If unauthorized (token expired or invalid), logout and redirect
  if (response.status === 401) {
    handleLogout();
    throw new Error('Session expired. Please login again.');
  }

  return response;
};

/**
 * Make an authenticated JSON API request
 * Automatically adds Content-Type header and handles JSON response
 *
 * @param {string} url - The API endpoint URL
 * @param {object} options - Fetch options (method, body, etc.)
 * @returns {Promise<any>} - The parsed JSON response
 */
export const authenticatedFetchJSON = async (url, options = {}) => {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };

  const response = await authenticatedFetch(url, {
    ...options,
    headers
  });

  // Only parse JSON if response has content
  if (response.status === 204 || response.headers.get('content-length') === '0') {
    return null;
  }

  return response.json();
};

export default authenticatedFetch;
