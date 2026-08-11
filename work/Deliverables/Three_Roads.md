# Week 4 Deliverable: Three Roads — Choose Your Stack with AI

**Student Name:** Jared Noel
**Course / Track:** Machine Learning Engineer — General AI Fluency
**Assignment:** Week 4, Build phase — aifluency.flyrank.ai/week-04.html#three-roads

---

## 1. The Four Constraints Given to AI

- **Budget:** Free tools and free hosting only — no paid tiers.
- **Honest skill level:** I know front-end basics but I'm not comfortable building a site from a blank file. I want a template or theme as scaffolding, not a from-scratch build.
- **What the portfolio needs to do:** it has to carry my content map — a Home page, a Work/Case Studies index, three individual case study pages (Problem → What I Did & Decided → Outcome → Proof), an About page, and a Contact page, with a "book a call" CTA repeated on every page.
- **How the work must be displayed:** long-form case-study writing, embedded screenshots, testimonials, and outbound links to two live demos (MemoAgent and LGU Risk Radar) that are already hosted separately on Vercel, plus GitHub repo links.
- **Whether anything needs to be dynamic yet:** yes, one thing — the contact form needs to actually send me an email (via the Resend API) when someone submits it. Nothing else on the site needs to be dynamic; the live demos already run on their own, separate deployments.

---

## 2. Three Stack Options

I asked Claude for three options, simplest to most powerful, each scored on how I'd build it, where I'd host it for free, whether it needs a backend, and the real trade-off — not just the upside.

### Option 1 — Simplest
- **Build:** Free Astro/Eleventy portfolio template, content dropped into existing pages
- **Host (free):** Netlify or Vercel
- **Backend:** No real backend — one tiny function or form service calling Resend
- **Trade-off:** Fastest to ship, but I inherit the template's idea of a "case study," which may fight my Problem → Decision → Outcome → Proof structure and can look template-y to people who browse a lot of portfolios.

### Option 2 — Middle (chosen)
- **Build:** Free Next.js/TypeScript template + case studies written as MDX files matching my content map
- **Host (free):** Vercel (same place my two live demos already run)
- **Backend:** One small serverless API route to call Resend — no database
- **Trade-off:** More setup than Option 1, since I'm editing real components, not a theme's blanks — but I get full control of the case-study layout and it's the same stack I already use, so it's not new to me.

### Option 3 — Most powerful
- **Build:** Same Next.js base, plus a headless CMS (Sanity free tier) so content is editable without redeploying
- **Host (free):** Vercel (site) + Sanity (content)
- **Backend:** Yes — CMS schema/API on top of the Resend function
- **Trade-off:** Most "production-system" looking, but solves a problem I don't have: 3 case studies I update rarely, not 30 I update daily. Extra setup time I don't have, given I still need to gather testimonials, before/after numbers, and screenshots.

---

## 3. Pressure-Test on the Front-Runner (Option 2)

**What breaks if I pick the simplest (Option 1)?**
The template's layout fights my specific case-study structure, and free portfolio themes are recognizable to the exact audience I'm targeting — technical leads who look at a lot of these.

**What do I maintain if I pick the most powerful (Option 3)?**
A CMS schema, its API tokens, and a second free-tier service with its own limits — on top of the Resend function — for content that barely changes.

**Can I finish this in two weeks?**
Yes, comfortably. The template handles scaffolding I'm not confident building from scratch, and I already know the underlying stack (Next.js/TypeScript), so I'm adapting, not learning from zero.

**Does it show my work the way it needs to be shown?**
Yes — MDX case studies map directly onto Problem → What I Did & Decided → Outcome → Proof, screenshots and demo links slot in as normal content, and hosting on Vercel keeps it visually and technically consistent with the two live demos I'm linking out to.

---

## 4. Decision & Rationale

**Chosen stack:** A free Next.js portfolio template as my starting scaffold, with case studies written in MDX, hosted on Vercel, plus one small serverless function that emails me through the Resend API when someone submits the contact form.

**Alternatives considered, and why I didn't pick them:**
Option 1 (a simpler static template with no framework) would have been faster, but free portfolio themes are built for blog-style posts, not the Problem → Decision → Outcome → Proof structure my case studies need — I'd spend my time fighting the layout instead of writing the content that actually proves my work.

Option 3 (adding a headless CMS) would let me edit content without touching code, but I only have three case studies that change rarely, not a library I'm updating constantly. A CMS means another service, another schema, and another free-tier limit to track — overhead for a problem I don't have yet.

**Can I maintain this?**
Yes. It's the same stack (Next.js/TypeScript) I already use on my backend projects, so updating a case study later is just editing a file and pushing to Git — no new tool to learn, and no service outside Vercel and Resend to keep alive.

**Does it show my work well?**
Yes. MDX case studies match my content map's Problem/What I Did/Outcome/Proof structure field-for-field, screenshots and testimonials sit naturally as page content, and hosting everything on Vercel — the same platform my two live demos already run on — makes the whole body of work read as one coherent, professionally-hosted system rather than a portfolio site plus two disconnected side projects.

**Backend question, answered honestly:**
Not yet, and not really even now. The only server-side piece is one small function that forwards contact-form submissions to Resend. There's no database, no user accounts, and nothing running when nobody's on the site — the actual AI systems (MemoAgent, LGU Risk Radar) already have their own separate deployments and don't need the portfolio to serve them.
