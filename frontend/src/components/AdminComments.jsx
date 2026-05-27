import React, { useEffect, useState } from 'react';

const API_URL = 'http://localhost:8003';
const TRACK_API_URL = 'http://localhost:8002';

const AdminComments = ({ token, onOpenTrackPage }) => {
  const [comments, setComments] = useState([]);
  const [tracks, setTracks] = useState({});
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

  const loadTrackData = async (trackId) => {
    if (tracks[trackId]) {
      return tracks[trackId];
    }
    
    try {
      const response = await fetch(`${TRACK_API_URL}/tracks/${trackId}`, {
        headers: authHeaders(),
      });
      
      if (response.ok) {
        const trackData = await response.json();
        setTracks(prev => ({ ...prev, [trackId]: trackData }));
        return trackData;
      }
    } catch (err) {
      console.error('Failed to load track:', err);
    }
    return null;
  };

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
        
        // Load track data for each comment
        const uniqueTrackIds = [...new Set(filteredData.map(c => c.track_id))];
        for (const trackId of uniqueTrackIds) {
          await loadTrackData(trackId);
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Ошибка загрузки комментариев');
      }
    } catch (err) {
      setError('Ошибка загрузки комментариев');
    } finally {
      setLoading(false);
    }
  };

  const hardDeleteComment = async (commentId) => {
    if (!window.confirm('Вы уверены, что хотите навсегда удалить этот комментарий? Это действие нельзя будет отменить.')) {
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
        setError(errorData.detail || 'Ошибка при удалении комментария');
      }
    } catch (err) {
      setError('Ошибка при удалении комментария');
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
        <h2 className="card-title">🔒 Админ доступ</h2>
        <p className="card-subtitle">Вы должны быть авторизованы как администратор, чтобы получить доступ к этой странице.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
          <div>
            <h2 className="card-title">🛡️ Администрирование комментариев</h2>
            <p className="card-subtitle">Управление всеми комментариями на платформе</p>
          </div>
          <button className="btn" onClick={loadComments} disabled={loading}>
            🔄 Обновить
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
              {filterOption === 'all' ? '📋 Все комментарии' : filterOption === 'active' ? '💬 Активные' : '🗑️ Удаленные'}
            </button>
          ))}
        </div>

        <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: '#666' }}>
          Отображение {comments.length} комментариев
        </div>
      </div>

      <div className="card">
        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <div className="spinner"></div>
            <p>Загрузка комментариев...</p>
          </div>
        ) : comments.length === 0 ? (
          <p style={{ color: '#666', textAlign: 'center', padding: '2rem' }}>
            Комментарии для выбранного фильтра не найдены.
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
                        (Удалено)
                      </span>
                    )}
                  </div>
                  <div>
                    <button
                      className="btn btn-danger"
                      onClick={() => hardDeleteComment(comment.id)}
                      style={{ fontSize: '0.8rem', padding: '0.25rem 0.5rem' }}
                      title="Удалить комментарий навсегда"
                    >
                      🗑️ Удалить навсегда
                    </button>
                  </div>
                </div>

                <div style={{ marginBottom: '0.5rem' }}>
                  {tracks[comment.track_id] ? (
                    <button
                      onClick={() => onOpenTrackPage && onOpenTrackPage(comment.track_id)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#1976d2',
                        cursor: 'pointer',
                        textDecoration: 'underline',
                        fontSize: '0.8rem',
                        padding: 0
                      }}
                    >
                      {tracks[comment.track_id].title} от {tracks[comment.track_id].artist}
                    </button>
                  ) : (
                    <span style={{ fontSize: '0.8rem', color: '#666' }}>
                      Track ID: {comment.track_id}
                    </span>
                  )}
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