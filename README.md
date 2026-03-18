# ComplianceBot Flow

An AI-powered multi-agent compliance flow built on the GitLab Duo Agent Platform that monitors merge requests, maps findings to compliance controls, and generates audit-ready evidence packages.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              GitLab Duo Agent Platform               │
│                                                     │
│  ┌──────────────┐    ┌──────────────────────────┐   │
│  │   Triggers   │───▶│     ComplianceBot Flow   │   │
│  │              │    │                          │   │
│  │ • MR Created │    │  ┌────────────────────┐  │   │
│  │ • Pipeline   │    │  │ 1. Scanner Agent   │  │   │
│  │   Completed  │    │  │   (MR Analysis)    │  │   │
│  │ • Schedule   │    │  └────────┬───────────┘  │   │
│  │   (Nightly)  │    │           │              │   │
│  │ • Manual     │    │  ┌────────▼───────────┐  │   │
│  │   Trigger    │    │  │ 2. Mapper Agent    │  │   │
│  └──────────────┘    │  │ (Control Mapping)  │  │   │
│                      │  └────────┬───────────┘  │   │
│                      │           │              │   │
│                      │  ┌────────▼───────────┐  │   │
│                      │  │ 3. Evidence Agent  │  │   │
│                      │  │ (Evidence Collect) │  │   │
│                      │  └────────┬───────────┘  │   │
│                      │           │              │   │
│                      │  ┌────────▼───────────┐  │   │
│                      │  │ 4. Reporter Agent  │  │   │
│                      │  │  (Report Generate) │  │   │
│                      │  └────────────────────┘  │   │
│                      └──────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Setup

1. Enable GitLab Duo Agent Platform
2. Push configurations to your project repository.
