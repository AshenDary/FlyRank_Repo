# Ship an Automation Workflow v2
**Student:** Jared Noel  
**Date:** August 27, 2026  
**Tool Used:** Claude Project (No-Code Workflow)  
**Pipeline:** Source-Grounded Study Notes

---

## 1. Step Diagram (The Workflow Flow)

+------------------+     +------------------+     +------------------+     +------------------+     +------------------+
|  STEP 1: GATHER  |---->| STEP 2: SYNTHESIZE|---->|  STEP 3: DRAFT   |---->|  STEP 4: REVIEW  |---->|  STEP 5: FORMAT  |
|  (Upload Sources)|     | (Extract Concepts|     | (Write Structured|     | (Critique & Find |     | (Add Summary,    |
|                  |     |  & Quotes)       |     |  Notes)          |     |   Gaps)          |     |  Quiz, Flashcards)|
+------------------+     +------------------+     +------------------+     +------------------+     +------------------+
        |                         |                         |                         |                         |
        v                         v                         v                         v                         v
+------------------+     +------------------+     +------------------+     +------------------+     +------------------+
|   Raw PDFs /     |     |   Concept Grid   |     |   Structured     |     |   Weakness       |     |   Final Study    |
|   Articles       |     |   (Evidence)     |     |   Document       |     |   Report         |     |   Pack           |
+------------------+     +------------------+     +------------------+     +------------------+     +------------------+


**Handoff Definition:** Each step's output becomes the input for the next step. The Concept Grid feeds the Draft; the Draft feeds the Review; the Review's fixes feed the Final Format.

---

## 2. System Configuration & All Prompts Used

### Project Setup
- **Platform:** Claude Projects (claude.ai)
- **Project Name:** `FL-04 Study Notes Workflow`
- **Knowledge Base:** Uploaded source files (PDFs/text) into Project Knowledge for grounding.

### Project Instructions (System Prompt)
*Pasted into the "Project Instructions" field:*

> "You are an expert academic researcher and study coach. You always ground your answers strictly in the Project Knowledge files. If information is not in the uploaded sources, you say 'Not found in sources.' You maintain a neutral, critical tone. You format outputs using markdown for readability."

### The 5-Step Prompts (Executed sequentially in the same chat thread)

| Step | Prompt (Copy-pasted exactly) |
| :--- | :--- |
| **1. GATHER** | *"I have uploaded [X] sources for this week's study topic: [Insert Topic Name]. Please confirm you have received all files and list the main titles/authors of each. Do not summarize content yet, just list them."* |
| **2. SYNTHESIZE** | *"Now, synthesize all the uploaded sources. Extract the absolute core concepts, key supporting evidence, and any direct contradictions between the authors. Organize your output into a 'Concept Grid' with these columns: **Concept** | **Source Mentioned** | **Supporting Quote** | **Page/Paraphrase**."* |
| **3. DRAFT** | *"Using the Concept Grid you just created, draft comprehensive study notes. Structure them as: 1. Core Thesis. 2. Key Arguments (3 major points). 3. Counterarguments & Limitations. 4. Glossary (Define 5 key terms)."* |
| **4. REVIEW** | *"Critique the draft you just wrote. Act as a strict professor. Identify the weakest argument, the biggest factual gap, and one logical inconsistency (if any). Provide specific recommendations on what must be fixed for accuracy."* |
| **5. FORMAT** | *"Now, produce the final version of the study notes. Apply the fixes from your critique. Then append: A 1-Page Executive Summary, 5 Multiple-Choice Quiz Questions with answers, and 10 Anki-style Flashcards (Q&A format)."* |

---

## 3. The Five Runs – Documented with Outputs

I ran the full 5-step pipeline on five distinct topics. Below is the summary table, followed by the full output highlights for Run 1 (Software Engineering) and snapshots for Runs 2–5.

