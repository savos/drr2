import { useState, useEffect } from 'react';

function AddUser() {
  const [formData, setFormData] = useState({
    firstname: '',
    lastname: '',
    position: '',
    email: ''
  });
  const [isSuperuser, setIsSuperuser] = useState(false);
  const [editingUserId, setEditingUserId] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const [emailValid, setEmailValid] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  // Users list state
  const [users, setUsers] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(true);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);

  // Fetch users on mount
  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const response = await fetch('/api/users/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (err) {
      console.error('Error fetching users:', err);
    } finally {
      setLoadingUsers(false);
    }
  };

  // Email validation
  const validateEmail = (email) => {
    if (!email) {
      setEmailValid(null);
      return false;
    }

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

  // Handle form field changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    if (name === 'email') {
      validateEmail(value);
    }
  };

  // Reset form to initial state
  const resetForm = () => {
    setFormData({
      firstname: '',
      lastname: '',
      position: '',
      email: ''
    });
    setIsSuperuser(false);
    setEditingUserId(null);
    setEmailValid(null);
    setError('');
  };

  // Open modal for adding new user - always start with blank form
  const openAddModal = () => {
    // Explicitly clear all form data - never load from backend
    setFormData({
      firstname: '',
      lastname: '',
      position: '',
      email: ''
    });
    setIsSuperuser(false);
    setEditingUserId(null);
    setEmailValid(null);
    setError('');
    setShowModal(true);
  };

  // Open modal for editing user
  const handleEdit = (user) => {
    setFormData({
      firstname: user.firstname || '',
      lastname: user.lastname || '',
      position: user.position || '',
      email: user.email || ''
    });
    setIsSuperuser(Boolean(user.is_superuser));
    setEditingUserId(user.id);
    setEmailValid(true);
    setError('');
    setSuccess('');
    setShowModal(true);
  };

  // Close modal
  const closeModal = () => {
    setShowModal(false);
    resetForm();
  };

  // Open delete confirmation modal
  const openDeleteModal = (user) => {
    setUserToDelete(user);
    setShowDeleteModal(true);
  };

  // Close delete confirmation modal
  const closeDeleteModal = () => {
    setShowDeleteModal(false);
    setUserToDelete(null);
  };

  // Handle delete confirmation
  const handleDelete = async () => {
    if (!userToDelete) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/users/${userToDelete.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('User deleted successfully');
        closeDeleteModal();
        fetchUsers();
      } else {
        setError(data.detail || 'Failed to delete user');
        closeDeleteModal();
      }
    } catch (err) {
      setError('Error deleting user');
      closeDeleteModal();
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validate email
    if (!validateEmail(formData.email)) {
      setError('Please enter a valid email address');
      return;
    }

    // Validate required fields
    if (!formData.firstname || !formData.lastname) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('Authentication token not found');
      }

      if (editingUserId) {
        // Update existing user
        const updateData = {
          firstname: formData.firstname,
          lastname: formData.lastname,
          position: formData.position || null,
          email: formData.email,
          is_superuser: isSuperuser
        };

        const response = await fetch(`/api/users/${editingUserId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(updateData),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'User update failed');
        }

        setSuccess('User updated successfully!');
        closeModal();
        fetchUsers();
      } else {
        // Create new user (without password)
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          throw new Error('User not authenticated');
        }
        const user = JSON.parse(userStr);
        const companyId = user.company_id;

        if (!companyId) {
          throw new Error('Company ID not found');
        }

        const response = await fetch('/api/users/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            firstname: formData.firstname,
            lastname: formData.lastname,
            position: formData.position || null,
            email: formData.email,
            company_id: companyId,
            is_superuser: isSuperuser,
            notifications: 'disabled',
            slack: 'disabled',
            teams: 'disabled',
            discord: 'disabled',
            telegram: 'disabled'
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'User creation failed');
        }

        setSuccess('User added successfully!');
        closeModal();
        fetchUsers();
      }
    } catch (err) {
      setError(err.message || 'Operation failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Check if form is valid for submission
  const isFormValid = () => {
    return formData.firstname && formData.lastname && emailValid;
  };

  // Get current user ID to prevent self-deletion
  const currentUser = JSON.parse(localStorage.getItem('user') || '{}');

  return (
    <div className="teams-page">
      <div className="page-header">
        <h1>User Management</h1>
        <p className="subtitle">Manage users in your company</p>
      </div>

      {error && !showModal && (
        <div className="alert alert-error">
          <span className="alert-icon">!</span>
          <span>{error}</span>
          <button className="alert-close" onClick={() => setError('')}>&times;</button>
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          <span className="alert-icon">&#10003;</span>
          <span>{success}</span>
          <button className="alert-close" onClick={() => setSuccess('')}>&times;</button>
        </div>
      )}

      {/* Users Table */}
      <div className="setup-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ margin: 0 }}>Company Users</h2>
          <button onClick={openAddModal} className="btn btn-primary">
            + Add User
          </button>
        </div>

        {loadingUsers ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading users...</p>
          </div>
        ) : users.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">&#128100;</div>
            <p>No users found. Click "Add User" to create one.</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e5e7eb', textAlign: 'left' }}>
                  <th style={{ padding: '12px 8px', fontWeight: '600', color: '#374151' }}>Name</th>
                  <th style={{ padding: '12px 8px', fontWeight: '600', color: '#374151' }}>Email</th>
                  <th style={{ padding: '12px 8px', fontWeight: '600', color: '#374151' }}>Position</th>
                  <th style={{ padding: '12px 8px', fontWeight: '600', color: '#374151' }}>Role</th>
                  <th style={{ padding: '12px 8px', fontWeight: '600', color: '#374151', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr
                    key={user.id}
                    style={{ borderBottom: '1px solid #e5e7eb' }}
                  >
                    <td style={{ padding: '12px 8px' }}>
                      {user.firstname} {user.lastname}
                      {user.id === currentUser.id && (
                        <span style={{
                          marginLeft: '8px',
                          fontSize: '0.75rem',
                          color: '#6366f1',
                          fontWeight: '500'
                        }}>(You)</span>
                      )}
                    </td>
                    <td style={{ padding: '12px 8px', color: '#6b7280' }}>{user.email}</td>
                    <td style={{ padding: '12px 8px', color: '#6b7280' }}>{user.position || '-'}</td>
                    <td style={{ padding: '12px 8px' }}>
                      <span className={`status-badge ${user.is_superuser ? 'status-active' : 'status-disabled'}`}>
                        {user.is_superuser ? 'Superuser' : 'User'}
                      </span>
                    </td>
                    <td style={{ padding: '12px 8px', textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', alignItems: 'center' }}>
                        <button
                          onClick={() => handleEdit(user)}
                          title="Edit user"
                          style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            padding: '4px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6b7280" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
                          </svg>
                        </button>
                        <button
                          onClick={() => openDeleteModal(user)}
                          disabled={user.id === currentUser.id}
                          title={user.id === currentUser.id ? 'Cannot delete yourself' : 'Delete user'}
                          style={{
                            background: 'none',
                            border: 'none',
                            cursor: user.id === currentUser.id ? 'not-allowed' : 'pointer',
                            padding: '4px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            opacity: user.id === currentUser.id ? 0.3 : 1
                          }}
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#dc2626" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && userToDelete && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '1rem'
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget) closeDeleteModal();
          }}
        >
          <div
            style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              width: '100%',
              maxWidth: '400px',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
            }}
          >
            <div style={{ padding: '1.5rem', textAlign: 'center' }}>
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '50%',
                backgroundColor: '#fef2f2',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem'
              }}>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#dc2626" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="15" y1="9" x2="9" y2="15"></line>
                  <line x1="9" y1="9" x2="15" y2="15"></line>
                </svg>
              </div>
              <h3 style={{ margin: '0 0 0.5rem', fontSize: '1.125rem', fontWeight: '600' }}>
                Delete User
              </h3>
              <p style={{ margin: '0 0 1.5rem', color: '#6b7280', fontSize: '0.875rem' }}>
                Are you sure you want to delete <strong>{userToDelete.firstname} {userToDelete.lastname}</strong>? This action cannot be undone.
              </p>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                <button
                  onClick={closeDeleteModal}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDelete}
                  className="btn btn-danger"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add/Edit User Modal */}
      {showModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '1rem'
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget) closeModal();
          }}
        >
          <div
            style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              width: '100%',
              maxWidth: '500px',
              maxHeight: '90vh',
              overflow: 'auto',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
            }}
          >
            {/* Modal Header */}
            <div style={{
              padding: '1.5rem',
              borderBottom: '1px solid #e5e7eb',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '600' }}>
                {editingUserId ? 'Edit User' : 'Add New User'}
              </h2>
              <button
                onClick={closeModal}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  color: '#6b7280',
                  lineHeight: 1
                }}
              >
                &times;
              </button>
            </div>

            {/* Modal Body */}
            <div style={{ padding: '1.5rem' }}>
              {error && showModal && (
                <div className="alert alert-error" style={{ marginBottom: '1rem' }}>
                  <span className="alert-icon">!</span>
                  <span>{error}</span>
                  <button className="alert-close" onClick={() => setError('')}>&times;</button>
                </div>
              )}

              <form onSubmit={handleSubmit}>
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
                  <label htmlFor="position">Position (Optional)</label>
                  <input
                    type="text"
                    id="position"
                    name="position"
                    value={formData.position}
                    onChange={handleChange}
                    maxLength={64}
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
                </div>

                <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <input
                      type="checkbox"
                      id="isSuperuser"
                      checked={isSuperuser}
                      onChange={(e) => setIsSuperuser(e.target.checked)}
                      style={{ width: 'auto', cursor: 'pointer' }}
                    />
                    <label htmlFor="isSuperuser" style={{ margin: 0, cursor: 'pointer', fontWeight: '600' }}>
                      This user is superuser
                    </label>
                  </div>
                  <div style={{
                    fontSize: '0.875rem',
                    color: '#666',
                    marginTop: '0.5rem',
                    marginLeft: '30px'
                  }}>
                    Superuser can add users, SSLs and domains
                  </div>
                </div>

                <div className="form-actions" style={{ marginTop: '1.5rem' }}>
                  <button
                    type="button"
                    onClick={closeModal}
                    className="btn btn-secondary"
                    disabled={loading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading || !isFormValid()}
                  >
                    {loading ? (editingUserId ? 'Updating...' : 'Adding...') : (editingUserId ? 'Update User' : 'Add User')}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AddUser;
