/**
 * Test cases for Chat API
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  sendChatMessage,
  getChatHistory,
  clearChatHistory,
  getAnalyticsSummary,
  getAnalyticsTrends,
} from '../api/chatApi';
import * as authApi from '../api/authApi';

// Mock fetch
global.fetch = vi.fn();

// Mock auth
vi.mock('../api/authApi', () => ({
  getToken: vi.fn(() => 'test_token'),
}));

describe('Chat API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('sendChatMessage', () => {
    it('sends POST request with message', async () => {
      const mockResponse = {
        reply: 'Test response',
        intent: 'general',
        suggestions: ['Option 1'],
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await sendChatMessage('Hello');

      expect(fetch).toHaveBeenCalledWith(
        'http://127.0.0.1:8000/chat',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test_token',
          }),
          body: JSON.stringify({ message: 'Hello' }),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('returns response with chart data for forecast', async () => {
      const mockResponse = {
        reply: 'Forecast generated',
        intent: 'forecast',
        suggestions: [],
        data: {
          product_id: 'P0001',
          history: [{ date: '2024-01-01', demand: 100 }],
          forecast: [{ date: '2024-01-02', predicted_demand: 110 }],
        },
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await sendChatMessage('Forecast for P0001');

      expect(result.data).toBeDefined();
      expect(result.data.product_id).toBe('P0001');
    });

    it('throws error on failed request', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Unauthorized' }),
      });

      await expect(sendChatMessage('Hello')).rejects.toThrow('Unauthorized');
    });

    it('throws generic error when no detail', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({}),
      });

      await expect(sendChatMessage('Hello')).rejects.toThrow('Chat request failed (500)');
    });
  });

  describe('getChatHistory', () => {
    it('fetches history without limit', async () => {
      const mockHistory = [
        { role: 'user', content: 'Hello', timestamp: '2024-01-01T10:00:00' },
        { role: 'assistant', content: 'Hi', timestamp: '2024-01-01T10:00:01' },
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockHistory,
      });

      const result = await getChatHistory();

      expect(fetch).toHaveBeenCalledWith(
        'http://127.0.0.1:8000/chat/history',
        expect.any(Object)
      );
      expect(result).toEqual(mockHistory);
    });

    it('passes limit parameter', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      await getChatHistory(10);

      expect(fetch).toHaveBeenCalledWith(
        'http://127.0.0.1:8000/chat/history?limit=10',
        expect.any(Object)
      );
    });

    it('throws error on failed request', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      await expect(getChatHistory()).rejects.toThrow('Failed to fetch chat history (401)');
    });
  });

  describe('clearChatHistory', () => {
    it('sends DELETE request', async () => {
      const mockResponse = {
        message: 'History cleared',
        cleared_messages: 5,
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await clearChatHistory();

      expect(fetch).toHaveBeenCalledWith(
        'http://127.0.0.1:8000/chat/history',
        expect.objectContaining({
          method: 'DELETE',
        })
      );
      expect(result.cleared_messages).toBe(5);
    });

    it('throws error on failed request', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      await expect(clearChatHistory()).rejects.toThrow('Failed to clear chat history (500)');
    });
  });

  describe('getAnalyticsSummary', () => {
    it('fetches analytics summary', async () => {
      const mockSummary = {
        overview: { total_records: 1000, total_products: 50 },
        top_by_demand: [{ product_id: 'P0001', avg_demand: 150 }],
        top_by_growth: [],
        declining: [],
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSummary,
      });

      const result = await getAnalyticsSummary();

      expect(fetch).toHaveBeenCalledWith(
        'http://127.0.0.1:8000/analytics/summary',
        expect.any(Object)
      );
      expect(result.overview.total_records).toBe(1000);
    });

    it('throws error on failed request', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      await expect(getAnalyticsSummary()).rejects.toThrow('Failed to fetch analytics summary (500)');
    });
  });

  describe('getAnalyticsTrends', () => {
    it('fetches analytics trends', async () => {
      const mockTrends = {
        growing: [{ product_id: 'P0001', growth_pct: 10 }],
        declining: [{ product_id: 'P0002', decline_pct: 5 }],
        stable: [],
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTrends,
      });

      const result = await getAnalyticsTrends();

      expect(fetch).toHaveBeenCalledWith(
        'http://127.0.0.1:8000/analytics/trends',
        expect.any(Object)
      );
      expect(result.growing.length).toBe(1);
      expect(result.declining.length).toBe(1);
    });

    it('throws error on failed request', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      await expect(getAnalyticsTrends()).rejects.toThrow('Failed to fetch analytics trends (500)');
    });
  });
});

describe('Authentication', () => {
  it('includes auth header when token exists', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ reply: 'Test', intent: 'general', suggestions: [] }),
    });

    await sendChatMessage('Test');

    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Authorization': 'Bearer test_token',
        }),
      })
    );
  });

  it('does not include auth header when no token', async () => {
    authApi.getToken.mockReturnValueOnce(null);

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ reply: 'Test', intent: 'general', suggestions: [] }),
    });

    await sendChatMessage('Test');

    const callArgs = fetch.mock.calls[0][1];
    expect(callArgs.headers['Authorization']).toBeUndefined();
  });
});
