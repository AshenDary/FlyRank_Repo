# Prompt Iteration Log: Machine Learning Task Framing (Lane 2)

## Task Description
- **Real FL-01 Audit Task:** Framing an ML pipeline that inputs 30,000 content pages and outputs a daily ranked priority queue (0.0 to 1.0 probability score) for content editors to refresh high-value, declining pages.

---

## Iteration 0: Naive Version (Baseline)
- **Technique:** None (Naive one-line prompt)
- **Prompt:** "How do I use machine learning to fix declining web pages?"
- **Output:**
> "To fix declining web pages with machine learning, you can build a predictive model using historical traffic data. First, collect metrics like page views, bounce rate, and search rankings. Next, train a regression or classification algorithm (such as Random Forest or Logistic Regression) to predict which pages are losing traffic. Once predicted, your team can manually inspect those pages and update the content, fix broken links, or improve SEO keywords to recover traffic."
- **Observed Difference & Note:** The baseline output is a vague, textbook summary. It offers generic advice without defining a clear target, continuous metrics, unit of analysis, or data leakage guards.

---

## Iteration 1: Role Assignment
- **Applied Technique:** Role Assignment
- **Prompt:** "Act as a Senior Machine Learning Engineer specializing in Search Engine Optimization (SEO) content systems. How do I frame a machine learning task to prioritize declining web pages for a content editing team?"
- **Output:**
> "As an ML Engineer, I recommend framing this as a **Scoring / Ranking task** rather than a simple classification problem. 
> 1. **Problem Definition:** Predict a continuous priority score $P \in [0, 1]$ representing the likelihood that a page requires editorial intervention.
> 2. **Workflow Integration:** Sort pages by $P$ to form a daily queue for editors.
> 3. **Key Consideration:** Avoid using future performance metrics in your feature set to prevent temporal target leakage."
- **Observed Difference & Note:** Setting the role immediately shifted the tone from a generic blog post to professional ML architecture advice. It introduced critical framing concepts like continuous scoring and data leakage.

---

## Iteration 2: Context and Motivation
- **Applied Technique:** Context and Motivation
- **Prompt:** "Act as a Senior Machine Learning Engineer specializing in SEO content systems. We manage 30,000 pages for a client. Content performance changes daily, but an editor can only inspect 10-20 pages per day. Random checking wastes time, while unaddressed traffic drops lose revenue. How should we frame an ML task to rank declining pages, using raw metrics like age, CTR, position, and 90-day impressions?"
- **Output:**
> "Given your constraint (10–20 manual reviews per day out of 30,000 pages), a standard binary classifier is insufficient because it flags thousands of pages equally without ordering them. 
> 
> You must frame this as a **Priority Scoring Queue**. Using continuous features (`content_age_days`, `days_since_last_update`, `avg_position`, `ctr`, and `impressions_90d`), the model outputs a probability score from 0.0 to 1.0. The editorial team simply processes the top $K$ pages from the sorted list each morning."
- **Observed Difference & Note:** Adding real business context (30,000 total pages vs. 10-20 daily reviews) grounded the solution. The AI stopped giving broad theory and specifically explained why fixed rules fail compared to a ranked queue.

---

## Iteration 3: Output Structure
- **Applied Technique:** Output Structure
- **Prompt:** "Act as a Senior Machine Learning Engineer. Frame our content refresh ML problem using the following strict Markdown structure:
  1. Task Type & Output Range
  2. Target / Proxy Flag Definition
  3. Feature Set & Data Leakage Guards
  4. Core Success Metric (Precision@K)
  5. Business Impact"
- **Output:**
> ### 1. Task Type & Output Range
> **Scoring / Ranking task** outputting a probability score $S \in [0.0, 1.0]$.
> 
> ### 2. Target / Proxy Flag Definition
> Binary proxy flag `needs_review = 1` if `trend_direction == 'down'` AND `impressions_90d >= 100`.
> 
> ### 3. Feature Set & Data Leakage Guards
> Allowed features: `content_age_days`, `days_since_last_update`, `avg_position`, `ctr`, `impressions_90d`.
> *Leakage Guard:* `trend_direction` is strictly excluded from features as it defines the target.
> 
> ### 4. Core Success Metric
> **Precision@K** (e.g., Precision@10) to optimize the accuracy of the top recommendations.
> 
> ### 5. Business Impact
> Focuses editor bandwidth on high-value declining pages, eliminating manual guessing.
- **Observed Difference & Note:** Forcing a strict structural format stripped away conversational filler and produced a clean, professional technical specification ready for code implementation.

---

## Iteration 4: Few-Shot Examples
- **Applied Technique:** Few-Shot Examples
- **Prompt:** "Act as a Senior Machine Learning Engineer. Frame our content refresh ML problem using strict Markdown formatting.
  
Here is an example of how to define a proxy target:
*Example:* `target_needs_review = 1` IF (`trend_direction == 'down'` AND `impressions_90d >= 100`) ELSE `0`.

