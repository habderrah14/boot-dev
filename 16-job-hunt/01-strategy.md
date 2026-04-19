# Chapter 01 — Strategy

> *"Most people lose the job hunt before they apply, because they treat it like a lottery instead of a project. This chapter makes it a project."*

## Learning objectives

By the end of this chapter you will be able to:

- Define a concrete target role with seniority, stack, industry, and location constraints.
- Build a weekly plan that balances applications, learning, networking, and rest.
- Pick the right pipeline shape for your situation (volume, precision, or referral-led).
- Set metrics that tell you what to change *before* you've burned through a month of effort.
- Budget time and money realistically for your specific background.

## Prerequisites & recap

- All earlier modules: the technical skills are the precondition; this chapter is about converting them into an offer.

## The simple version

The job hunt is a sales funnel. Applications go in at the top; offers come out at the bottom. At every stage — application, recruiter screen, tech screen, onsite, offer — some percentage converts to the next. You can improve conversion at any stage, or you can feed the top of the funnel harder. Both work. Optimizing the wrong stage wastes months.

Your job before applying to anything is to define your target (what role, where, at what level), choose a pipeline shape (volume, precision, or referral-led), build a weekly plan, and set up a tracker so you can diagnose problems after 30 applications instead of 200.

## Visual flow

```
  ┌──────────┐    ┌───────────┐    ┌───────────┐    ┌────────┐    ┌───────┐
  │ Define   │───▶│  Apply    │───▶│ Recruiter │───▶│ Tech   │───▶│ Offer │
  │ Target   │    │ (volume/  │    │  Screen   │    │ Screen │    │       │
  └──────────┘    │ precision)│    │  40-70%   │    │ 30-60% │    │20-40% │
       │          └───────────┘    └───────────┘    └────────┘    └───────┘
       │               ▲
       ▼               │
  ┌──────────┐         │
  │ Network  │─────────┘
  │ (warm    │  referrals boost conversion
  │  intros) │  at every stage
  └──────────┘
```
*Figure 1-1. The job-hunt funnel. Networking feeds and accelerates every stage.*

## Concept deep-dive

### The funnel numbers

Typical entry-level conversion in a normal market:

| Stage | Conversion |
|---|---|
| Application → recruiter response | 5–15% |
| Recruiter response → tech screen | 40–70% |
| Tech screen → onsite | 30–60% |
| Onsite → offer | 20–40% |

Multiply it out: **~200–400 targeted applications** per offer is a reasonable rough number for junior roles. If your numbers are worse than that by 2x, something upstream is broken. If they're better, your targeting or network is working.

### Target definition

Before you write one line of a resume, write *this* down. One paragraph:

> I am looking for a **[level]** **[role]** role at a **[company size]** in **[industry / product type]**, remote or in **[cities]**, starting salary **[range]**, using **[primary stack]**.

Example:

> I am looking for a **junior** **backend engineer** role at a **Series B–D startup** in **fintech or dev tools**, remote or in **Berlin / Lisbon**, starting €45–60k, using **Python or TypeScript**.

Fuzzy targets attract fuzzy responses. A sharp target lets you filter postings in 10 seconds and tailor your resume in 3 minutes.

### Three pipeline shapes

Pick one primary shape. Mixing is fine; defaulting to "all three, badly" is not.

**1. Volume.** 20–40 applications a week on job boards. Works when your resume already reads well and you're willing to tolerate low response rates. Junior-friendly if your projects speak loudly.

**2. Precision.** 5–10 applications a week, each with a tailored resume, a cover note, and ideally a mutual connection. Higher conversion, much slower top-of-funnel.

**3. Referral-led.** Networking first (see [chapter 07](07-networking.md)); applications follow warm introductions. Near-mandatory at well-known companies for juniors. Highest conversion, but requires an existing or actively-built network.

### Weekly plan template

| Day | Block 1 (2h) | Block 2 (2h) | Block 3 (2h) |
|---|---|---|---|
| Mon | Apply to 8–10 roles | Practice DSA (1 medium) | Networking outreach (3 msgs) |
| Tue | Apply to 6 roles | System design reading | Project work |
| Wed | Deep-work on a project | DSA (1 medium + 1 easy) | Rest |
| Thu | Apply to 8 roles | Mock interview | Networking follow-ups |
| Fri | Apply to 4 roles | Interviews (if scheduled) | Weekly review |
| Sat | Rest | Rest | Rest |
| Sun | Plan next week | 90-min project or content | Rest |

