import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  CircularProgress,
  Typography,
  Box,
  MenuItem
} from '@mui/material';
import { apiClient } from '../../api/client';

interface ManualAssessmentModalProps {
  open: boolean;
  onClose: () => void;
  onResult: (result: any) => void;
  dynamicFields?: string[];
}

const ManualAssessmentModal: React.FC<ManualAssessmentModalProps> = ({ open, onClose, onResult, dynamicFields = [] }) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<Record<string, any>>({
    age: 30,
    gender: 'Male',
    height_cm: 170,
    weight_kg: 70,
    sleep_hours: 7.0,
    daily_steps: 5000,
    systolic_bp: 120,
    diastolic_bp: 80,
    fasting_blood_sugar: 90,
    hba1c: 5.5,
    aqi: 50,
    daily_calories: 2000,
    exercise_frequency: 'Occasionally'
  });

  // Initialize dynamic fields if not present
  React.useEffect(() => {
    if (dynamicFields.length > 0) {
      setFormData(prev => {
        const next = { ...prev };
        let changed = false;
        dynamicFields.forEach(f => {
          if (next[f] === undefined) {
            next[f] = 0;
            changed = true;
          }
        });
        return changed ? next : prev;
      });
    }
  }, [dynamicFields]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'gender' || name === 'exercise_frequency' ? value : Number(value)
    }));
  };

  const bmi = formData.height_cm > 0 
    ? (formData.weight_kg / Math.pow(formData.height_cm / 100, 2)).toFixed(1) 
    : 0;

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const res = await apiClient.post('/assessment/generate', formData);
      onResult(res.data);
      onClose();
    } catch (err) {
      console.error("Assessment Failed", err);
      alert("Failed to generate assessment.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Manual Health Assessment</DialogTitle>
      <DialogContent dividers>
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Auto-Calculated BMI: {bmi}
          </Typography>
        </Box>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={4}>
            <TextField fullWidth label="Age" name="age" type="number" value={formData.age} onChange={handleChange} />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <TextField select fullWidth label="Gender" name="gender" value={formData.gender} onChange={handleChange}>
              <MenuItem value="Male">Male</MenuItem>
              <MenuItem value="Female">Female</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
             <TextField fullWidth label="Height (cm)" name="height_cm" type="number" value={formData.height_cm} onChange={handleChange} />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
             <TextField fullWidth label="Weight (kg)" name="weight_kg" type="number" value={formData.weight_kg} onChange={handleChange} />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
             <TextField fullWidth label="Sleep (Hours)" name="sleep_hours" type="number" value={formData.sleep_hours} onChange={handleChange} />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
             <TextField fullWidth label="Daily Steps" name="daily_steps" type="number" value={formData.daily_steps} onChange={handleChange} />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
             <TextField fullWidth label="Systolic BP" name="systolic_bp" type="number" value={formData.systolic_bp} onChange={handleChange} />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
             <TextField fullWidth label="Diastolic BP" name="diastolic_bp" type="number" value={formData.diastolic_bp} onChange={handleChange} />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
             <TextField fullWidth label="Fasting Blood Sugar" name="fasting_blood_sugar" type="number" value={formData.fasting_blood_sugar} onChange={handleChange} />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
             <TextField fullWidth label="HbA1c" name="hba1c" type="number" value={formData.hba1c} onChange={handleChange} />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
             <TextField fullWidth label="Local AQI" name="aqi" type="number" value={formData.aqi} onChange={handleChange} />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
             <TextField fullWidth label="Daily Calories" name="daily_calories" type="number" value={formData.daily_calories} onChange={handleChange} />
          </Grid>
          <Grid item xs={12} sm={12} md={4}>
            <TextField select fullWidth label="Exercise Frequency" name="exercise_frequency" value={formData.exercise_frequency} onChange={handleChange}>
              <MenuItem value="Never">Never</MenuItem>
              <MenuItem value="Occasionally">Occasionally</MenuItem>
              <MenuItem value="Regularly">Regularly</MenuItem>
            </TextField>
          </Grid>
          {dynamicFields.map(field => (
            <Grid item xs={12} sm={6} md={4} key={field}>
              <TextField 
                fullWidth 
                label={field.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())} 
                name={field} 
                type="number" 
                value={formData[field] || ''} 
                onChange={handleChange} 
              />
            </Grid>
          ))}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="inherit" disabled={loading}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" disabled={loading}>
          {loading ? <CircularProgress size={24} /> : "Generate Assessment"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ManualAssessmentModal;
