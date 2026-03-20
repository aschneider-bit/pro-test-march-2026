# OFW Pro Product — Prototype Spec

## Overview

A streamlined pro (attorney/mediator) experience with three core flows: simplified signup, custody schedule creation, and AI-assisted parenting plan generation.

**Workflow:** Sign up → Create custody schedule → Create parenting plan → Send to client → Generate document

---

## 1. Pro Signup (Simplified)

### Goal
Reduce friction to get a pro account created fast. Defer non-essential fields to post-signup onboarding.

### Signup Form Fields (MVP)
- First name
- Last name
- Email
- Password (user-chosen)
- Username (user-chosen)
- Address (Google Maps autocomplete)
- Account type (attorney / mediator / other)

### Removed from Signup
These fields are **cut entirely** — not needed:
- Title
- Credentials
- Timezone

### Deferred to Onboarding (post-signup)
Collected after account creation, not blocking signup:
- Country code + phone number
- Work phone extension
- Security question + answer
- 4-digit security code + confirmation
- "How did you hear about OFW"

### Acceptance Criteria
- [ ] User can complete signup with only the MVP fields
- [ ] Address field uses Google Maps Places autocomplete
- [ ] User sets their own username and password
- [ ] After signup, user lands in onboarding flow for deferred fields
- [ ] Onboarding fields are skippable (not required to proceed)

---

## 2. Custody Navigator

### Goal
Provide a visual custody schedule builder as a dedicated tab in the pro navigation.

### Requirements
- New **"Custody Navigator"** tab in the main pro navigation
- Styling follows the pro product design guidelines (see: `/Users/aschneider/Downloads/cozi-design-guidelines.pdf`)
- Schedule data is reusable — it integrates into the Parenting Plan (Section 3)

### Reference
- Existing product: https://www.custodynavigator.com/

### Acceptance Criteria
- [ ] "Custody Navigator" tab appears in pro nav
- [ ] Pro can create/edit a custody schedule
- [ ] Schedule data is accessible from the Parenting Plan flow
- [ ] Visual styling matches pro design guidelines

---

## 3. Parenting Plan

### Goal
AI-assisted parenting plan creation: upload an existing plan (image/PDF), auto-generate a structured form, then let the client fill in their sections and generate a final document.

### Flow

**Step 1: Pro creates plan**
- New **"Parenting Plan"** tab in pro navigation
- Pro uploads an image/PDF of their existing parenting plan form
- System parses the upload and generates a structured form

**Step 2: Pro fills in their sections**
The form includes these sections (all optional — only relevant ones need completion):

| Section | Notes |
|---------|-------|
| Child/ren | Names, DOBs |
| Schedules | Pulls from Custody Navigator |
| Physical custody | |
| Legal custody | |
| Moving | |
| Exchanges | |
| Exchanges by flight | |
| Supervised visitation | |
| Changes to parenting time | |
| Access to child's information | |
| Health | |
| School | |
| Extracurricular activities | |
| Transportation | |
| Out-of-area travel | |
| Third-party contact | |
| Child care | |
| Child rearing | |
| Alcohol, tobacco and drugs | |
| Communication between parents | |
| Communication with child | |
| Expenses and money | |
| Taxes | |
| Child support | |
| Military | |
| Counseling | |
| Death | |
| Future revisions | |
| Signatures | |
| Miscellaneous | |

**Step 3: Send to client**
- Pro clicks "Send to Client" → generates a unique link
- Client opens the link and fills out their sections

**Step 4: Generate document**
- Pro clicks "Generate Document" to produce the final parenting plan
- Export integrates with document storage: Dropbox, Microsoft SharePoint, etc.

### Reference
- Existing intake flow: https://app.custodyxchange.com/a/parenting-plan/provisions

### Acceptance Criteria
- [ ] "Parenting Plan" tab appears in pro nav
- [ ] Pro can upload an image/PDF of an existing parenting plan
- [ ] System generates a structured form from the upload
- [ ] Form contains all sections listed above
- [ ] Schedules section pulls data from Custody Navigator
- [ ] Pro can generate a shareable link for the client
- [ ] Client can fill out their sections via the link
- [ ] Pro can generate a final document
- [ ] Document can be exported to Dropbox / SharePoint

---

## 4. Prototype Decisions

### What this prototype proves
- Simplified signup converts faster
- Custody Navigator + Parenting Plan work as an integrated flow
- AI-assisted form generation from uploaded plans is viable
- Client collaboration via shared link works

### What this prototype does NOT include
- Payment / billing
- Full onboarding analytics
- Native mobile app
- Real Dropbox/SharePoint integration (mock the export for prototype)
- Real Google Maps API (can mock autocomplete for prototype)

### Technical Notes for Prototype
- Use mock data for custody schedules if needed
- Parenting plan upload → form generation can be mocked or use basic OCR
- Client link can be a simple unique URL with a form view
- Document generation can produce a styled HTML/PDF output

---

## 5. Screen Inventory

| Screen | Route | Description |
|--------|-------|-------------|
| Signup | `/join/pro` | Simplified registration form |
| Onboarding | `/onboarding` | Deferred fields collection |
| Dashboard | `/dashboard` | Pro home with nav tabs |
| Custody Navigator | `/custody-navigator` | Schedule builder |
| Parenting Plan — Create | `/parenting-plan/new` | Upload + form generation |
| Parenting Plan — Edit | `/parenting-plan/:id` | Section-by-section editor |
| Parenting Plan — Client View | `/parenting-plan/:id/client` | Shared link for client |
| Parenting Plan — Generate | `/parenting-plan/:id/generate` | Document preview + export |
