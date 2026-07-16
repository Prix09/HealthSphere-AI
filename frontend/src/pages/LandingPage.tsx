import React, { useState } from 'react';
import { Box, Typography, Button, Container, Card, useTheme, alpha, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions, TextField, CircularProgress, IconButton } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Analytics, Security, Speed, AutoGraph, LocalHospital, MonitorHeart } from '@mui/icons-material';
import { apiClient } from '../api/client';
import { useThemeContext } from '../context/ThemeContext';
import { Brightness4, Brightness7 } from '@mui/icons-material';

const footerContent: Record<string, string> = {
  'Analytics': 'HealthSphere Analytics provides real-time, interactive dashboards that aggregate your biometrics across multiple wearable devices, delivering instant clarity on your physiological trends. You can track minute-by-minute fluctuations in your vitals to optimize your daily routine and spot long-term patterns.',
  'Machine Learning': 'Our proprietary ML engines use continuous telemetry to predict acute health events before they happen, giving you unparalleled proactive insights into your longevity. Using ensemble models, we continuously analyze sleep, activity, and environmental factors to generate a dynamic risk score.',
  'Data Pipelines': 'Built on ultra-low latency architecture, our data pipelines securely ingest and normalize massive volumes of multi-modal health data instantly. Whether uploading CSVs or streaming via API, our pipelines handle schema enforcement and data cleaning on the fly.',
  'Security': 'We employ military-grade AES-256 encryption, zero-knowledge architecture, and strict RBAC controls to ensure your health data remains unequivocally yours. All predictive processing happens within isolated, ephemeral containers to guarantee data privacy.',
  'About Us': 'HealthSphere AI was founded on the belief that predictive intelligence is the future of human longevity. We are an interdisciplinary team of clinicians, ML engineers, and data scientists dedicated to shifting healthcare from reactive to proactive.',
  'Careers': 'Join us in building the intelligence layer for human health. We are hiring world-class engineers, medical professionals, and designers. We offer competitive equity, remote flexibility, and the chance to work on life-saving technology. Check out our open roles.',
  'Blog': 'Explore our latest research, feature updates, and deep dives into the intersection of machine learning and clinical telemetry on the HealthSphere Blog. Stay updated on our breakthrough algorithmic models and partnerships.',
  'Contact': 'Need to reach out? Contact our support team at hello@healthsphere.ai for enterprise sales, partnership inquiries, or general support. We typically respond to all inquiries within 24 hours.'
};

