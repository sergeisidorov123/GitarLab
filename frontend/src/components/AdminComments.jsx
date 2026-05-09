import React, { useEffect, useState } from 'react';

const API_URL = 'http://localhost:8003';

const AdminComments = ({ token }) => {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, deleted, active

  useEffect(() => {
    loadComments();
  }, [filter]);

  const authHeaders = () => ({
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  });

  const loadComments = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/admin/comments/`, {
        headers: authHeaders(),
      });

      if (response.ok) {
        const data = await response.json();
        let filteredData = data;

        if (filter === 'deleted') {
          filteredData = data.filter(comment => comment.is_deleted);
        } else if (filter === 'active') {
          filteredData = data.filter(comment => !comment.is_deleted);
        }

        setComments(filteredData);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to load comments');
      }
    } catch (err) {
      setError('Failed to load comments');
    } finally {
      setLoading(false);
    }
  };

  const hardDeleteComment = async (commentId) => {
    if (!window.confirm('Are you sure you want to permanently delete this comment? This action cannot be undone.')) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/admin/comments/${commentId}`, {
        method: 'DELETE',
        headers: authHeaders(),
      });

      if (response.ok) {
        loadComments();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to delete comment');
      }
    } catch (err) {
      setError('Failed to delete comment');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  if (!token) {
    return (
      <div className="card">
        <h2 className="card-title">🔒 Admin Access Required</h2>
        <p className="card-subtitle">You must be logged in as an administrator to access this page.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
          <div>
            <h2 className="card-title">🛡️ Comment Administration</h2>
            <p className="card-subtitle">Manage all comments across the platform</p>
          </div>
          <button className="btn" onClick={loadComments} disabled={loading}>
            🔄 Refresh
          </button>
        </div>

        {error && (
          <div style={{ color: '#d32f2f', marginBottom: '1rem', padding: '0.5rem', background: '#ffebee', borderRadius: '4px' }}>
            {error}
          </div>
        )}

        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
          {['all', 'active', 'deleted'].map((filterOption) => (
            <button
              key={filterOption}
              className={`btn ${filter === filterOption ? 'active' : ''}`}
              onClick={() => setFilter(filterOption)}
            >
              {filterOption === 'all' ? '📋 All Comments' : filterOption === 'active' ? '💬 Active' : '🗑️ Deleted'}
            </button>
          ))}
        </div>

        <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: '#666' }}>
          Showing {comments.length} comments
        </div>
      </div>

      <div className="card">
        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <div className="spinner"></div>
            <p>Loading comments...</p>
          </div>
        ) : comments.length === 0 ? (
          <p style={{ color: '#666', textAlign: 'center', padding: '2rem' }}>
            No comments found for the selected filter.
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {comments.map((comment) => (
              <div
                key={comment.id}
                style={{
                  border: '1px solid #e0e0e0',
                  borderRadius: '8px',
                  padding: '1rem',
                  background: comment.is_deleted ? '#f5f5f5' : '#fff',
                  opacity: comment.is_deleted ? 0.7 : 1,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <div>
                    <strong>{comment.author_username}</strong>
                    <span style={{ color: '#666', fontSize: '0.8rem', marginLeft: '0.5rem' }}>
                      {formatDate(comment.created_at)}
                    </span>
                    {comment.is_deleted && (
                      <span style={{ color: '#d32f2f', fontSize: '0.8rem', marginLeft: '0.5rem' }}>
                        (Deleted)
                      </span>
                    )}
                  </div>
                  <div>
                    <button
                      className="btn btn-danger"
                      onClick={() => hardDeleteComment(comment.id)}
                      style={{ fontSize: '0.8rem', padding: '0.25rem 0.5rem' }}
                      title="Permanently delete this comment"
                    >
                      🗑️ Delete Permanently
                    </button>
                  </div>
                </div>

                <div style={{ marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.8rem', color: '#666' }}>
                    Track ID: {comment.track_id}
                  </span>
                  {comment.parent_id && (
                    <span style={{ fontSize: '0.8rem', color: '#666', marginLeft: '1rem' }}>
                      Reply to comment #{comment.parent_id}
                    </span>
                  )}
                </div>

                <p style={{
                  margin: '0.5rem 0',
                  whiteSpace: 'pre-wrap',
                  fontStyle: comment.is_deleted ? 'italic' : 'normal'
                }}>
                  {comment.content}
                </p>

                {comment.updated_at && comment.updated_at !== comment.created_at && (
                  <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '0.5rem' }}>
                    Last updated: {formatDate(comment.updated_at)}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminComments;