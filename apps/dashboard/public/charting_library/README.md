# Official TradingView Charting Library Installation Directory

Place official licensed TradingView Charting Library vendor assets in this directory when acquired:

```
apps/dashboard/public/charting_library/
├── charting_library.min.js
├── charting_library.d.ts
├── charting_library.standalone.js
├── bundles/
│   ├── en.js
│   ├── vendors.js
│   └── ...
└── static/
    ├── css/
    └── ...
```

## Drop-In Capability
The Project GOAT Charting Engine (`apps/dashboard/src/charting/`) detects the presence of `charting_library.min.js` at runtime via `TradingViewLoader.ts` and automatically attaches `new TradingView.widget({...})` with GOAT's REST API DataFeed adapter (`TradingViewDataFeed.ts`).
