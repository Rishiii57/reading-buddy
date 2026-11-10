# TASK 2: BUILD AN AUTONOMOUS AI PRODUCT ORGANISATION FOR READING BUDDY

## ROLE

Act as a Principal AI Systems Architect, Senior Product Manager, Multi-Agent Systems Engineer, AI/ML Engineer and Software Engineering Lead.

We are building Reading Buddy, an AI-powered reading tutor exclusively designed for children from Nursery to Class 4.

We want to create an AI-powered product organisation consisting of 50 simulated child users, an AI Product Manager, a specialised AI Engineering Team and an independent AI QA Team.

The objective is to create a continuous product improvement system.

Our AI agents should experience the product from different children's perspectives, discover usability and learning problems, communicate their findings to the Product Manager, and generate actionable technical requirements.

The Engineering Team should implement those requirements, and the QA Team should independently validate the improvements.

This entire process should be repeatable.

Do not simply create agents that generate feedback from prompts. Build a system that interacts with the actual Reading Buddy application and produces evidence-based findings.

---

# PART 1: UNDERSTAND THE EXISTING PROJECT

Before implementing anything:

1. Explore the complete Reading Buddy codebase.
2. Understand the frontend and backend architecture.
3. Understand the STT and TTS integrations.
4. Understand the poem library and recitation functionality.
5. Study the tutor state machine and text alignment logic.
6. Understand the existing testing infrastructure.
7. Identify how users navigate and interact with the application.
8. Identify existing technical limitations.

Create an initial architecture report.

Do not unnecessarily rewrite existing functionality.

The new multi-agent system should integrate with the existing application without breaking its current functionality.

---

# PART 2: BUILD 50 DISTINCT AI CHILD USER AGENTS

This is the foundation of our system.

We want 50 independent AI agents that simulate children using Reading Buddy.

IMPORTANT: Our actual target audience consists exclusively of children from Nursery to Class 4.

All 50 agents must represent children within this age and learning range.

Do not include parents, teachers, developers or adults as user personas.

## A. Persona distribution

Create 50 distinct personas with the following initial distribution:

| Learning stage | Number of agents |
|---|---:|
| Nursery | 10 |
| LKG | 8 |
| UKG | 8 |
| Class 1 | 6 |
| Class 2 | 6 |
| Class 3 | 6 |
| Class 4 | 6 |
| Total | 50 |

You may modify the distribution if your research suggests a better representation.

## B. Individual persona characteristics

Every agent must have an individual profile containing:

1. Unique agent ID.
2. Grade and approximate age.
3. Reading proficiency.
4. Language preference.
5. Vocabulary level.
6. Pronunciation ability.
7. Attention span.
8. Confidence while reading.
9. Patience level.
10. Learning preferences.
11. Common reading mistakes.
12. Technology familiarity.
13. Expected interaction style.
14. Specific testing objectives.

Include different learning abilities and behavioural patterns.

Examples:

- A Nursery child who needs audio guidance for almost everything.
- An LKG child who confuses similar-sounding letters.
- A UKG child who can read individual words but struggles with sentences.
- A Class 1 child who frequently skips small words.
- A Class 2 child who reads quickly but mispronounces words.
- A Class 3 child who struggles with reading expression.
- A Class 4 child who reads fluently but needs help with rhythm and intonation.

Do not create 50 agents that differ only in their names.

Their reading abilities, expectations and behaviour must be meaningfully different.

## C. Language distribution

The agents should collectively test:

- English.
- Hindi.
- Gujarati.

Ensure all three languages are adequately represented across different grade levels.

Include children who are more comfortable in one language and struggle with another.

Do not assume that all children have equal proficiency in all three languages.

## D. Realistic behaviour simulation

The agents should behave naturally rather than behaving like professional software testers.

Examples:

- A child may not understand what to do after opening the application.
- A child may repeatedly click the wrong button.
- A child may lose interest in a long poem.
- A child may struggle to understand Buddy's instructions.
- A child may get frustrated if Buddy interrupts too frequently.
- A child may repeat a line because they did not understand it.
- A child may skip words unintentionally.
- A child may enjoy listening but dislike reading aloud.
- A child may want to replay the poem.
- A child may stop midway through a session.

