import { create } from 'zustand';

// Types for social media optimization
export type SocialPlatform = 'instagram' | 'linkedin' | 'twitter' | 'facebook';
export type ContentType = 'post' | 'story' | 'carousel' | 'infographic' | 'video' | 'article';
export type ToneOfVoice = 'professional' | 'thought_leader' | 'educational' | 'inspirational' | 'conversational';

export interface ContentOptimization {
  platform: SocialPlatform;
  content_type: ContentType;
  title: string;
  caption: string;
  hashtags: string[];
  tone: ToneOfVoice;
  call_to_action: string;
  image_specs: {
    dimensions: [number, number];
    aspect_ratio: number;
    format: string;
    quality: number;
    color_profile: string;
    brand_elements_required: boolean;
  };
  engagement_elements: string[];
  optimal_posting_time: string;
  performance_predictions: Record<string, number>;
  brand_compliance: Record<string, boolean>;
}

export interface EngagementPrediction {
  predicted_metrics: Record<string, number>;
  confidence_score: number;
  key_factors: string[];
  optimization_suggestions: string[];
  risk_factors: string[];
  expected_timeline: Record<string, number>;
}

export interface ScheduledContent {
  content_id: string;
  scheduled_time: string;
  priority: string;
  platform: SocialPlatform;
  content_type: ContentType;
  tags: string[];
  performance_prediction: Record<string, number>;
  status: string;
}

interface AppState {
  // General app state
  isLoading: boolean;
  setIsLoading: (isLoading: boolean) => void;
  
  // Social media optimization state
  currentOptimization: ContentOptimization | null;
  multiPlatformCampaign: Record<string, ContentOptimization[]> | null;
  engagementPrediction: EngagementPrediction | null;
  contentSchedule: ScheduledContent[] | null;
  optimizationHistory: ContentOptimization[];
  
  // Actions
  setCurrentOptimization: (optimization: ContentOptimization | null) => void;
  setMultiPlatformCampaign: (campaign: Record<string, ContentOptimization[]> | null) => void;
  setEngagementPrediction: (prediction: EngagementPrediction | null) => void;
  setContentSchedule: (schedule: ScheduledContent[] | null) => void;
  addToHistory: (optimization: ContentOptimization) => void;
  clearHistory: () => void;
  
  // Form state
  inputContent: string;
  selectedPlatforms: SocialPlatform[];
  selectedContentType: ContentType;
  selectedTone: ToneOfVoice;
  targetAudience: string;
  
  // Form actions
  setInputContent: (content: string) => void;
  setSelectedPlatforms: (platforms: SocialPlatform[]) => void;
  setSelectedContentType: (type: ContentType) => void;
  setSelectedTone: (tone: ToneOfVoice) => void;
  setTargetAudience: (audience: string) => void;
  
  // UI state
  activeTab: string;
  sidebarOpen: boolean;
  setActiveTab: (tab: string) => void;
  setSidebarOpen: (open: boolean) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  // General app state
  isLoading: false,
  setIsLoading: (isLoading: boolean) => set({ isLoading }),
  
  // Social media optimization state
  currentOptimization: null,
  multiPlatformCampaign: null,
  engagementPrediction: null,
  contentSchedule: null,
  optimizationHistory: [],
  
  // Actions
  setCurrentOptimization: (optimization) => set({ currentOptimization: optimization }),
  setMultiPlatformCampaign: (campaign) => set({ multiPlatformCampaign: campaign }),
  setEngagementPrediction: (prediction) => set({ engagementPrediction: prediction }),
  setContentSchedule: (schedule) => set({ contentSchedule: schedule }),
  addToHistory: (optimization) => {
    const { optimizationHistory } = get();
    const newHistory = [optimization, ...optimizationHistory.slice(0, 9)]; // Keep last 10
    set({ optimizationHistory: newHistory });
  },
  clearHistory: () => set({ optimizationHistory: [] }),
  
  // Form state
  inputContent: '',
  selectedPlatforms: ['linkedin'],
  selectedContentType: 'post',
  selectedTone: 'professional',
  targetAudience: 'business_leaders',
  
  // Form actions
  setInputContent: (content) => set({ inputContent: content }),
  setSelectedPlatforms: (platforms) => set({ selectedPlatforms: platforms }),
  setSelectedContentType: (type) => set({ selectedContentType: type }),
  setSelectedTone: (tone) => set({ selectedTone: tone }),
  setTargetAudience: (audience) => set({ targetAudience: audience }),
  
  // UI state
  activeTab: 'optimize',
  sidebarOpen: true,
  setActiveTab: (tab) => set({ activeTab: tab }),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
}));
