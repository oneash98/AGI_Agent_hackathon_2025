import { Box, Typography, Button, Container, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import HealthAndSafetyIcon from '@mui/icons-material/HealthAndSafety';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import DescriptionIcon from '@mui/icons-material/Description';

const Home = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <DescriptionIcon sx={{ fontSize: 40, color: 'primary.main' }} />,
      title: '건강검진 결과 분석',
      description: 'AI가 건강검진 결과를 자세히 분석하여 핵심 정보를 추출합니다.',
    },
    {
      icon: <HealthAndSafetyIcon sx={{ fontSize: 40, color: 'primary.main' }} />,
      title: '맞춤형 진료과 추천',
      description: '분석된 결과를 바탕으로 적합한 진료과를 추천해드립니다.',
    },
    {
      icon: <LocalHospitalIcon sx={{ fontSize: 40, color: 'primary.main' }} />,
      title: '주변 병원 찾기',
      description: '추천된 진료과의 주변 병원을 찾아 위치 정보를 제공합니다.',
    },
  ];

  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Box
        sx={{
          pt: 8,
          pb: 6,
          textAlign: 'center',
        }}
      >
        <Typography
          component="h1"
          variant="h2"
          color="primary"
          gutterBottom
          sx={{ fontWeight: 'bold' }}
        >
          AI 건강검진 분석 도우미
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          건강검진 결과를 AI가 분석하여 맞춤형 정보를 제공해드립니다.
          <br />
          당신의 건강한 삶을 위한 첫걸음을 시작하세요.
        </Typography>
        <Button
          variant="contained"
          size="large"
          onClick={() => navigate('/analysis')}
          sx={{ mt: 4 }}
        >
          지금 시작하기
        </Button>
      </Box>

      {/* Features Section */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' }, gap: 4, mt: 4 }}>
        {features.map((feature, index) => (
          <Paper
            key={index}
            sx={{
              p: 4,
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              borderRadius: 2,
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 3,
              },
            }}
          >
            {feature.icon}
            <Typography variant="h5" component="h2" sx={{ mt: 2, mb: 2 }}>
              {feature.title}
            </Typography>
            <Typography color="text.secondary">
              {feature.description}
            </Typography>
          </Paper>
        ))}
      </Box>
    </Container>
  );
};

export default Home; 