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
  List,
  ListItem,
  ListIcon,
  useColorModeValue,
  Icon,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  CircularProgress,
  CircularProgressLabel,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Select,
  SimpleGrid,
} from '@chakra-ui/react';
import {
  FiCheckCircle,
  FiAlertCircle,
  FiXCircle,
  FiEye,
  FiTrendingUp,
  FiTarget,
  FiBarChart,
  FiInfo,
  FiRefreshCw,
} from 'react-icons/fi';

export default function BrandValidationDashboard() {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Mock validation data
  const validationStats = {
    totalValidations: 342,
    passedValidations: 304,
    failedValidations: 38,
    averageScore: 87.3,
    improvementTrend: '+5.2%',
  };

  const recentValidations = [
    {
      id: 'VAL-001',
      contentType: 'Instagram Post',
      score: 94,
      status: 'passed',
      issues: 1,
      timestamp: '2 hours ago',
      platform: 'Instagram'
    },
    {
      id: 'VAL-002',
      contentType: 'LinkedIn Article',
      score: 76,
      status: 'needs_improvement',
      issues: 4,
      timestamp: '3 hours ago',
      platform: 'LinkedIn'
    },
    {
      id: 'VAL-003',
      contentType: 'Twitter Post',
      score: 91,
      status: 'passed',
      issues: 2,
      timestamp: '5 hours ago',
      platform: 'Twitter'
    },
    {
      id: 'VAL-004',
      contentType: 'Facebook Cover',
      score: 65,
      status: 'failed',
      issues: 7,
      timestamp: '1 day ago',
      platform: 'Facebook'
    },
  ];

  const validationCategories = {
    visualIdentity: { score: 92, issues: 3, trend: '+2.1%' },
    contentVoice: { score: 85, issues: 5, trend: '+1.8%' },
    platformCompliance: { score: 88, issues: 2, trend: '+3.2%' },
    brandConsistency: { score: 90, issues: 1, trend: '+1.5%' },
    accessibility: { score: 83, issues: 4, trend: '+4.1%' },
  };

  const commonIssues = [
    {
      issue: 'Non-brand colors detected',
      frequency: 23,
      severity: 'high',
      suggestion: 'Use only approved BYMB brand colors',
    },
    {
      issue: 'Missing brand logo',
      frequency: 18,
      severity: 'critical',
      suggestion: 'Add BYMB logo to all content',
    },
    {
      issue: 'Insufficient brand vocabulary',
      frequency: 15,
      severity: 'medium',
      suggestion: 'Incorporate more BYMB-specific terminology',
    },
    {
      issue: 'Low color contrast',
      frequency: 12,
      severity: 'medium',
      suggestion: 'Improve contrast for better accessibility',
    },
    {
      issue: 'Text exceeds platform limits',
      frequency: 8,
      severity: 'low',
      suggestion: 'Shorten content to meet platform requirements',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed': return 'green';
      case 'needs_improvement': return 'yellow';
      case 'failed': return 'red';
      default: return 'gray';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'green.500';
    if (score >= 80) return 'yellow.500';
    if (score >= 70) return 'orange.500';
    return 'red.500';
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

  return (
    <VStack spacing={8} align="stretch">
      {/* Overview Stats */}
      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6}>
        <Card bg={cardBg}>
          <CardBody>
            <Stat>
              <StatLabel fontSize="sm" color="gray.500">Total Validations</StatLabel>
              <StatNumber fontSize="2xl" color="brand.deepBlue">
                {validationStats.totalValidations}
              </StatNumber>
              <StatHelpText fontSize="xs">
                <Icon as={FiTrendingUp} color="green.500" />
                {validationStats.improvementTrend}
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={cardBg}>
          <CardBody>
            <Stat>
              <StatLabel fontSize="sm" color="gray.500">Pass Rate</StatLabel>
              <StatNumber fontSize="2xl" color="brand.successGreen">
                {Math.round((validationStats.passedValidations / validationStats.totalValidations) * 100)}%
              </StatNumber>
              <StatHelpText fontSize="xs">
                {validationStats.passedValidations}/{validationStats.totalValidations} passed
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={cardBg}>
          <CardBody>
            <Stat>
              <StatLabel fontSize="sm" color="gray.500">Average Score</StatLabel>
              <StatNumber fontSize="2xl" color="brand.gold">
                {validationStats.averageScore}
              </StatNumber>
              <StatHelpText fontSize="xs">
                Brand compliance score
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={cardBg}>
          <CardBody>
            <Stat>
              <StatLabel fontSize="sm" color="gray.500">Failed Validations</StatLabel>
              <StatNumber fontSize="2xl" color="brand.alertRed">
                {validationStats.failedValidations}
              </StatNumber>
              <StatHelpText fontSize="xs">
                Need attention
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Category Breakdown */}
      <Card bg={cardBg}>
        <CardHeader>
          <HStack>
            <Icon as={FiBarChart} color="brand.deepBlue" />
            <Heading size="md" color="brand.deepBlue">Validation Categories</Heading>
          </HStack>
        </CardHeader>
        <CardBody>
          <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }} gap={6}>
            {Object.entries(validationCategories).map(([category, data]) => (
              <Box key={category}>
                <VStack spacing={3}>
                  <CircularProgress
                    value={data.score}
                    color={getScoreColor(data.score)}
                    size="80px"
                    thickness="6px"
                  >
                    <CircularProgressLabel fontSize="sm" fontWeight="bold">
                      {data.score}
                    </CircularProgressLabel>
                  </CircularProgress>
                  
                  <Box textAlign="center">
                    <Text fontWeight="semibold" fontSize="sm" color="gray.700" textTransform="capitalize">
                      {category.replace(/([A-Z])/g, ' $1').trim()}
                    </Text>
                    <Text fontSize="xs" color="gray.500">
                      {data.issues} issues • {data.trend}
                    </Text>
                  </Box>
                </VStack>
              </Box>
            ))}
          </Grid>
        </CardBody>
      </Card>

      <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={8}>
        {/* Recent Validations */}
        <GridItem>
          <Card bg={cardBg}>
            <CardHeader>
              <Flex justify="space-between" align="center">
                <HStack>
                  <Icon as={FiTarget} color="brand.deepBlue" />
                  <Heading size="md" color="brand.deepBlue">Recent Validations</Heading>
                </HStack>
                <Button size="sm" variant="outline" colorScheme="bymb" leftIcon={<FiRefreshCw />}>
                  Refresh
                </Button>
              </Flex>
            </CardHeader>
            <CardBody>
              <Table variant="simple" size="sm">
                <Thead>
                  <Tr>
                    <Th fontSize="xs">Content</Th>
                    <Th fontSize="xs">Score</Th>
                    <Th fontSize="xs">Status</Th>
                    <Th fontSize="xs">Issues</Th>
                    <Th fontSize="xs">Time</Th>
                    <Th fontSize="xs">Actions</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {recentValidations.map((validation) => (
                    <Tr key={validation.id}>
                      <Td>
                        <VStack align="start" spacing={0}>
                          <Text fontSize="sm" fontWeight="medium">
                            {validation.contentType}
                          </Text>
                          <Text fontSize="xs" color="gray.500">
                            {validation.platform} • {validation.id}
                          </Text>
                        </VStack>
                      </Td>
                      <Td>
                        <Text fontSize="sm" fontWeight="bold" color={getScoreColor(validation.score)}>
                          {validation.score}
                        </Text>
                      </Td>
                      <Td>
                        <Badge
                          colorScheme={getStatusColor(validation.status)}
                          size="sm"
                          textTransform="capitalize"
                        >
                          {validation.status.replace('_', ' ')}
                        </Badge>
                      </Td>
                      <Td>
                        <Text fontSize="sm">{validation.issues}</Text>
                      </Td>
                      <Td>
                        <Text fontSize="xs" color="gray.500">
                          {validation.timestamp}
                        </Text>
                      </Td>
                      <Td>
                        <Button size="xs" variant="ghost" colorScheme="bymb">
                          <Icon as={FiEye} />
                        </Button>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </CardBody>
          </Card>
        </GridItem>

        {/* Common Issues */}
        <GridItem>
          <Card bg={cardBg} h="full">
            <CardHeader>
              <HStack>
                <Icon as={FiAlertCircle} color="brand.gold" />
                <Heading size="md" color="brand.deepBlue">Common Issues</Heading>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack spacing={4} align="stretch">
                {commonIssues.map((issue, index) => (
                  <Box key={index} p={3} bg="gray.50" borderRadius="md">
                    <HStack justify="space-between" mb={2}>
                      <Badge
                        colorScheme={getSeverityColor(issue.severity)}
                        size="sm"
                        textTransform="uppercase"
                      >
                        {issue.severity}
                      </Badge>
                      <Text fontSize="sm" fontWeight="bold" color="gray.600">
                        {issue.frequency}x
                      </Text>
                    </HStack>
                    
                    <Text fontSize="sm" fontWeight="medium" color="gray.700" mb={1}>
                      {issue.issue}
                    </Text>
                    
                    <Text fontSize="xs" color="gray.500">
                      {issue.suggestion}
                    </Text>
                  </Box>
                ))}
              </VStack>
            </CardBody>
          </Card>
        </GridItem>
      </Grid>

      {/* Quick Actions */}
      <Card bg={cardBg}>
        <CardBody>
          <Flex justify="space-between" align="center" flexWrap="wrap" gap={4}>
            <Box>
              <Text fontWeight="semibold" color="brand.deepBlue" mb={1}>
                Brand Validation Tools
              </Text>
              <Text fontSize="sm" color="gray.600">
                Validate content against BYMB brand guidelines
              </Text>
            </Box>
            <HStack spacing={3}>
              <Select placeholder="Filter by platform" size="sm" maxW="200px">
                <option value="instagram">Instagram</option>
                <option value="linkedin">LinkedIn</option>
                <option value="twitter">Twitter</option>
                <option value="facebook">Facebook</option>
              </Select>
              <Button variant="outline" colorScheme="bymb" size="sm">
                View All Validations
              </Button>
              <Button variant="bymb" size="sm">
                Validate New Content
              </Button>
            </HStack>
          </Flex>
        </CardBody>
      </Card>

      {/* Recommendations Alert */}
      <Alert status="info" borderRadius="md">
        <AlertIcon />
        <Box>
          <AlertTitle fontSize="sm" color="brand.deepBlue">Validation Recommendations</AlertTitle>
          <AlertDescription fontSize="sm">
            Focus on improving color compliance and ensuring brand logo presence. 
            Consider creating templates for frequently failed content types.
          </AlertDescription>
        </Box>
      </Alert>
    </VStack>
  );
}