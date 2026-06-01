# Building a Code Review Culture

Good code reviews are the highest-leverage activity in software engineering.
One review can prevent bugs, teach patterns, and raise standards.

## The Goal of Code Review

Not finding bugs in code. That is a side effect.
The real goals are:
1. Share knowledge across the team
2. Ensure consistent quality and patterns
3. Catch design issues early
4. Build shared ownership
5. Mentor junior engineers

## For the Author

### 1. Make Your PR Easy to Review

- Keep PRs small (under 400 lines)
- Write a clear description (what, why, how)
- Reference issues and design docs
- Add comments on tricky parts

### 2. Respond to Feedback Gracefully

- Thank reviewers for their time
- Explain your decisions, dont defend them
- If you disagree, discuss in person
- Make requested changes quickly

### 3. Dont Take It Personally

The code is being reviewed, not you.
Every comment is an opportunity to improve.

## For the Reviewer

### 1. Review in Layers

1. Does the PR do what it says? (5 seconds)
2. Is the design right? (30 seconds)
3. Is the code correct? (2 minutes)
4. Are there edge cases? (1 minute)
5. Is the code testable? (30 seconds)

### 2. Write Helpful Comments

BAD: "Fix this"
GOOD: "This query does N+1 requests. Use a JOIN or batch query instead.
The user list endpoint is called 100 rps, so this matters."

BAD: "Use async/await"
GOOD: "This HTTP call blocks the event loop for 100ms.
At 50 rps, this adds 5 seconds of blocking per second.
Use httpx.AsyncClient with timeout."

### 3. Focus on What Matters

Prioritize:
- Correctness (will this break?)
- Security (can this be exploited?)
- Performance (will this scale?)
- Maintainability (can we change this later?)

Dont nitpick:
- Formatting (linters handle this)
- Style preferences (agree as a team)
- Trivial nits

## PR Size Matters

PRs under 200 lines: thorough review, quick turnaround.
PRs 200-400 lines: decent review, some fatigue.
PRs 400+ lines: superficial review, bugs slip through.

Keep PRs small. Review more often.

## Review Velocity

Review within 4 hours during work hours.
If a PR sits for days, the author context-switches.
Fast reviews = fast feedback = fast delivery.

## When to Approve

Approve when:
- You understand the code
- It is architecturally sound
- It handles errors properly
- It has tests
- It is secure

Dont block on:
- Style preferences
- Perfect solutions
- Things you can fix yourself

## Building the Culture

1. Set expectations: review within 4 hours
2. Rotate reviewers: everyone reviews everyone
3. Celebrate good reviews: "great catch!"
4. Review design docs before code
5. Make review part of onboarding


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.


## Practice

Apply this lesson today.
