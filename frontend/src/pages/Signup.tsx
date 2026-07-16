import React, { useState } from 'react';
import { Box, Card, CardContent, Typography, TextField, Button, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';

export const Signup: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await apiClient.post('/auth/signup', formData);
      navigate('/login');
    } catch (err: any) {
      if (err.code === 'ERR_NETWORK') {
        setError('Unable to connect to the server. Please try again.');
      } else {
        setError(err.response?.data?.detail || 'Failed to create account');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'background.default' }}>
      <Card sx={{ maxWidth: 450, width: '100%', p: 2, boxShadow: 6, borderRadius: 2 }}>
        <CardContent>
          <Typography variant="h4" gutterBottom align="center" color="primary" sx={{ fontWeight: 700 }}>
            HealthSphere AI
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" gutterBottom align="center" sx={{ mb: 3 }}>
            Create your account
          </Typography>

          {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Full Name"
              variant="outlined"
              margin="normal"
              required
              value={formData.full_name}
              onChange={e => setFormData({ ...formData, full_name: e.target.value })}
            />
            <TextField
              fullWidth
              label="Email Address"
              type="email"
              variant="outlined"
              margin="normal"
              required
              value={formData.email}
              onChange={e => setFormData({ ...formData, email: e.target.value })}
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              variant="outlined"
              margin="normal"
              required
              value={formData.password}
              onChange={e => setFormData({ ...formData, password: e.target.value })}
            />
            
            <Button
              fullWidth
              type="submit"
              variant="contained"
              size="large"
              disabled={loading}
              sx={{ mt: 3, mb: 2, py: 1.5, fontWeight: 600 }}
            >
              {loading ? 'Creating Account...' : 'Sign Up'}
            </Button>
            <Button
              fullWidth
              variant="text"
              onClick={() => navigate('/login')}
              sx={{ fontWeight: 500 }}
            >
              Already have an account? Sign In
            </Button>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
};