Allow agents to fail, abandon tasks or misunderstand the application.

These failures are valuable product insights.

## E. Independent user journeys

Every agent should receive an appropriate objective.

Examples:

- Discover how to start reading.
- Select and listen to a poem.
- Read an entire poem.
- Make intentional reading mistakes.
- Understand corrections.
- Recover after making mistakes.
- Restart a session.
- Explore different poems.
- Use the application independently.

Not every agent needs to test every feature.

Create diverse journeys to avoid repetitive feedback.

---

# PART 3: REAL PRODUCT INTERACTION

Agents must interact with the actual running Reading Buddy application.

They should not simply read the repository documentation and generate opinions.

Investigate and implement the best approach using:

- Playwright.
- Browser automation.
- Computer-use frameworks.
- Appropriate multi-agent browser interaction tools.

The agents should be able to:

1. Open the application.
2. Navigate the interface.
3. Discover features.
4. Click buttons.
5. Select poems.
6. Listen to audio.
7. Interact with the reading interface.
8. Attempt reading tasks.
9. Make mistakes.
10. Pause and resume.
11. Observe feedback.
12. Complete or abandon sessions.

If browser-based interaction is insufficient for a feature, identify an alternative testing mechanism.

### Important: Blind user testing

Initially, agents should not have access to:

- Source code.
- Internal developer documentation.
- Expected test results.
- Known bugs.
- Product Manager findings.

They should receive only the basic introduction that a real child would receive.

This prevents developer knowledge from influencing their feedback.

Each agent should have its own isolated session and persona context.

Agents must not see each other's feedback before submitting their initial reports.

---

# PART 4: AI PRODUCT MANAGER

Create one central AI Product Manager.

This is the most important component of the system.

The Product Manager must act as an experienced Product Manager specialising in children's educational products, AI applications, user experience and learning systems.

Its primary responsibility is to represent the perspective of the child using Reading Buddy.

It should not think like a developer trying to defend existing implementation decisions.

## A. Feedback aggregation

Collect reports from all 50 agents.

Analyse:

- Individual user journeys.
- Repeated complaints.
- Confusing interactions.
- Difficult features.
- Learning difficulties.
- Engagement problems.
- Incorrect feedback.
- Pronunciation problems.
- Unnecessary interruptions.
- Session abandonment.

## B. Root-cause identification

Do not simply count complaints.

For example, if 20 agents report pronunciation problems, investigate whether they are experiencing the same underlying issue.

Group similar problems together.

Also preserve important issues affecting only a small group.

A problem affecting Nursery children may be extremely important even if only a few agents encounter it.

## C. Product prioritisation

Prioritise issues using:

- Severity.
- Frequency.
- Number of affected personas.
- Grade-level impact.
- Language-specific impact.
- Learning outcome impact.
- User experience impact.
- Implementation complexity.
- Expected improvement.

Assign:

- P0: Critical.
- P1: High priority.
- P2: Medium priority.
- P3: Low priority.

## D. Convert user feedback into technical requirements

The Product Manager must communicate in precise technical language.

For example:

USER FEEDBACK:

"Buddy keeps interrupting me when I pause to think."

PRODUCT MANAGER REQUIREMENT:

"Review the tutor's silence-detection and interruption logic. Introduce configurable hesitation thresholds based on reading proficiency and contextual speech activity. Prevent unnecessary intervention during short pauses. Validate using slow-reading and hesitant-reading test cases."

Every requirement must include:

1. Problem statement.
2. Affected personas.
3. Supporting evidence.
4. Root-cause hypothesis.
5. Expected behaviour.
6. Technical implementation requirements.
7. Acceptance criteria.
8. Validation methodology.
9. Priority.

## E. Product Manager outputs

Generate:

- USER_RESEARCH_REPORT.md
- PRODUCT_REQUIREMENTS.md
- PRODUCT_BACKLOG.md
- USER_JOURNEY_ANALYSIS.md
- PRIORITISATION_REPORT.md

The Product Manager should also maintain a history of decisions and unresolved problems.

