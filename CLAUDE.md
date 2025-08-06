* # \# Project Notes and Requirements
* # ==============================
* # 
* # \## Project Overview
* # ----------------
* # 
* # \*   \*\*Project\*\*: Social Media Content Visual Pipeline for BYMB Consultancy
* # &nbsp;   
* # \*   \*\*Foundation\*\*: Existing MVP Template (https://github.com/bader1919/MVP)
* # &nbsp;   
* # \*   \*\*Owner\*\*: Bader Abdulrahim, BYMB Consultancy founder
* # &nbsp;   
* # \*   \*\*Location\*\*: Manama, Kingdom of Bahrain
* # &nbsp;   
* # \*   \*\*Experience\*\*: 23+ years expertise, $35M+ client results
* # &nbsp;   
* # 
* # \## Core Problem
* # ------------
* # 
* # \*   Empty social media feeds due to visual content bottleneck
* # &nbsp;   
* # \*   Website launch delayed waiting for images
* # &nbsp;   
* # \*   Need: Input business insight → output branded visuals quickly
* # &nbsp;   
* # 
* # \## Business Requirements
* # ---------------------
* # 
* # \*   Generate consistent social media content
* # &nbsp;   
* # \*   Reduce content creation time significantly
* # &nbsp;   
* # \*   Launch website with branded visuals
* # &nbsp;   
* # \*   Maintain brand consistency across all content
* # &nbsp;   
* # 
* # \## Technical Stack (Using Existing Template)
* # -----------------------------------------
* # 
* # \*   Frontend: Next.js 14 + TypeScript + Chakra UI + Zustand (existing)
* # &nbsp;   
* # \*   Backend: FastAPI + Python 3.11 (existing)
* # &nbsp;   
* # \*   Containers: Docker + Docker Compose (existing)
* # &nbsp;   
* # \*   AI Integration: Freepik API (new addition)
* # &nbsp;   
* # 
* # \## Implementation Approach
* # -----------------------
* # 
* # \*   Extend existing MVP template rather than build from scratch
* # &nbsp;   
* # \*   Add Freepik API integration to existing FastAPI backend
* # &nbsp;   
* # \*   Use existing Chakra UI components for frontend interface
* # &nbsp;   
* # \*   Leverage existing Zustand state management patterns
* # &nbsp;   
* # \*   Maintain existing Docker deployment setup
* # &nbsp;   
* # 
* # \## File Structure Changes
* # ----------------------
* # 
* # \*   Extend existing backend/api/routes.py with content generation endpoints
* # &nbsp;   
* # \*   Add new services for Freepik integration
* # &nbsp;   
* # \*   Create new frontend pages using existing patterns
* # &nbsp;   
* # \*   Add new Zustand store following existing structure
* # &nbsp;   
* # 
* # \## User Workflow Goal
* # ------------------
* # 
* # \*   Input business insight
* # &nbsp;   
* # \*   System generates branded visuals automatically
* # &nbsp;   
* # \*   Download ready-to-post content
* # &nbsp;   
* # \*   Significantly faster than current manual process
* # &nbsp;   
* # 
* # \## Key Integration
* # ---------------
* # 
* # \*   Freepik API for image generation
* # &nbsp;   
* # \*   Existing MVP template as foundation
* # &nbsp;   
* # \*   Brand consistency automation
* # &nbsp;   
* # \*   Multi-platform content optimizationtions, and any important guidelines