| Run | Topic | Input Sources | Date | Output Highlights (First 3 lines of Executive Summary) |
| :--- | :--- | :--- | :--- | :--- |
| **1** | Software Engineering (Modules 1–4) | 4 course lecture PDFs (CCSFEN1L) | Aug 26 | *"The core thesis is the management of complexity through structured processes, balanced against the unpredictability of human creativity. The course presents an unresolved trade-off: plan-driven methods prioritize documentation, while agile methods prioritize adaptability. The material does not declare a winner, framing the choice as context-dependent."* |
| **2** | Climate Change Policy 2026 | 5 UN/IPCC policy briefs | Aug 26 | *"The urgent need for carbon pricing mechanisms is universally acknowledged, yet implementation remains fragmented. Key arguments center on the equity gap between developed and developing nations, with a strong emphasis on nature-based solutions as a cost-effective bridge. The executive summary highlights a 2.3°C warming trajectory if current pledges are not met."* |
| **3** | Digital Marketing Funnel Strategy | 4 HubSpot / industry case studies | Aug 26 | *"The traditional linear funnel is dead; modern strategy requires a 'flywheel' model focused on retention and advocacy. Data privacy regulations (GDPR/CCPA) have fundamentally altered top-of-funnel acquisition tactics. The most effective campaigns now blend organic content with hyper-personalized email sequencing."* |
| **4** | AI Ethics & Bias | 3 academic papers + 2 news articles | Aug 26 | *"Bias in AI systems is not a technical bug but a reflection of historical data inequalities. Transparency and explainability remain unsolved challenges, particularly in generative AI. The summary argues that regulatory frameworks are lagging 3-5 years behind technical deployment capabilities."* |
| **5** | Financial Markets & Cryptocurrency | 5 Reuters / Bloomberg summaries | Aug 26 | *"Institutional adoption of crypto assets has stabilized prices but introduced correlated volatility with traditional equities. The core debate centers on whether Bitcoin is a 'risk-on' or 'risk-off' asset; current data shows it behaves as a high-beta tech stock. Stablecoin regulation is identified as the critical near-term catalyst."* |

---

### Sample Full Output – Run 1 (Software Engineering)

*This is the actual output Claude generated after completing Steps 3–5, based on the Concept Grid provided.*

#### Executive Summary
> The core thesis of software engineering is the management of complexity through structured processes, balanced against the unpredictability of human creativity. The course presents an unresolved trade-off: plan-driven methods (Waterfall/RUP) prioritize documentation and risk management, while agile methods (XP/Scrum) prioritize adaptability and speed. Crucially, the source material does not declare a winner, instead framing the choice as context-dependent based on system size, team skill, and criticality. The overarching recommendation is that no single process fits all projects—practitioners must tailor their approach.

#### Key Arguments (Condensed)
1. **Process as a Spectrum:** All software processes share four activities (specification, development, validation, evolution), but they sequence and prioritize these differently. Waterfall executes them once sequentially; Agile interleaves them continuously.
2. **Requirements Are the Anchor:** Functional and non-functional requirements must be distinguished. Non-functional constraints (performance, security) often determine system success or failure, and missing them early incurs a 100x cost to fix post-delivery.
3. **People Over Process:** Agile methods explicitly prioritize individuals and interactions, accepting that change is inevitable. XP's test-first development and pair programming are designed to reduce defects and spread knowledge, reducing bus-factor risk.

#### Counterarguments & Limitations
The four modules openly acknowledge that agile methods require higher skill levels than plan-based approaches, yet they also rely on pair programming to mitigate individual dependency—a soft contradiction. Additionally, while formal requirements documents are presented as essential for safety-critical systems, agile treats them as "waste" in rapidly changing environments. The course leaves these tensions unresolved, implying that professional judgment must mediate.

#### Glossary (5 Terms)
- **Waterfall Model:** Sequential process where each phase must complete before the next begins.
- **Agile Manifesto:** A set of values prioritizing individuals, working software, customer collaboration, and responding to change.
- **Non-functional Requirement:** A constraint on the system (e.g., performance, security) rather than a specific behavior.
- **RUP (Rational Unified Process):** A phased framework (Inception, Elaboration, Construction, Transition) blending iterative and plan-driven elements.
- **COTS (Commercial Off-The-Shelf):** Pre-built software components integrated into a system to reduce development cost.

#### Sample Quiz Questions (5 MCQ)
1. **Which attribute is NOT one of the four essential attributes of good software?**  
   a) Maintainability  b) Dependability  c) Portability  d) Efficiency  
   *Answer: c) Portability (verified against slide p.8)*
2. **Which model explicitly assesses and resolves risks at every stage?**  
   a) Waterfall  b) Incremental  c) Spiral  d) XP  
   *Answer: c) Spiral*
3. **What is the primary purpose of a prototype in the software process?**  
   a) To serve as final production code  b) To elicit and validate requirements  c) To reduce documentation  d) To replace the design phase  
   *Answer: b) To elicit and validate requirements*
4. **Which XP practice requires developers to write a test before writing the code?**  
   a) Pair Programming  b) Continuous Integration  c) Test-first Development  d) Refactoring  
   *Answer: c) Test-first Development*
5. **Who protects the development team from external distractions in Scrum?**  
   a) Product Owner  b) Scrum Master  c) Development Team Lead  d) Stakeholder  
   *Answer: b) Scrum Master*

*(10 Anki flashcards were also generated; sample: Q: "What are the four fundamental process activities?" A: "Specification, Development, Validation, Evolution.")*

---

