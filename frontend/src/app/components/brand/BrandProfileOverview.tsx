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
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Divider,
  useColorModeValue,
  Icon,
  Tag,
  TagLabel,
  Wrap,
  WrapItem,
  Progress,
} from '@chakra-ui/react';
import {
  FiMapPin,
  FiAward,
  FiTrendingUp,
  FiUsers,
  FiTarget,
  FiHeart,
  FiBriefcase,
  FiStar,
} from 'react-icons/fi';

export default function BrandProfileOverview() {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // BYMB Brand Data
  const brandData = {
    companyName: 'BYMB Consultancy',
    founder: 'Bader Abdulrahim',
    location: 'Manama, Kingdom of Bahrain',
    experience: '23+ years',
    clientResults: '$35M+',
    tagline: 'Be Your Most Beautiful - In Business & Beyond',
    mission: 'Empowering businesses to achieve their most beautiful potential through strategic transformation',
    vision: 'To be the premier consultancy driving meaningful business transformation in the Gulf region',
    values: [
      'Excellence in execution',
      'Strategic thinking',
      'Authentic relationships',
      'Continuous innovation',
      'Results-driven approach',
      'Cultural sensitivity'
    ],
    brandColors: [
      { name: 'BYMB Deep Blue', hex: '#1B365D', usage: 'Primary brand color - authority, trust, professionalism' },
      { name: 'BYMB Gold', hex: '#D4AF37', usage: 'Accent color - premium, achievement, success' },
      { name: 'Gulf Teal', hex: '#2E8B8B', usage: 'Regional connection, stability' },
      { name: 'Warm Gray', hex: '#6B7280', usage: 'Supporting text, subtle backgrounds' },
    ],
    brandFonts: [
      { name: 'Inter', usage: 'Headlines, body text', weight: 'Primary' },
      { name: 'Playfair Display', usage: 'Quotes, elegant emphasis', weight: 'Accent' },
    ],
    personalityTraits: [
      'Authoritative yet approachable',
      'Strategic and insightful',
      'Culturally aware',
      'Results-focused',
      'Professionally warm',
      'Confidently humble'
    ]
  };

  const brandMetrics = {
    brandComplianceScore: 92,
    totalTemplates: 24,
    contentGenerated: 156,
    validationsPassed: 89,
  };

  return (
    <VStack spacing={8} align="stretch">
      {/* Header Section */}
      <Card bg={cardBg} border="1px solid" borderColor={borderColor}>
        <CardBody>
          <Flex direction={{ base: 'column', md: 'row' }} gap={8}>
            {/* Brand Identity */}
            <Box flex="1">
              <VStack align="start" spacing={4}>
                <Box>
                  <Heading size="xl" color="brand.deepBlue" fontFamily="accent" mb={2}>
                    {brandData.companyName}
                  </Heading>
                  <Text fontSize="lg" color="brand.gold" fontStyle="italic" mb={4}>
                    {brandData.tagline}
                  </Text>
                </Box>

                <SimpleGrid columns={{ base: 1, sm: 2 }} spacing={4} w="full">
                  <HStack>
                    <Icon as={FiUsers} color="brand.deepBlue" />
                    <Text fontSize="sm" color="gray.600">
                      <Text as="span" fontWeight="semibold">Founder:</Text> {brandData.founder}
                    </Text>
                  </HStack>
                  
                  <HStack>
                    <Icon as={FiMapPin} color="brand.deepBlue" />
                    <Text fontSize="sm" color="gray.600">
                      <Text as="span" fontWeight="semibold">Location:</Text> {brandData.location}
                    </Text>
                  </HStack>
                  
                  <HStack>
                    <Icon as={FiAward} color="brand.gold" />
                    <Text fontSize="sm" color="gray.600">
                      <Text as="span" fontWeight="semibold">Experience:</Text> {brandData.experience}
                    </Text>
                  </HStack>
                  
                  <HStack>
                    <Icon as={FiTrendingUp} color="brand.successGreen" />
                    <Text fontSize="sm" color="gray.600">
                      <Text as="span" fontWeight="semibold">Client Results:</Text> {brandData.clientResults}
                    </Text>
                  </HStack>
                </SimpleGrid>
              </VStack>
            </Box>

            {/* Brand Metrics */}
            <Box flex="1">
              <SimpleGrid columns={2} spacing={4}>
                <Stat>
                  <StatLabel fontSize="xs" color="gray.500">Brand Compliance</StatLabel>
                  <StatNumber fontSize="2xl" color="brand.successGreen">
                    {brandMetrics.brandComplianceScore}%
                  </StatNumber>
                  <Progress
                    value={brandMetrics.brandComplianceScore}
                    colorScheme="green"
                    size="sm"
                    mt={2}
                  />
                </Stat>

                <Stat>
                  <StatLabel fontSize="xs" color="gray.500">Templates</StatLabel>
                  <StatNumber fontSize="2xl" color="brand.deepBlue">
                    {brandMetrics.totalTemplates}
                  </StatNumber>
                  <StatHelpText fontSize="xs">Active templates</StatHelpText>
                </Stat>

                <Stat>
                  <StatLabel fontSize="xs" color="gray.500">Content Generated</StatLabel>
                  <StatNumber fontSize="2xl" color="brand.gold">
                    {brandMetrics.contentGenerated}
                  </StatNumber>
                  <StatHelpText fontSize="xs">This month</StatHelpText>
                </Stat>

                <Stat>
                  <StatLabel fontSize="xs" color="gray.500">Validations</StatLabel>
                  <StatNumber fontSize="2xl" color="brand.successGreen">
                    {brandMetrics.validationsPassed}%
                  </StatNumber>
                  <StatHelpText fontSize="xs">Passed rate</StatHelpText>
                </Stat>
              </SimpleGrid>
            </Box>
          </Flex>
        </CardBody>
      </Card>

      <Grid templateColumns={{ base: '1fr', lg: '1fr 1fr' }} gap={8}>
        {/* Mission & Vision */}
        <GridItem>
          <Card bg={cardBg} h="full">
            <CardHeader pb={2}>
              <HStack>
                <Icon as={FiTarget} color="brand.deepBlue" />
                <Heading size="md" color="brand.deepBlue">Mission & Vision</Heading>
              </HStack>
            </CardHeader>
            <CardBody pt={2}>
              <VStack spacing={4} align="start">
                <Box>
                  <Text fontWeight="semibold" color="brand.gold" mb={2}>Mission</Text>
                  <Text fontSize="sm" color="gray.600" lineHeight="1.6">
                    {brandData.mission}
                  </Text>
                </Box>
                
                <Box>
                  <Text fontWeight="semibold" color="brand.gold" mb={2}>Vision</Text>
                  <Text fontSize="sm" color="gray.600" lineHeight="1.6">
                    {brandData.vision}
                  </Text>
                </Box>
              </VStack>
            </CardBody>
          </Card>
        </GridItem>

        {/* Brand Values */}
        <GridItem>
          <Card bg={cardBg} h="full">
            <CardHeader pb={2}>
              <HStack>
                <Icon as={FiHeart} color="brand.deepBlue" />
                <Heading size="md" color="brand.deepBlue">Brand Values</Heading>
              </HStack>
            </CardHeader>
            <CardBody pt={2}>
              <Wrap spacing={2}>
                {brandData.values.map((value, index) => (
                  <WrapItem key={index}>
                    <Tag
                      size="sm"
                      bg="brand.deepBlue"
                      color="white"
                      borderRadius="full"
                    >
                      <TagLabel>{value}</TagLabel>
                    </Tag>
                  </WrapItem>
                ))}
              </Wrap>
            </CardBody>
          </Card>
        </GridItem>
      </Grid>

      <Grid templateColumns={{ base: '1fr', lg: '1fr 1fr' }} gap={8}>
        {/* Brand Colors */}
        <GridItem>
          <Card bg={cardBg}>
            <CardHeader pb={2}>
              <Heading size="md" color="brand.deepBlue">Brand Colors</Heading>
            </CardHeader>
            <CardBody pt={2}>
              <VStack spacing={3} align="stretch">
                {brandData.brandColors.map((color, index) => (
                  <Flex key={index} align="center" gap={4}>
                    <Box
                      w="40px"
                      h="40px"
                      bg={color.hex}
                      borderRadius="md"
                      border="1px solid"
                      borderColor="gray.200"
                    />
                    <Box flex="1">
                      <Text fontWeight="semibold" fontSize="sm" color="gray.700">
                        {color.name}
                      </Text>
                      <Text fontSize="xs" color="gray.500" mt={1}>
                        {color.hex} • {color.usage}
                      </Text>
                    </Box>
                  </Flex>
                ))}
              </VStack>
            </CardBody>
          </Card>
        </GridItem>

        {/* Typography & Personality */}
        <GridItem>
          <VStack spacing={6} align="stretch" h="full">
            {/* Typography */}
            <Card bg={cardBg} flex="1">
              <CardHeader pb={2}>
                <Heading size="md" color="brand.deepBlue">Typography</Heading>
              </CardHeader>
              <CardBody pt={2}>
                <VStack spacing={3} align="stretch">
                  {brandData.brandFonts.map((font, index) => (
                    <Box key={index}>
                      <HStack justify="space-between" mb={1}>
                        <Text fontWeight="semibold" fontSize="sm" color="gray.700">
                          {font.name}
                        </Text>
                        <Badge
                          colorScheme={font.weight === 'Primary' ? 'blue' : 'yellow'}
                          size="sm"
                        >
                          {font.weight}
                        </Badge>
                      </HStack>
                      <Text fontSize="xs" color="gray.500">
                        {font.usage}
                      </Text>
                    </Box>
                  ))}
                </VStack>
              </CardBody>
            </Card>

            {/* Personality Traits */}
            <Card bg={cardBg} flex="1">
              <CardHeader pb={2}>
                <HStack>
                  <Icon as={FiStar} color="brand.gold" />
                  <Heading size="md" color="brand.deepBlue">Brand Personality</Heading>
                </HStack>
              </CardHeader>
              <CardBody pt={2}>
                <Wrap spacing={2}>
                  {brandData.personalityTraits.map((trait, index) => (
                    <WrapItem key={index}>
                      <Tag
                        size="sm"
                        bg="brand.gold"
                        color="brand.deepBlue"
                        borderRadius="full"
                      >
                        <TagLabel fontSize="xs">{trait}</TagLabel>
                      </Tag>
                    </WrapItem>
                  ))}
                </Wrap>
              </CardBody>
            </Card>
          </VStack>
        </GridItem>
      </Grid>

      {/* Actions */}
      <Card bg={cardBg}>
        <CardBody>
          <Flex justify="space-between" align="center" flexWrap="wrap" gap={4}>
            <Box>
              <Text fontWeight="semibold" color="brand.deepBlue" mb={1}>
                Brand Profile Management
              </Text>
              <Text fontSize="sm" color="gray.600">
                Maintain and update your brand identity system
              </Text>
            </Box>
            <HStack spacing={3}>
              <Button variant="outline" colorScheme="bymb" size="sm">
                Export Brand Guide
              </Button>
              <Button variant="bymb" size="sm">
                Update Profile
              </Button>
            </HStack>
          </Flex>
        </CardBody>
      </Card>
    </VStack>
  );
}