---

# PART 5: AI ENGINEERING TEAM

Create a specialised Engineering Team.

The Engineering Team receives approved requirements from the Product Manager.

It must not independently invent product features or change product direction.

Create specialised roles:

### 1. AI/ML Engineer
Responsible for:
- Model accuracy.
- Model adaptation.
- Fine-tuning feasibility.
- Inference optimisation.
- Evaluation.

### 2. Speech AI Engineer
Responsible for:
- STT.
- TTS.
- Pronunciation.
- Audio processing.
- Speech recognition failures.

### 3. NLP Engineer
Responsible for:
- Language processing.
- Text normalisation.
- Hindi and Gujarati language handling.
- Word-level comparison.
- Context understanding.

### 4. Backend Engineer
Responsible for:
- API integrations.
- Tutor state management.
- Backend logic.
- Session handling.
- Performance.

### 5. Frontend Engineer
Responsible for:
- User interface.
- Interaction logic.
- Accessibility.
- Reading experience.
- Audio controls.

### 6. Data Engineer
Responsible for:
- Poem datasets.
- Audio assets.
- Evaluation datasets.
- Data management.
- Caching.

### 7. Integration Engineer
Responsible for:
- Component integration.
- API compatibility.
- System stability.
- Deployment readiness.

## Engineering workflow

For every requirement:

1. Read the approved requirement.
2. Inspect the relevant code.
3. Identify the technical root cause.
4. Propose a solution.
5. Implement the solution.
6. Run unit tests.
7. Run integration tests.
8. Document the implementation.
9. Submit the change for QA.

Maintain clear ownership of files and modules.

Avoid conflicting changes when multiple agents work in parallel.

Use version control and isolated branches or worktrees where appropriate.

---

# PART 6: INDEPENDENT AI QA TEAM

Create an independent QA Team.

The QA Team should not blindly trust the Engineering Team's claims.

It must validate every important change.

Responsibilities:

- Functional testing.
- Regression testing.
- User journey testing.
- Edge-case testing.
- Speech testing.
- Language testing.
- Audio testing.
- Performance testing.

For every completed requirement:

1. Reproduce the original issue.
2. Test the new implementation.
3. Check the acceptance criteria.
4. Run relevant regression tests.
5. Compare before-and-after behaviour.
6. Submit a validation report.

If the issue remains unresolved, return it to Engineering with evidence.

Do not allow the Product Manager to mark an issue as resolved merely because code has been changed.

Resolution requires validation.

---

# PART 7: RESEARCH AND INTEGRATE OPEN-SOURCE AGENT FRAMEWORKS

Before building the complete architecture, research the following projects:

1. Humanish:
https://github.com/danielgwilson/humanish

2. AutoUser:
https://github.com/renjie-liu/autouser

3. Persona UX Test:
https://github.com/Ericwong5021/persona-ux-test

4. Test Pilot Loop:
https://github.com/suhuandds/test-pilot-loop

5. Braintrust Simulator:
https://github.com/Innex/braintrust-simulator

6. Human Experience:
https://github.com/andrew-shwetzer/human-experience

Investigate each repository for:

- Agent architecture.
- Persona management.
- Browser automation.
- Multi-agent orchestration.
- Feedback collection.
- Reporting.
- Testing capabilities.
- Integration complexity.
- Licence.
- Maintenance status.

Do not blindly install every repository.

Verify that the repositories exist and that their current code and documentation match their stated capabilities.

Choose the most useful frameworks and integrate them into one coherent architecture.

Avoid unnecessary dependencies.

If a framework is unsuitable, explain why and implement an alternative.

Create:

OPEN_SOURCE_RESEARCH.md

This document must explain what was selected, what was rejected and why.

---

# PART 8: READING BUDDY-SPECIFIC TESTING

All testing must focus on children from Nursery to Class 4.

## A. Reading experience

Test:

- First-line behaviour.
- Subsequent-line behaviour.
- Word highlighting.
- Line transitions.
- Stanza transitions.
- Skipped words.
- Repeated words.
- Incorrect pronunciation.
- Self-correction.
- Hesitation.
- Long pauses.
- Reading speed.
- Reading confidence.

