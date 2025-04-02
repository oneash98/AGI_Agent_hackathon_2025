import React, { useState, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Button,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import type { Theme } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DeleteIcon from '@mui/icons-material/Delete';
import { Message, AnalysisFile } from '../types/analysis';
import axios from 'axios';

const exampleQuestions = [
  '이 데이터의 주요 특징은 무엇인가요?',
  '데이터의 이상치가 있나요?',
  '시계열 분석 결과를 보여주세요.',
];

const dummyResponses = [
  {
    question: '이 데이터의 주요 특징은 무엇인가요?',
    response: `분석한 데이터의 주요 특징은 다음과 같습니다:

1. 기술 통계량
- 평균: 45.3
- 중앙값: 42.1
- 표준편차: 15.2

2. 분포 특성
- 정규분포에 가까운 형태
- 약간의 우측 편향성 관찰
- 극단값 3개 발견

3. 시계열 특성
- 계절성 패턴 존재
- 상승 추세 확인
- 주기성: 약 12개월

자세한 분석이 필요하신 부분이 있다면 말씀해 주세요.`,
  },
  {
    question: '데이터의 이상치가 있나요?',
    response: `데이터 이상치 분석 결과입니다:

1. 이상치 탐지 방법
- IQR(Inter Quartile Range) 방법 사용
- Z-score 분석
- LOF(Local Outlier Factor) 적용

2. 발견된 이상치
- 총 5개의 이상치 발견
- 신뢰구간(95%) 벗어난 값: 3개
- 극단적 이상치: 2개

3. 이상치 특성
- 주로 상위 극단값에 분포
- 특정 시점에 집중(2024년 1월)
- 패턴성 없는 무작위성

이상치 처리 방안에 대해 논의가 필요하시다면 말씀해 주세요.`,
  },
  {
    question: '시계열 분석 결과를 보여주세요.',
    response: `시계열 분석 결과를 공유드립니다:

1. 추세 분석
- 전반적인 상승 추세
- 연간 성장률: 5.2%
- 변곡점: 2023년 3분기

2. 계절성
- 뚜렷한 계절 패턴 존재
- 피크: 매년 4분기
- 저점: 매년 2분기 초반

3. 예측 모델 결과
- ARIMA 모델 적용
- 6개월 예측 신뢰도: 85%
- 주요 변동 요인 식별

추가적인 시계열 분석이 필요하시다면 구체적으로 말씀해 주세요.`,
  },
];

const API_BASE_URL = 'http://localhost:8000';

const AnalysisPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: '안녕하세요! 데이터 분석을 도와드리겠습니다. 분석하실 파일을 업로드해주세요.',
      sender: 'ai',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [files, setFiles] = useState<AnalysisFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isBackendAvailable, setIsBackendAvailable] = useState(true);

  // Check backend availability
  React.useEffect(() => {
    const checkBackend = async () => {
      try {
        await axios.get(`${API_BASE_URL}/api/summary`);
        setIsBackendAvailable(true);
      } catch (error) {
        console.log('Backend not available, falling back to dummy data');
        setIsBackendAvailable(false);
      }
    };
    checkBackend();
  }, []);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFiles = event.target.files;
    if (!uploadedFiles) return;

    const newFiles: AnalysisFile[] = Array.from(uploadedFiles).map((file, index) => ({
      id: Date.now() + index,
      name: file.name,
      size: file.size,
      type: file.type,
      uploadedAt: new Date(),
    }));

    setFiles((prev) => [...prev, ...newFiles]);

    if (isBackendAvailable) {
      try {
        const formData = new FormData();
        Array.from(uploadedFiles).forEach((file) => {
          formData.append('files', file);
        });

        const response = await axios.post(`${API_BASE_URL}/api/analyze`, formData);
        const fileMessage: Message = {
          id: messages.length + 1,
          text: `파일 분석 결과:\n${JSON.stringify(response.data.data, null, 2)}`,
          sender: 'ai',
          timestamp: new Date(),
          files: Array.from(uploadedFiles),
        };
        setMessages((prev) => [...prev, fileMessage]);
      } catch (error) {
        console.error('Error uploading files:', error);
        // Fallback to dummy behavior
        const fileMessage: Message = {
          id: messages.length + 1,
          text: `파일이 업로드되었습니다: ${newFiles.map(f => f.name).join(', ')}`,
          sender: 'ai',
          timestamp: new Date(),
          files: Array.from(uploadedFiles),
        };
        setMessages((prev) => [...prev, fileMessage]);
      }
    } else {
      // Dummy behavior
      const fileMessage: Message = {
        id: messages.length + 1,
        text: `파일이 업로드되었습니다: ${newFiles.map(f => f.name).join(', ')}`,
        sender: 'ai',
        timestamp: new Date(),
        files: Array.from(uploadedFiles),
      };
      setMessages((prev) => [...prev, fileMessage]);
    }
  };

  const handleDeleteFile = (fileId: number) => {
    setFiles((prev) => prev.filter((file) => file.id !== fileId));
  };

  const handleSend = async (text: string) => {
    if (!text.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      text: text,
      sender: 'user',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    if (isBackendAvailable) {
      try {
        let response;
        if (text.includes('진료과')) {
          response = await axios.post(`${API_BASE_URL}/api/suggest-specialty`, { query: text });
          const aiResponse = response.data.suggestion;
          setMessages((prev) => [
            ...prev,
            {
              id: prev.length + 2,
              text: aiResponse,
              sender: 'ai',
              timestamp: new Date(),
            },
          ]);
        } else {
          response = await axios.get(`${API_BASE_URL}/api/summary`);
          const aiResponse = response.data.summary;
          setMessages((prev) => [
            ...prev,
            {
              id: prev.length + 2,
              text: aiResponse,
              sender: 'ai',
              timestamp: new Date(),
            },
          ]);
        }
      } catch (error) {
        console.error('Error getting response:', error);
        // Fallback to dummy behavior
        fallbackToDummyResponse(text);
      }
    } else {
      // Use dummy response
      fallbackToDummyResponse(text);
    }

    setInput('');
  };

  const fallbackToDummyResponse = (text: string) => {
    const matchingResponse = dummyResponses.find((r) => r.question === text);
    const aiResponse = matchingResponse?.response || 
      '죄송합니다. 현재 해당 질문에 대한 상세 분석이 준비되지 않았습니다. 다른 질문을 해주시거나, 좀 더 구체적으로 문의해 주시면 감사하겠습니다.';

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: prev.length + 2,
          text: aiResponse,
          sender: 'ai',
          timestamp: new Date(),
        },
      ]);
    }, 1000);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* File Upload Section */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '600px', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              건강검진 파일 업로드
            </Typography>
            <Box sx={{ mb: 3 }}>
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                onChange={handleFileUpload}
                multiple
                accept=".csv,.xlsx,.json"
              />
              <Button
                fullWidth
                variant="outlined"
                startIcon={<CloudUploadIcon />}
                onClick={() => fileInputRef.current?.click()}
                sx={{ mb: 2 }}
              >
                파일 선택
              </Button>
              <Typography variant="body2" color="text.secondary" align="center">
                지원 형식: CSV, XLSX, JSON
              </Typography>
            </Box>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="subtitle2" gutterBottom>
              업로드된 파일
            </Typography>
            <List sx={{ flexGrow: 1, overflowY: 'auto' }}>
              {files.map((file) => (
                <ListItem key={file.id}>
                  <ListItemText
                    primary={file.name}
                    secondary={`${(file.size / 1024).toFixed(1)} KB - ${new Date(
                      file.uploadedAt
                    ).toLocaleTimeString()}`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => handleDeleteFile(file.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Chat Section */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: '600px', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              데이터 분석 어시스턴트
            </Typography>

            {/* Example Questions */}
            <Box sx={{ mb: 3, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {exampleQuestions.map((question, index) => (
                <Button
                  key={index}
                  variant="outlined"
                  size="small"
                  onClick={() => handleSend(question)}
                  sx={{
                    borderRadius: 2,
                    textTransform: 'none',
                    borderColor: 'divider',
                  }}
                >
                  {question}
                </Button>
              ))}
            </Box>

            {/* Messages Area */}
            <Box
              sx={{
                flexGrow: 1,
                overflowY: 'auto',
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
                mb: 2,
              }}
            >
              {messages.map((message) => (
                <Box
                  key={message.id}
                  sx={{
                    display: 'flex',
                    gap: 1,
                    alignItems: 'flex-start',
                    flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
                  }}
                >
                  <Avatar
                    sx={{
                      bgcolor: message.sender === 'user' ? 'primary.main' : 'secondary.main',
                      width: 32,
                      height: 32,
                    }}
                  >
                    {message.sender === 'user' ? <PersonIcon /> : <SmartToyIcon />}
                  </Avatar>
                  <Paper
                    sx={{
                      p: 2,
                      maxWidth: '70%',
                      backgroundColor: message.sender === 'user' ? 'primary.main' : 'background.paper',
                      color: message.sender === 'user' ? 'primary.contrastText' : 'text.primary',
                      borderRadius: 2,
                      whiteSpace: 'pre-wrap',
                    }}
                  >
                    <Typography variant="body1">{message.text}</Typography>
                    {message.files && (
                      <Box sx={{ mt: 1 }}>
                        {message.files.map((file, index) => (
                          <Typography
                            key={index}
                            variant="caption"
                            sx={{ display: 'block', color: 'text.secondary' }}
                          >
                            📎 {file.name} ({(file.size / 1024).toFixed(1)} KB)
                          </Typography>
                        ))}
                      </Box>
                    )}
                    <Typography
                      variant="caption"
                      sx={{
                        display: 'block',
                        mt: 1,
                        color: message.sender === 'user' ? 'primary.light' : 'text.secondary',
                      }}
                    >
                      {message.timestamp.toLocaleTimeString()}
                    </Typography>
                  </Paper>
                </Box>
              ))}
            </Box>

            {/* Input Area */}
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="메시지를 입력하세요..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend(input);
                  }
                }}
                size="small"
              />
              <IconButton
                color="primary"
                onClick={() => handleSend(input)}
                disabled={!input.trim()}
              >
                <SendIcon />
              </IconButton>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalysisPage; 