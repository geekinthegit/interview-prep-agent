# Shared Instructions for Coding Agents

* Before starting work, read the relevant files and check the current state. Do not guess filenames or implementation details.
* Work only within the requested scope. Report issues outside that scope without modifying them.
* Do not unilaterally change established research decisions or methods in the code.
* Do not change [proposed] to [decided] without the user's explicit approval.

## Following and Updating the Workflow

* Before starting work, check the current workflow and progress.
* If new work conflicts with existing information, report the conflict first and confirm the direction with the user. Routine implementation and edits that do not conflict may proceed within the requested scope.
* The workflow is a revisable work plan. When a change is needed, propose the change, explain why, and identify the affected steps.
* After the user approves a change, update the workflow document and proceed accordingly.
* After completing work, update the progress status to reflect the actual work performed.

## Execution Restrictions

* Do not make API calls without authorization.
* If API calls are needed, first report what will be called and how many times. Execute only after receiving the user's permission.
* Test, debugging, and sample calls require the same prior permission.
* Do not run commands that change the environment, including pip install, conda install, or package upgrades.
* If an environment change appears necessary, report the reason and stop.
* Do not modify ~/.zshrc, environment variables, or API key settings without authorization.
* Treat source data as read-only.

## Git Restrictions

* Do not run git commit.
* Do not run git push.
* Do not create or delete branches, merge, rebase, or otherwise make substantial changes to repository state unless requested by the user.
* After completing work, report the changed files and diff. Leave commit and push to the user after their review.

## Code and Validation

* Do not change expected values, assertions, exclusion rules, or validation criteria merely to make tests pass.
* Report validation failures as failures.
* Clearly distinguish checks that were actually run from those that were not.
* If temporary data, mocks, or synthetic examples are used, clearly distinguish them from actual research data.
* Before creating new implementations, check existing code for functions, paths, label mappings, or other components that should be reused.

## File Changes

* Modify only files directly related to the request.
* Do not undertake large-scale refactoring, move or rename files, or reformat entire files without authorization.
* If documentation and code conflict, report the conflict first. Do not decide on your own which one to change.
* Do not add generated files or derived data to Git tracking if they are covered by .gitignore.

## Completion Report

When work is complete, briefly report:

1. Files changed
2. Commands executed
3. Validation performed and results
4. Failures or unresolved issues
5. Issues found outside the requested scope that were left unchanged

Do not commit, push, make API calls, or change the environment without the user's explicit approval.