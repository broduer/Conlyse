import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'intro',
    'deployment',
    'server-observer',
    'server-converter',
    'desktop',
    {
      type: 'category',
      label: 'ConflictInterface',
      items: [
        'conflict-interface/getting-started',
        'conflict-interface/live-games',
        'conflict-interface/replay-analysis',
        {
          type: 'category',
          label: 'Developer Guide',
          items: [
            'conflict-interface/data-types',
            'conflict-interface/replay-system',
          ],
        },
      ],
    },
  ],
};

export default sidebars;
