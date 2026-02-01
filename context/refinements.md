# Blog Refinements

# Blog Refinements & Learnings

## Purpose
Track patterns, preferences, and adjustments to the daily blog post generation system for Asymmetrical Collage.

---

## Current AI Generation Instructions (v1.3)

### Master Template
**Core Themes:** Freedom, liberty, personal values, building for resilience, building for permanence, self-reliance, long-term thinking

**Tone:** Courageous and optimistic. Not preachy or pessimistic. Inspiring action and reflection.

**Style Influences:** Seth Godin (punchy, ends with reflection) + Naval Ravikant (aphoristic, philosophical clarity)

**Format:**
- 50-300 words
- Strong opening hook
- One core idea, clearly expressed
- End with question, assertion, directive, or observation (VARY â€” do not default to questions)
- No fluff or filler
- Use article-template.md for all file creation (includes `image: ""` field)
- Create files with bash heredoc, NOT create_file tool (strips frontmatter dashes)

**Variety:** Each of the 3 drafts should take a different approach:
1. One provocative/challenging
2. One observational/philosophical
3. One practical/actionable

**Avoid:** Doom-and-gloom, partisan politics, empty platitudes, corporate-speak, aspirational advice without actionable grounding

**Credibility Integration:** Risk management angle added naturally in some posts without forcing it.

**Topics to Avoid (Until Further Clarity):**
- Multiple income streams / side hustles - Popular online but unclear how feasible/accessible for most people. Feels aspirational rather than actionable. May revisit when Laurent has clearer perspective on realistic path vs. internet mythology.

**CRITICAL: Past Posts Check**
Before generating drafts, Claude must:
1. **Review recent posts** (last 7-10 days) to avoid repetitive themes or concepts
2. **Check for contradictions** - New posts shouldn't contradict previous positions unless there's a deliberate reason
3. **Mine past posts for depth** - Previous posts can suggest angles to explore further or related concepts to develop
4. **Flag similar drafts** - If a draft is too close to a recent post, discard and generate a replacement
5. **Check specific examples** â€” not just themes. If an example (climbing rope, politician/offshore, etc.) was used recently, don't reuse it
6. **Check for thinker echoes** â€” especially Taleb. If a framework comes from a known thinker, ensure examples are original, not theirs

**CRITICAL: Three Drafts Only**
If none of three drafts work, that's feedback about the system â€” not a signal to generate more. Poor options mean: past posts check failed, quality bar miscalibrated, theme selection off, or instructions need refinement.

**CRITICAL: Laurent's Original Concepts**
When Laurent provides his own concept or framework (e.g., large organization convergence), ask him to sketch the framing first before drafting. Claude's attempt at framing these was too bland.

---

## Posts Published

### February 1, 2026: "Luck Has a Surface Area"
**Selected:** Draft 2 (Observational - Foundation)

**What worked:**
- Explores virgin territory: Luck & Opportunity theme (surface area for serendipity)
- "Luck is not a gift. It's a math problem." reframes luck as engineerable
- Three concrete examples (reads widely, talks to strangers, ships regularly) establish pattern
- "None of them planned it. All of them created the conditions." is the key insight
- Natural companion to "Bet Small, Win Big" - both about engineerable upside
- Ending is assertion (varied from recent directive/question pattern)

**Refinements made:**
- None - draft was ready as written

**Key insight:** Luck and asymmetric bets are two sides of the same coin. Yesterday's post said "risk little, gain much." Today's says "expose yourself, and favorable outcomes find you." Together they form a mini-arc: asymmetric bets are the strategy, surface area is the mechanism.

**Discarded drafts:**
- Draft 1 (Permission vs Permissionless) strong but saved for future - aligns with sovereignty theme
- Draft 3 (Emergence from banked draft) solid, still available for future publication

---

### January 31, 2026: "Bet Small, Win Big"
**Selected:** Draft 3 (Provocative - Foundation)

**What worked:**
- HIGH PRIORITY banked draft refined and published - explains "Asymmetrical Collage" blog name/philosophy
- Concrete examples (start blog, meet someone, learn skill) are specific and relatable
- "Engineering favorable odds" reframes from gambling to strategy
- Directive ending (not question): "Risk little. Stand to gain much. Repeat."
- Core concept: limited downside, unlimited upside = asymmetric bets worth taking
- Tightened using Scott Adams principles from banked version

