'use client';

import { ChakraProvider, extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
  colors: {
    brand: {
      // BYMB Primary Colors
      deepBlue: '#1B365D',
      gold: '#D4AF37',
      white: '#FFFFFF',
      
      // BYMB Secondary Colors
      gulfTeal: '#2E8B8B',
      warmGray: '#6B7280',
      successGreen: '#059669',
      alertRed: '#DC2626',
      
      // Legacy colors for compatibility
      pink: '#eb088a',
      purple: '#8a08eb',
    },
    // BYMB Brand Color Scales
    bymb: {
      50: '#F0F4F8',
      100: '#D9E2EC',
      200: '#BCCCDC',
      300: '#9FB3C8',
      400: '#829AB1',
      500: '#1B365D',
      600: '#102A47',
      700: '#0B1E33',
      800: '#06141F',
      900: '#030A0F',
    },
    accent: {
      50: '#FFFBF0',
      100: '#FEF3C7',
      200: '#FDE68A',
      300: '#FCD34D',
      400: '#FBBF24',
      500: '#D4AF37',
      600: '#B8941F',
      700: '#9C7914',
      800: '#805E0B',
      900: '#644405',
    }
  },
  fonts: {
    heading: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
    body: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
    accent: 'Playfair Display, Georgia, serif',
  },
  fontWeights: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  styles: {
    global: {
      body: {
        bg: 'white',
        color: 'gray.800',
      },
      'html, body': {
        fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
      },
    },
  },
  components: {
    Button: {
      variants: {
        bymb: {
          bg: 'brand.deepBlue',
          color: 'white',
          _hover: {
            bg: 'bymb.600',
            transform: 'translateY(-1px)',
          },
          _active: {
            bg: 'bymb.700',
            transform: 'translateY(0)',
          },
        },
        bymbGold: {
          bg: 'brand.gold',
          color: 'brand.deepBlue',
          fontWeight: 'semibold',
          _hover: {
            bg: 'accent.600',
            transform: 'translateY(-1px)',
          },
          _active: {
            bg: 'accent.700',
            transform: 'translateY(0)',
          },
        },
      },
    },
    Card: {
      baseStyle: {
        container: {
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          borderRadius: '12px',
        },
      },
    },
  },
});

export function Providers({ children }: { children: React.ReactNode }) {
  return <ChakraProvider theme={theme}>{children}</ChakraProvider>;
}
