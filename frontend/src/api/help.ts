/**
 * ヘルプシステムAPI呼び出し
 */
import apiClient from './axios';
import type {
  FaqListResponse,
  FaqSearchResponse,
  ChatRequest,
  ChatResponse,
} from '@/types/help';

/**
 * ヘルプAPI
 */
export const helpApi = {
  /**
   * FAQ一覧取得
   */
  async getFaqs(params?: {
    category?: string;
    language?: string;
  }): Promise<FaqListResponse> {
    const response = await apiClient.get<FaqListResponse>('/help/faqs', {
      params: {
        language: params?.language || 'ja',
        ...(params?.category && { category: params.category }),
      },
    });
    return response.data;
  },

  /**
   * FAQ検索
   */
  async searchFaqs(params: {
    query: string;
    language?: string;
    limit?: number;
  }): Promise<FaqSearchResponse> {
    const response = await apiClient.get<FaqSearchResponse>('/help/search', {
      params: {
        q: params.query,
        language: params.language || 'ja',
        limit: params.limit || 10,
      },
    });
    return response.data;
  },

  /**
   * AIチャット送信
   */
  async sendChat(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>('/help/chat', request);
    return response.data;
  },
};

