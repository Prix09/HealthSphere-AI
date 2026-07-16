import React, { useEffect, useState } from 'react';
import { Box, Typography, Card, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button, Dialog, DialogTitle, DialogContent, DialogActions, Select, MenuItem, FormControl, InputLabel, CircularProgress, Alert, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import { apiClient } from '../api/client';
import { DashboardSkeleton } from '../components/common/SkeletonLoader';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

export const Datasets: React.FC = () => {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [open, setOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [datasetType, setDatasetType] = useState('auto');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchDatasets = async () => {
    try {
      const res = await apiClient.get('/analytics/datasets');
      setDatasets(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleDelete = async (id: number) => {
    try {
      await apiClient.delete(`/analytics/datasets/${id}`);
      setSuccess('Dataset successfully deleted!');
      fetchDatasets();
    } catch (err) {
      console.error('Failed to delete dataset', err);
      setError('Failed to delete dataset');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file.');
      return;
    }
    setUploading(true);
    setError('');
    setSuccess('');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('dataset_type', datasetType);

    try {
      await apiClient.post('/analytics/datasets/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setSuccess('Dataset successfully integrated!');
      setFile(null);
      setOpen(false);
      fetchDatasets();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  if (loading) return <DashboardSkeleton />;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Dataset Management
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<CloudUploadIcon />} 
          onClick={() => setOpen(true)}
          sx={{ background: 'linear-gradient(90deg, #00F5A0, #00D2FF)', color: '#021815' }}
        >
          Integrate Dataset
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      <Card>
        <TableContainer>
          <Table sx={{ minWidth: 650 }}>
            <TableHead>
              <TableRow sx={{ bgcolor: 'background.default' }}>
                <TableCell><Typography sx={{ fontWeight: 'bold' }}>Dataset ID</Typography></TableCell>
                <TableCell><Typography sx={{ fontWeight: 'bold' }}>Name</Typography></TableCell>
                <TableCell><Typography sx={{ fontWeight: 'bold' }}>Version</Typography></TableCell>
                <TableCell><Typography sx={{ fontWeight: 'bold' }}>Rows</Typography></TableCell>
                <TableCell><Typography sx={{ fontWeight: 'bold' }}>Uploaded At</Typography></TableCell>
                <TableCell align="right"><Typography sx={{ fontWeight: 'bold' }}>Actions</Typography></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {datasets.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No datasets registered.
                  </TableCell>
                </TableRow>
              )}
              {datasets.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>{row.id}</TableCell>
                  <TableCell><Typography sx={{ fontWeight: 500 }}>{row.name}</Typography></TableCell>
                  <TableCell>{row.version}</TableCell>
                  <TableCell>{row.row_count}</TableCell>
                  <TableCell>{new Date(row.uploaded_at).toLocaleDateString()}</TableCell>
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

      <Dialog open={open} onClose={() => !uploading && setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Integrate New Dataset</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            {error && <Alert severity="error">{error}</Alert>}
            
            <FormControl fullWidth>
              <InputLabel>Dataset Type / Schema</InputLabel>
              <Select
                value={datasetType}
                label="Dataset Type / Schema"
                onChange={(e) => setDatasetType(e.target.value)}
              >
                <MenuItem value="auto">Auto-Detect</MenuItem>
                <MenuItem value="health">Health Records</MenuItem>
                <MenuItem value="fitness">Fitness / Activity</MenuItem>
                <MenuItem value="environmental">Environmental / AQI</MenuItem>
              </Select>
            </FormControl>

            <Button
              variant="outlined"
              component="label"
              startIcon={<CloudUploadIcon />}
              fullWidth
            >
              {file ? file.name : "Select CSV File"}
              <input
                type="file"
                hidden
                accept=".csv"
                onChange={(e) => {
                  if (e.target.files && e.target.files.length > 0) {
                    setFile(e.target.files[0]);
                  }
                }}
              />
            </Button>
            <Typography variant="caption" color="text.secondary">
              Unknown columns will be automatically detected and stored without breaking existing models.
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpen(false)} disabled={uploading}>Cancel</Button>
          <Button 
            onClick={handleUpload} 
            variant="contained" 
            disabled={!file || uploading}
          >
            {uploading ? <CircularProgress size={24} /> : "Upload & Integrate"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
