# Git Workflow: Trunk-Based Development

Your git workflow affects your deployment frequency and collaboration.

## Trunk-Based Development

The simplest and most effective workflow.

Rules:
1. Main branch is always deployable
2. Short-lived feature branches (max 2 days)
3. Direct commits to main (or short-lived branches)
4. Feature flags for incomplete features
5. Frequent integrations (daily)

Benefits:
1. Less merge conflicts
2. Faster feedback
3. Easier rollbacks
4. Continuous deployment ready
5. Less ceremony

## Feature Branch Workflow

1. Create branch from main
2. Work on feature
3. Open PR
4. Review and merge
5. Delete branch

Keep branches small (under 400 lines).
Merge at least daily.

## Commit Messages

Good format:
type(scope): short description

feat(order): add payment confirmation email
fix(auth): handle expired tokens gracefully
refactor(users): extract validation logic
docs: add API documentation for orders
test: add integration tests for payments
chore: update dependencies

BAD:
fix bug
update code
changes
asdf

## Code Review Checklist

Before opening PR:
- [ ] Tests pass
- [ ] Linter passes
- [ ] Type checker passes
- [ ] No debug code (prints, breakpoints)
- [ ] Code is self-documenting
- [ ] Error handling is complete
- [ ] Security concerns addressed

## Handling Conflicts

1. Rebase your branch on main
2. Resolve conflicts locally
3. Force push (if you are the only contributor)
4. Notify team of the merge

git checkout feature-branch
git rebase main
git push --force-with-lease

## Git Bisect for Bug Hunting

Find the commit that introduced a bug:

git bisect start
git bisect bad  # current version is bad
git bisect good v1.0  # last known good version
# Git checks out middle commit
# Test and mark: git bisect good / git bisect bad
# Repeat until the faulty commit is found
git bisect reset


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.
