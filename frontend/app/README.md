# UML Diagram Generator - React Frontend

A modern React frontend for AI-powered UML diagram generation and validation from natural language requirements.

## 🎯 Project Overview

This frontend supports a two-step workflow for generating UML class diagrams:
1. **Validate** - Analyze requirements for clarity, completeness, and modelability
2. **Generate** - Create PlantUML diagrams from validated requirements

## 📁 Project Structure

```
src/
├── api/                          # API layer (mock implementations)
│   ├── index.ts                  # Main API exports
│   ├── types.ts                  # API response types
│   └── mock.ts                   # Mock implementations
│
├── types/                        # Domain types
│   └── index.ts                  # Project, Run, etc.
│
├── store/                        # State management
│   └── useProjectStore.ts        # Zustand store for projects
│
├── hooks/                        # Custom React hooks
│   ├── useValidation.ts          # Validation API hook
│   └── useGeneration.ts          # Generation API hook
│
├── components/
│   ├── layout/
│   │   └── AppLayout.tsx         # Main 3-column layout
│   │
│   ├── projects/
│   │   ├── ProjectsSidebar.tsx   # Left sidebar
│   │   ├── ProjectCard.tsx       # Individual project card
│   │   └── NewProjectModal.tsx   # Create project dialog
│   │
│   ├── requirements/
│   │   ├── RequirementsEditor.tsx # Center column
│   │   ├── RunHistory.tsx        # Chat-like history
│   │   ├── RunHistoryItem.tsx    # Single run item
│   │   └── RequirementsInput.tsx # Input area with buttons
│   │
│   ├── results/
│   │   ├── ResultsPanel.tsx      # Right column
│   │   ├── ScoreCard.tsx         # Metrics display
│   │   ├── FeedbackCard.tsx      # AI feedback
│   │   └── DiagramSection.tsx    # Diagram preview + tabs
│   │
│   ├── diagram/
│   │   ├── DiagramPreview.tsx    # Thumbnail preview
│   │   ├── DiagramFullscreenModal.tsx  # Full view with zoom/pan
│   │   └── CodeViewer.tsx        # PlantUML code display
│   │
│   └── ui/                       # Reusable UI components
│       ├── Button.tsx
│       ├── Badge.tsx
│       ├── Modal.tsx
│       ├── Tabs.tsx
│       └── ProgressBar.tsx
│
├── pages/
│   └── UmlGeneratorPage.tsx      # Main application page
│
├── utils/
│   ├── plantuml.ts               # PlantUML encoding utilities
│   └── download.ts               # File download helpers
│
├── App.tsx
├── main.tsx
└── index.css                     # Tailwind imports + custom styles
```

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## 🎨 Design Philosophy

- **3-column dashboard layout** for efficient workspace organization
- **Chat-like history** to track multiple validation/generation runs
- **Progressive disclosure** - scores summary → detailed feedback → full diagram
- **Zoom/pan support** for large, complex UML diagrams

## 🔌 API Integration

The `src/api/` layer is designed for easy backend integration:

```typescript
// Currently uses mock implementations
// To connect real backend, update src/api/index.ts:

import { validateRequirements, generateFromRequirements } from './real-api';
// instead of
import { validateRequirements, generateFromRequirements } from './mock';
```

## ⌨️ Keyboard Shortcuts

- `Ctrl/Cmd + Enter` - Generate diagram
- `Ctrl/Cmd + Shift + Enter` - Validate only
- `Escape` - Close modals

## 📝 License

MIT - For thesis project demonstration purposes.
