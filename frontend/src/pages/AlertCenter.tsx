import React, { useEffect, useState } from 'react';
import { Box, Typography, Card, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import { apiClient } from '../api/client';
import { DashboardSkeleton } from '../components/common/SkeletonLoader';

export const AlertCenter: React.FC = () => {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAlerts = async () => {
    try {
      const res = await apiClient.get('/analytics/alerts');
      setAlerts(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleDelete = async (id: number) => {
    try {
      await apiClient.delete(`/analytics/alerts/${id}`);
      fetchAlerts(); // Refresh the list
    } catch (err) {
      console.error('Failed to delete alert', err);
    }
  };

  if (loading) return <DashboardSkeleton />;

  return (
    <Box>
      <Typography variant="h4" sx={{ fontWeight: 'bold',  mb: 4 }}>
        Alert Center
      </Typography>

      <Card>
        <TableContainer>
          <Table sx={{ minWidth: 650 }}>
            <TableHead>
              <TableRow sx={{ bgcolor: 'background.default' }}>
                <TableCell><Typography sx={{ fontWeight: 'bold' }}>ID</Typography></TableCell>
                <TableCell><Typography sx={{ fontWeight: 'bold' }}>Type</Typography></TableCell>
                <TableCell><Typography sx={{ fontWeight: 'bold' }}>Severity</Typography></TableCell>
                <TableCell><Typography sx={{ fontWeight: 'bold' }}>Message</Typography></TableCell>
                <TableCell><Typography sx={{ fontWeight: 'bold' }}>Created At</Typography></TableCell>
                <TableCell align="right"><Typography sx={{ fontWeight: 'bold' }}>Actions</Typography></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {alerts.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No active alerts.
                  </TableCell>
                </TableRow>
              )}
              {alerts.map((row, index) => (
                <TableRow key={row.id}>
                  <TableCell>{index + 1}</TableCell>
                  <TableCell>{row.alert_type}</TableCell>
                  <TableCell>
                    <Chip 
                      label={row.severity} 
                      color={row.severity === 'high' ? 'error' : row.severity === 'medium' ? 'warning' : 'info'} 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell dangerouslySetInnerHTML={{ __html: row.message }}></TableCell>
                  <TableCell>{new Date(row.created_at).toLocaleString()}</TableCell>
                  <TableCell align="right">
                    <IconButton color="error" onClick={() => handleDelete(row.id)}>
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
    </Box>
  );
};
