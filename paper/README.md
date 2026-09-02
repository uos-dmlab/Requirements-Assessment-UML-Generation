# Paper

**Automated Requirements Assessment and UML Generation from Natural Language**
Amir Zhumagaliyev, Han-joon Kim
*2026 IEEE/ACIS 24th International Conference on Software Engineering, Management and
Applications (SERA)*, Towson, MD, USA, May 2026.

**DOI:** [10.1109/SERA69989.2026.11618662](https://doi.org/10.1109/SERA69989.2026.11618662)
**ISBN:** 979-8-3195-0657-3 · **ISSN:** 2770-8209

### Abstract

Large Language Models increasingly generate UML diagrams from natural language
requirements, yet current approaches produce diagrams with systematic errors:
hallucinated attributes, over-engineered structures, and anti-pattern violations. Our
analysis of ChatGPT reveals these are predictable patterns, not random failures, stemming
from two root causes: generation uses unconstrained prompts without methodology-specific
guidance, and outputs lack grounding in established diagram notation. We present a
two-stage approach addressing both issues. First, a three-layer validation pipeline
assesses requirements across eight quality dimensions, providing actionable improvement
hints to users. Second, a generator with Retrieval-Augmented Generation retrieves patterns
from official PlantUML documentation, using principled prompts grounded in Larman's and
Cockburn's UML methodology. Evaluation across 15 test cases with 75 generation runs
demonstrates 100% class diagram usability and 96% use case diagram usability versus 87%
and 72% for ChatGPT respectively.

### BibTeX

```bibtex
@inproceedings{zhumagaliyev2026,
  author    = {Zhumagaliyev, Amir and Kim, Han-joon},
  title     = {Automated Requirements Assessment and {UML} Generation from
               Natural Language},
  booktitle = {2026 IEEE/ACIS 24th International Conference on Software Engineering,
               Management and Applications (SERA)},
  address   = {Towson, MD, USA},
  publisher = {IEEE},
  year      = {2026},
  month     = may,
  doi       = {10.1109/SERA69989.2026.11618662},
  isbn      = {979-8-3195-0657-3},
  issn      = {2770-8209}
}
```

### Why there is no PDF here

Copyright in the published article is held by IEEE. IEEE permits authors to post the
*accepted* version on a personal or institutional site with a prescribed copyright notice,
but does **not** permit posting the final published version. The article is available from
IEEE Xplore via the DOI above.

### Supplementary material

Test cases, ground truth, system prompts, the evaluation protocol and per-case results are
in [`../artifacts/`](../artifacts/) and archived at
[zenodo.org/records/19683182](https://zenodo.org/records/19683182).