**Refinements made:**
- Changed from generic examples in banked draft to more specific ones
- "That's not gambling. That's engineering favorable odds" makes the strategic nature clear
- Three-word imperative ending creates rhythm and memorability

**Key insight:** This is THE post that explains the blog's foundational philosophy. Asymmetric bets - where you risk small amounts for potentially large gains - are the framework for personal sovereignty, optionality, and growth. Publishing this completes a key piece of the blog's identity arc.

**Discarded drafts:**
- Draft 1 (systems vs goals) was solid but not as foundational
- Draft 2 (barbell strategy) was pure Taleb - 90/10 split, barbell framework, even the examples echoed his work

**Process note:** Caught myself echoing Taleb again (twice this week). Need systematic check: when using frameworks from specific thinkers, am I using their examples too? Concepts can be discussed, but examples should be original or clearly attributed.

---

### January 30, 2026: "What You Don't See"
**Selected:** Draft 2 (Practical - Foundation)

**What worked:**
- Explores virgin territory: Infrastructure & Foundations theme (invisible work)
- Concrete examples (website, power, roads) establish pattern
- Pivot to personal (health, relationships, routines) makes it relevant
- "Infrastructure is invisible when it works" names the insight
- Ending is directive, not question (breaks the repetitive pattern)

**Refinements made:**
- Changed ending from repetitive question format to actionable directive
- Original: "What invisible work are you neglecting?"
- Final: "Step back occasionally. Assess what works that you might take for granted. Tend to it before it forces your attention."
- This provides concrete suggestion rather than formulaic question

**Key insight:** Breaking the question-ending pattern required collaborative refinement. Laurent noted the "What are you not doing?" formula was getting stale. The new directive ending is more actionable and varied. This is a pattern to continue - vary between questions, assertions, directives, and observations.

**Discarded drafts:**
- Draft 1 (Lindy Effect) opened too similar to Nassim Taleb's examples (books, tools, ideas surviving time)
- Draft 3 (large organization convergence) was Laurent's concept but framing felt bland - needs Laurent to sketch framing first before drafting

**Process note:** Today revealed ending formula overuse. Need to systematically vary: questions, assertions, directives, observations. Also need to catch when echoing specific thinkers' examples (not just concepts).

---

### January 29, 2026: "Watch What They Buy"
**Selected:** Draft 2 (Practical - Foundation)

**What worked:**
- Applies "expensive signals" concept from central bank gold observation in WEEKLY_INPUTS
- Three concrete examples (politician/offshore, executive/stock, central banker/gold) establish pattern
- Multiple ways of stating principle reinforces clarity
- Connects to sovereignty/Bitcoin themes naturally without forcing it
- Very actionable: "follow the money" is immediately applicable

**Refinements made:**
- Changed "Talk costs nothing" â†’ "Talk is cheap" (more idiomatic)
- Changed "Moving money costs everything" â†’ "Money speaks" (parallel structure, more concise)
- Changed "You don't need to decode the language" â†’ "Don't decipher the words" (more active)
- Changed "You need to follow the money" â†’ "Follow the money" (direct command)
- Removed "actually" from "What people risk reveals what they actually think" (cleaner)
- Changed "When their words point one way and their wallet points another" â†’ "When their words and wallets point in opposite directions" (clearer spatial metaphor)

**Key insight:** Expensive signals framework cuts through jargon and narrative. When people risk money/reputation/opportunity cost, they're signaling true beliefs. This connects to skin in the game theme and provides practical lens for reading situations. Much more original than attempting to copy the brilliant source tweet.

**Discarded drafts:**
- Draft 1 (large organization convergence) was solid but would benefit from asking reader how to build better model
- Draft 3 (permissionless) needed edits to be production ready

---

### January 28, 2026: "Then What?"
**Selected:** Draft 2 (Observational - Foundation)