export const LandingPage: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { toggleTheme, mode } = useThemeContext();

  const [modalOpen, setModalOpen] = useState(false);
  const [modalTitle, setModalTitle] = useState('');
  const [modalText, setModalText] = useState('');
  
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFooterClick = (item: string) => {
    setModalTitle(item);
    setModalText(footerContent[item] || 'More information coming soon.');
    setModalOpen(true);
  };

  const handleSubscribe = async () => {
    if (!email) return;
    setLoading(true);
    try {
      await apiClient.post('/analytics/subscribe', { email });
      setModalTitle('Subscription Successful!');
      setModalText(`A real email has been dispatched to ${email} (via the backend SMTP server configuration) containing specifics about HealthSphere Company.\n\nThe email also includes a prompt asking if you would like to receive our daily blogs update!`);
      setModalOpen(true);
      setEmail('');
    } catch (e) {
      console.error("Subscription error", e);
      alert("Failed to subscribe. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const features = [
    { icon: <Analytics fontSize="large" />, title: 'Real-time Analytics', desc: 'Monitor your health metrics in real-time with enterprise-grade dashboards and millisecond latency.' },
    { icon: <AutoGraph fontSize="large" />, title: 'Predictive Insights', desc: 'Leverage cutting-edge Machine Learning models for proactive health forecasting and risk assessment.' },
    { icon: <Speed fontSize="large" />, title: 'High Performance', desc: 'Built on a modern stack capable of processing massive health datasets instantly without bottlenecks.' },
    { icon: <Security fontSize="large" />, title: 'Enterprise Security', desc: 'Your data is secured with industry-leading AES-256 encryption and strict RBAC access controls.' },
    { icon: <MonitorHeart fontSize="large" />, title: 'Continuous Monitoring', desc: 'Integrate directly with wearable APIs to stream and analyze continuous biometric telemetry.' },
    { icon: <LocalHospital fontSize="large" />, title: 'Clinical Precision', desc: 'Designed with healthcare professionals to ensure models meet clinical standards of accuracy.' },
  ];

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'transparent', overflowX: 'hidden' }}>
      
      {/* Background Glow Orbs */}
      <Box sx={{
        position: 'absolute', top: '-10%', left: '-5%', width: '40vw', height: '40vw',
        background: `radial-gradient(circle, rgba(0, 245, 160, 0.15) 0%, transparent 70%)`,
        zIndex: 0, borderRadius: '50%', filter: 'blur(60px)', pointerEvents: 'none'
      }} />
      <Box sx={{
        position: 'absolute', top: '20%', right: '-10%', width: '30vw', height: '30vw',
        background: `radial-gradient(circle, rgba(0, 210, 255, 0.12) 0%, transparent 70%)`,
        zIndex: 0, borderRadius: '50%', filter: 'blur(60px)', pointerEvents: 'none'
      }} />

      {/* Floating Navbar */}
      <Box sx={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 1000,
        py: 2, px: { xs: 2, md: 6 },
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        backgroundColor: 'rgba(2, 24, 21, 0.6)',
        backdropFilter: 'blur(20px)',
        borderBottom: `1px solid rgba(255, 255, 255, 0.05)`
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, cursor: 'pointer' }} onClick={() => navigate('/')}>
          <img src="/logo.png" alt="Logo" style={{ width: 40, height: 40, borderRadius: 8 }} />
          <Typography variant="h5" className="neon-text" sx={{ fontWeight: 800, letterSpacing: '-0.5px' }}>
            HealthSphere
          </Typography>
        </Box>
        <Box sx={{ gap: 2, display: 'flex', alignItems: 'center' }}>
          <IconButton color="inherit" onClick={toggleTheme}>
            {mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
          </IconButton>
          <Button variant="text" sx={{ fontWeight: 600, color: theme.palette.text.primary, display: { xs: 'none', sm: 'block' } }} onClick={() => navigate('/login')}>
            Sign In
          </Button>
          <Button variant="contained" sx={{ 
            borderRadius: '8px', px: 3, fontWeight: 600, textTransform: 'none', 
            background: 'linear-gradient(90deg, #00F5A0, #00D2FF)', color: '#021815',
            boxShadow: '0 0 15px rgba(0, 245, 160, 0.3)'
          }} onClick={() => navigate('/signup')}>
            Get Started
          </Button>
        </Box>
      </Box>

      {/* Hero Section */}
      <Container maxWidth="lg" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', pt: { xs: 16, md: 24 }, pb: 10, position: 'relative', zIndex: 1 }}>
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 8, alignItems: 'center' }}>
          <Box>
            <Box sx={{ display: 'inline-block', px: 2, py: 0.5, borderRadius: '20px', border: `1px solid rgba(0, 245, 160, 0.3)`, backgroundColor: 'rgba(0, 245, 160, 0.05)', mb: 3 }}>
              <Typography variant="caption" sx={{ fontWeight: 700, color: '#00F5A0', textTransform: 'uppercase', letterSpacing: '1px' }}>
                v2.0 is now live
              </Typography>
            </Box>
            <Typography variant="h1" sx={{ fontWeight: 800, color: theme.palette.text.primary, lineHeight: 1.1, fontSize: { xs: '2.5rem', md: '4.5rem' }, letterSpacing: '-2px', mb: 3 }}>
              Intelligence Layer for <Typography component="span" className="neon-text" sx={{ fontSize: 'inherit', fontWeight: 'inherit' }}>Human Health</Typography>
            </Typography>
            <Typography variant="h6" color="text.secondary" component="p" sx={{ mb: 5, lineHeight: 1.7, fontWeight: 400, maxWidth: '90%' }}>
              A powerful, real-time predictive analytics platform engineered for scale. Ingest, analyze, and visualize complex biometric telemetry with clinical-grade machine learning.
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button variant="contained" size="large" sx={{ 
                py: 1.5, px: 4, fontSize: '1rem', borderRadius: '10px', fontWeight: 600, textTransform: 'none', 
                background: `linear-gradient(90deg, #00F5A0, #00D2FF)`, color: '#021815',
                '&:hover': { transform: 'translateY(-2px)', boxShadow: `0 8px 20px rgba(0, 245, 160, 0.4)` }, transition: 'all 0.2s' 
              }} onClick={() => navigate('/signup')}>
                Start Building Free
              </Button>
              <Button variant="outlined" size="large" className="glass-panel" sx={{ 
                py: 1.5, px: 4, fontSize: '1rem', borderRadius: '10px', fontWeight: 600, textTransform: 'none', 
                borderColor: 'rgba(255, 255, 255, 0.1)', color: theme.palette.text.primary, 
                '&:hover': { borderColor: 'rgba(255, 255, 255, 0.2)', backgroundColor: 'rgba(255, 255, 255, 0.05)' } 
              }} onClick={() => navigate('/login')}>
                View Dashboard
              </Button>
            </Box>
          </Box>
          
          <Box>
            {/* Abstract UI Graphic */}
            <Box className="glass-panel" sx={{
              position: 'relative', width: '100%', height: '450px',
              borderRadius: '24px',
              overflow: 'hidden', p: 3, display: 'flex', flexDirection: 'column', gap: 2
            }}>
              {/* Fake UI Header */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, borderBottom: `1px solid rgba(255,255,255,0.05)`, pb: 2 }}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: '#ef4444' }} />
                  <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: '#f59e0b' }} />
                  <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: '#10b981' }} />
                </Box>
                <Typography variant="caption" sx={{ fontWeight: 600, color: 'text.secondary' }}>Metrics Dashboard</Typography>
              </Box>
              
              {/* Fake UI Cards */}
              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                {[1, 2].map((i) => (
                  <Box key={i} sx={{ flex: 1, height: 80, borderRadius: '12px', bgcolor: 'rgba(0, 245, 160, 0.05)', border: `1px solid rgba(0, 245, 160, 0.1)`, p: 2, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                    <Box sx={{ width: '40%', height: 8, bgcolor: 'rgba(0, 245, 160, 0.2)', borderRadius: 4, mb: 1.5 }} />
                    <Box sx={{ width: '70%', height: 16, bgcolor: 'rgba(0, 245, 160, 0.4)', borderRadius: 4 }} />
                  </Box>
                ))}
              </Box>

              {/* Fake UI Chart */}
              <Box sx={{ flex: 1, borderRadius: '12px', bgcolor: 'rgba(255, 255, 255, 0.02)', border: `1px solid rgba(255, 255, 255, 0.05)`, position: 'relative', overflow: 'hidden' }}>
                <Box sx={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: '70%', background: `linear-gradient(180deg, transparent 0%, rgba(0, 245, 160, 0.1) 100%)` }} />
                <svg width="100%" height="100%" preserveAspectRatio="none" style={{ position: 'absolute', bottom: 0 }}>
                  <path d="M0,100 C50,80 100,120 150,60 C200,0 250,90 300,50 L300,150 L0,150 Z" fill="rgba(0, 245, 160, 0.1)" />
                  <path d="M0,100 C50,80 100,120 150,60 C200,0 250,90 300,50" fill="none" stroke="#00F5A0" strokeWidth="3" />
                </svg>
              </Box>
            </Box>
          </Box>
        </Box>

        {/* Features Section */}
        <Box sx={{ mt: 20, position: 'relative', zIndex: 1 }}>
          <Box sx={{ textAlign: 'center', mb: 8 }}>
            <Typography variant="h3" sx={{ fontWeight: 800, mb: 2, letterSpacing: '-0.5px' }}>
              Built for Scale and Precision
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ fontWeight: 400, maxWidth: 600, mx: 'auto' }}>
              Everything you need to process, analyze, and act upon health data in real-time.
            </Typography>
          </Box>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' }, gap: 4 }}>
            {features.map((f, i) => (
              <Card key={i} className="glass-panel" sx={{ 
                height: '100%', 
                p: 3, 
                borderRadius: '16px',
                transition: 'all 0.3s ease',
                '&:hover': { 
                  transform: 'translateY(-5px)', 
                  boxShadow: `0 20px 40px rgba(0, 245, 160, 0.1) !important`,
                  borderColor: 'rgba(0, 245, 160, 0.3) !important',
                } 
              }}>
                <Box sx={{ 
                  mb: 3, p: 2, 
                  display: 'inline-flex',
                  borderRadius: '12px', 
                  backgroundColor: 'rgba(0, 245, 160, 0.1)',
                  color: '#00F5A0'
                }}>
                  {f.icon}
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.5 }}>
                  {f.title}
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                  {f.desc}
                </Typography>
              </Card>
            ))}
          </Box>
        </Box>
        
        {/* CTA Section */}
        <Box sx={{ 
          mt: 20, mb: 10, p: { xs: 4, md: 8 }, 
          borderRadius: '24px',
          background: `linear-gradient(135deg, rgba(0, 245, 160, 0.1), rgba(0, 210, 255, 0.1))`,
          border: '1px solid rgba(0, 245, 160, 0.2)',
          textAlign: 'center',
          boxShadow: `0 20px 40px rgba(0, 245, 160, 0.1)`
        }}>
          <Typography variant="h3" sx={{ fontWeight: 800, mb: 3 }}>
            Ready to transform your health analytics?
          </Typography>
          <Typography variant="h6" sx={{ mb: 5, opacity: 0.9, fontWeight: 400, maxWidth: 600, mx: 'auto', color: 'text.secondary' }}>
            Join forward-thinking enterprises building the next generation of predictive healthcare on HealthSphere AI.
          </Typography>
          <Button variant="contained" size="large" sx={{ 
            py: 2, px: 6, fontSize: '1.1rem', borderRadius: '12px', fontWeight: 700, 
            background: 'linear-gradient(90deg, #00F5A0, #00D2FF)', color: '#021815',
            '&:hover': { transform: 'scale(1.02)' }
          }} onClick={() => navigate('/signup')}>
            Create Your Account
          </Button>
        </Box>
      </Container>
      
      {/* Footer */}
      <Box className="glass-panel" sx={{ py: 6, borderTop: `1px solid rgba(255,255,255,0.05)`, mt: 'auto', borderRadius: 0 }}>
        <Container maxWidth="lg">
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr 1fr 2fr' }, gap: 4, mb: 4 }}>
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                <img src="/logo.png" alt="Logo" style={{ width: 32, height: 32, borderRadius: 6 }} />
                <Typography variant="h6" className="neon-text" sx={{ fontWeight: 800 }}>HealthSphere</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 300, lineHeight: 1.6 }}>
                The world's most advanced platform for predictive health intelligence and real-time telemetry processing.
              </Typography>
            </Box>
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, textTransform: 'uppercase', color: theme.palette.mode === 'dark' ? '#E2E8F0' : theme.palette.text.primary }}>Platform</Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                {['Analytics', 'Machine Learning', 'Data Pipelines', 'Security'].map(item => (
                  <Typography key={item} variant="body2" color="text.secondary" onClick={() => handleFooterClick(item)} sx={{ cursor: 'pointer', '&:hover': { color: theme.palette.mode === 'dark' ? '#00F5A0' : theme.palette.primary.main } }}>{item}</Typography>
                ))}
              </Box>
            </Box>
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, textTransform: 'uppercase', color: theme.palette.mode === 'dark' ? '#E2E8F0' : theme.palette.text.primary }}>Company</Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                {['About Us', 'Careers', 'Blog', 'Contact'].map(item => (
                  <Typography key={item} variant="body2" color="text.secondary" onClick={() => handleFooterClick(item)} sx={{ cursor: 'pointer', '&:hover': { color: theme.palette.mode === 'dark' ? '#00F5A0' : theme.palette.primary.main } }}>{item}</Typography>
                ))}
              </Box>
            </Box>
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, textTransform: 'uppercase', color: theme.palette.mode === 'dark' ? '#E2E8F0' : theme.palette.text.primary }}>Stay Updated</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Subscribe to our newsletter for the latest AI health updates.
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Box component="input" placeholder="Enter your email" value={email} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)} sx={{ 
                  flex: 1, p: 1.5, borderRadius: '8px', border: `1px solid ${theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.2)'}`,
                  backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.02)', color: theme.palette.text.primary,
                  outline: 'none', '&:focus': { borderColor: theme.palette.mode === 'dark' ? '#00F5A0' : theme.palette.primary.main }
                }} />
                <Button variant="contained" onClick={handleSubscribe} disabled={loading} sx={{ borderRadius: '8px', background: 'linear-gradient(90deg, #00F5A0, #00D2FF)', color: '#021815' }}>
                  {loading ? <CircularProgress size={24} /> : 'Subscribe'}
                </Button>
              </Box>
            </Box>
          </Box>
          <Box sx={{ borderTop: `1px solid ${theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.1)'}`, pt: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
            <Typography variant="body2" color="text.secondary">
              &copy; {new Date().getFullYear()} HealthSphere AI Inc. All rights reserved.
            </Typography>
            <Box sx={{ display: 'flex', gap: 3 }}>
              <Typography variant="body2" color="text.secondary" sx={{ cursor: 'pointer', '&:hover': { color: theme.palette.text.primary } }}>Privacy Policy</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ cursor: 'pointer', '&:hover': { color: theme.palette.text.primary } }}>Terms of Service</Typography>
            </Box>
          </Box>
        </Container>
      </Box>
      <Dialog open={modalOpen} onClose={() => setModalOpen(false)} maxWidth="sm" fullWidth sx={{ '& .MuiDialog-paper': { background: theme.palette.mode === 'dark' ? '#021815' : '#fff', border: `1px solid ${theme.palette.mode === 'dark' ? 'rgba(0, 245, 160, 0.2)' : 'rgba(0,0,0,0.1)'}`, borderRadius: 3 } }}>
        <DialogTitle sx={{ color: theme.palette.text.primary, fontWeight: 'bold' }}>{modalTitle}</DialogTitle>
        <DialogContent dividers sx={{ borderColor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)' }}>
          <DialogContentText sx={{ color: theme.palette.text.secondary, whiteSpace: 'pre-wrap' }}>
            {modalText}
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setModalOpen(false)} variant="contained" sx={{ background: 'linear-gradient(90deg, #00F5A0, #00D2FF)', color: '#021815', fontWeight: 'bold' }}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
