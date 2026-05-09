import React, { useEffect, useState } from 'react';

const API_URL = 'http://localhost:8003';

const Comments = ({ trackId, token }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [replyingTo, setReplyingTo] = useState(null);
  const [replyText, setReplyText] = useState('');
  const [editingComment, setEditingComment] = useState(null);
  const [editText, setEditText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    if (token) {
      // Fetch current user info
      fetch('http://localhost:8002/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => setCurrentUser(data))
        .catch(() => setCurrentUser(null));
    } else {
      setCurrentUser(null);
    }

    if (trackId) {
      loadComments();
    }
  }, [trackId, token]);

  const authHeaders = () => {
    return token
      ? {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      : { 'Content-Type': 'application/json' };
  };

  const loadComments = async () => {
    try {
      const response = await fetch(`${API_URL}/comments/track/${trackId}`);
      const data = await response.json();
      if (response.ok) {
        setComments(data);
      }
    } catch (err) {
      console.error('Failed to load comments:', err);
    }
  };

  const submitComment = async (content, parentId = null) => {
    if (!token) {
      setError('You must be logged in to comment');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/comments/`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({
          content,
          track_id: trackId,
          parent_id: parentId,
        }),
      });

      if (response.ok) {
        setNewComment('');
        setReplyText('');
        setReplyingTo(null);
        loadComments();
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to post comment');
      }
    } catch (err) {
      setError('Failed to post comment');
    } finally {
      setLoading(false);
    }
  };

  const updateComment = async (commentId, content) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/comments/${commentId}`, {
        method: 'PUT',
        headers: authHeaders(),
        body: JSON.stringify({ content }),
      });

      if (response.ok) {
        setEditingComment(null);
        setEditText('');
        loadComments();
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to update comment');
      }
    } catch (err) {
      setError('Failed to update comment');
    } finally {
      setLoading(false);
    }
  };

  const deleteComment = async (commentId) => {
    if (!window.confirm('Are you sure you want to delete this comment?')) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/comments/${commentId}`, {
        method: 'DELETE',
        headers: authHeaders(),
      });

      if (response.ok) {
        loadComments();
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to delete comment');
      }
    } catch (err) {
      setError('Failed to delete comment');
    } finally {
      setLoading(false);
    }
  };

  const renderComment = (comment, depth = 0) => {
    const isAuthor = currentUser && comment.author_id === currentUser.id;

    return (
      <div key={comment.id} style={{ marginLeft: `${depth * 20}px`, marginBottom: '1rem' }}>
        <div style={{
          background: depth > 0 ? '#f8f9fa' : '#fff',
          border: '1px solid #e0e0e0',
          borderRadius: '8px',
          padding: '1rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
            <div>
              <strong>{comment.author_username}</strong>
              <span style={{ color: '#666', fontSize: '0.8rem', marginLeft: '0.5rem' }}>
                {new Date(comment.created_at).toLocaleString()}
              </span>
            </div>
            {isAuthor && (
              <div>
                <button
                  onClick={() => {
                    setEditingComment(comment.id);
                    setEditText(comment.content);
                  }}
                  style={{ marginRight: '0.5rem', fontSize: '0.8rem' }}
                >
                  ✎ Edit
                </button>
                <button
                  onClick={() => deleteComment(comment.id)}
                  style={{ fontSize: '0.8rem', color: '#d32f2f' }}
                >
                  🗑 Delete
                </button>
              </div>
            )}
          </div>

          {editingComment === comment.id ? (
            <div>
              <textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                style={{ width: '100%', minHeight: '60px', marginBottom: '0.5rem', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ddd' }}
              />
              <div>
                <button
                  onClick={() => updateComment(comment.id, editText)}
                  disabled={loading}
                  style={{ marginRight: '0.5rem' }}
                >
                  Save
                </button>
                <button
                  onClick={() => {
                    setEditingComment(null);
                    setEditText('');
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <p style={{ margin: '0.5rem 0', whiteSpace: 'pre-wrap' }}>
              {comment.content ? comment.content.replace(/[<>\"&]/g, (match) => {
                const escapeMap = {
                  '<': '&lt;',
                  '>': '&gt;',
                  '"': '&quot;',
                  '&': '&amp;'
                };
                return escapeMap[match] || match;
              }) : 'No content'}
            </p>
          )}

          {token && depth < 3 && (
            <button
              onClick={() => setReplyingTo(replyingTo === comment.id ? null : comment.id)}
              style={{ fontSize: '0.8rem', color: '#1976d2', marginTop: '0.5rem' }}
            >
              {replyingTo === comment.id ? 'Cancel Reply' : 'Reply'}
            </button>
          )}

          {replyingTo === comment.id && (
            <div style={{ marginTop: '0.5rem' }}>
              <textarea
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                placeholder="Write a reply..."
                style={{ width: '100%', minHeight: '60px', marginBottom: '0.5rem', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ddd' }}
              />
              <button
                onClick={() => submitComment(replyText, comment.id)}
                disabled={loading || !replyText.trim()}
              >
                Reply
              </button>
            </div>
          )}
        </div>

        {comment.replies && comment.replies.map(reply => renderComment(reply, depth + 1))}
      </div>
    );
  };

  if (!trackId) {
    return null;
  }

  return (
    <div style={{ marginTop: '2rem' }}>
      <h3 style={{ marginBottom: '1rem' }}>💬 Comments</h3>

      {error && (
        <div style={{ color: '#d32f2f', marginBottom: '1rem', padding: '0.5rem', background: '#ffebee', borderRadius: '4px' }}>
          {error}
        </div>
      )}

      {token ? (
        <div style={{ marginBottom: '2rem' }}>
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Share your thoughts about this tuning..."
            style={{ width: '100%', minHeight: '80px', padding: '0.75rem', borderRadius: '8px', border: '1px solid #ddd', marginBottom: '0.5rem' }}
          />
          <button
            onClick={() => submitComment(newComment)}
            disabled={loading || !newComment.trim()}
            style={{ padding: '0.5rem 1rem', borderRadius: '4px', background: '#1976d2', color: 'white', border: 'none' }}
          >
            {loading ? 'Posting...' : 'Post Comment'}
          </button>
        </div>
      ) : (
        <p style={{ color: '#666', fontStyle: 'italic' }}>
          Please log in to leave comments.
        </p>
      )}

      <div>
        {comments.length === 0 ? (
          <p style={{ color: '#666', fontStyle: 'italic', textAlign: 'center', padding: '2rem' }}>
            No comments yet. Be the first to share your thoughts!
          </p>
        ) : (
          comments.map(comment => renderComment(comment))
        )}
      </div>
    </div>
  );
};

export default Comments;