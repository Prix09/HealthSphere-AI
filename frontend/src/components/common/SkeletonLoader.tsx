import React from 'react';
import { Card, CardContent, Skeleton, Box, Grid } from '@mui/material';

export const KPISkeleton: React.FC = () => (
  <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
    <CardContent>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Skeleton variant="text" width="40%" height={24} />
        <Skeleton variant="circular" width={24} height={24} />
      </Box>
      <Skeleton variant="text" width="60%" height={60} />
      <Skeleton variant="text" width="30%" height={24} sx={{ mt: 'auto' }} />
    </CardContent>
  </Card>
);

export const ChartSkeleton: React.FC = () => (
  <Card sx={{ height: 400 }}>
    <CardContent>
      <Skeleton variant="text" width="30%" height={32} sx={{ mb: 2 }} />
      <Skeleton variant="rectangular" width="100%" height={300} sx={{ borderRadius: 1 }} />
    </CardContent>
  </Card>
);

export const DashboardSkeleton: React.FC = () => (
  <Box>
    <Skeleton variant="text" width="20%" height={40} sx={{ mb: 3 }} />
    <Grid container spacing={3}>
      {[1, 2, 3, 4].map((i) => (
        <Grid size={{ xs: 12, sm: 6, md: 3 }} key={i}>
          <Skeleton variant="rectangular" height={140} sx={{ borderRadius: 2 }} />
        </Grid>
      ))}
      <Grid size={{ xs: 12, md: 8 }}>
        <Skeleton variant="rectangular" height={400} sx={{ borderRadius: 2 }} />
      </Grid>
      <Grid size={{ xs: 12, md: 4 }}>
        <Skeleton variant="rectangular" height={400} sx={{ borderRadius: 2 }} />
      </Grid>
    </Grid>
  </Box>
);