Adapt to your reality. The **discipline** to cap applications and protect rest is what prevents the 10-week burnout spiral.

### Metrics you actually track

In a spreadsheet (or Notion database), per application:

- Date applied
- Company, role, link to posting
- Source (board / referral / direct)
- Resume version used
- Recruiter response date (or "no response")
- Outcome at each stage

After 30 applications, compute your application-to-response rate. If it's under 5%, the problem is upstream — resume, LinkedIn, or targeting. Pause and fix before applying to another 30.

### Budgeting time

Treat the hunt like a 20–30 hour/week part-time job if you're employed, 40–50 if you're not. More than that is panic. Less than 20 is a hobby.

Plan for:
- **3 months** if you have 1+ year professional experience and a reasonable network.
- **6 months** for a junior switcher with strong projects.
- **9–12 months** for bootcamp grads in a tight market or non-traditional backgrounds.

Budget cash runway accordingly. Financial panic costs you good offers by making you accept mediocre ones.

### When the market is bad

Observable signs: shrinking tech hiring, ghost postings, non-responsive recruiters, rescinded offers. Adjustments:

- Widen the target: geography, industry, stack.
- Lean on networking harder — cold applications convert worse in every downturn.
- Ship visible work (open source, technical writing) to stand out in a full inbox.
- Extend the timeline. "6 months" becomes "9–12." Budget accordingly.

Don't quit a job you have to enter a bad market without offers in hand.

### What "strategy" does *not* mean

- Applying to 1,000 roles with a generic resume — that's noise.
- Spending six weeks perfecting a portfolio before sending a single application — that's procrastination.
- Refusing to apply until you "feel ready" — the market decides when you're ready, not you.

## Why these design choices

**Why define a target before applying?** Because without one, you waste time on roles you'd reject, tailor to nothing, and can't diagnose your funnel. A target is a filter — it makes every downstream decision faster.

**Why track metrics this early?** Because job-hunting *feels* productive even when it isn't. A tracker makes failure visible after 30 applications instead of 200. If your response rate is 1%, adding more applications is like throwing more darts with your eyes closed.

**Why cap weekly hours?** Because burnout is the biggest risk to a long-term hunt. A burned-out candidate sends sloppy applications, bombs interviews, and accepts bad offers. Sustainable cadence beats sprint-and-crash every time.

**When you'd pick differently:** If you're employed and passive, reduce to 10 hours/week of pure networking — no applications. If you have a hard deadline (visa expiration, lease ending), increase intensity but schedule explicit rest days.

## Production-quality code

For career chapters, this section contains practical artifacts.

### Target statement template

```
I am looking for a [junior / mid / senior] [role title] role
at a [company size / stage] in [industry],
[remote / hybrid / on-site] in [cities],
starting salary [range],
using [primary stack].
```

### Tracking spreadsheet columns

```
Date | Company | Role | Link | Source | Resume Version |
Referrer | Recruiter Response Date | Tech Screen Date |
Onsite Date | Outcome | Next Action | Notes
```

### Weekly review checklist

```
1. Applications sent this week: ___
2. Responses received: ___
3. Application-to-response rate (cumulative): ___%
4. Tech screens this week: ___
5. What's the weakest funnel stage right now?
6. One thing to change next week:
7. Hours worked this week: ___
8. Did I protect rest days? Y/N
```

## Security notes

N/A — this chapter covers job-search strategy, not software systems.

## Performance notes

N/A — the "performance" of a job search is measured by funnel conversion rates, covered in the metrics section above.

## Common mistakes

| Symptom | Cause | Fix |
|---|---|---|
| No target defined; drifting toward whichever recruiter is loudest | Skipping the target-definition step | Write the one-paragraph target statement before sending any application |
| Response rate is 1% after 80 applications | Resume, targeting, or channel is broken upstream | Pause applications; audit resume clarity, role-fit, and application channel |
| Applying while exhausted; sloppy cover notes, wrong company names | No rest schedule; treating the hunt as a 7-day marathon | Cap hours, protect rest days, batch application sessions in focused blocks |
| No metrics after 6 weeks | No tracker, or tracker isn't reviewed weekly | Set up the spreadsheet on day one; schedule a 30-minute weekly review |
| Pure volume with a weak resume | Applying broadly before ensuring the resume communicates clearly | Get three reviews (engineer, recruiter, non-technical friend) before sending another 30 |

## Practice

**Warm-up.** Write your one-paragraph target definition. Share it with one friend and iterate once based on their feedback.

<details><summary>Show solution</summary>

