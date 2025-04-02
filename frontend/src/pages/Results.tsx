import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import WarningIcon from '@mui/icons-material/Warning';
import { useState, useEffect } from 'react';

interface AnalysisResults {
  summary: string;
  health_info: {
    [key: string]: any;
  };
  specialty: string;
}

const Results = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [results, setResults] = useState<AnalysisResults | null>(null);

  useEffect(() => {
    if (location.state?.results) {
      setResults(location.state.results);
    } else {
      navigate('/analysis');
    }
  }, [location.state, navigate]);

  if (!results) {
    return null;
  }

  const renderHealthInfo = () => {
    const items = Object.entries(results.health_info);
    return (
      <List>
        {items.map(([key, value], index) => (
          <ListItem key={index}>
            <ListItemIcon>
              {value.status === 'normal' ? (
                <CheckCircleIcon color="success" />
              ) : (
                <WarningIcon color="warning" />
              )}
            </ListItemIcon>
            <ListItemText
              primary={key}
              secondary={value.description}
              primaryTypographyProps={{
                fontWeight: value.status === 'normal' ? 'normal' : 'bold',
              }}
            />
          </ListItem>
        ))}
      </List>
    );
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 8 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          분석 결과
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {/* 요약 정보 */}
          <Box>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                검진 결과 요약
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {results.summary}
              </Typography>
            </Paper>
          </Box>

          <Box sx={{ display: 'flex', gap: 4 }}>
            {/* 상세 건강 정보 */}
            <Box sx={{ flex: '1 1 66.66%' }}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  상세 건강 정보
                </Typography>
                <Divider sx={{ mb: 2 }} />
                {renderHealthInfo()}
              </Paper>
            </Box>

            {/* 추천 진료과 */}
            <Box sx={{ flex: '1 1 33.33%' }}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  추천 진료과
                </Typography>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexDirection: 'column',
                    mt: 2,
                  }}
                >
                  <LocalHospitalIcon
                    sx={{ fontSize: 48, color: 'primary.main', mb: 2 }}
                  />
                  <Typography variant="h5" color="primary" gutterBottom>
                    {results.specialty}
                  </Typography>
                </Box>
              </Paper>

              {/* 주변 병원 찾기 버튼 */}
              <Button
                variant="contained"
                fullWidth
                sx={{ mt: 2 }}
                onClick={() => {
                  // TODO: Implement hospital search functionality
                }}
              >
                주변 병원 찾기
              </Button>
            </Box>
          </Box>
        </Box>

        {/* 새로운 분석 시작 버튼 */}
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Button
            variant="outlined"
            size="large"
            onClick={() => navigate('/analysis')}
          >
            새로운 분석 시작
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default Results; 