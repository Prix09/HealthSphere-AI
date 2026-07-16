import React, { useEffect, useState } from 'react';
import { Box, Typography, Card, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip } from '@mui/material';
import { apiClient } from '../api/client';
import { DashboardSkeleton } from '../components/common/SkeletonLoader';

export const ModelRegistry: React.FC = () => {
  const [models, setModels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const res = await apiClient.get('/analytics/models');
        setModels(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchModels();
  }, []);

  if (loading) return <DashboardSkeleton />;

  return (
    <Box>
      <Typography variant="h4" sx={{ fontWeight: 'bold',  mb: 4 }}>
        Model Registry
      </Typography>

      <Card>
        <TableContainer>
          <Table sx={{ minWidth: 650 }}>
            <TableHead>
              <TableRow sx={{ bgcolor: 'background.default' }}>
                <TableCell><Typography sx={{ fontWeight: 'bold' }}>Model Name</Typography></TableCell>
                <TableCell><Typography sx={{ fontWeight: 'bold' }}>Version</Typography></TableCell>
                <TableCell><Typography sx={{ fontWeight: 'bold' }}>Status</Typography></TableCell>
                <TableCell><Typography sx={{ fontWeight: 'bold' }}>Accuracy</Typography></TableCell>
                <TableCell><Typography sx={{ fontWeight: 'bold' }}>ROC AUC</Typography></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {models.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    No models trained yet.
                  </TableCell>
                </TableRow>
              )}
              {models.map((row) => (
                <TableRow key={row.id} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                  <TableCell component="th" scope="row">
                    <Typography sx={{ fontWeight: 500 }}>{row.model_name}</Typography>
                  </TableCell>
                  <TableCell>{row.version}</TableCell>
                  <TableCell>
                    <Chip 
                      label={row.is_active ? "Active" : "Archived"} 
                      color={row.is_active ? "success" : "default"} 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>
                    {row.metrics?.accuracy ? `${(row.metrics.accuracy * 100).toFixed(1)}%` : 'N/A'}
                  </TableCell>
                  <TableCell>
                    {row.metrics?.roc_auc ? row.metrics.roc_auc.toFixed(3) : 'N/A'}
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