## B. Tutor behaviour

Test:

- Quality of corrections.
- Appropriateness of hints.
- Timing of interruptions.
- Encouragement.
- Repeated instructions.
- Context retention.
- Unnecessary corrections.
- Behaviour consistency.
- Age-appropriate language.

## C. Poetry experience

Test:

- Poem selection.
- Poem suitability for grade level.
- Recitation quality.
- Pronunciation.
- Rhythm.
- Intonation.
- Audio synchronisation.
- Listen-first experience.
- Replay functionality.
- Complete poem playback.

## D. Language experience

Test English, Hindi and Gujarati separately.

Pay attention to:

- Language-specific pronunciation.
- Similar-sounding words.
- Matras.
- Nasalisation.
- Vowel length.
- Word segmentation.
- Transliteration.
- Regional pronunciation variations.

## E. Technical experience

Test:

- Microphone permissions.
- STT failures.
- TTS failures.
- Network interruptions.
- Latency.
- Audio playback failures.
- Session reconnection.
- Pause and resume.
- Duplicate events.
- Unexpected application states.

---

# PART 9: SEPARATE SPEECH AND AUDIO EVALUATION

Browser agents cannot fully evaluate speech recognition simply by clicking buttons.

Build a separate audio evaluation system.

Use:

- Appropriately licensed speech datasets.
- Generated speech.
- Consenting adult recordings.
- Synthetic test cases.

Do not collect real children's voices without appropriate parental consent and safeguards.

Test:

- Different accents.
- Different speaking speeds.
- Hesitation.
- Whispering.
- Background noise.
- Similar-sounding words.
- Incorrect words.
- Repeated words.
- Skipped words.

Where possible, send audio through the same processing pipeline used by the actual application.

Measure:

- Word Error Rate.
- False correction rate.
- Missed error rate.
- Alignment accuracy.
- Response latency.
- Language-wise performance.

Do not confuse simulated user satisfaction with measured speech-recognition accuracy.

The Product Manager must receive both reports and analyse them together.

---

# PART 10: CONTINUOUS PRODUCT IMPROVEMENT LOOP

Implement the complete workflow:

50 CHILD USER AGENTS
        ↓
ACTUAL PRODUCT INTERACTIONS
        ↓
INDIVIDUAL USER EXPERIENCE REPORTS
        ↓
CENTRALISED FEEDBACK COLLECTION
        ↓
AI PRODUCT MANAGER
        ↓
ROOT-CAUSE ANALYSIS
        ↓
PRODUCT REQUIREMENTS
        ↓
AI ENGINEERING TEAM
        ↓
IMPLEMENTATION
        ↓
INDEPENDENT QA TEAM
        ↓
REPEAT USER TESTING
        ↓
PRODUCT IMPROVEMENT

The system must maintain historical testing cycles.

For every cycle, identify:

- Newly discovered issues.
- Previously unresolved issues.
- Successfully fixed issues.
- Regressions.
- Improvements in usability.
- Improvements in learning experience.
- Language-specific differences.
- Grade-specific differences.

The system must learn from previous testing cycles without allowing agents to simply repeat old feedback.

Re-test previously problematic scenarios after fixes.

---

# PART 11: RESOURCE MANAGEMENT AND ORCHESTRATION

We want 50 agents, but we do not want uncontrolled resource consumption.

Implement:

- Configurable agent count.
- Configurable parallel execution.
- Batch execution.
- Independent agent sessions.
- Execution status tracking.
- Failure recovery.
- Retry mechanisms.
- Token usage monitoring.
- API usage monitoring.
- Cost estimation.
- Report storage.
- Run-level summaries.

Start with five agents.

Once the system works correctly, expand to 10 and then all 50.

Do not run 50 expensive model instances simultaneously by default.

Use shared infrastructure where appropriate, but preserve independent persona contexts.

Make the system modular so that we can add more personas later.

---

# PART 12: SAFETY AND AUTONOMY RULES

The Product Manager must not directly modify source code.

The Engineering Team must work from approved requirements.

The QA Team must independently validate changes.

Do not allow agents to:

