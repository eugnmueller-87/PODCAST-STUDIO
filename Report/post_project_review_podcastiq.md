# Post-Project Review - PodcastIQ

**Lab: Stakeholders & Real-World Scope**
*Ironhack - Week 2, April 2026*
*Team: Eugen Müller · Markus von Aschoff · Gunter Maximilian Kleber*

---

## Part 1 - Project Snapshot

**Problem:**
- Creating a podcast episode from existing content (articles, reports, videos) takes hours of manual work
- Most teams skip audio entirely because the production effort is too high
- There is no simple, affordable tool that does this without a studio or technical skills

**Intended users:**
- Employees across different companies and industries
- Anyone who creates written or video content and wants to repurpose it as audio
- No technical background required. The tool is designed for everyday business users

**What we built:**
- A browser-based tool. No installation needed
- Users paste text, drop in a URL, upload a PDF, or link a YouTube video
- The tool produces a ready-to-download podcast episode in under 60 seconds
- Output includes: MP3 audio file, full transcript, episode title, summary and tags
- Built-in safety check: blocks harmful or discriminatory content before processing

---

## Part 2 - Stakeholder Impact

| # | Stakeholder | Role | What they need | Risk if ignored | Influence | Interest |
|---|---|---|---|---|---|---|
| 1 | **Creator / Customer** | Direct user - produces episodes with the tool | Fast, reliable output that works every time without needing IT support | Drops the tool after one bad experience; zero retention | High | High |
| 2 | **Listener / End User** | Consumes the generated audio | Accurate content that reflects what the source actually said | Creator's reputation is damaged if the episode distorts the original material | Low | High |
| 3 | **Product Owner** | Defines what gets built and prioritises features | A product that solves a real business problem and can be handed to a client | Without clear ownership, features get built that nobody asked for and real needs get missed | High | High |
| 4 | **Finance / Budget** | Approves and monitors API and hosting costs | Predictable costs per episode. No surprise invoices | A bug or open access could burn through the monthly budget in a day with no warning | High | Low |
| 5 | **Legal & Compliance** | Accountable for data handling and copyright exposure | No user content stored longer than needed; GDPR obligations met | Storing submitted documents indefinitely creates regulatory liability and potential fines | High | Medium |
| 6 | **InfoSec** | Responsible for access control and credential safety | Credentials not stored in code; tool protected by login; usage auditable | A leaked API key or open URL means anyone can use the tool and run up costs or extract data | High | Low |
| 7 | **Works Council** | Represents employee interests in the deploying organisation | Clarity on how the tool is used, what data it processes, and whether it affects job roles | If employees feel the tool is monitoring them or replacing their work without consultation, rollout fails | Medium | Medium |

---

## Part 3 - From Demo to "Real Project"

### Dimension 1 - Service Continuity & Incident Response

**Current state:**
- No uptime monitoring in place
- If the service breaks, nobody gets notified, users discover it themselves
- No process for who responds or how quickly

**What would change for production:**
- Set agreed service levels with the client upfront (e.g. 99% availability during business hours)
- Automated alert within 5 minutes if an episode generation fails
- Simple runbook: who handles what, and what users are told when something goes wrong

---

### Dimension 2 - Access Control & Credential Security

**Current state:**
- No login on the tool, anyone with the link can use it
- API credentials stored in a plain-text file alongside the code
- No way to track who used the tool or how much

**What would change for production:**
- Tool protected by user login before client handoff, at minimum a shared password for small teams
- All credentials moved to a secure store managed by the client's IT team, not in the codebase
- Usage logged per user so cost and activity can be tracked and capped

---

### Dimension 3 - Cost Visibility & Budget Governance

**Current state:**
- Every episode costs money (AI API charges) with no cap or alert
- No cost dashboard or monthly report
- One bad session or open access could exhaust a monthly budget instantly

**What would change for production:**
- Monthly budget ceiling agreed with Finance before go-live
- Hard limit per session (max document size, max episodes per user per day)
- Alert triggered when monthly spend hits 80% of the agreed limit
- Simple cost report for the client each month: cost per episode, broken down by input type

---

### Dimension 4 - Data Handling & Regulatory Compliance

**Current state:**
- Every generation writes the full source text and script to a log file. No expiry
- If a user submits a confidential document, that content sits on the server indefinitely
- No way for a user to request deletion of their data

**What would change for production:**
- Written data retention policy agreed with Legal before the first real user accesses the tool
- Logs store operational metadata only (episode length, provider used), not the actual content
- Deletion process in place: user can request their data is removed within a defined timeframe
- Mandatory for any deployment serving European users under GDPR

---

### Dimension 5 - Client Handoff & Ongoing Ownership

**Current state:**
- Documentation written for developers, not for the client's day-to-day team
- No operator guide, no user guide, no defined support process after handoff
- "Done" was assumed to mean the demo worked, nothing more

**What would change for production:**
- Handoff package as a formal deliverable, not an afterthought:
  - **User guide** - how to get good results, what the tool can and cannot do
  - **Operator guide** - how to manage credentials, read logs, handle common problems
- 30-day support window with agreed response times after go-live
- "Done" defined in writing at the start of the project, not assumed at the end

---

## Part 4 - Revision Brief

### Before

- Goal: build a tool that generates a podcast episode from any content source in under 60 seconds
- Success = demo runs without crashing, all four input types work, audio sounds convincing
- Scope was not formally defined — features were added as ideas came up during development
- Testing happened ad-hoc, close to the demo, not planned as part of the process
- Roles and responsibilities within the team were informal, whoever picked up a task, did it
- No agreed Git workflow — commits, branches, and merges were handled inconsistently
- Questions about cost, security, data handling, and client handoff were out of scope

---

### After

**Testing**
- Excessive testing before the demo is mandatory. That was not ideal.
- Every new feature added complexity to the pipeline and introduced new failure points
- With more features, the number of things that can break grows fast. Testing time must scale with it
- A simple test checklist per input type (text, URL, YouTube, PDF) should be run after every change, not only before the presentation

**Scope**
- Scope was not defined at the start. This caused features to be added without a clear boundary
- For a real project: agree the scope in writing before any work begins, including what is explicitly out of scope
- Changes to scope during the project require a decision, not just a conversation

**Collaboration, Roles & Responsibility**
- Team roles were unclear. No defined owner for product decisions, testing, or deployment
- For a real project: assign a Product Owner (prioritises features and accepts deliverables), a Tech Lead (owns architecture and code quality), and a QA owner (owns testing sign-off)
- Every task should have one owner — not a group assumption that someone will handle it

**Git — Standard Operating Procedures / Playbook**
- Commits were made directly to main without a consistent branching strategy
- For a real project: define and follow a simple Git playbook from day one:
  - `main` = stable, demo-ready code only
  - `develop` = active development branch
  - Feature branches for each new piece of work, merged via pull request, not direct push
  - Commit messages must describe what changed and why, not just "fix" or "update"
  - No API keys, passwords, or credentials ever committed to the repository
