Title: When Best Practices Meet Reality: A Lesson in Engineering Flexibility
Date: 2024-04-11
Category: Engineering Culture
Tags: engineering-culture, ci/cd, git, github
Slug: CICD-as-an-option


In my journey as a data engineer, I've come to understand that textbook engineering approaches don't always translate perfectly to real-world scenarios. One experience in particular stands out as a profound learning moment that shaped my approach to technical disagreements and team collaboration.

Often times, I must admit it, I have been jealous of backend engineers who have the luxury of working in a world where CI/CD is the norm and where if a crash happens, well.. it's kind of a big deal - money is one the line and customers are impacted.

## Challenge
As the sole data engineer in a nascent three-person data team, I encountered a significant philosophical disagreement with my manager about our CI/CD practices for our dbt repository. Coming from an engineering background that emphasized stability and code quality, I strongly believed we needed proper branch protection and review processes before code could be merged into our main branch.

My manager, who had more experience building data teams from scratch and liked to shoot from the proverbial hit, advocated for a more lightweight approach - allowing direct pushes to the main branch without formal reviews or protection. This approach ran counter to everything I understood about engineering best practices. It created genuine tension between my desire to implement what I saw as proper safeguards and my respect for my manager's experience.

The challenge wasn't just technical but deeply personal: How could I reconcile my engineering principles with a completely different approach? Was I being too rigid in applying textbook solutions to our specific context? The situation forced me to examine whether I was prioritizing engineering ideals over practical needs.

## Action
Rather than digging in my heels or quietly harboring disagreement, I took several deliberate steps:
First, I clearly articulated my concerns about potential risks, explaining specifically how unreviewed code could lead to production issues that might affect our stakeholders.

I used concrete examples from my experience to illustrate the potential problems.
Second, I asked probing questions to understand my manager's rationale. Instead of framing the conversation as a debate to win, I approached it as an opportunity to learn from someone with different experiences and priorities.

Third, I acknowledged the constraints we faced as a small team. We had limited resources and aggressive timelines, which might make formal processes burdensome.
Most importantly, I made a conscious decision to trust my manager's judgment and agreed to try his approach, despite my reservations. I suggested we set clear expectations about reviewing the decision once we had more data about how it worked in practice.

## Solution
The outcome was surprising and educational. Our lightweight approach did indeed allow us to move much faster than a more formal process would have permitted. While we did experience some production issues, they were manageable and less catastrophic than I had feared. The speed and agility we gained proved more valuable at our early stage than perfect stability.

As our team and codebase grew, we gradually introduced more structure - adding some review processes for critical components while maintaining flexibility elsewhere. This hybrid approach emerged organically as we learned what worked for our specific context.
The experience fundamentally changed my approach to engineering decisions. I learned that best practices are guidelines, not commandments, and their application should be tailored to specific circumstances. What works for a large, established engineering team may not be appropriate for a small, rapidly evolving data function.

## Feedback
This experience provided several forms of feedback that shaped my professional development:
Immediate feedback came from seeing our team's velocity increase. We delivered more features and insights faster than I had anticipated, which directly benefited our stakeholders. This concrete result challenged my assumption that formality always leads to better outcomes.

Self-reflection revealed how my attachment to certain practices was partially rooted in my identity as an engineer rather than objective analysis of our needs. This awareness has made me more open to questioning my assumptions in other areas.
My relationship with my manager strengthened through this disagreement. By showing that I could prioritize team success over being right, I built trust that has led to more meaningful collaboration on subsequent decisions.

Most significantly, I gained a more nuanced understanding of engineering excellence. I now recognize that truly good engineering isn't about rigidly applying best practices, but about making thoughtful tradeoffs that balance immediate needs with long-term considerations.

Today, when faced with similar decisions, I approach them with both principles and pragmatism, understanding that context matters enormously. I've learned to evaluate engineering choices not just by their technical merits but by how well they serve the broader goals of the team and organization. This balanced perspective has made me a more effective engineer and collaborator, capable of both advocating for good practices and adapting to the realities of each unique situation.
