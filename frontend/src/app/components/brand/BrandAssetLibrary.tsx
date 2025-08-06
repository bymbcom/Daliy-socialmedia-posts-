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
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Progress,
  Tooltip,
  useClipboard,
  useToast,
} from '@chakra-ui/react';
import {
  FiSearch,
  FiUpload,
  FiDownload,
  FiCopy,
  FiTrash2,
  FiImage,
  FiType,
  FiPalette,
  FiLayers,
  FiFileText,
  FiCheckCircle,
  FiFolder,
  FiMoreVertical,
  FiEye,
  FiEdit,
} from 'react-icons/fi';

export default function BrandAssetLibrary() {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  // Mock asset data
  const assetStats = {
    totalAssets: 87,
    logoVariants: 8,
    colorPalettes: 5,
    fonts: 4,
    patterns: 12,
    storageUsed: 245, // MB
    storageLimit: 1000, // MB
  };

  const logoAssets = [
    {
      id: 'LOGO-001',
      name: 'Primary Logo',
      filename: 'bymb-primary-logo.svg',
      type: 'SVG',
      size: '24 KB',
      dimensions: '400x150',
      usage: 'Main brand applications, light backgrounds',
      downloadUrl: '#',
      previewUrl: '/api/placeholder/400/150',
      compliance: 100,
      lastModified: '2 days ago'
    },
    {
      id: 'LOGO-002',
      name: 'Reverse Logo',
      filename: 'bymb-reverse-logo.svg',
      type: 'SVG',
      size: '26 KB',
      dimensions: '400x150',
      usage: 'Dark backgrounds, overlays',
      downloadUrl: '#',
      previewUrl: '/api/placeholder/400/150',
      compliance: 100,
      lastModified: '2 days ago'
    },
    {
      id: 'LOGO-003',
      name: 'Icon Mark',
      filename: 'bymb-icon-mark.svg',
      type: 'SVG',
      size: '8 KB',
      dimensions: '100x100',
      usage: 'Small spaces, social profiles',
      downloadUrl: '#',
      previewUrl: '/api/placeholder/100/100',
      compliance: 100,
      lastModified: '1 week ago'
    },
    {
      id: 'LOGO-004',
      name: 'Horizontal Lock-up',
      filename: 'bymb-horizontal.svg',
      type: 'SVG',
      size: '32 KB',
      dimensions: '600x200',
      usage: 'Wide formats, headers',
      downloadUrl: '#',
      previewUrl: '/api/placeholder/600/200',
      compliance: 100,
      lastModified: '1 week ago'
    }
  ];

  const colorPalettes = [
    {
      id: 'PAL-001',
      name: 'Primary Brand Colors',
      colors: [
        { name: 'BYMB Deep Blue', hex: '#1B365D', usage: 'Primary brand color' },
        { name: 'BYMB Gold', hex: '#D4AF37', usage: 'Accent color' },
        { name: 'BYMB White', hex: '#FFFFFF', usage: 'Clean backgrounds' }
      ],
      usage: 234,
      compliance: 100
    },
    {
      id: 'PAL-002',
      name: 'Secondary Colors',
      colors: [
        { name: 'Gulf Teal', hex: '#2E8B8B', usage: 'Regional connection' },
        { name: 'Warm Gray', hex: '#6B7280', usage: 'Supporting text' },
        { name: 'Success Green', hex: '#059669', usage: 'Growth, results' },
        { name: 'Alert Red', hex: '#DC2626', usage: 'Urgent actions' }
      ],
      usage: 89,
      compliance: 95
    }
  ];

  const fontAssets = [
    {
      id: 'FONT-001',
      name: 'Inter',
      filename: 'Inter-Variable.woff2',
      type: 'WOFF2',
      size: '456 KB',
      weights: ['400', '500', '600', '700'],
      usage: 'Headlines, body text',
      compliance: 100,
      downloadUrl: '#'
    },
    {
      id: 'FONT-002',
      name: 'Playfair Display',
      filename: 'PlayfairDisplay-Variable.woff2',
      type: 'WOFF2',
      size: '234 KB',
      weights: ['400', '700'],
      usage: 'Quotes, elegant emphasis',
      compliance: 100,
      downloadUrl: '#'
    }
  ];

  const patternAssets = [
    {
      id: 'PAT-001',
      name: 'Subtle Grid',
      filename: 'subtle-grid.png',
      type: 'PNG',
      size: '12 KB',
      dimensions: '200x200',
      usage: 'Background texture',
      previewUrl: '/api/placeholder/200/200',
      compliance: 100
    },
    {
      id: 'PAT-002',
      name: 'Geometric Pattern',
      filename: 'geometric.png',
      type: 'PNG',
      size: '18 KB',
      dimensions: '200x200',
      usage: 'Decorative overlay',
      previewUrl: '/api/placeholder/200/200',
      compliance: 95
    }
  ];

  const { hasCopied, onCopy } = useClipboard('');

  const handleCopyColor = (hex: string) => {
    navigator.clipboard.writeText(hex).then(() => {
      toast({
        title: 'Color copied!',
        description: `${hex} copied to clipboard`,
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
    });
  };

  const handleDownload = (assetName: string) => {
    toast({
      title: 'Download started',
      description: `Downloading ${assetName}...`,
      status: 'info',
      duration: 2000,
      isClosable: true,
    });
  };

  return (
    <VStack spacing={8} align="stretch">
      {/* Asset Stats */}
      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6}>
        <Card bg={cardBg}>
          <CardBody>
            <VStack spacing={2}>
              <Icon as={FiLayers} boxSize="24px" color="brand.deepBlue" />
              <Text fontSize="2xl" fontWeight="bold" color="brand.deepBlue">
                {assetStats.totalAssets}
              </Text>
              <Text fontSize="sm" color="gray.500" textAlign="center">
                Total Assets
              </Text>
            </VStack>
          </CardBody>
        </Card>

        <Card bg={cardBg}>
          <CardBody>
            <VStack spacing={2}>
              <Icon as={FiImage} boxSize="24px" color="brand.gold" />
              <Text fontSize="2xl" fontWeight="bold" color="brand.gold">
                {assetStats.logoVariants}
              </Text>
              <Text fontSize="sm" color="gray.500" textAlign="center">
                Logo Variants
              </Text>
            </VStack>
          </CardBody>
        </Card>

        <Card bg={cardBg}>
          <CardBody>
            <VStack spacing={2}>
              <Icon as={FiPalette} boxSize="24px" color="brand.gulfTeal" />
              <Text fontSize="2xl" fontWeight="bold" color="brand.gulfTeal">
                {assetStats.colorPalettes}
              </Text>
              <Text fontSize="sm" color="gray.500" textAlign="center">
                Color Palettes
              </Text>
            </VStack>
          </CardBody>
        </Card>

        <Card bg={cardBg}>
          <CardBody>
            <VStack spacing={1}>
              <Text fontSize="sm" color="gray.500">Storage Used</Text>
              <Text fontSize="lg" fontWeight="bold" color="brand.deepBlue">
                {assetStats.storageUsed} MB
              </Text>
              <Progress
                value={(assetStats.storageUsed / assetStats.storageLimit) * 100}
                colorScheme="blue"
                size="sm"
                w="full"
              />
              <Text fontSize="xs" color="gray.400">
                of {assetStats.storageLimit} MB
              </Text>
            </VStack>
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
                <Input placeholder="Search assets..." size="sm" />
              </InputGroup>

              <Select placeholder="Asset Type" size="sm" maxW="150px">
                <option value="logos">Logos</option>
                <option value="colors">Colors</option>
                <option value="fonts">Fonts</option>
                <option value="patterns">Patterns</option>
                <option value="templates">Templates</option>
              </Select>

              <Select placeholder="Sort by" size="sm" maxW="150px">
                <option value="name">Name</option>
                <option value="date">Date Modified</option>
                <option value="usage">Usage</option>
                <option value="size">File Size</option>
              </Select>
            </HStack>

            <HStack spacing={3}>
              <Button size="sm" variant="outline" colorScheme="bymb">
                Organize Assets
              </Button>
              <Button size="sm" variant="bymb" leftIcon={<FiUpload />} onClick={onOpen}>
                Upload Asset
              </Button>
            </HStack>
          </Flex>
        </CardBody>
      </Card>

      {/* Asset Library Tabs */}
      <Tabs variant="enclosed" colorScheme="bymb">
        <TabList>
          <Tab>
            <HStack>
              <Icon as={FiImage} />
              <Text>Logos</Text>
            </HStack>
          </Tab>
          <Tab>
            <HStack>
              <Icon as={FiPalette} />
              <Text>Colors</Text>
            </HStack>
          </Tab>
          <Tab>
            <HStack>
              <Icon as={FiType} />
              <Text>Fonts</Text>
            </HStack>
          </Tab>
          <Tab>
            <HStack>
              <Icon as={FiLayers} />
              <Text>Patterns</Text>
            </HStack>
          </Tab>
        </TabList>

        <TabPanels>
          {/* Logo Assets */}
          <TabPanel px={0}>
            <Grid
              templateColumns={{
                base: '1fr',
                md: 'repeat(2, 1fr)',
                lg: 'repeat(3, 1fr)',
                xl: 'repeat(4, 1fr)'
              }}
              gap={6}
            >
              {logoAssets.map((logo) => (
                <Card key={logo.id} bg={cardBg} overflow="hidden">
                  <Box position="relative" bg="gray.50" p={4} textAlign="center">
                    <Image
                      src={logo.previewUrl}
                      alt={logo.name}
                      maxH="120px"
                      mx="auto"
                      fallback={
                        <Box h="120px" display="flex" alignItems="center" justifyContent="center">
                          <Icon as={FiImage} boxSize="40px" color="gray.400" />
                        </Box>
                      }
                    />
                    <Box position="absolute" top={2} right={2}>
                      <HStack spacing={1}>
                        <Tooltip label="View">
                          <Button size="xs" variant="ghost" bg="white">
                            <Icon as={FiEye} />
                          </Button>
                        </Tooltip>
                        <Tooltip label="Download">
                          <Button 
                            size="xs" 
                            variant="ghost" 
                            bg="white"
                            onClick={() => handleDownload(logo.name)}
                          >
                            <Icon as={FiDownload} />
                          </Button>
                        </Tooltip>
                      </HStack>
                    </Box>
                  </Box>

                  <CardBody>
                    <VStack align="start" spacing={3}>
                      <Box w="full">
                        <HStack justify="space-between" align="start">
                          <VStack align="start" spacing={1} flex="1">
                            <Text fontWeight="semibold" fontSize="sm">
                              {logo.name}
                            </Text>
                            <Text fontSize="xs" color="gray.500">
                              {logo.filename}
                            </Text>
                          </VStack>
                          <Badge colorScheme="green" size="sm">
                            {logo.compliance}%
                          </Badge>
                        </HStack>
                      </Box>

                      <Box w="full">
                        <Text fontSize="xs" color="gray.600" mb={2}>
                          Usage Guidelines
                        </Text>
                        <Text fontSize="xs" color="gray.500" noOfLines={2}>
                          {logo.usage}
                        </Text>
                      </Box>

                      <Grid templateColumns="1fr 1fr" gap={4} w="full" fontSize="xs">
                        <Box>
                          <Text color="gray.500">Type</Text>
                          <Text fontWeight="medium">{logo.type}</Text>
                        </Box>
                        <Box>
                          <Text color="gray.500">Size</Text>
                          <Text fontWeight="medium">{logo.size}</Text>
                        </Box>
                        <Box>
                          <Text color="gray.500">Dimensions</Text>
                          <Text fontWeight="medium">{logo.dimensions}</Text>
                        </Box>
                        <Box>
                          <Text color="gray.500">Modified</Text>
                          <Text fontWeight="medium">{logo.lastModified}</Text>
                        </Box>
                      </Grid>

                      <HStack justify="space-between" w="full" pt={2}>
                        <Button size="sm" variant="outline" colorScheme="bymb">
                          Use Asset
                        </Button>
                        <HStack spacing={1}>
                          <Button size="sm" variant="ghost" colorScheme="bymb">
                            <Icon as={FiCopy} />
                          </Button>
                          <Button size="sm" variant="ghost" colorScheme="bymb">
                            <Icon as={FiEdit} />
                          </Button>
                        </HStack>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>
              ))}
            </Grid>
          </TabPanel>

          {/* Color Palettes */}
          <TabPanel px={0}>
            <Grid templateColumns={{ base: '1fr', lg: 'repeat(2, 1fr)' }} gap={6}>
              {colorPalettes.map((palette) => (
                <Card key={palette.id} bg={cardBg}>
                  <CardHeader>
                    <HStack justify="space-between">
                      <VStack align="start" spacing={0}>
                        <Text fontWeight="semibold" fontSize="md">
                          {palette.name}
                        </Text>
                        <Text fontSize="sm" color="gray.500">
                          {palette.colors.length} colors • {palette.usage} uses
                        </Text>
                      </VStack>
                      <Badge colorScheme="green" size="sm">
                        {palette.compliance}%
                      </Badge>
                    </HStack>
                  </CardHeader>
                  <CardBody pt={0}>
                    <VStack spacing={4} align="stretch">
                      {palette.colors.map((color, index) => (
                        <Flex key={index} align="center" gap={4}>
                          <Tooltip label="Click to copy color">
                            <Box
                              w="50px"
                              h="50px"
                              bg={color.hex}
                              borderRadius="md"
                              border="1px solid"
                              borderColor="gray.200"
                              cursor="pointer"
                              onClick={() => handleCopyColor(color.hex)}
                              _hover={{ transform: 'scale(1.05)' }}
                              transition="transform 0.2s"
                            />
                          </Tooltip>
                          <Box flex="1">
                            <HStack justify="space-between" align="start">
                              <VStack align="start" spacing={0}>
                                <Text fontWeight="semibold" fontSize="sm">
                                  {color.name}
                                </Text>
                                <Text fontSize="xs" color="gray.500">
                                  {color.hex} • {color.usage}
                                </Text>
                              </VStack>
                              <Button
                                size="xs"
                                variant="ghost"
                                onClick={() => handleCopyColor(color.hex)}
                              >
                                <Icon as={FiCopy} />
                              </Button>
                            </HStack>
                          </Box>
                        </Flex>
                      ))}
                    </VStack>
                  </CardBody>
                </Card>
              ))}
            </Grid>
          </TabPanel>

          {/* Font Assets */}
          <TabPanel px={0}>
            <Grid templateColumns={{ base: '1fr', lg: 'repeat(2, 1fr)' }} gap={6}>
              {fontAssets.map((font) => (
                <Card key={font.id} bg={cardBg}>
                  <CardBody>
                    <VStack align="start" spacing={4}>
                      <HStack justify="space-between" w="full">
                        <VStack align="start" spacing={0}>
                          <Text fontWeight="semibold" fontSize="lg" fontFamily={font.name.toLowerCase()}>
                            {font.name}
                          </Text>
                          <Text fontSize="sm" color="gray.500">
                            {font.filename}
                          </Text>
                        </VStack>
                        <Badge colorScheme="green" size="sm">
                          {font.compliance}%
                        </Badge>
                      </HStack>

                      <Box w="full">
                        <Text 
                          fontSize="xl" 
                          fontFamily={font.name.toLowerCase()}
                          color="brand.deepBlue"
                          mb={2}
                        >
                          The quick brown fox jumps over the lazy dog
                        </Text>
                        <Text 
                          fontSize="sm" 
                          fontFamily={font.name.toLowerCase()}
                          color="gray.600"
                        >
                          ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789
                        </Text>
                      </Box>

                      <Grid templateColumns="1fr 1fr" gap={4} w="full" fontSize="sm">
                        <Box>
                          <Text fontSize="xs" color="gray.500">Weights Available</Text>
                          <HStack spacing={1} flexWrap="wrap">
                            {font.weights.map((weight) => (
                              <Badge key={weight} size="sm" variant="outline">
                                {weight}
                              </Badge>
                            ))}
                          </HStack>
                        </Box>
                        <Box>
                          <Text fontSize="xs" color="gray.500">File Size</Text>
                          <Text fontWeight="medium">{font.size}</Text>
                        </Box>
                        <Box gridColumn="1 / -1">
                          <Text fontSize="xs" color="gray.500">Usage</Text>
                          <Text fontWeight="medium" fontSize="sm">{font.usage}</Text>
                        </Box>
                      </Grid>

                      <HStack justify="space-between" w="full" pt={2}>
                        <Button 
                          size="sm" 
                          variant="outline" 
                          colorScheme="bymb"
                          onClick={() => handleDownload(font.name)}
                        >
                          Download Font
                        </Button>
                        <Button size="sm" variant="ghost" colorScheme="bymb">
                          View Specimens
                        </Button>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>
              ))}
            </Grid>
          </TabPanel>

          {/* Pattern Assets */}
          <TabPanel px={0}>
            <Grid
              templateColumns={{
                base: '1fr',
                md: 'repeat(2, 1fr)',
                lg: 'repeat(3, 1fr)',
                xl: 'repeat(4, 1fr)'
              }}
              gap={6}
            >
              {patternAssets.map((pattern) => (
                <Card key={pattern.id} bg={cardBg} overflow="hidden">
                  <Box position="relative" bg="gray.50" p={4} textAlign="center">
                    <Image
                      src={pattern.previewUrl}
                      alt={pattern.name}
                      w="full"
                      h="120px"
                      objectFit="cover"
                      fallback={
                        <Box h="120px" display="flex" alignItems="center" justifyContent="center">
                          <Icon as={FiLayers} boxSize="40px" color="gray.400" />
                        </Box>
                      }
                    />
                    <Box position="absolute" top={2} right={2}>
                      <Badge colorScheme="green" size="sm">
                        {pattern.compliance}%
                      </Badge>
                    </Box>
                  </Box>

                  <CardBody>
                    <VStack align="start" spacing={3}>
                      <Box w="full">
                        <Text fontWeight="semibold" fontSize="sm" mb={1}>
                          {pattern.name}
                        </Text>
                        <Text fontSize="xs" color="gray.500">
                          {pattern.filename}
                        </Text>
                      </Box>

                      <Grid templateColumns="1fr 1fr" gap={4} w="full" fontSize="xs">
                        <Box>
                          <Text color="gray.500">Type</Text>
                          <Text fontWeight="medium">{pattern.type}</Text>
                        </Box>
                        <Box>
                          <Text color="gray.500">Size</Text>
                          <Text fontWeight="medium">{pattern.size}</Text>
                        </Box>
                        <Box>
                          <Text color="gray.500">Dimensions</Text>
                          <Text fontWeight="medium">{pattern.dimensions}</Text>
                        </Box>
                        <Box>
                          <Text color="gray.500">Usage</Text>
                          <Text fontWeight="medium">{pattern.usage}</Text>
                        </Box>
                      </Grid>

                      <HStack justify="space-between" w="full" pt={2}>
                        <Button 
                          size="sm" 
                          variant="outline" 
                          colorScheme="bymb"
                          onClick={() => handleDownload(pattern.name)}
                        >
                          Download
                        </Button>
                        <HStack spacing={1}>
                          <Button size="sm" variant="ghost" colorScheme="bymb">
                            <Icon as={FiEye} />
                          </Button>
                          <Button size="sm" variant="ghost" colorScheme="bymb">
                            <Icon as={FiEdit} />
                          </Button>
                        </HStack>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>
              ))}
            </Grid>
          </TabPanel>
        </TabPanels>
      </Tabs>

      {/* Upload Asset Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader color="brand.deepBlue">Upload Brand Asset</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={6} align="stretch">
              <Box
                border="2px dashed"
                borderColor="brand.deepBlue"
                borderRadius="md"
                p={8}
                textAlign="center"
                bg="brand.deepBlue"
                color="white"
                _hover={{ bg: 'bymb.600' }}
                cursor="pointer"
              >
                <Icon as={FiUpload} boxSize="40px" mb={4} />
                <Text fontSize="lg" fontWeight="medium" mb={2}>
                  Drop files here or click to browse
                </Text>
                <Text fontSize="sm" opacity={0.8}>
                  Supported formats: PNG, JPG, SVG, WOFF, WOFF2
                </Text>
              </Box>

              <Grid templateColumns="1fr 1fr" gap={4}>
                <FormControl>
                  <FormLabel fontSize="sm">Asset Type</FormLabel>
                  <Select>
                    <option value="logo">Logo</option>
                    <option value="color">Color Palette</option>
                    <option value="font">Font File</option>
                    <option value="pattern">Pattern/Texture</option>
                    <option value="template">Template</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel fontSize="sm">Usage Category</FormLabel>
                  <Select>
                    <option value="primary">Primary</option>
                    <option value="secondary">Secondary</option>
                    <option value="accent">Accent</option>
                    <option value="supporting">Supporting</option>
                  </Select>
                </FormControl>
              </Grid>

              <FormControl>
                <FormLabel fontSize="sm">Asset Name</FormLabel>
                <Input placeholder="Enter descriptive name for the asset..." />
              </FormControl>

              <FormControl>
                <FormLabel fontSize="sm">Usage Guidelines</FormLabel>
                <Input placeholder="When and how should this asset be used..." />
              </FormControl>

              <Box p={4} bg="gray.50" borderRadius="md">
                <Text fontSize="sm" fontWeight="medium" color="gray.700" mb={2}>
                  Brand Compliance Check
                </Text>
                <Text fontSize="xs" color="gray.600">
                  All uploaded assets will be automatically checked for brand compliance 
                  and assigned a compliance score based on BYMB brand guidelines.
                </Text>
              </Box>
            </VStack>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button variant="bymb">
              Upload Asset
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </VStack>
  );
}