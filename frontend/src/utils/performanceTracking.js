import { useEffect, useCallback } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Generate or get session ID
const getSessionId = () => {
  let sessionId = sessionStorage.getItem('user_session');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('user_session', sessionId);
  }
  return sessionId;
};

// Track event helper
const trackEvent = async (siteId, eventType, value = 1.0) => {
  try {
    await axios.post(`${API}/track/event`, {
      site_id: siteId,
      event_type: eventType,
      value: value,
      user_session: getSessionId(),
      page_url: window.location.href
    });
  } catch (error) {
    console.error('Tracking error:', error);
  }
};

// Track CTA click
export const trackCtaClick = (siteId) => {
  trackEvent(siteId, 'cta_click');
};

// Track affiliate click
export const trackAffiliateClick = (siteId) => {
  trackEvent(siteId, 'affiliate_click');
};

// Track impression
export const trackImpression = (siteId) => {
  trackEvent(siteId, 'impression');
};

// Track scroll depth
export const trackScrollDepth = (siteId, depth) => {
  trackEvent(siteId, 'scroll', depth);
};

// Track time on page
export const trackTimeOnPage = (siteId, seconds) => {
  trackEvent(siteId, 'time_on_page', seconds);
};

// Custom hook for tracking bonus card visibility and interactions
export const usePerformanceTracking = (siteId) => {
  const startTime = Date.now();

  useEffect(() => {
    if (!siteId) return;

    // Track impression when component mounts
    trackImpression(siteId);

    // Track scroll depth
    const handleScroll = () => {
      const scrollPercent = Math.round(
        (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
      );
      // Only track significant scroll milestones
      if (scrollPercent > 0 && scrollPercent % 25 === 0) {
        trackScrollDepth(siteId, scrollPercent);
      }
    };

    window.addEventListener('scroll', handleScroll);

    // Track time on page when leaving
    return () => {
      window.removeEventListener('scroll', handleScroll);
      const timeSpent = Math.round((Date.now() - startTime) / 1000);
      if (timeSpent > 5) { // Only track if more than 5 seconds
        trackTimeOnPage(siteId, timeSpent);
      }
    };
  }, [siteId]);

  const handleCtaClick = useCallback(() => {
    trackCtaClick(siteId);
  }, [siteId]);

  const handleAffiliateClick = useCallback(() => {
    trackAffiliateClick(siteId);
  }, [siteId]);

  return { handleCtaClick, handleAffiliateClick };
};

// Batch tracking for multiple impressions
export const trackBatchImpressions = async (siteIds) => {
  if (!siteIds || siteIds.length === 0) return;

  const events = siteIds.map(siteId => ({
    site_id: siteId,
    event_type: 'impression',
    value: 1.0,
    user_session: getSessionId(),
    page_url: window.location.href
  }));

  try {
    await axios.post(`${API}/track/batch`, events);
  } catch (error) {
    console.error('Batch tracking error:', error);
  }
};

export default {
  trackCtaClick,
  trackAffiliateClick,
  trackImpression,
  trackScrollDepth,
  trackTimeOnPage,
  trackBatchImpressions,
  usePerformanceTracking
};
