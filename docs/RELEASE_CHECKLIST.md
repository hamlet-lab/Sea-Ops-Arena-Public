# Public Release Checklist

Use this checklist before merging or publishing any substantive change.

## Repository origin

- [ ] The change was authored in this public repository.
- [ ] No private commit, branch, tag, tree, patch, or blob was imported.
- [ ] No private repository history was merged, rebased, cherry-picked, or force-pushed here.

## Content boundary

- [ ] The change exposes only public Arena inputs, outputs, scenarios, simulator behavior, or scoring.
- [ ] Proprietary controller implementation remains behind `ControllerAdapter`.
- [ ] No internal state representation is mirrored in public benchmark types.
- [ ] No proprietary policy/governance/admission/commit logic is present.
- [ ] No private architecture, research, patent, or invention material is present.
- [ ] No confidential invariant is disclosed through a test, fixture, example, error message, diagram, or comment.

## Sensitive material

- [ ] Secret/credential scan is clean.
- [ ] Private internal-name scan is clean. The deny-list used for this scan is stored outside this repository.
- [ ] No production endpoint, customer data, raw private trace, prompt corpus, or infrastructure secret is present.

## Semantic review

- [ ] A reviewer considered whether multiple harmless-looking files could be combined to infer proprietary controller internals.
- [ ] Public schemas are benchmark-native rather than copies of private schemas.
- [ ] Public examples are synthetic and do not reconstruct internal workflows.
- [ ] Commit messages reveal no private implementation detail.

## Final diff

- [ ] Full diff reviewed.
- [ ] New and deleted files reviewed.
- [ ] Tests reviewed.
- [ ] Documentation reviewed.
- [ ] Generated artifacts reviewed.

If any item is uncertain, do not publish the detail.
