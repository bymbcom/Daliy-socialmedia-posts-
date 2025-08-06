'use client';

import {
  Box,
  Card,
  CardBody,
  CardHeader,
  Flex,
  Grid,
  GridItem,
  Heading,
  HStack,
  VStack,
  Text,
  Badge,
  Button,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useColorModeValue,
  Icon,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Select,
  SimpleGrid,
  Switch,
  FormControl,
  FormLabel,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  CircularProgress,
  CircularProgressLabel,
  Tooltip,
} from '@chakra-ui/react';
import {
  FiShield,
  FiTrendingUp,
  FiTrendingDown,
  FiAlertTriangle,
  FiCheckCircle,
  FiXCircle,
  FiSettings,
  FiBarChart3,
  FiActivity,
  FiZap,
  FiEye,
  FiRefreshCw,
} from 'react-icons/fi';

export default function BrandComplianceMonitor() {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Mock compliance data
  const complianceOverview = {
    overallScore: 87,
    trend: '+3.2%',
    contentCompliant: 156,
    contentTotal: 178,
    criticalIssues: 3,
    lastUpdated: '5 minutes ago',
  };

  const complianceRules = [
    {
      id: 'CR-001',
      name: 'Brand Logo Presence',
      description: 'All content must include BYMB logo',
      enforcement: 'strict',
      compliance: 94,
      violations: 8,
      enabled: true,
    },
    {
      id: 'CR-002',
      name: 'Color Palette Compliance',
      description: 'Only approved brand colors allowed',
      enforcement: 'moderate',
      compliance: 89,
      violations: 15,
      enabled: true,
    },
    {
      id: 'CR-003',
      name: 'Typography Standards',
      description: 'Use approved fonts (Inter, Playfair Display)',
      enforcement: 'moderate',
      compliance: 92,
      violations: 6,
      enabled: true,
    },
    {
      id: 'CR-004',
      name: 'Voice & Tone Guidelines',
      description: 'Content must match BYMB brand voice',
      enforcement: 'flexible',
      compliance: 85,
      violations: 22,
      enabled: true,
    },
    {
      id: 'CR-005',
      name: 'Platform Specifications',
      description: 'Content optimized for target platform',
      enforcement: 'moderate',
      compliance: 91,
      violations: 12,
      enabled: true,
    },
    {
      id: 'CR-006',
      name: 'Accessibility Standards',
      description: 'WCAG AA compliance for accessibility',
      enforcement: 'flexible',
      compliance: 78,
      violations: 31,
      enabled: false,
    },
  ];

  const recentViolations = [
    {
      id: 'V-001',
      content: 'Instagram Post - Business Insight',
      rule: 'Brand Logo Presence',
      severity: 'critical',
      platform: 'Instagram',
      timestamp: '2 hours ago',
      status: 'pending',
    },
    {
      id: 'V-002',
      content: 'LinkedIn Article - Case Study',
      rule: 'Color Palette Compliance',
      severity: 'high',
      platform: 'LinkedIn',
      timestamp: '3 hours ago',
      status: 'auto-corrected',
    },
    {
      id: 'V-003',
      content: 'Twitter Post - Achievement',
      rule: 'Voice & Tone Guidelines',
      severity: 'medium',
      platform: 'Twitter',
      timestamp: '5 hours ago',
      status: 'reviewed',
    },
    {
      id: 'V-004',
      content: 'Facebook Cover Photo',
      rule: 'Platform Specifications',
      severity: 'low',
      platform: 'Facebook',
      timestamp: '1 day ago',
      status: 'resolved',
    },
  ];

  const platformCompliance = [
    { platform: 'Instagram', compliance: 89, content: 45, violations: 5 },
    { platform: 'LinkedIn', compliance: 92, content: 38, violations: 3 },
    { platform: 'Twitter', compliance: 85, content: 52, violations: 8 },
    { platform: 'Facebook', compliance: 88, content: 43, violations: 6 },
  ];

  const enforcementSettings = {
    autoCorrection: true,
    realTimeMonitoring: true,
    emailNotifications: false,
    slackIntegration: true,
    enforcementLevel: 'moderate',
  };

  const getEnforcementColor = (enforcement: string) => {
    switch (enforcement) {
      case 'strict': return 'red';
      case 'moderate': return 'yellow';
      case 'flexible': return 'green';
      default: return 'gray';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'red';
      case 'high': return 'orange';
      case 'medium': return 'yellow';
      case 'low': return 'blue';
      default: return 'gray';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved': return 'green';
      case 'auto-corrected': return 'blue';
      case 'reviewed': return 'yellow';
      case 'pending': return 'red';
      default: return 'gray';
    }
  };

  return (
    <VStack spacing={8} align="stretch">
      {/* Compliance Overview */}
      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6}>
        <Card bg={cardBg}>
          <CardBody>
            <Stat>
              <StatLabel fontSize="sm" color="gray.500">Overall Compliance</StatLabel>
              <HStack>
                <StatNumber fontSize="2xl" color="brand.deepBlue">
                  {complianceOverview.overallScore}%
                </StatNumber>
                <Icon 
                  as={FiTrendingUp} 
                  color="green.500" 
                  size="sm"
                />
              </HStack>
              <StatHelpText fontSize="xs" color="green.500">
                {complianceOverview.trend} this week
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={cardBg}>
          <CardBody>
            <Stat>
              <StatLabel fontSize="sm" color="gray.500">Compliant Content</StatLabel>
              <StatNumber fontSize="2xl" color="brand.successGreen">
                {complianceOverview.contentCompliant}
              </StatNumber>
              <StatHelpText fontSize="xs">
                of {complianceOverview.contentTotal} total
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={cardBg}>
          <CardBody>
            <Stat>
              <StatLabel fontSize="sm" color="gray.500">Critical Issues</StatLabel>
              <StatNumber fontSize="2xl" color="brand.alertRed">
                {complianceOverview.criticalIssues}
              </StatNumber>
              <StatHelpText fontSize="xs">
                Require immediate attention
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={cardBg}>
          <CardBody>
            <Stat>
              <StatLabel fontSize="sm" color="gray.500">Last Updated</StatLabel>
              <StatNumber fontSize="lg" color="brand.warmGray">
                {complianceOverview.lastUpdated}
              </StatNumber>
              <StatHelpText fontSize="xs">
                <Icon as={FiActivity} color="green.500" />
                Real-time monitoring
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Critical Issues Alert */}
      {complianceOverview.criticalIssues > 0 && (
        <Alert status="error" borderRadius="md">
          <AlertIcon />
          <Box flex="1">
            <AlertTitle fontSize="sm" color="red.600">Critical Compliance Issues Detected!</AlertTitle>
            <AlertDescription fontSize="sm">
              {complianceOverview.criticalIssues} content items require immediate attention to maintain brand standards.
            </AlertDescription>
          </Box>
          <Button size="sm" colorScheme="red" variant="outline">
            Review Issues
          </Button>
        </Alert>
      )}

      <Tabs variant="enclosed" colorScheme="bymb">
        <TabList>
          <Tab>Compliance Rules</Tab>
          <Tab>Platform Analysis</Tab>
          <Tab>Recent Violations</Tab>
          <Tab>Settings</Tab>
        </TabList>

        <TabPanels>
          {/* Compliance Rules Tab */}
          <TabPanel px={0}>
            <Card bg={cardBg}>
              <CardHeader>
                <HStack justify="space-between">
                  <HStack>
                    <Icon as={FiShield} color="brand.deepBlue" />
                    <Heading size="md" color="brand.deepBlue">Brand Compliance Rules</Heading>
                  </HStack>
                  <Button size="sm" variant="outline" colorScheme="bymb">
                    Add Rule
                  </Button>
                </HStack>
              </CardHeader>
              <CardBody>
                <Table variant="simple">
                  <Thead>
                    <Tr>
                      <Th>Rule</Th>
                      <Th>Enforcement</Th>
                      <Th>Compliance</Th>
                      <Th>Violations</Th>
                      <Th>Status</Th>
                      <Th>Actions</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {complianceRules.map((rule) => (
                      <Tr key={rule.id}>
                        <Td>
                          <VStack align="start" spacing={0}>
                            <Text fontSize="sm" fontWeight="medium">
                              {rule.name}
                            </Text>
                            <Text fontSize="xs" color="gray.500">
                              {rule.description}
                            </Text>
                          </VStack>
                        </Td>
                        <Td>
                          <Badge
                            colorScheme={getEnforcementColor(rule.enforcement)}
                            size="sm"
                            textTransform="capitalize"
                          >
                            {rule.enforcement}
                          </Badge>
                        </Td>
                        <Td>
                          <HStack>
                            <CircularProgress
                              value={rule.compliance}
                              color={rule.compliance >= 90 ? 'green.500' : rule.compliance >= 80 ? 'yellow.500' : 'red.500'}
                              size="40px"
                              thickness="6px"
                            >
                              <CircularProgressLabel fontSize="xs" fontWeight="bold">
                                {rule.compliance}%
                              </CircularProgressLabel>
                            </CircularProgress>
                          </HStack>
                        </Td>
                        <Td>
                          <Text fontSize="sm" color={rule.violations > 0 ? 'red.500' : 'green.500'}>
                            {rule.violations}
                          </Text>
                        </Td>
                        <Td>
                          <Switch
                            isChecked={rule.enabled}
                            colorScheme="bymb"
                            size="sm"
                          />
                        </Td>
                        <Td>
                          <HStack spacing={2}>
                            <Tooltip label="View details">
                              <Button size="xs" variant="ghost">
                                <Icon as={FiEye} />
                              </Button>
                            </Tooltip>
                            <Tooltip label="Configure">
                              <Button size="xs" variant="ghost">
                                <Icon as={FiSettings} />
                              </Button>
                            </Tooltip>
                          </HStack>
                        </Td>
                      </Tr>
                    ))}
                  </Tbody>
                </Table>
              </CardBody>
            </Card>
          </TabPanel>

          {/* Platform Analysis Tab */}
          <TabPanel px={0}>
            <Grid templateColumns={{ base: '1fr', lg: '1fr 1fr' }} gap={8}>
              <GridItem>
                <Card bg={cardBg}>
                  <CardHeader>
                    <HStack>
                      <Icon as={FiBarChart3} color="brand.deepBlue" />
                      <Heading size="md" color="brand.deepBlue">Platform Compliance</Heading>
                    </HStack>
                  </CardHeader>
                  <CardBody>
                    <VStack spacing={6}>
                      {platformCompliance.map((platform) => (
                        <Box key={platform.platform} w="full">
                          <Flex justify="space-between" align="center" mb={2}>
                            <Text fontSize="sm" fontWeight="medium">
                              {platform.platform}
                            </Text>
                            <Text fontSize="sm" fontWeight="bold" color="brand.deepBlue">
                              {platform.compliance}%
                            </Text>
                          </Flex>
                          <Progress
                            value={platform.compliance}
                            colorScheme={platform.compliance >= 90 ? 'green' : platform.compliance >= 80 ? 'yellow' : 'red'}
                            size="sm"
                            borderRadius="full"
                          />
                          <HStack justify="space-between" mt={1}>
                            <Text fontSize="xs" color="gray.500">
                              {platform.content} content items
                            </Text>
                            <Text fontSize="xs" color={platform.violations > 0 ? 'red.500' : 'gray.500'}>
                              {platform.violations} violations
                            </Text>
                          </HStack>
                        </Box>
                      ))}
                    </VStack>
                  </CardBody>
                </Card>
              </GridItem>

              <GridItem>
                <Card bg={cardBg}>
                  <CardHeader>
                    <Heading size="md" color="brand.deepBlue">Compliance Trends</Heading>
                  </CardHeader>
                  <CardBody>
                    <VStack spacing={4} align="stretch">
                      <Box p={4} bg="green.50" borderRadius="md" border="1px solid" borderColor="green.200">
                        <HStack justify="space-between">
                          <VStack align="start" spacing={0}>
                            <Text fontSize="sm" fontWeight="medium" color="green.700">
                              Improved Areas
                            </Text>
                            <Text fontSize="xs" color="green.600">
                              Logo presence +15%
                            </Text>
                          </VStack>
                          <Icon as={FiTrendingUp} color="green.500" boxSize="20px" />
                        </HStack>
                      </Box>

                      <Box p={4} bg="yellow.50" borderRadius="md" border="1px solid" borderColor="yellow.200">
                        <HStack justify="space-between">
                          <VStack align="start" spacing={0}>
                            <Text fontSize="sm" fontWeight="medium" color="yellow.700">
                              Needs Attention
                            </Text>
                            <Text fontSize="xs" color="yellow.600">
                              Color compliance -3%
                            </Text>
                          </VStack>
                          <Icon as={FiTrendingDown} color="yellow.500" boxSize="20px" />
                        </HStack>
                      </Box>

                      <Box p={4} bg="blue.50" borderRadius="md" border="1px solid" borderColor="blue.200">
                        <HStack justify="space-between">
                          <VStack align="start" spacing={0}>
                            <Text fontSize="sm" fontWeight="medium" color="blue.700">
                              Auto-Corrections
                            </Text>
                            <Text fontSize="xs" color="blue.600">
                              34 issues resolved automatically
                            </Text>
                          </VStack>
                          <Icon as={FiZap} color="blue.500" boxSize="20px" />
                        </HStack>
                      </Box>
                    </VStack>
                  </CardBody>
                </Card>
              </GridItem>
            </Grid>
          </TabPanel>

          {/* Recent Violations Tab */}
          <TabPanel px={0}>
            <Card bg={cardBg}>
              <CardHeader>
                <HStack justify="space-between">
                  <HStack>
                    <Icon as={FiAlertTriangle} color="brand.gold" />
                    <Heading size="md" color="brand.deepBlue">Recent Violations</Heading>
                  </HStack>
                  <Button size="sm" variant="outline" colorScheme="bymb" leftIcon={<FiRefreshCw />}>
                    Refresh
                  </Button>
                </HStack>
              </CardHeader>
              <CardBody>
                <Table variant="simple">
                  <Thead>
                    <Tr>
                      <Th>Content</Th>
                      <Th>Rule Violated</Th>
                      <Th>Severity</Th>
                      <Th>Platform</Th>
                      <Th>Time</Th>
                      <Th>Status</Th>
                      <Th>Actions</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {recentViolations.map((violation) => (
                      <Tr key={violation.id}>
                        <Td>
                          <Text fontSize="sm" fontWeight="medium">
                            {violation.content}
                          </Text>
                        </Td>
                        <Td>
                          <Text fontSize="sm" color="gray.600">
                            {violation.rule}
                          </Text>
                        </Td>
                        <Td>
                          <Badge
                            colorScheme={getSeverityColor(violation.severity)}
                            size="sm"
                            textTransform="capitalize"
                          >
                            {violation.severity}
                          </Badge>
                        </Td>
                        <Td>
                          <Text fontSize="sm">{violation.platform}</Text>
                        </Td>
                        <Td>
                          <Text fontSize="xs" color="gray.500">
                            {violation.timestamp}
                          </Text>
                        </Td>
                        <Td>
                          <Badge
                            colorScheme={getStatusColor(violation.status)}
                            size="sm"
                            variant="outline"
                          >
                            {violation.status.replace('-', ' ')}
                          </Badge>
                        </Td>
                        <Td>
                          <Button size="xs" variant="ghost" colorScheme="bymb">
                            Review
                          </Button>
                        </Td>
                      </Tr>
                    ))}
                  </Tbody>
                </Table>
              </CardBody>
            </Card>
          </TabPanel>

          {/* Settings Tab */}
          <TabPanel px={0}>
            <Grid templateColumns={{ base: '1fr', lg: '1fr 1fr' }} gap={8}>
              <GridItem>
                <Card bg={cardBg}>
                  <CardHeader>
                    <HStack>
                      <Icon as={FiSettings} color="brand.deepBlue" />
                      <Heading size="md" color="brand.deepBlue">Enforcement Settings</Heading>
                    </HStack>
                  </CardHeader>
                  <CardBody>
                    <VStack spacing={6} align="stretch">
                      <FormControl display="flex" alignItems="center" justifyContent="space-between">
                        <FormLabel htmlFor="auto-correction" mb="0" fontSize="sm">
                          Auto-Correction
                        </FormLabel>
                        <Switch
                          id="auto-correction"
                          isChecked={enforcementSettings.autoCorrection}
                          colorScheme="bymb"
                        />
                      </FormControl>

                      <FormControl display="flex" alignItems="center" justifyContent="space-between">
                        <FormLabel htmlFor="real-time" mb="0" fontSize="sm">
                          Real-time Monitoring
                        </FormLabel>
                        <Switch
                          id="real-time"
                          isChecked={enforcementSettings.realTimeMonitoring}
                          colorScheme="bymb"
                        />
                      </FormControl>

                      <FormControl display="flex" alignItems="center" justifyContent="space-between">
                        <FormLabel htmlFor="email-notifications" mb="0" fontSize="sm">
                          Email Notifications
                        </FormLabel>
                        <Switch
                          id="email-notifications"
                          isChecked={enforcementSettings.emailNotifications}
                          colorScheme="bymb"
                        />
                      </FormControl>

                      <FormControl display="flex" alignItems="center" justifyContent="space-between">
                        <FormLabel htmlFor="slack-integration" mb="0" fontSize="sm">
                          Slack Integration
                        </FormLabel>
                        <Switch
                          id="slack-integration"
                          isChecked={enforcementSettings.slackIntegration}
                          colorScheme="bymb"
                        />
                      </FormControl>

                      <FormControl>
                        <FormLabel fontSize="sm">Enforcement Level</FormLabel>
                        <Select value={enforcementSettings.enforcementLevel} size="sm">
                          <option value="strict">Strict - No deviations allowed</option>
                          <option value="moderate">Moderate - Minor deviations with warnings</option>
                          <option value="flexible">Flexible - Major deviations with corrections</option>
                          <option value="advisory">Advisory - Recommendations only</option>
                        </Select>
                      </FormControl>
                    </VStack>
                  </CardBody>
                </Card>
              </GridItem>

              <GridItem>
                <Card bg={cardBg}>
                  <CardHeader>
                    <Heading size="md" color="brand.deepBlue">Notification Preferences</Heading>
                  </CardHeader>
                  <CardBody>
                    <VStack spacing={4} align="stretch">
                      <Box p={4} bg="gray.50" borderRadius="md">
                        <Text fontSize="sm" fontWeight="medium" mb={2}>Critical Issues</Text>
                        <Text fontSize="xs" color="gray.600" mb={3}>
                          Immediate notifications for critical brand violations
                        </Text>
                        <HStack spacing={4}>
                          <Switch size="sm" isChecked colorScheme="red" />
                          <Text fontSize="xs">Instant alerts</Text>
                        </HStack>
                      </Box>

                      <Box p={4} bg="gray.50" borderRadius="md">
                        <Text fontSize="sm" fontWeight="medium" mb={2}>Daily Summary</Text>
                        <Text fontSize="xs" color="gray.600" mb={3}>
                          Daily compliance summary and recommendations
                        </Text>
                        <HStack spacing={4}>
                          <Switch size="sm" isChecked colorScheme="bymb" />
                          <Text fontSize="xs">Email at 9:00 AM</Text>
                        </HStack>
                      </Box>

                      <Box p={4} bg="gray.50" borderRadius="md">
                        <Text fontSize="sm" fontWeight="medium" mb={2}>Weekly Report</Text>
                        <Text fontSize="xs" color="gray.600" mb={3}>
                          Comprehensive brand compliance analytics
                        </Text>
                        <HStack spacing={4}>
                          <Switch size="sm" isChecked={false} colorScheme="bymb" />
                          <Text fontSize="xs">Every Monday</Text>
                        </HStack>
                      </Box>
                    </VStack>
                  </CardBody>
                </Card>
              </GridItem>
            </Grid>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </VStack>
  );
}