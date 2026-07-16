import React from 'react';
import { Card, CardContent, Typography, Box, Alert, AlertTitle, Chip } from '@mui/material';

interface AssessmentResultCardProps {
  result: any;
}

const AssessmentResultCard: React.FC<AssessmentResultCardProps> = ({ result }) => {
  if (!result) return null;

  const { insight, derived_metrics, prediction, alerts, isDailyInsight } = result;

  // Attempt to parse out the insight structure if it contains specific lines (basic formatting)
  // Usually the AI output is a markdown-like string or plain text. We just render it.

  const isHighRisk = prediction?.prediction === 1 || String(prediction?.prediction).toLowerCase().includes('high');

  return (
    <Card sx={{ mt: 3, boxShadow: '0 8px 32px rgba(0,0,0,0.1)', borderRadius: '16px' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
            {isDailyInsight ? "AI Health Summary" : "Instant AI Insight"}
          </Typography>
          {derived_metrics?.bmi && (
            <Chip 
              label={`BMI: ${derived_metrics.bmi}`} 
              color="primary" 
              variant="outlined" 
            />
          )}
        </Box>
        
        {alerts && alerts.length > 0 ? (
          <Box sx={{ mb: 3 }}>
            {alerts.map((a: any, i: number) => (
              <Alert key={i} severity={a.severity === 'critical' || a.severity === 'high' ? 'error' : 'warning'} sx={{ mb: 1 }}>
                <AlertTitle>{a.alert_type.replace(/_/g, ' ').toUpperCase()}</AlertTitle>
                <span dangerouslySetInnerHTML={{ __html: a.message }} />
              </Alert>
            ))}
          </Box>
        ) : (
          !isDailyInsight && (
            <Alert severity={isHighRisk ? "warning" : "success"} sx={{ mb: 3 }}>
              <AlertTitle>{isHighRisk ? "Elevated Risk Detected" : "Health Status Stable"}</AlertTitle>
              Based on the manual parameters provided, your prediction model indicates a {isHighRisk ? "High" : "Low"} risk.
            </Alert>
          )
        )}

        <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: '8px' }}>
          <Typography 
            variant="body1" 
            sx={{ lineHeight: 1.8 }}
            dangerouslySetInnerHTML={{ __html: (insight || '').replace(/\n/g, '<br/>') }}
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default AssessmentResultCard;