**What worked:**
- Explores virgin territory: Mental Models theme (second-order thinking)
- Two concrete examples (raise prices, cut costs) make framework actionable
- "Consequences of the consequences" names the key insight
- Clean structure: example â†’ definition â†’ example â†’ principle â†’ closer
- Parallel closing: "First-order sees the move. Second-order sees the game."
- Title as pivot question throughout

**Refinements made:**
- None - draft was ready as written

**Key insight:** Second-order thinking is immediately applicable mental model. The "then what?" question is simple enough to use daily but powerful enough to change decision quality. Two business examples ground the concept without feeling corporate.

**Discarded drafts:**
- Draft 1 (jargon/central bank) was derivative of brilliant source tweet
- Draft 3 (climbing rope/margin of safety) repeated example from earlier this month
- Drafts 4, 5, 6, 7, 8 were generated in error (system should stop at 3 drafts)

**Process note:** Today revealed instruction gaps - needed explicit checks for (1) specific example reuse, (2) derivative vs original work, (3) stopping at three drafts. Updated to v1.3 with these safeguards.

---

### January 27, 2026: "The Cost of Switching"
**Selected:** Draft 2 (Observational - Foundation)

**What worked:**
- Explores virgin territory: Attention & Focus theme (context switching cost)
- "It bleeds" as visceral metaphor for invisible cost
- Concrete narrative (code â†’ Slack â†’ return) makes abstract concept tangible
- "Rebuild the mental model" names the invisible work
- "Death by a thousand context switches" is memorable phrase
- Parallel structure in closing: "best work...uninterrupted / worst work...fragments"

**Refinements made:**
- Kept "tax that compounds" despite initial question - the compounding happens over time (lost momentum, missed insights, opportunity cost) not within a single day

**Key insight:** Laurent noted compounding operates at multiple timescales. Within a day, switching costs add up (15 interruptions = 15 rebuilds). Over time, those lost deep work sessions compound into missed progress and opportunity cost. Keeping "compounds" captures the higher-level truth.

**Discarded drafts:**
- Draft 1 (privacy/compartmentalization) felt too basic, like selling password managers
- Draft 3 (optimize for what?) too similar to recent posts

---

### January 26, 2026: "When Networks Help, When They Hurt"
**Selected:** Draft 2 (Observational - Foundation)

**What worked:**
- Introduces genuine tension: when does scale help vs hurt?
- Bitcoin vs startup contrast reveals underlying mechanism (independence vs coordination)
- Mathematical precision (n(n-1)/2 explained concretely) adds credibility
- "Creates leverage through focus" ties to broader blog themes
- Strategic framework: "Scale what strengthens. Tighten what weakens."

**Refinements made:**
- Changed "Bitcoin's security increases with each miner" â†’ "Each network node and miner increases Bitcoin's security" (technical accuracy + active voice)
- Changed "A language becomes more useful" â†’ "More people speaking a language makes it more useful" (active voice)
- Removed em-dash from formula explanation, added concrete example: "With ten people, that's forty-five connections to manage"
- Changed "Keep tight" â†’ "Tighten" (stronger verb)
- Changed "scales impact" â†’ "creates leverage" (better thematic fit)
- Changed "The difference?" â†’ "The difference is independence." (more assertive, states insight directly)

**Key insight:** This explores virgin territory from Game Theory & Incentives theme. The tension between network effects and coordination costs is a genuinely useful lens for deciding what to scale vs what to keep small. Personal expertise (Bitcoin) grounds abstract concept.

---

### January 17, 2026: "The Courage to Be Boring"
**Selected:** Draft 1 (Provocative - Foundation)

**What worked:**
- Counter-cultural message resonated strongly
- "But boring pays off" pivot was effective
- Concrete examples (lab, garage, library, practice room) grounded the concept
- "What if boring paid off?" as RSS summary was intriguing and memorable

**Refinements made:**
- Added "But boring pays off" line to strengthen the payoff angle
- Shifted from pure courage framing to ROI/results perspective
- RSS summary became the hook rather than explanation

**Key insight:** Challenging performative culture hits hard. Posts that give permission to do unsexy work are liberating.

---

### January 16, 2026: "The Skill Stack Audit"
**Selected:** Draft 3 (Practical - Foundation, with Risk Management angle)

