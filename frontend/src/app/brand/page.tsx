'use client';

import {
  Box,
  Container,
  Heading,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  VStack,
  useColorModeValue,
} from '@chakra-ui/react';

import BrandProfileOverview from '../components/brand/BrandProfileOverview';
import BrandValidationDashboard from '../components/brand/BrandValidationDashboard';
import BrandComplianceMonitor from '../components/brand/BrandComplianceMonitor';
import BrandTemplateManager from '../components/brand/BrandTemplateManager';
import BrandAssetLibrary from '../components/brand/BrandAssetLibrary';

export default function BrandManagementPage() {
  const bgColor = useColorModeValue('gray.50', 'gray.900');

  return (
    <Box minH="100vh" bg={bgColor}>
      <Container maxW="container.xl" py={8}>
        <VStack spacing={8} align="stretch">
          <Box textAlign="center">
            <Heading
              as="h1"
              size="2xl"
              color="brand.deepBlue"
              fontFamily="accent"
              mb={4}
            >
              BYMB Brand Management
            </Heading>
            <Heading
              as="h2"
              size="md"
              color="brand.warmGray"
              fontWeight="normal"
            >
              Comprehensive brand consistency and asset management system
            </Heading>
          </Box>

          <Tabs
            variant="soft-rounded"
            colorScheme="bymb"
            size="lg"
          >
            <TabList
              bg="white"
              p={2}
              borderRadius="xl"
              boxShadow="sm"
              overflowX="auto"
            >
              <Tab minW="fit-content">Brand Profile</Tab>
              <Tab minW="fit-content">Validation</Tab>
              <Tab minW="fit-content">Compliance</Tab>
              <Tab minW="fit-content">Templates</Tab>
              <Tab minW="fit-content">Assets</Tab>
            </TabList>

            <TabPanels>
              <TabPanel px={0}>
                <BrandProfileOverview />
              </TabPanel>
              <TabPanel px={0}>
                <BrandValidationDashboard />
              </TabPanel>
              <TabPanel px={0}>
                <BrandComplianceMonitor />
              </TabPanel>
              <TabPanel px={0}>
                <BrandTemplateManager />
              </TabPanel>
              <TabPanel px={0}>
                <BrandAssetLibrary />
              </TabPanel>
            </TabPanels>
          </Tabs>
        </VStack>
      </Container>
    </Box>
  );
}