A good target statement is specific enough that someone else could filter job postings for you. Test: could a friend read your target and find 5 matching postings in 15 minutes? If not, it's too vague.

</details>

**Standard.** Build your tracking spreadsheet with the columns listed above. If you've already applied to roles, backfill those entries.

<details><summary>Show solution</summary>

Use Google Sheets, Notion, or Airtable. Include all columns. The key test: after 30 entries, can you compute your application-to-response rate in under 2 minutes? If not, the tracker structure needs simplification.

</details>

**Bug hunt.** You've applied to 80 roles: 1 recruiter screen, 0 tech screens. Which funnel stage is broken and what do you fix first?

<details><summary>Show solution</summary>

Top-of-funnel is broken. 1/80 ≈ 1% response rate. Diagnose in order: (1) target mismatch — applying to senior roles as a junior? (2) resume clarity — does it communicate your role in 15 seconds? (3) channel — only using LinkedIn Easy Apply? (4) targeting — generic applications vs roles matching your stack. Fix (1) and (2) before sending another application.

</details>

**Stretch.** List 100 specific target companies matching your paragraph. For each, identify the role page URL and one existing employee you could reach out to.

<details><summary>Show solution</summary>

Use LinkedIn company search, Wellfound, and Hacker News "Who is Hiring" threads filtered by your stack and location. For each company: note their careers page URL and find one engineer on LinkedIn whose profile matches your target team. This list becomes your precision-application pipeline.

</details>

**Stretch++.** Compute your expected timeline: assuming 200 applications per offer and your realistic weekly application cadence, how many weeks until an offer? Does your cash runway cover it?

<details><summary>Show solution</summary>

Example: 25 applications/week → 200 / 25 = 8 weeks to expected offer. Add 4 weeks buffer for interview cycles. Total: ~12 weeks. If your savings cover 12 weeks of living expenses, you're safe. If not, either increase cadence, reduce expenses, or take contract work as a bridge.

</details>

## In plain terms (newbie lane)
If `Strategy` feels abstract, think of it as a practical tool to make your backend work more predictable and easier to debug. Use this chapter to build one clear mental model first, then add details.

> **Newbies often think:** this topic is only theory and memorization.  
> **Actually:** it is a workflow aid that helps you make better decisions under real project pressure.


## Quiz

1. The job hunt is best modeled as:
    (a) a lottery (b) a sales funnel (c) a single-shot exam (d) networking only

2. A good target statement includes:
    (a) salary, level, role, stack, location (b) just "software engineer" (c) only your tech stack (d) only company size

3. The "volume" pipeline shape is appropriate when:
    (a) you have zero network and no resume (b) your resume reads strongly and you want throughput (c) always (d) never

4. If your application-to-response rate is 1% after 80 applications:
    (a) apply to 80 more (b) pause and fix upstream (resume, targeting) (c) quit (d) network only

5. Weekly review's primary purpose is to:
    (a) feel productive (b) detect broken funnel stages early and adjust (c) please your manager (d) count applications

**Short answer:**

6. Explain why precision pipelines are slower but often convert better for juniors.

7. How does knowing your cash runway change your strategy choice?

*Answers: 1-b, 2-a, 3-b, 4-b, 5-b.*

## Learn-by-doing mini-project

Full brief (goal, acceptance criteria, hints, stretch): [01-strategy — mini-project](mini-projects/01-strategy-project.md).

## Where this idea reappears

- **Same thread elsewhere:** trace how this chapter’s primitives show up in production systems — not only in this language or layer.
- **Cross-module links (read next when you feel stuck):**
  - [Integration projects (cross-module builds)](../appendix-projects/README.md) — tie every earlier module into interview stories.
  - [System design primer](../appendix-system-design.md) — vocabulary for scaling conversations post-modules.

  - [Concept threads (hub)](../appendix-threads/README.md) — state, errors, and performance reading trails.


## Chapter summary

- Define the target before applying to anything — fuzzy targets produce fuzzy results.
- Pipeline shape is a deliberate choice: volume, precision, or referral-led. Pick one and hedge.
- Track metrics weekly; fix the broken stage, not whichever stage feels easiest.
- Budget time (20–40 hours/week) and money (3–12 months runway) before starting.

## Further reading

- *The 2-Hour Job Search* by Steve Dalton — excellent on volume + precision balance.
- Patrick McKenzie, ["Salary Negotiation: Make More Money"](https://www.kalzumeus.com/2012/01/23/salary-negotiation/) — shaping the offer influences early strategy.
- Next: [projects](02-projects.md).