Now apply this logic to frame our entire pipeline (Task Type, Target Proxy, Features & Leakage, Metrics, and Impact)."
- **Output:**
> ### Pipeline Framing Specification
> * **Unit of Analysis:** 1 row = 1 unique content page (`content_id`).
> * **Target Definition:** `needs_review = 1` IF (`trend_direction == 'down'` AND `impressions_90d >= 100`) ELSE `0`. (Yields 13,152 positive cases out of 30,000 pages).
> * **Model Output:** Probability score $P(\text{needs\_review} = 1) \in [0, 1]$.
> * **Feature Matrix:** `[content_age_days, days_since_last_update, avg_position, ctr, impressions_90d]`. Excludes `trend_direction` and off-limits columns (`health_score`, `priority_score`).
> * **Metric:** Precision@10 (Primary), ROC-AUC (Secondary).
- **Observed Difference & Note:** Providing a concrete few-shot example eliminated ambiguity around target definitions. The AI successfully adopted the exact boolean filter logic and explicitly called out off-limits synthetic columns.

---

## Iteration 5: Step Decomposition
- **Applied Technique:** Step Decomposition (Chain of Thought)
- **Prompt:** "Act as a Senior Machine Learning Engineer. Work step-by-step to frame our content refresh ML task:
  Step 1: Define the unit of analysis and verify row uniqueness.
  Step 2: Construct the binary proxy flag and state explicit data leakage guards.
  Step 3: Define the task type and scoring range.
  Step 4: Select primary and secondary evaluation metrics tailored to a daily human workflow.
  Step 5: Summarize why ML beats a fixed heuristic rule."
- **Output:**
> ### Step 1: Unit of Analysis
> Verified that each row represents exactly one unique content page (`content_id`).
> 
> ### Step 2: Target Proxy & Data Leakage Guard
> Target proxy `needs_review` is defined using raw columns: `(trend_direction == 'down') & (impressions_90d >= 100)`.
> **Leakage Guard:** `trend_direction` is used *only* to construct the target label and is dropped from the feature matrix $X$.
> 
> ### Step 3: Task Type & Output Range
> Supervised Scoring / Ranking task predicting $P(\text{needs\_review} = 1 \mid X) \in [0, 1]$.
> 
> ### Step 4: Metric Selection
> * **Primary:** Precision@K (Precision@10/Precision@20). Editors only review 10–20 pages per day; the top of the queue must be accurate.
> * **Secondary:** ROC-AUC to monitor overall model discrimination across all 30,000 pages.
> 
> ### Step 5: Why ML Beats Fixed Rules
> Fixed rules create an unsorted bucket of 13,152 pages. ML evaluates continuous signals simultaneously to output a smooth ranking score, giving editors a prioritized queue.
- **Observed Difference & Note:** Breaking the prompt into step-by-step execution forced maximum logical rigor. The AI cleanly separated the proxy creation from the feature matrix construction and explicitly justified Precision@K based on editor constraints.

---

## Cross-Model Comparison (Claude vs. ChatGPT)

### Tested Prompt
The finalized **Iteration 5 Prompt** (Step Decomposition) was evaluated across both models.

### Comparison Table
| Feature / Dimension | Claude (Claude 3.5 / 3.7 Sonnet) | ChatGPT (GPT-4o) |
| :--- | :--- | :--- |
| **Tone & Style** | Direct, concise, software-engineering focused. | Enthusiastic, structured, slightly conversational. |
| **Schema Adherence** | Followed the 5 steps strictly without adding extra fluff. | Followed the 5 steps well, but added extra introductory and concluding summaries. |
| **Technical Accuracy** | Handled data leakage (`trend_direction`) precisely in step 2. | Correctly identified leakage, but required double-checking to ensure synthetic columns weren't suggested. |
| **Failure Points** | Output was slightly dense; preferred code/math notation over bulleted prose. | Included mild corporate filler ("maximize editorial synergy"). |

### Specific Findings
Claude excelled at concise technical execution, keeping strictly to the requested markdown schema. ChatGPT provided higher visual readability with bold formatting, but introduced slightly more filler language.

---

## Final Reusable Prompt Template

```text
Act as a Senior Machine Learning Engineer. I need you to frame a Machine Learning task for [INSERT BUSINESS CONTEXT / PROBLEM].

Work step-by-step through the following instructions:

1. **Unit of Analysis:** Identify what 1 row in the dataset represents and verify entity uniqueness.
2. **Target / Proxy Definition:** Define a binary target flag (`0` or `1`) using raw dataset conditions. Explicitly name any columns that must be excluded from features to prevent data leakage.
3. **Task Type:** Define the ML task type (e.g., Scoring/Ranking) and specify the mathematical output range (e.g., probability score from 0.0 to 1.0).
4. **Metric Selection:** Select a primary metric (e.g., Precision@K) tailored to human capacity/workflow constraints, and a secondary overall metric (e.g., ROC-AUC).
5. **Business Justification:** Explain why Machine Learning outperforms a simple fixed rule or heuristic for this use case.

### Formatting Constraint:
Output your answer using clean Markdown headers matching Steps 1 through 5.
```
