title: Friction is Not Your Enemy
Date: 2026-05-08
Category: AI & Engineering Culture
Tags: ai-assisted-programming, engineering-culture, prototyping, software-engineering, llm
Slug: friction-is-not-your-enemy

These ideas come from a talk I had the pleasure of delivering at the HHL Leipzig Graduate School of Management, and I think they are an interesting time-stamp to share in the shifting landscape of AI prototyping.

In the context of who I am, I spent the better part of my career as a data engineer. And somewhere in the middle of that career, AI-assisted programming showed up.

## Friction is not your enemy

Speed feels like an obvious win, and things get built quicker. Ideas can get shipped at a speed and quality that it's almost plausible to imagine that everyone who has access to a token or two is a senior full-stack engineer. But there's a hidden cost embedded in that speed that most entrepreneurs aren't thinking about… yet.

Why bother talking to engineering when they will whinge about something irrelevant like "who is going to maintain this code" or design for "it's not fitting our brand book"? Why bother with all that friction when you can just get it done!

Well, that's the very point I am trying to challenge. Friction is not your enemy. Not to be cheesy about it, but I am on the side that these types of conversations aren't a bug. They are features necessary to build robust ideas.

There's a quote from Ken Norton, a PM at Google, that I find myself repeating quite frequently: if product and engineering are always in 100% agreement, one of them is redundant. Disagreement between disciplines is how ideas get stress-tested. Remove the friction, and you remove the audit.

## Engineers have more culture baked into them than most people realise

Software engineers, for all the jokes about their communication skills, have quietly built some of the most sophisticated collaborative cultures of any industry:

* **Blameless post-mortems**: where if something breaks, it's a system failure, not an individual's fault.
* **Documentation as a health signal**: a well-documented codebase is a healthy codebase, even though the docs don't run.
* **CI/CD pipelines**: that let you ship iteratively and roll back when things go wrong.
* **Bus Factor**: the idea that no single person should be so critical that losing them breaks everything.
* **Test-driven development**: where you define what success looks like before you build. (Evaluation-driven development is an interesting topic to mention here.)

These aren't technical practices. They're cultural ones. And they exist precisely because engineers learned, the hard way, that speed without structure creates fragile systems.

And this is where I introduce an idea to ponder: instead of software-as-a-service we pivot to acknowledge ✨software ✨as ✨a ✨culture ✨.

*Sidebar - I have been known to appreciate a catchy phrase, and I believe this one will take approximately two weeks before my friends and colleagues politely ask me to move on to the next one.*

## Becoming a senior engineer is not about how much code you push

Reflecting on my own career, I, alongside many, do not think seniority in engineering is about technical competency alone. It's not about the documentation you've read or the languages you know. It's about the trauma ✌️, the lived experience of migrating a legacy service into something new, watching it go wrong in ways you didn't anticipate, and carrying that with you into every decision you make afterwards. If you've been there, you know what I am talking about.

That kind of knowledge doesn't come from a course or pressing tab for an agent to auto-complete. It comes from other people's past mistakes, and eventually your own. And it's humbling. (Hyrum's law is a great read on the topic)

The brilliance of AI, within the lens of this being a cautionary tale, is that it lets you build like a senior. The technical output looks right. The architecture seems sound. But you don't have the scar tissue. You haven't felt the 2am incident where a deployment took down production. You haven't inherited the codebase that someone built too fast and then left. And so you won't naturally preempt the mistakes that experienced engineers avoid almost on instinct - until the security vulnerabilities surface, until the design starts to crack, until it's almost too late.

This is why the cultural practices matter so much. Blameless culture, documentation, CI/CD, Bus Factor - these aren't bureaucracy. They're institutional memory. They're the way a team encodes its trauma so the next person doesn't have to repeat it.

Prototype with AI so that if you get hit by a bus on the way to work, an intern could pick it up instantly - that's the goal.

Embrace the speed. But do it carefully.

By mid-2025, AI-generated code was introducing over 10,000 new security vulnerabilities per month across studied repositories - a tenfold spike in just six months. Nearly half of AI-generated code contains security vulnerabilities, and 58% of developers admit to trusting AI outputs without testing them (Apiiro). Speed without scrutiny has a long tail.

The LLM is a black box, and you can't see inside it. So your job as a builder is to instrument everything around it. Log your outputs. Monitor your billing. Measure what the model is actually doing. You control the perimeter even if you can't control the interior. The engineering cultural practices above aren't relics but exactly the toolkit you need to ship fast without shipping blind.

## We've been here before

In the nineties, moving from assembly to object-oriented languages felt like cheating to some people. Then Python came along and opened programming to an entirely new wave of people. Data scientists, analysts, people without traditional CS backgrounds and the purists worried again. To be fair as a data engineer, this was a little painful to watch, but also in all honesty, the work got done, and that's what pushes the needle.

## Conclusion

The TLDR on this topic is to embrace your own friction and temper the vibes down a bit. To welcome thinking like a whiny engineer, because odds are, there's a reason for it.

Who knows, if you are lucky enough, you too will gain enough trauma to have the instinct to pivot a micro-service B2C to a monolith B2B 💖

*Benjamin Trollope is a Customer Engineer at Google, based in Berlin. This article is adapted from a talk delivered at the HHL Leipzig Graduate School of Management.*