- Delete major functionality without approval.
- Modify credentials.
- Expose API keys.
- Deploy to production without approval.
- Make irreversible changes.
- Collect personal information from real children.
- Store children's real voices without appropriate safeguards.

All significant code changes must be version-controlled.

Require human approval for major architecture changes and production releases.

The simulated children are testing personas, not actual child participants.

---

# PART 13: REPORTING AND DASHBOARD

Build a central reporting system.

At the end of each testing cycle, provide:

### User research
- Number of agents executed.
- Number of successful sessions.
- Number of abandoned sessions.
- Problems discovered.
- Grade-wise findings.
- Language-wise findings.

### Product management
- Top recurring problems.
- Highest-priority issues.
- Approved requirements.
- Deferred requirements.
- Expected impact.

### Engineering
- Tasks completed.
- Files modified.
- Technical solutions.
- Model or configuration changes.

### QA
- Tests passed.
- Tests failed.
- Regression results.
- Remaining limitations.

Create a simple dashboard or structured reporting interface to monitor the complete process.

Do not spend unnecessary time building a sophisticated dashboard before the underlying workflow works.

---

# PART 14: REQUIRED DELIVERABLES

At the end, provide:

1. Working multi-agent architecture.
2. 50 distinct child personas.
3. Independent user simulation framework.
4. Actual browser interaction capability.
5. AI Product Manager.
6. AI Engineering Team.
7. Independent AI QA Team.
8. Speech and audio evaluation framework.
9. Central feedback collection system.
10. Product prioritisation engine.
11. Continuous improvement workflow.
12. Historical testing reports.
13. Execution dashboard or equivalent reporting system.
14. Complete setup instructions.

Create these documentation files:

- AGENT_ARCHITECTURE.md
- PERSONA_LIBRARY.md
- PRODUCT_MANAGER_GUIDELINES.md
- ENGINEERING_WORKFLOW.md
- QA_WORKFLOW.md
- OPEN_SOURCE_RESEARCH.md
- USER_RESEARCH_REPORT.md
- PRODUCT_REQUIREMENTS.md
- PRODUCT_BACKLOG.md
- AGENT_EVALUATION_REPORT.md
- PRODUCT_IMPROVEMENT_HISTORY.md
- RUN_INSTRUCTIONS.md

---

# PART 15: IMPLEMENTATION PHASES

Work in this exact sequence.

### Phase 1: Project audit and research

Understand Reading Buddy and research open-source frameworks.

### Phase 2: Architecture design

Design the multi-agent organisation and define responsibilities.

### Phase 3: Pilot user agents

Build five distinct child personas and verify actual application interactions.

### Phase 4: Product Manager

Build the central feedback aggregation, prioritisation and requirement generation system.

### Phase 5: Engineering and QA

Build specialised engineering and independent QA workflows.

### Phase 6: Expand to 50 agents

Implement the complete persona library and scalable execution system.

### Phase 7: Audio evaluation

Build independent speech and audio testing.

### Phase 8: Complete product cycle

Run a complete cycle from user testing through implementation and validation.

### Phase 9: Final evaluation

Compare the initial and improved product using measurable results.

Do not skip phases.

Do not claim a feature works unless it has actually been implemented and tested.

If something is blocked by an API limitation, explain it and implement the best practical alternative.

---

# FINAL OBJECTIVE

We want Reading Buddy to have its own AI-powered product organisation.

Imagine 50 children with different learning abilities independently using our application.

Each experiences the product differently.

Some enjoy it. Some struggle. Some get confused. Some encounter pronunciation issues. Some find the interface difficult.

The Product Manager understands their experiences and identifies what genuinely needs to improve.

It translates those findings into precise technical instructions.

The Engineering Team implements them.

The QA Team verifies the changes.

The 50 agents then test the improved product again.

This process continues through multiple cycles.

The final outcome should be a significantly more accurate, intuitive, engaging and reliable reading tutor for children from Nursery to Class 4.

Build a real working system, not a conceptual multi-agent demonstration.

Prioritise realistic child-user behaviour, evidence-based product decisions, measurable improvements and reliable engineering.