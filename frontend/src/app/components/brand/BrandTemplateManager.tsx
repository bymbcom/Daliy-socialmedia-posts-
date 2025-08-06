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
  Image,
  useColorModeValue,
  Icon,
  Select,
  Input,
  InputGroup,
  InputLeftElement,
  SimpleGrid,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  FormControl,
  FormLabel,
  Textarea,
  Switch,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Progress,
  Tooltip,
} from '@chakra-ui/react';
import {
  FiSearch,
  FiPlus,
  FiEdit,
  FiTrash2,
  FiCopy,
  FiDownload,
  FiEye,
  FiMoreVertical,
  FiLayers,
  FiStar,
  FiTrendingUp,
  FiCalendar,
  FiFilter,
} from 'react-icons/fi';

export default function BrandTemplateManager() {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const { isOpen, onOpen, onClose } = useDisclosure();

  // Mock template data
  const templateStats = {
    totalTemplates: 24,
    activeTemplates: 21,
    usageThisMonth: 156,
    averageCompliance: 89,
  };

  const templates = [
    {
      id: 'TPL-001',
      name: 'Instagram Quote Post',
      description: 'Clean, minimal quote template with BYMB branding',
      category: 'Quote',
      platform: 'Instagram',
      layoutStyle: 'Minimal',
      dimensions: '1080x1080',
      complianceScore: 94,
      usage: 23,
      lastUsed: '2 hours ago',
      status: 'active',
      preview: '/api/placeholder/300/300'
    },
    {
      id: 'TPL-002',
      name: 'LinkedIn Insight Post',
      description: 'Professional template for sharing business insights',
      category: 'Insight',
      platform: 'LinkedIn',
      layoutStyle: 'Professional',
      dimensions: '1200x628',
      complianceScore: 91,
      usage: 18,
      lastUsed: '3 hours ago',
      status: 'active',
      preview: '/api/placeholder/300/157'
    },
    {
      id: 'TPL-003',
      name: 'Company Achievement',
      description: 'Elegant template for company announcements and achievements',
      category: 'Announcement',
      platform: 'LinkedIn',
      layoutStyle: 'Elegant',
      dimensions: '1200x628',
      complianceScore: 96,
      usage: 15,
      lastUsed: '1 day ago',
      status: 'active',
      preview: '/api/placeholder/300/157'
    },
    {
      id: 'TPL-004',
      name: 'Twitter Thought Leadership',
      description: 'Twitter-optimized template for thought leadership content',
      category: 'Thought Leadership',
      platform: 'Twitter',
      layoutStyle: 'Modern',
      dimensions: '1200x675',
      complianceScore: 87,
      usage: 12,
      lastUsed: '2 days ago',
      status: 'active',
      preview: '/api/placeholder/300/169'
    },
    {
      id: 'TPL-005',
      name: 'Facebook Event Cover',
      description: 'Event cover template with brand consistency',
      category: 'Event',
      platform: 'Facebook',
      layoutStyle: 'Executive',
      dimensions: '1920x1080',
      complianceScore: 78,
      usage: 5,
      lastUsed: '1 week ago',
      status: 'needs_update',
      preview: '/api/placeholder/300/169'
    },
    {
      id: 'TPL-006',
      name: 'Instagram Story Template',
      description: 'Vertical story template with dynamic content areas',
      category: 'Story',
      platform: 'Instagram',
      layoutStyle: 'Modern',
      dimensions: '1080x1920',
      complianceScore: 92,
      usage: 8,
      lastUsed: '3 days ago',
      status: 'active',
      preview: '/api/placeholder/169/300'
    }
  ];

  const categories = ['All', 'Quote', 'Insight', 'Announcement', 'Thought Leadership', 'Event', 'Story'];
  const platforms = ['All', 'Instagram', 'LinkedIn', 'Twitter', 'Facebook'];
  const layoutStyles = ['All', 'Minimal', 'Professional', 'Elegant', 'Modern', 'Executive'];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'green';
      case 'needs_update': return 'yellow';
      case 'draft': return 'gray';
      case 'archived': return 'red';
      default: return 'gray';
    }
  };

  const getComplianceColor = (score: number) => {
    if (score >= 90) return 'green.500';
    if (score >= 80) return 'yellow.500';
    if (score >= 70) return 'orange.500';
    return 'red.500';
  };

  const getPlatformIcon = (platform: string) => {
    // In a real app, you'd return appropriate platform icons
    return FiLayers;
  };

  return (
    <VStack spacing={8} align="stretch">
      {/* Template Stats */}
      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6}>
        <Card bg={cardBg}>
          <CardBody>
            <Stat>
              <StatLabel fontSize="sm" color="gray.500">Total Templates</StatLabel>
              <StatNumber fontSize="2xl" color="brand.deepBlue">
                {templateStats.totalTemplates}
              </StatNumber>
              <StatHelpText fontSize="xs">
                {templateStats.activeTemplates} active
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={cardBg}>
          <CardBody>
            <Stat>
              <StatLabel fontSize="sm" color="gray.500">Usage This Month</StatLabel>
              <StatNumber fontSize="2xl" color="brand.gold">
                {templateStats.usageThisMonth}
              </StatNumber>
              <StatHelpText fontSize="xs" color="green.500">
                <Icon as={FiTrendingUp} />
                +12% from last month
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card bg={cardBg}>
          <CardBody>
            <Stat>
              <StatLabel fontSize="sm" color="gray.500">Avg. Compliance</StatLabel>
              <StatNumber fontSize="2xl" color="brand.successGreen">
                {templateStats.averageCompliance}%
              </StatNumber>
              <Progress
                value={templateStats.averageCompliance}
                colorScheme="green"
                size="sm"
                mt={2}
              />
            </Stat>
          </CardBody>
        </Card>

        <Card bg={cardBg}>
          <CardBody>
            <Stat>
              <StatLabel fontSize="sm" color="gray.500">Most Popular</StatLabel>
              <StatNumber fontSize="md" color="brand.deepBlue">
                Quote Templates
              </StatNumber>
              <StatHelpText fontSize="xs">
                41 uses this month
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Controls */}
      <Card bg={cardBg}>
        <CardBody>
          <Flex justify="space-between" align="center" flexWrap="wrap" gap={4}>
            <HStack spacing={4} flex="1" minW="300px">
              <InputGroup maxW="300px">
                <InputLeftElement>
                  <Icon as={FiSearch} color="gray.400" />
                </InputLeftElement>
                <Input placeholder="Search templates..." size="sm" />
              </InputGroup>

              <Select placeholder="Category" size="sm" maxW="150px">
                {categories.map(category => (
                  <option key={category} value={category.toLowerCase()}>
                    {category}
                  </option>
                ))}
              </Select>

              <Select placeholder="Platform" size="sm" maxW="150px">
                {platforms.map(platform => (
                  <option key={platform} value={platform.toLowerCase()}>
                    {platform}
                  </option>
                ))}
              </Select>

              <Button size="sm" variant="outline" colorScheme="bymb" leftIcon={<FiFilter />}>
                More Filters
              </Button>
            </HStack>

            <HStack spacing={3}>
              <Button size="sm" variant="outline" colorScheme="bymb">
                Import Template
              </Button>
              <Button size="sm" variant="bymb" leftIcon={<FiPlus />} onClick={onOpen}>
                Create Template
              </Button>
            </HStack>
          </Flex>
        </CardBody>
      </Card>

      {/* Templates Grid */}
      <Grid
        templateColumns={{
          base: '1fr',
          md: 'repeat(2, 1fr)',
          lg: 'repeat(3, 1fr)',
          xl: 'repeat(4, 1fr)'
        }}
        gap={6}
      >
        {templates.map((template) => (
          <Card key={template.id} bg={cardBg} overflow="hidden" _hover={{ transform: 'translateY(-2px)' }} transition="all 0.2s">
            <Box position="relative">
              <Image
                src={template.preview}
                alt={template.name}
                w="full"
                h="200px"
                objectFit="cover"
                bg="gray.100"
                fallback={
                  <Box
                    w="full"
                    h="200px"
                    bg="gray.100"
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                  >
                    <Icon as={FiLayers} boxSize="40px" color="gray.400" />
                  </Box>
                }
              />
              <Box position="absolute" top={3} right={3}>
                <Menu>
                  <MenuButton
                    as={Button}
                    size="sm"
                    variant="ghost"
                    bg="white"
                    _hover={{ bg: 'gray.100' }}
                  >
                    <Icon as={FiMoreVertical} />
                  </MenuButton>
                  <MenuList>
                    <MenuItem icon={<FiEye />}>Preview</MenuItem>
                    <MenuItem icon={<FiEdit />}>Edit</MenuItem>
                    <MenuItem icon={<FiCopy />}>Duplicate</MenuItem>
                    <MenuItem icon={<FiDownload />}>Export</MenuItem>
                    <MenuItem icon={<FiTrash2 />} color="red.500">Delete</MenuItem>
                  </MenuList>
                </Menu>
              </Box>
              <Box position="absolute" top={3} left={3}>
                <HStack spacing={2}>
                  <Badge
                    colorScheme={getStatusColor(template.status)}
                    size="sm"
                    textTransform="capitalize"
                  >
                    {template.status.replace('_', ' ')}
                  </Badge>
                  {template.usage > 20 && (
                    <Badge colorScheme="yellow" size="sm" leftIcon={<FiStar />}>
                      Popular
                    </Badge>
                  )}
                </HStack>
              </Box>
            </Box>

            <CardBody>
              <VStack align="start" spacing={3}>
                <Box w="full">
                  <HStack justify="space-between" align="start">
                    <VStack align="start" spacing={1} flex="1">
                      <Text fontWeight="semibold" fontSize="sm" color="gray.800">
                        {template.name}
                      </Text>
                      <Text fontSize="xs" color="gray.500" noOfLines={2}>
                        {template.description}
                      </Text>
                    </VStack>
                    <Tooltip label={`Compliance Score: ${template.complianceScore}%`}>
                      <Box
                        w="30px"
                        h="30px"
                        borderRadius="full"
                        bg={getComplianceColor(template.complianceScore)}
                        display="flex"
                        alignItems="center"
                        justifyContent="center"
                        color="white"
                        fontSize="xs"
                        fontWeight="bold"
                      >
                        {template.complianceScore}
                      </Box>
                    </Tooltip>
                  </HStack>
                </Box>

                <HStack justify="space-between" w="full">
                  <VStack align="start" spacing={0}>
                    <HStack>
                      <Icon as={getPlatformIcon(template.platform)} color="brand.deepBlue" boxSize="12px" />
                      <Text fontSize="xs" color="gray.600">{template.platform}</Text>
                    </HStack>
                    <Text fontSize="xs" color="gray.500">{template.dimensions}</Text>
                  </VStack>
                  
                  <VStack align="end" spacing={0}>
                    <Text fontSize="xs" color="gray.600">{template.usage} uses</Text>
                    <Text fontSize="xs" color="gray.500">{template.lastUsed}</Text>
                  </VStack>
                </HStack>

                <HStack spacing={2} w="full">
                  <Badge size="xs" colorScheme="blue">
                    {template.category}
                  </Badge>
                  <Badge size="xs" variant="outline">
                    {template.layoutStyle}
                  </Badge>
                </HStack>

                <HStack justify="space-between" w="full" pt={2}>
                  <Button size="xs" variant="outline" colorScheme="bymb">
                    Use Template
                  </Button>
                  <HStack spacing={1}>
                    <Button size="xs" variant="ghost" colorScheme="bymb">
                      <Icon as={FiEye} />
                    </Button>
                    <Button size="xs" variant="ghost" colorScheme="bymb">
                      <Icon as={FiEdit} />
                    </Button>
                  </HStack>
                </HStack>
              </VStack>
            </CardBody>
          </Card>
        ))}
      </Grid>

      {/* Create Template Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader color="brand.deepBlue">Create New Template</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4} align="stretch">
              <FormControl>
                <FormLabel fontSize="sm">Template Name</FormLabel>
                <Input placeholder="Enter template name..." />
              </FormControl>

              <FormControl>
                <FormLabel fontSize="sm">Description</FormLabel>
                <Textarea placeholder="Describe the template purpose and usage..." rows={3} />
              </FormControl>

              <Grid templateColumns="1fr 1fr" gap={4}>
                <FormControl>
                  <FormLabel fontSize="sm">Category</FormLabel>
                  <Select placeholder="Select category">
                    {categories.slice(1).map(category => (
                      <option key={category} value={category.toLowerCase()}>
                        {category}
                      </option>
                    ))}
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel fontSize="sm">Platform</FormLabel>
                  <Select placeholder="Select platform">
                    {platforms.slice(1).map(platform => (
                      <option key={platform} value={platform.toLowerCase()}>
                        {platform}
                      </option>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid templateColumns="1fr 1fr" gap={4}>
                <FormControl>
                  <FormLabel fontSize="sm">Layout Style</FormLabel>
                  <Select placeholder="Select style">
                    {layoutStyles.slice(1).map(style => (
                      <option key={style} value={style.toLowerCase()}>
                        {style}
                      </option>
                    ))}
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel fontSize="sm">Dimensions</FormLabel>
                  <Select placeholder="Select dimensions">
                    <option value="1080x1080">1080x1080 (Square)</option>
                    <option value="1200x628">1200x628 (Landscape)</option>
                    <option value="1080x1920">1080x1920 (Story)</option>
                    <option value="custom">Custom</option>
                  </Select>
                </FormControl>
              </Grid>

              <FormControl display="flex" alignItems="center" justifyContent="space-between">
                <FormLabel htmlFor="active-status" mb="0" fontSize="sm">
                  Set as Active Template
                </FormLabel>
                <Switch id="active-status" colorScheme="bymb" />
              </FormControl>

              <Box p={4} bg="gray.50" borderRadius="md">
                <Text fontSize="sm" fontWeight="medium" color="gray.700" mb={2}>
                  Brand Compliance Features
                </Text>
                <VStack align="start" spacing={2}>
                  <HStack>
                    <Switch size="sm" colorScheme="bymb" defaultChecked />
                    <Text fontSize="xs">Automatic logo placement</Text>
                  </HStack>
                  <HStack>
                    <Switch size="sm" colorScheme="bymb" defaultChecked />
                    <Text fontSize="xs">Brand color enforcement</Text>
                  </HStack>
                  <HStack>
                    <Switch size="sm" colorScheme="bymb" defaultChecked />
                    <Text fontSize="xs">Typography validation</Text>
                  </HStack>
                  <HStack>
                    <Switch size="sm" colorScheme="bymb" />
                    <Text fontSize="xs">Voice tone analysis</Text>
                  </HStack>
                </VStack>
              </Box>
            </VStack>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button variant="bymb">
              Create Template
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </VStack>
  );
}