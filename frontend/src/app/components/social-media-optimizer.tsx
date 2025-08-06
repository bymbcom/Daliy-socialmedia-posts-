'use client';

import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Textarea,
  Button,
  Select,
  Checkbox,
  CheckboxGroup,
  Stack,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Badge,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Spinner,
  useToast,
  Divider,
  Tag,
  TagLabel,
  IconButton,
  Tooltip,
  Progress,
  Flex,
  Spacer
} from '@chakra-ui/react';
import { 
  FiTarget, 
  FiTrendingUp, 
  FiCalendar, 
  FiBarChart3, 
  FiShare2,
  FiCopy,
  FiDownload,
  FiRefreshCw,
  FiEye,
  FiThumbsUp,
  FiMessageSquare
} from 'react-icons/fi';

import { useAppStore, SocialPlatform, ContentType, ToneOfVoice, ContentOptimization } from '../stores/app-store';

const PLATFORM_COLORS: Record<SocialPlatform, string> = {
  linkedin: 'blue',
  instagram: 'purple', 
  twitter: 'cyan',
  facebook: 'blue'
};

const PLATFORM_ICONS: Record<SocialPlatform, string> = {
  linkedin: '💼',
  instagram: '📸',
  twitter: '🐦',
  facebook: '👥'
};