**What worked:**
- Clear compounding vs. linear distinction
- Time as the multiplier made the concept powerful
- Leverage connection elevated it beyond career advice
- Einstein quote added authority and universality
- Low time preference ties to broader themes

**Refinements made:**
- Added time as explicit multiplier ("Time amplifies their value")
- Connected compounding to leverage building
- Added Einstein compound interest quote
- Changed ending from "career optimization" to "building leverage by putting time on your side and adopting a low time preference"
- RSS summary: "Compounding skills and low time preference" - dense and conceptual

**Key insight:** Best posts incorporate multiple related concepts (compounding + leverage + time preference) without feeling cluttered. Risk management lens adds credibility when applied to personal decisions.

---

### January 15, 2026: "Signal vs. Noise in Your Own Life"
**Selected:** Draft 2 (Observational/Philosophical)

**What worked:**
- Extends familiar concept (information filtering) to life decisions
- Concrete and relatable opening
- Clear progression from information â†’ commitments

**Discarded:**
- Draft 3 (threat modeling) was too similar to Jan 14's "Test Your Dependencies" - both about identifying vulnerabilities and protecting against them

**Key insight:** Need systematic check for repetition with recent posts. Implemented "Past Posts Check" requirement in generation instructions (v1.1).

---

### January 14, 2026: "Test Your Dependencies"
**Selected:** Draft 3 (Practical/Actionable - Risk Management)

**What worked:**
- Collaborative refinement process improved the post significantly
- Risk management angle felt natural and grounded
- Concrete examples (passwords, accounts, documentation) made it visceral
- Succession planning reference landed without being morbid

**Refinements made:**
- Changed "Risk managers" â†’ "Risk professionals" (more inclusive)
- Removed arbitrary "72 hours" timeframe â†’ gave readers agency to choose their own
- Changed "during actual crises" â†’ "when their backs are against the wall" (more human)
- Added succession planning example: "piecing together what wasn't documented"
- Changed "Business continuity planning" â†’ "Contingency planning" (more universal)
- Made final question more inviting: "What do you think you would discover..."

**Key insight:** Risk management content works best when grounded in relatable scenarios (death, passwords, documentation) rather than abstract frameworks.

---

### January 13, 2026: "Building in Public vs. Building in Private"
**Selected:** Draft 2 (Observational/Philosophical)

**What worked:**
- Explores strategic tension relevant to Laurent's actual daily practice
- Acknowledges both modes have value rather than prescribing one
- Ends with actionable question about current needs

**Challenge identified:**
- No obvious punchy one-liner for RSS summary - had to craft one separately
- May need to build in more "extractable" phrases for future philosophical posts

**Key insight:** Laurent wants variety across posts - flagged that Draft 1 felt too similar to previous "preparation vs. action" themes

---

### January 12, 2026: "The Illusion of Later"
**Selected:** Draft 2 (Observational/Philosophical)

**What worked:**
- Opening contrast: "We treat time like it's abundant and attention like it's scarce. We should do the opposite."
- Core anchor phrase: "the discomfort of now"
- Final question had right balance of challenge and invitation

**Refinements made:**
- Removed "regret" language (felt like downer/desperate rather than urgent)
- Changed "distant collapse" to "waiting for the perfect moment" (less doom-y)
- Simplified confusing "unlearn" sentence
- Final question went through multiple iterations:
  - Original: "What would you do differently if you knew 'later' wasn't coming?"
  - Revised: "What would change if you stopped treating today like a rehearsal?"
  - Final: "What are you saving for later that deserves today?"

**Key insight:** Optimistic urgency > regretful urgency. Focus forward, not backward.

---

### January 11, 2026: "The Comfort Tax"
**Selected:** [Details to be added]

---

## Selection Patterns

### Week 4 (Jan 26 â€“ Feb 1, 2026)
- **Draft 1 (Provocative):** Selected 0 times
- **Draft 2 (Observational/Practical):** Selected 6 times
- **Draft 3 (Practical/Banked):** Selected 1 time

**Pattern:** Draft 2 is consistently the strongest. Laurent gravitates toward observational framing with concrete examples. Provocative drafts are generated but rarely selected â€” either too close to a known thinker or not grounded enough.

