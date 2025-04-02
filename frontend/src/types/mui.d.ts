import { Theme } from '@mui/material/styles';
import { GridProps as MuiGridProps } from '@mui/material/Grid';

declare module '@mui/material/Grid' {
  interface GridProps extends MuiGridProps {
    item?: boolean;
    container?: boolean;
    component?: React.ElementType;
  }
}

export {}; 