export default function SocialMediaOptimizer() {
  const {
    isLoading,
    setIsLoading,
    currentOptimization,
    setCurrentOptimization,
    multiPlatformCampaign,
    setMultiPlatformCampaign,
    engagementPrediction,
    setEngagementPrediction,
    inputContent,
    setInputContent,
    selectedPlatforms,
    setSelectedPlatforms,
    selectedContentType,
    setSelectedContentType,
    selectedTone,
    setSelectedTone,
    targetAudience,
    setTargetAudience,
    activeTab,
    setActiveTab,
    addToHistory
  } = useAppStore();

  const toast = useToast();
  const [apiError, setApiError] = useState<string | null>(null);

  const handleOptimizeContent = async () => {
    if (!inputContent.trim()) {
      toast({
        title: 'Content Required',
        description: 'Please enter content to optimize',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsLoading(true);
    setApiError(null);

    try {
      if (selectedPlatforms.length === 1) {
        // Single platform optimization
        const response = await fetch('/api/social-media/optimize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: inputContent,
            platform: selectedPlatforms[0],
            content_type: selectedContentType,
            target_audience: targetAudience,
            tone: selectedTone
          })
        });

        if (!response.ok) {
          throw new Error(`API Error: ${response.status}`);
        }

        const optimization = await response.json();
        setCurrentOptimization(optimization);
        addToHistory(optimization);

        // Also get engagement prediction
        await getPrediction(optimization);

        toast({
          title: 'Content Optimized',
          description: `Successfully optimized for ${selectedPlatforms[0]}`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } else {
        // Multi-platform optimization
        const response = await fetch('/api/social-media/multi-platform', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: inputContent,
            platforms: selectedPlatforms,
            content_types: [selectedContentType],
            target_audience: targetAudience
          })
        });

        if (!response.ok) {
          throw new Error(`API Error: ${response.status}`);
        }

        const result = await response.json();
        setMultiPlatformCampaign(result.campaign);

        toast({
          title: 'Multi-Platform Campaign Generated',
          description: `Optimized for ${selectedPlatforms.length} platforms`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';
      setApiError(errorMessage);
      toast({
        title: 'Optimization Failed',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getPrediction = async (optimization: ContentOptimization) => {
    try {
      const response = await fetch('/api/engagement/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: optimization.caption,
          platform: optimization.platform,
          content_type: optimization.content_type,
          hashtags: optimization.hashtags,
          posting_time: optimization.optimal_posting_time,
          tone: optimization.tone
        })
      });

      if (response.ok) {
        const prediction = await response.json();
        setEngagementPrediction(prediction);
      }
    } catch (error) {
      console.error('Failed to get engagement prediction:', error);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: 'Copied to Clipboard',
      status: 'success',
      duration: 2000,
      isClosable: true,
    });
  };

  const formatMetric = (value: number, type: 'percentage' | 'number' | 'multiplier' = 'percentage') => {
    switch (type) {
      case 'percentage':
        return `${(value * 100).toFixed(1)}%`;
      case 'multiplier':
        return `${value.toFixed(1)}x`;
      case 'number':
        return value.toLocaleString();
      default:
        return value.toString();
    }
  };

  return (
    <Box p={6} maxW="100%" mx="auto">
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" color="blue.600" mb={2}>
            Social Media Content Optimizer
          </Heading>
          <Text color="gray.600">
            Transform your business insights into engaging, platform-optimized social media content
          </Text>
        </Box>

        {/* Input Section */}
        <Card>
          <CardHeader>
            <Heading size="md">Content Input</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Box>
                <Text mb={2} fontWeight="semibold">Your Business Insight</Text>
                <Textarea
                  value={inputContent}
                  onChange={(e) => setInputContent(e.target.value)}
                  placeholder="Enter your business insight, strategy tip, or thought leadership content here..."
                  size="lg"
                  minH="120px"
                  resize="vertical"
                />
              </Box>

              <SimpleGrid columns={[1, 2, 4]} spacing={4}>
                <Box>
                  <Text mb={2} fontWeight="semibold">Target Platforms</Text>
                  <CheckboxGroup
                    value={selectedPlatforms}
                    onChange={(values) => setSelectedPlatforms(values as SocialPlatform[])}
                  >
                    <Stack spacing={2}>
                      {(['linkedin', 'instagram', 'twitter', 'facebook'] as SocialPlatform[]).map((platform) => (
                        <Checkbox key={platform} value={platform} colorScheme={PLATFORM_COLORS[platform]}>
                          <HStack>
                            <Text>{PLATFORM_ICONS[platform]}</Text>
                            <Text textTransform="capitalize">{platform}</Text>
                          </HStack>
                        </Checkbox>
                      ))}
                    </Stack>
                  </CheckboxGroup>
                </Box>

                <Box>
                  <Text mb={2} fontWeight="semibold">Content Type</Text>
                  <Select
                    value={selectedContentType}
                    onChange={(e) => setSelectedContentType(e.target.value as ContentType)}
                  >
                    <option value="post">Post</option>
                    <option value="carousel">Carousel</option>
                    <option value="infographic">Infographic</option>
                    <option value="story">Story</option>
                    <option value="video">Video</option>
                    <option value="article">Article</option>
                  </Select>
                </Box>

                <Box>
                  <Text mb={2} fontWeight="semibold">Tone of Voice</Text>
                  <Select
                    value={selectedTone}
                    onChange={(e) => setSelectedTone(e.target.value as ToneOfVoice)}
                  >
                    <option value="professional">Professional</option>
                    <option value="thought_leader">Thought Leader</option>
                    <option value="educational">Educational</option>
                    <option value="inspirational">Inspirational</option>
                    <option value="conversational">Conversational</option>
                  </Select>
                </Box>

                <Box>
                  <Text mb={2} fontWeight="semibold">Target Audience</Text>
                  <Select
                    value={targetAudience}
                    onChange={(e) => setTargetAudience(e.target.value)}
                  >
                    <option value="business_leaders">Business Leaders</option>
                    <option value="entrepreneurs">Entrepreneurs</option>
                    <option value="corporate_executives">Corporate Executives</option>
                    <option value="small_business_owners">Small Business Owners</option>
                  </Select>
                </Box>
              </SimpleGrid>

              <Button
                colorScheme="blue"
                size="lg"
                onClick={handleOptimizeContent}
                isLoading={isLoading}
                loadingText="Optimizing..."
                leftIcon={<FiTarget />}
                disabled={!inputContent.trim() || selectedPlatforms.length === 0}
              >
                Optimize Content
              </Button>
            </VStack>
          </CardBody>
        </Card>

        {/* Error Display */}
        {apiError && (
          <Alert status="error">
            <AlertIcon />
            <AlertTitle>Optimization Error:</AlertTitle>
            <AlertDescription>{apiError}</AlertDescription>
          </Alert>
        )}

        {/* Results Section */}
        {(currentOptimization || multiPlatformCampaign) && (
          <Tabs index={activeTab === 'results' ? 0 : 1} onChange={(index) => setActiveTab(index === 0 ? 'results' : 'analytics')}>
            <TabList>
              <Tab>Optimized Content</Tab>
              <Tab>Analytics & Predictions</Tab>
            </TabList>

            <TabPanels>
              {/* Content Results Tab */}
              <TabPanel px={0}>
                {currentOptimization ? (
                  <SinglePlatformResults optimization={currentOptimization} onCopy={copyToClipboard} />
                ) : multiPlatformCampaign ? (
                  <MultiPlatformResults campaign={multiPlatformCampaign} onCopy={copyToClipboard} />
                ) : null}
              </TabPanel>

              {/* Analytics Tab */}
              <TabPanel px={0}>
                <AnalyticsPanel 
                  optimization={currentOptimization} 
                  prediction={engagementPrediction}
                  campaign={multiPlatformCampaign}
                />
              </TabPanel>
            </TabPanels>
          </Tabs>
        )}
      </VStack>
    </Box>
  );
}

// Single Platform Results Component
function SinglePlatformResults({ 
  optimization, 
  onCopy 
}: { 
  optimization: ContentOptimization; 
  onCopy: (text: string) => void;
}) {
  return (
    <Card>
      <CardHeader>
        <HStack>
          <Text fontSize="2xl">{PLATFORM_ICONS[optimization.platform]}</Text>
          <Heading size="md" textTransform="capitalize">
            {optimization.platform} Optimization
          </Heading>
          <Spacer />
          <Badge colorScheme={PLATFORM_COLORS[optimization.platform]} variant="subtle">
            {optimization.content_type}
          </Badge>
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack spacing={4} align="stretch">
          {/* Title */}
          {optimization.title && (
            <Box>
              <HStack mb={2}>
                <Text fontWeight="semibold">Title</Text>
                <Spacer />
                <IconButton
                  icon={<FiCopy />}
                  aria-label="Copy title"
                  size="sm"
                  variant="ghost"
                  onClick={() => onCopy(optimization.title)}
                />
              </HStack>
              <Text p={3} bg="gray.50" borderRadius="md" fontSize="lg" fontWeight="medium">
                {optimization.title}
              </Text>
            </Box>
          )}

          {/* Caption */}
          <Box>
            <HStack mb={2}>
              <Text fontWeight="semibold">Optimized Caption</Text>
              <Spacer />
              <IconButton
                icon={<FiCopy />}
                aria-label="Copy caption"
                size="sm"
                variant="ghost"
                onClick={() => onCopy(optimization.caption)}
              />
            </HStack>
            <Box p={3} bg="gray.50" borderRadius="md" maxH="200px" overflowY="auto">
              <Text whiteSpace="pre-wrap" fontSize="sm">
                {optimization.caption}
              </Text>
            </Box>
          </Box>

          {/* Hashtags */}
          <Box>
            <HStack mb={2}>
              <Text fontWeight="semibold">Hashtags ({optimization.hashtags.length})</Text>
              <Spacer />
              <IconButton
                icon={<FiCopy />}
                aria-label="Copy hashtags"
                size="sm"
                variant="ghost"
                onClick={() => onCopy(optimization.hashtags.join(' '))}
              />
            </HStack>
            <Flex wrap="wrap" gap={2}>
              {optimization.hashtags.map((hashtag, index) => (
                <Tag key={index} size="sm" colorScheme={PLATFORM_COLORS[optimization.platform]}>
                  <TagLabel>{hashtag}</TagLabel>
                </Tag>
              ))}
            </Flex>
          </Box>

          {/* Call to Action */}
          <Box>
            <Text fontWeight="semibold" mb={2}>Call to Action</Text>
            <Text p={3} bg="blue.50" borderRadius="md" color="blue.800">
              {optimization.call_to_action}
            </Text>
          </Box>

          {/* Posting Time */}
          <SimpleGrid columns={[1, 2]} spacing={4}>
            <Box>
              <Text fontWeight="semibold" mb={2}>Optimal Posting Time</Text>
              <HStack p={3} bg="green.50" borderRadius="md">
                <FiCalendar />
                <Text color="green.800">{optimization.optimal_posting_time}</Text>
              </HStack>
            </Box>

            <Box>
              <Text fontWeight="semibold" mb={2}>Content Tone</Text>
              <Badge colorScheme="purple" p={2} borderRadius="md" textTransform="capitalize">
                {optimization.tone.replace('_', ' ')}
              </Badge>
            </Box>
          </SimpleGrid>

          {/* Brand Compliance */}
          <Box>
            <Text fontWeight="semibold" mb={2}>Brand Compliance Check</Text>
            <SimpleGrid columns={[1, 2]} spacing={2}>
              {Object.entries(optimization.brand_compliance).map(([key, value]) => (
                <HStack key={key}>
                  <Badge colorScheme={value ? 'green' : 'red'} variant="subtle">
                    {value ? '✓' : '✗'}
                  </Badge>
                  <Text fontSize="sm" textTransform="capitalize">
                    {key.replace('_', ' ')}
                  </Text>
                </HStack>
              ))}
            </SimpleGrid>
          </Box>
        </VStack>
      </CardBody>
    </Card>
  );
}

// Multi Platform Results Component  
function MultiPlatformResults({ 
  campaign, 
  onCopy 
}: { 
  campaign: Record<string, ContentOptimization[]>;
  onCopy: (text: string) => void;
}) {
  return (
    <VStack spacing={4} align="stretch">
      <Text fontSize="lg" fontWeight="semibold">
        Multi-Platform Campaign ({Object.keys(campaign).length} platforms)
      </Text>
      
      {Object.entries(campaign).map(([platform, optimizations]) => (
        <Card key={platform}>
          <CardHeader pb={2}>
            <HStack>
              <Text fontSize="xl">{PLATFORM_ICONS[platform as SocialPlatform]}</Text>
              <Heading size="sm" textTransform="capitalize">{platform}</Heading>
              <Badge colorScheme={PLATFORM_COLORS[platform as SocialPlatform]} variant="subtle">
                {optimizations.length} content piece{optimizations.length !== 1 ? 's' : ''}
              </Badge>
            </HStack>
          </CardHeader>
          <CardBody pt={2}>
            {optimizations.map((opt, index) => (
              <Box key={index} mb={4} p={3} border="1px" borderColor="gray.200" borderRadius="md">
                <VStack spacing={3} align="stretch">
                  <HStack>
                    <Badge variant="outline">{opt.content_type}</Badge>
                    <Spacer />
                    <IconButton
                      icon={<FiCopy />}
                      aria-label="Copy content"
                      size="sm"
                      variant="ghost"
                      onClick={() => onCopy(`${opt.caption}\n\n${opt.hashtags.join(' ')}`)}
                    />
                  </HStack>
                  
                  <Text fontSize="sm" noOfLines={3}>
                    {opt.caption}
                  </Text>
                  
                  <HStack spacing={2}>
                    {opt.hashtags.slice(0, 3).map((hashtag, hIndex) => (
                      <Tag key={hIndex} size="xs" colorScheme={PLATFORM_COLORS[platform as SocialPlatform]}>
                        {hashtag}
                      </Tag>
                    ))}
                    {opt.hashtags.length > 3 && (
                      <Text fontSize="xs" color="gray.500">
                        +{opt.hashtags.length - 3} more
                      </Text>
                    )}
                  </HStack>
                </VStack>
              </Box>
            ))}
          </CardBody>
        </Card>
      ))}
    </VStack>
  );
}

// Analytics Panel Component
function AnalyticsPanel({ 
  optimization, 
  prediction, 
  campaign 
}: { 
  optimization: ContentOptimization | null;
  prediction: any;
  campaign: Record<string, ContentOptimization[]> | null;
}) {
  if (!optimization && !campaign) {
    return (
      <Alert status="info">
        <AlertIcon />
        <AlertDescription>
          Optimize content first to see analytics and performance predictions.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      {/* Performance Predictions */}
      {prediction && (
        <Card>
          <CardHeader>
            <HStack>
              <FiTrendingUp />
              <Heading size="md">Engagement Predictions</Heading>
              <Badge colorScheme="blue" variant="subtle">
                {(prediction.confidence_score * 100).toFixed(0)}% confidence
              </Badge>
            </HStack>
          </CardHeader>
          <CardBody>
            <SimpleGrid columns={[2, 4]} spacing={4} mb={4}>
              {Object.entries(prediction.predicted_metrics).map(([metric, value]) => (
                <Stat key={metric}>
                  <StatLabel fontSize="xs" textTransform="capitalize">
                    {metric.replace('_', ' ')}
                  </StatLabel>
                  <StatNumber fontSize="lg">
                    {typeof value === 'number' ? (value * 100).toFixed(1) + '%' : value}
                  </StatNumber>
                </Stat>
              ))}
            </SimpleGrid>

            {prediction.optimization_suggestions?.length > 0 && (
              <Box>
                <Text fontWeight="semibold" mb={2}>Optimization Suggestions</Text>
                <VStack align="stretch" spacing={1}>
                  {prediction.optimization_suggestions.map((suggestion: string, index: number) => (
                    <Text key={index} fontSize="sm" p={2} bg="blue.50" borderRadius="md">
                      • {suggestion}
                    </Text>
                  ))}
                </VStack>
              </Box>
            )}
          </CardBody>
        </Card>
      )}

      {/* Content Analysis */}
      {optimization && (
        <Card>
          <CardHeader>
            <HStack>
              <FiBarChart3 />
              <Heading size="md">Content Analysis</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <SimpleGrid columns={[1, 3]} spacing={4}>
              {Object.entries(optimization.performance_predictions).map(([key, value]) => (
                <Stat key={key}>
                  <StatLabel fontSize="xs" textTransform="capitalize">
                    {key.replace('_', ' ')}
                  </StatLabel>
                  <StatNumber fontSize="md">
                    {typeof value === 'number' ? (value * 100).toFixed(1) + '%' : value}
                  </StatNumber>
                  <StatHelpText>
                    <Progress 
                      value={typeof value === 'number' ? value * 100 : 0} 
                      size="sm" 
                      colorScheme={value > 0.5 ? 'green' : value > 0.3 ? 'yellow' : 'red'}
                    />
                  </StatHelpText>
                </Stat>
              ))}
            </SimpleGrid>
          </CardBody>
        </Card>
      )}

      {/* Campaign Overview */}
      {campaign && (
        <Card>
          <CardHeader>
            <HStack>
              <FiShare2 />
              <Heading size="md">Campaign Overview</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <SimpleGrid columns={[2, 4]} spacing={4}>
              <Stat>
                <StatLabel>Total Platforms</StatLabel>
                <StatNumber>{Object.keys(campaign).length}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Content Pieces</StatLabel>
                <StatNumber>
                  {Object.values(campaign).reduce((acc, opts) => acc + opts.length, 0)}
                </StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Avg Engagement</StatLabel>
                <StatNumber>
                  {(Object.values(campaign)
                    .flat()
                    .reduce((acc, opt) => acc + (opt.performance_predictions.engagement_rate || 0), 0) / 
                    Object.values(campaign).flat().length * 100
                  ).toFixed(1)}%
                </StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Brand Compliance</StatLabel>
                <StatNumber>
                  {(Object.values(campaign)
                    .flat()
                    .filter(opt => opt.brand_compliance.overall_compliant)
                    .length / Object.values(campaign).flat().length * 100
                  ).toFixed(0)}%
                </StatNumber>
              </Stat>
            </SimpleGrid>
          </CardBody>
        </Card>
      )}
    </VStack>
  );
}