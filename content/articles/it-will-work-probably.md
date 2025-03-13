Title: It will get done, probably
Date: 2022-11-10
Category: Engineering Culture
Tags: engineering, organization, leadership, decision-making, Google Analytics, Mixpanel, SDK, data-warehouse, data-engineering
Slug: it-will-work-probably

We've all had those moments when we're convinced we know better than everyone else in the room. A few years ago, I found myself in exactly this position - watching what I believed was a doomed technical decision unfold, absolutely certain I was the only one who saw the inevitable train wreck ahead.

## The Situation

Picture this: I joined as a junior data engineer, excited to learn. Then, within months, my entire team departed—manager, senior engineers, everyone. Suddenly, I was the "expert" on Google Analytics for a global company simply because I was the last one standing.

This accidental inheritance came with a twist: I was responsible for all front-end analytics across the organization with virtually no authority to influence decisions. When I was eventually promoted to mid-level, it merely formalized the responsibility I'd already been shouldering, not the influence I needed.

Then came a critical decision point: continue with expensive GA as it migrated from Universal Analytics to GA4, switch to another third-party solution like Mixpanel, or leverage an in-house SDK that had been developed for ad tracking.

This wasn't just any SDK—it was a neglected codebase with no commits in 18 months, created by a niche team sheltered from global operations, for a very specific purpose. Red flags everywhere.

## My Confident (and Wrong) Assessment

When leadership decided to go with the in-house SDK option, I was certain disaster loomed. I raised concerns about maintenance issues, knowledge gaps, and schema limitations. During meetings, I'd present detailed technical arguments only to watch them evaporate in the face of higher-level business priorities.

I was the domain expert but also the youngest and newest person in the room. Directors and VPs with decades of experience nodded politely at my concerns before continuing down their chosen path. Classic responsibility without authority—I'd be accountable for implementation success but had no real say in the strategic approach.

I documented my concerns, sent carefully-worded emails, and prepared contingency plans for what I saw as the inevitable failure ahead. I was so convinced of my technical assessment that I couldn't imagine any other outcome.

And I was so sure I was right.

## The Humbling Plot Twist

Here's where things get interesting: I was right about the challenges—and simultaneously wrong about the outcome.

The implementation was exactly the nightmare I predicted. The lack of maintenance created technical debt we had to address on the fly. Knowledge gaps meant weeks of archaeological code diving and tracking down former team members for context. The schema limitations required creative workarounds that weren't pretty. We hit every single roadblock I had warned about, sometimes in ways even more frustrating than I'd anticipated.

For a while, I found myself in the uncomfortable position of thinking "I told you so" while simultaneously scrambling to make things work.

Yet despite all these legitimate challenges—which did indeed cause significant difficulties—the project succeeded. The implementation took longer than planned, required more resources than budgeted, and created more developer headaches than anyone had anticipated, but it worked.

Why? Because I underestimated the collective intelligence, creativity, and determination of a company full of brilliant engineers. Once the decision was made from the top down, people rallied. Knowledge gaps were bridged. Maintenance issues were addressed. Schema problems were solved. The impossible became merely difficult, and difficult became done.

That SDK I was convinced would fail? It's still powering front-end tracking across all the company's apps today.

## What I Learned

This experience fundamentally changed how I approach large-scale technical implementations:

1. **Success isn't binary** - "Will it work?" is the wrong question. "How well and how quickly will it work?" is much more useful.

2. **Collective intelligence trumps individual insight** - No matter how solid my technical assessment might be, the combined problem-solving capability of dozens of smart engineers will find paths forward I couldn't imagine.

3. **Organizational momentum matters** - Top-down buy-in creates unstoppable force that overcomes obstacles that seemed insurmountable from my limited vantage point.

4. **Perfect is the enemy of done** - There's never a perfect solution, but that doesn't mean we can't build something that works effectively.

Most importantly, I learned humility. I learned that my technical expertise, while valuable, doesn't give me perfect predictive powers. I learned to voice concerns (always important) while remaining open to being wonderfully, gloriously wrong.

In the complex intersection of engineering challenges and organizational dynamics, certainty is often the first casualty—and that's actually a good thing. It makes room for collective problem-solving that produces results better than any single engineer could predict.

Now when I face similar situations, I approach them with more curiosity than certainty. After all, being proven wrong in this case didn't just lead to a successful project—it made me a better engineer.