### Week 1 (Jan 11-17, 2026)
- Draft 2 (Philosophical) dominant selection

**Emerging preferences:**
- Observational style with concrete examples consistently wins
- Laurent values originality over cleverness
- Posts that name something readers feel but haven't articulated tend to land
- Endings that aren't questions are often stronger

---

## Voice & Tone Observations

### What's Working
- Short declarative sentences (Scott Adams applied)
- Concrete examples before abstract principle (not after)
- Parallel structure in closings ("First-order sees the move. Second-order sees the game.")
- Naming the insight explicitly rather than implying it
- Active voice throughout
- No em-dashes (flagged as AI signal)

### What to Adjust
- Stop defaulting to question endings â€” vary with assertions, directives, observations
- When using frameworks from known thinkers, find original examples
- Laurent's original concepts need his framing first â€” don't draft from scratch

---

## Topic Frequency (as of Feb 1)

### Risk Management Integration
- Posts naturally incorporating risk frameworks: 2 (Test Dependencies, Watch What They Buy)
- Posts without risk angle: 20
- Sweet spot frequency: ~1 per week feels natural

### Theme Distribution (Week 4)
- Game Theory & Incentives: 2 (Networks, Watch What They Buy)
- Attention & Focus: 1 (Cost of Switching)
- Mental Models: 1 (Then What?)
- Infrastructure: 1 (What You Don't See)
- Asymmetry & Leverage: 2 (Bet Small Win Big, Luck Has Surface Area)

### Gaps to fill in Week 5+
- Nature & Systems (untouched)
- Historical Patterns (untouched)
- Permission vs Permissionless (draft banked, ready)
- Privacy & Security (one attempt discarded as too basic)
- Communication & Influence (untouched)
- Decision-Making (Red Lines banked, Systems vs Goals banked)

---

## Reader Feedback

### Direct Comments
- [Track any reader responses]

### Engagement Patterns
- [RSS subscriber count]
- [Twitter engagement]
- [Which posts get shared]

---

## Adjustments Log

### Version 1.3 (January 28, 2026)
**Changes:**
- Added explicit check for specific example reuse (not just themes)
- Added check for derivative vs original work
- Added "three drafts only" rule â€” poor options signal instruction issues
- Added em-dash ban (AI signal)
- Added article-template.md requirement (includes image field)
- Added bash heredoc requirement (create_file strips frontmatter dashes)
- Added rule: Laurent's original concepts need his framing first

**Reasoning:**
- Taleb echo caught 3 times in one week
- Question-ending formula became stale
- create_file tool corrupted frontmatter on download
- Laurent's org convergence concept was flattened when Claude drafted from scratch

### Version 1.1 (January 15, 2026)
**Changes:**
- Added Past Posts Check requirement

**Reasoning:**
- Repetition caught mid-week 1 (threat modeling too close to Test Dependencies)

---

## Questions to Revisit

- Is 3 drafts the right number, or would 2 or 4 work better?
- How often should risk management themes appear naturally? (~1/week seems right)
- Are 50-300 words the right range, or should we narrow it?
- Should we occasionally let Laurent sketch a concept first, then Claude drafts? (Yes â€” proven with org convergence)
- How to handle Taleb-adjacent concepts without echoing his examples?

---

## Success Metrics

### Consistency
- Target: 7 posts per week
- Actual: 7/7 (Week 4), 7/7 (Week 1)
- Running total: 22 consecutive posts (Jan 11 â€“ Feb 1)

### Quality Indicators
- Posts requiring no refinement: 3/7 this week (Then What?, Cost of Switching, Luck Has Surface Area)
- Posts selected on first pass: 7/7 this week
- Average iteration cycles: ~1.2 (most posts need minor tweaks or none)

### Process Efficiency
- Generation â†’ selection is fast when drafts hit the mark
- Collaborative refinement (What You Don't See ending) adds value when needed
- Banking strong discarded drafts prevents waste

---

**Last Updated:** February 1, 2026
**System Version:** v1.3
**Total Posts Published:** 22 consecutive days (Jan 11 â€“ Feb 1, 2026)
**Banked Drafts:** 9 (3 ready/near-ready, 5 needs work, 1 published)
