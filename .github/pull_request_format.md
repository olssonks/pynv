## Commit Message Format
Commits follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) format. Each commit message consists of a **header**, a **body** and a **footer**. Pull requests should also follow this format. gThe header has a special
format that includes a **type**, a **scope** and a **subject**:

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```
## Header
### Types of changes

Types help with automating change logs. Commits without a type are now excepted.
Allowed types are: "build", "docs", "feat", "fix", "revert", "test"
    - build: package and publish new verions
    - docs: Update documention, including docstrings
    - feat: New functionality, e.g. new device, engine, analysis method, etc. 
        Minor version will be incremented 0.x.0
    - fix: Bug fixes. Patch version will be incremented 0.0.x
    - revert: revert to a previous commit
    - test: test some meta-action now relate to the code, like github workflows
        or IDE integration. Does not get noted in change log

### Scope (optional)
Indicate the issue number or part of the code which the commit is
mainly addressing. Try to keep commits to a single scope.

### Subject
Brief statement explaining change, such as "add Blank device".

## Body
Description of the commit, including a summary of the changes with any relevant motivation and context.

## Footer (optional)
The footer section is used to note any breaking commits. Something like adding or 
replacing a library. The footer should read as:
BREAKING CHANGE: specific note of what changes will break.

## Checklist:

- Code follows the project's coding style
- Self-reviewed the code
- Made corresponding changes to the documentation
- Added relevant unit tests to test the changes
- All unit tests pass locally with the changes
- No dependent changes are required to be merged or published