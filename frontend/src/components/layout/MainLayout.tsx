import React, { useState } from 'react';
import { Box, Drawer, AppBar, Toolbar, List, Typography, Divider, IconButton, ListItem, ListItemButton, ListItemIcon, ListItemText, useTheme } from '@mui/material';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { 
  Menu as MenuIcon, 
  Dashboard, 
  Analytics, 
  Storage, 
  Warning, 
  Settings, 
  Logout, 
  Brightness4, 
  Brightness7,
  ModelTraining
} from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';
import { useThemeContext } from '../../context/ThemeContext';

const drawerWidth = 260;

export const MainLayout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();
  const { toggleTheme, mode } = useThemeContext();
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const navItems = [
    { text: 'Dashboard', icon: <Dashboard />, path: '/dashboard' },
    { text: 'Analytics', icon: <Analytics />, path: '/dashboard/analytics' },
    { text: 'Model Registry', icon: <ModelTraining />, path: '/dashboard/models' },
    { text: 'Datasets', icon: <Storage />, path: '/dashboard/datasets' },
    { text: 'Alerts', icon: <Warning />, path: '/dashboard/alerts' },
  ];

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box 
        onClick={() => navigate('/')} 
        sx={{ p: 3, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}
      >
        <img src="/logo.png" alt="Logo" style={{ width: 32, height: 32, marginRight: 12, borderRadius: 8 }} />
        <Typography variant="h6" className="neon-text" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
          HealthSphere
        </Typography>
      </Box>
      <Divider />
      <List sx={{ px: 2, flexGrow: 1 }}>
        {navItems.map((item) => {
          const active = location.pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
              <ListItemButton
                selected={active}
                onClick={() => navigate(item.path)}
               sx={{
                  borderRadius: 2,
                  ...(active && {
                    bgcolor: 'rgba(0, 245, 160, 0.1)',
                    color: '#00F5A0',
                    border: '1px solid rgba(0, 245, 160, 0.3)',
                    '&:hover': {
                      bgcolor: 'rgba(0, 245, 160, 0.2)',
                    },
                    '& .MuiListItemIcon-root': {
                      color: '#00F5A0',
                    },
                  }),
                  ...(!active && {
                    '&:hover': {
                      bgcolor: 'rgba(255, 255, 255, 0.05)',
                    }
                  })
                }}
            >
                <ListItemIcon sx={{ minWidth: 40, color: active ? 'inherit' : 'text.secondary' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text} 
                 sx={{ '& .MuiListItemText-primary': { fontWeight: active ? 600 : 500 } }} 
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
      <Divider />
      <List sx={{ px: 2 }}>
        <ListItem disablePadding sx={{ mt: 1 }}>
          <ListItemButton onClick={logout} sx={{ borderRadius: 2, color: 'error.main', '&:hover': { bgcolor: 'rgba(244, 67, 54, 0.1)' } }}>
            <ListItemIcon sx={{ minWidth: 40, color: 'error.main' }}>
              <Logout />
            </ListItemIcon>
            <ListItemText primary="Sign out" />
          </ListItemButton>
        </ListItem>
      </List>
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          {user?.email}
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'transparent' }}>
      <AppBar
        position="fixed"
        elevation={0}
       sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          bgcolor: 'rgba(2, 24, 21, 0.5)',
          backdropFilter: 'blur(20px)',
          borderBottom: `1px solid rgba(255,255,255,0.05)`,
          color: 'text.primary',
        }}
    >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
           sx={{ mr: 2, display: { sm: 'none' } }}
        >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            {navItems.find(i => i.path === location.pathname)?.text || 'Platform'}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton color="inherit" onClick={toggleTheme}>
              {mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
       sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
    >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, 
          }}
         sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
      >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
         sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth, borderRight: `1px solid ${theme.palette.divider}` },
          }}
          open
      >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)` }, overflowX: 'hidden' }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
};
