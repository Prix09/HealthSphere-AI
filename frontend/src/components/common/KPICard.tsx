import React from 'react';
import { Card, CardContent, Typography, Box, Tooltip, IconButton } from '@mui/material';
import { ArrowUpward, ArrowDownward, InfoOutlined } from '@mui/icons-material';

interface KPICardProps {
  title: string;
  value: string | number;
  trend?: number;
  trendLabel?: string;
  icon?: React.ReactNode;
  tooltipText?: string;
}

export const KPICard: React.FC<KPICardProps> = ({ title, value, trend, trendLabel, icon, tooltipText }) => {
  const isPositive = trend !== undefined && trend >= 0;
  
  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography color="text.secondary" variant="subtitle2" sx={{ fontWeight: '600', textTransform: 'uppercase' }}>
              {title}
            </Typography>
            {tooltipText && (
              <Tooltip title={tooltipText} placement="top" arrow>
                <IconButton size="small" sx={{ ml: 0.5, p: 0 }}>
                  <InfoOutlined fontSize="small" sx={{ color: 'text.secondary' }} />
                </IconButton>
              </Tooltip>
            )}
          </Box>
          {icon && (
            <Box sx={{ color: 'primary.main', opacity: 0.8 }}>
              {icon}
            </Box>
          )}
        </Box>
        <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
          {value}
        </Typography>
        
        {trend !== undefined && (
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 'auto' }}>
            {isPositive ? (
              <ArrowUpward sx={{ color: 'success.main', fontSize: 16, mr: 0.5 }} />
            ) : (
              <ArrowDownward sx={{ color: 'error.main', fontSize: 16, mr: 0.5 }} />
            )}
            <Typography 
              variant="body2" 
              color={isPositive ? 'success.main' : 'error.main'}
              sx={{ fontWeight: '600' }}
            >
              {Math.abs(trend)}%
            </Typography>
            {trendLabel && (
              <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                {trendLabel}
              </Typography>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