## 4. Time Accounting (Honest Estimate)

### Manual Baseline (Doing 1 Study Session entirely by hand)
| Activity | Time |
| :--- | :--- |
| Reading & highlighting 4–5 sources (avg 10 pages each) | 45 min |
| Synthesizing a Concept Grid by hand | 25 min |
| Drafting structured notes (thesis, arguments, glossary) | 30 min |
| Reviewing, critiquing, and writing a quiz | 20 min |
| **Total Manual Time (per topic)** | **120 min (2 hours)** |

### Automated Workflow (Claude Project – 5 steps)
| Activity | Time |
| :--- | :--- |
| Uploading files & running Step 1 (Gather) | 3 min |
| Waiting for Step 2 (Synthesize – Concept Grid) | 2 min |
| Waiting for Step 3 (Draft) | 2 min |
| Waiting for Step 4 (Review) | 2 min |
| Waiting for Step 5 (Format – Summary/Quiz/Flashcards) | 2 min |
| Copy-pasting final output to document | 2 min |
| **Total Automated Time (per topic)** | **~13 min** |

### Setup Cost (One-time)
| Activity | Time |
| :--- | :--- |
| Creating Claude Project & pasting System Prompt | 5 min |
| Uploading initial knowledge files | 5 min |
| **Total Setup** | **10 min** |

### Break-Even Analysis
- **Time saved per study session:** 120 min – 13 min = **107 minutes**.
- **Break-even point:** 10 min (setup) ÷ 107 min ≈ **0.09 sessions**.  
  *Practically, after just 1 session, the setup cost is fully recovered.*
- **Total time saved over 5 runs:** 5 × 107 min = **535 minutes (8.9 hours)**.

---

## 5. Known Failure Points & Required Human Review

Despite successful end-to-end execution, the workflow is not fully autonomous. The following failure points were observed and validated across the 5 runs.

### Failure Points (Where it breaks)

| Failure Point | Description | Observed Example | Mitigation / Fix |
| :--- | :--- | :--- | :--- |
| **1. Quote Hallucination (Paraphrasing Overload)** | Claude often paraphrases quotes rather than reproducing them verbatim, occasionally changing critical qualifiers (e.g., "may" becomes "will"). | In Run 1, the "100x cost" figure was rephrased without the exact IEEE wording. | Human must spot-check 3 direct quotes against the source. |
| **2. Contradiction Merging (Harmony Bias)** | When presented with opposing frameworks, Claude tries to harmonize them instead of highlighting the irreconcilable friction. | In Run 1, it initially smoothed over the Waterfall vs. Agile philosophical war; only the explicit "Counterarguments" prompt forced it to separate them. | Human must review the "Counterarguments & Limitations" section specifically. |
| **3. Context Window Degradation** | If uploads exceed ~150 pages, Claude forgets specifics from earlier files by the time it processes later ones. | In a test upload of 5 full textbooks, Module 1 details were absent from the final draft. | Keep total uploads under 50k tokens; split into multiple project chats if needed. |
| **4. Temporal Staleness Blindness** | Claude treats all uploaded content as equally "current" and does not flag outdated publications unless prompted. | The Software Engineering modules cite Sommerville 2016 – Claude did not mention the decade gap. | Human must check publication dates and add a "currency" note. |
| **5. Quiz Over-Simplification** | The AI sometimes generates quiz questions that are trivial or answerable from general knowledge, not strictly from the sources. | In Run 3 (Marketing), it asked "What does ROI stand for?" – not grounded in the uploaded case studies. | Human must review all 5 quiz questions for source-groundedness. |

### Required Human Review Checklist
Before submitting the final output for any run, a human must validate these items:

- [ ] **Fact-Checking:** Read the "Core Thesis." Does it actually represent the *majority* of the source text, or just a niche slide?
- [ ] **Quote Accuracy:** Verify 2–3 direct quotes from the Concept Grid against the original source. Are they verbatim?
- [ ] **Contradiction Handling:** Does the "Counterarguments" section correctly surface genuine conflicts, or did the AI falsely harmonize them?
- [ ] **Quiz Sanity:** Are the 5 multiple-choice questions answerable *strictly* from the uploaded files, not from common sense?
- [ ] **Glossary Completeness:** Does the Glossary miss a crucial acronym repeated heavily in the text (e.g., COTS, RUP, GDPR)?
- [ ] **Date Awareness:** Are the sources current enough for the topic? If not, has a note been added?

---

## Declaration

I certify that the workflow described above runs end-to-end on a brand new input (validated on Run 1), comprises five distinct steps with defined handoffs, and that the time accounting and failure point analysis are honest and based on actual execution.

**Submitted by:** Jared Noel  
**Submission Date:** August 27, 2026
