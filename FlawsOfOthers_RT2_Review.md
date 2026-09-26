# Second-order red-team review (RT2) of the *Discursive Networks* red-team review

**Document audited (RT1):** [FlawsOfOthers_RedTeam_Review.md](FlawsOfOthers_RedTeam_Review.md), dated September 25, 2026
**Manuscript under RT1's review:** [FlawsOfOthers.tex](FlawsOfOthers.tex) and [FlawsOfOthers.bib](FlawsOfOthers.bib)
**RT2 date:** September 26, 2026
**Verdict:** Adopt RT1, with the amendments below. All 20 of RT1's diagnoses hold, and every number it reports reproduces. However, RT1 is materially incomplete in ten places. In several of them, an author who followed its remediation and passed its completion checks would still submit a false or unsupported claim.

## Scope and method

RT1's stated checksums still match the files on disk, so its line references are valid:

```text
FlawsOfOthers.tex                F7137D7B7FC536F6478D6163E991BE966B13DA995DAA02D8897153A15ECCDB0A
FlawsOfOthers.bib                B43CC0DD5790A5D2EFE544E28C2C5459578670EE9DB322004F4030F9DF66B21F
FlawsOfOthers_RedTeam_Review.md  2D8F77CE7AB445605232D95075AB28152CC7A069A0783AEA858878F64C1E3DB6
```

In this document, "RT1 line N" means a line of the RT1 review, "tex N" a line of the manuscript source, and "bib N" a line of the bibliography.

The audit ran as 24 independent investigations. There was one for each RT1 item and four whole-document sweeps: RT1's internal consistency, a fresh mathematical read of the manuscript, a non-mathematical gap search, and the coherence of the remediations as one program of work. A separate skeptic re-checked each investigation and was instructed to refute its findings. Only findings that survived that pass are reported, at the severity the skeptic assigned. Where skeptic passes disagreed, I adjudicated from primary sources. The load-bearing new claims were then spot-checked directly: git tags and history, the cited manuscript lines, the bibliography fields, and the key recomputations.

The checks covered:

- recomputing every number in RT1 in Python;
- re-running RT1's reproduction command into a scratch directory;
- transcribing the appendix logging algorithms and attacking them;
- checking bibliography records against Crossref, arXiv, the ACL Anthology, and the doi.org handle service;
- searching the git history of the cited repository across all branches and tags.

No project file was modified.

Severity scale:

- **Critical:** following RT1 would leave or introduce an error in a headline result. No critical deficiency was found.
- **Major:** materially incomplete or misleading. A compliant revision would still contain a false or unsupported claim, or RT1's check would not detect the flaw.
- **Minor:** imprecision that a careful author would still want fixed.

## What RT1 got right

Every quantitative claim in RT1 reproduces exactly:

| RT1 claim | Recomputed |
|---|---|
| R01 counterexample: λ/d = 0.5 < p/(p+q) = 0.9, yet f* = 0.95/1.15 | 19/23 = 0.826087 |
| R01 illustrative case: 0.289474 < 0.285714 is false, yet one-peer rate f* | 5/21 = 0.238095 |
| R01 unclamped n_min at a=.01, q=.5, d=.05, ε=.5 | ⌈−8.8⌉ = −8 (clamped: 1) |
| R02 delivered error with rejection | 0.10/0.18 = 55.56% |
| R03 f₉ (rate) and Pr(Binomial(1000, f₉) ≥ 51) | 15/329 = 0.0455927; 0.2253222 |
| R05 net-benefit condition hb < aΔb | exact; 0 mismatches in 200,000 random draws |
| R06 generate-then-review fixed point, and its value at b=1 | a(1−b)/[b+a(1−b)]; 0 |
| R08 agents for a 1% expected target (rate branch) | 40 (39.8158 unrounded) |
| R10 terminal means for both scripts, the CI, the run interval, and the width ratio | all match; ratio 32.01 |
| R13 four attacks against a faithful transcription of the appendix | all four return VERIFIED |
| R15 literal call count for three rounds with three agents | 21 (versus the manuscript's 12) |
| R17 corrected records for the three named entries | confirmed against arXiv, Springer, and Crossref |
| R20 s=1, ρ=1, one critic gives α_out = αc; d=0 and d=1 raise errors | confirmed |

RT1's reproduction command regenerates all four CSVs byte-identically. The shipped PNGs are byte-identical to the regeneration, and the PDFs differ only in Matplotlib's `CreationDate`. This confirms RT1's advice to compare CSVs rather than PDFs. None of RT1's twenty diagnoses was refuted, and every priority assignment was judged defensible.

## Summary

| RT1 item | Diagnosis | Remediation | Most important RT2 amendment |
|---|---|---|---|
| R01 | Confirmed | Sound | Qualify the "approaches zero" limit and extend coverage to tex 1300–1301 and 1322 (minor) |
| R02 | Confirmed | **Deficient** | Missed the unhedged instance at tex 329–331; state the exact worsening criterion (**D1**) |
| R03 | Confirmed | Sound | A marginal tail bound does not control risk over a horizon; add "expected" consistently (minor) |
| R04 | Confirmed | **Deficient** | Option 2 silently destroys the corollary's αc floor (**D2**) |
| R05 | Confirmed | **Incomplete** | Harm is not carried into agent-count sizing; the replacement text omits it (**D3**) |
| R06 | Confirmed | Sound | Use the stronger finite-n counterexample; widen the phrase search (minor) |
| R07 | Confirmed | Sound | The completion check does not test that claims were narrowed (**D4**) |
| R08 | Confirmed | Sound | The "exact vs approximate" check already passes on the unrepaired manuscript (minor) |
| R09 | Confirmed | Sound | Add tex 1856 and 1939–1941; the "a and b only" branch needs q and d separately (minor) |
| R10 | Confirmed | Sound | Legacy scripts and HEAD PNGs; d=0.19 was derived from the false criterion (minor) |
| R11 | Confirmed | Sound | Evidence understated: the tagged engine exists, but asyncio and hash-chain code exist in no revision (**D5**) |
| R12 | Confirmed | Sound | Completion check misses failure paths; its unanimity clause is vacuous (minor) |
| R13 | Confirmed | Sound | Check misses canonical serialization, per-agent chain omission, and migration laundering (**D6**) |
| R14 | Confirmed | Sound | "Decentralized / without central oversight" at tex 1848 is unaddressed (minor) |
| R15 | Confirmed | Sound | Backward-pass claim contradicts tex 182; the check would not catch it surviving (minor) |
| R16 | Confirmed | **Incomplete** | Missed a wholly unsupported citation inside its own range; scope covers numbers only (**D7**) |
| R17 | Confirmed | **Deficient** | At least 11 more defective entries; the audit method cannot detect coauthor errors (**D8**) |
| R18 | Confirmed | **Incomplete** | Overlooks the manuscript's existing formal predicate at tex 356–363 (**D9**) |
| R19 | Confirmed | **Incomplete** | Novelty is compared only against predecessors the manuscript already cites (**D10**) |
| R20 | Confirmed | Sound | The check verifies that outputs are defined, not that they are correct (minor) |

## Major deficiencies

### D1 (R02) — The strongest instance is missed, and the counterexample is easy to dismiss

**What RT1 misses.** R02 cites tex 545–625 and 1201–1209 and says "Later prose calls it 'delivered invalidity.'" The sharpest instance of the flaw comes *before* the theorem, in the Methods overview at tex 329–331:

> "discursive networks reduce delivered invalidity when critics detect a nonzero fraction of non-common-mode errors and flagged errors are successfully repaired or rejected."

This sentence carries no false-positive qualifier. RT1's own example satisfies it word for word (δ=.5 > 0, ρ=1, rejection), and delivered error still rises from 20% to 55.56%. By contrast, the two instances RT1 does cite are hedged: tex 620 adds "false-positive burden is manageable" and tex 1206 adds "acceptable." A repair confined to RT1's locations therefore leaves the one falsified headline sentence in place.

**Why the evidence is weaker than it needs to be.** RT1's example has flag precision 5/41 = 0.122, below the 20% base rate, and a false-positive burden of 0.72 per claim. Its flags are evidence that a claim is *valid*, so an author can dismiss the example as pathological and as excluded by the hedges. RT1 also never states the exact condition for harm. Under any policy that rejects flagged claims (ρ > 0), delivered error exceeds α exactly when

```text
η_m > (1−c)·δ_m     ⇔     flag precision < α.
```

The condition does not depend on ρ. It also shows that the manuscript's hedge regulates the wrong quantity: the absolute burden (1−α)η_m matters less than η_m relative to (1−c)δ_m. A realistic counterexample uses an informative critic with a large shared blind spot: α=.1, c=.9, δ=.9, η=.2. The burden is a modest 0.18, yet delivered error is 11.22% against 10% baseline, with coverage 0.811. This defeats the hedged sentence at tex 1204–1207 as well.

**Formula scope.** RT1's coverage and delivered-error formulas (RT1 lines 83–88) silently assume ρ=1, but the remediation offers them "for any rejection policy." The general forms are

```text
coverage  = 1 − ρ[αD + (1−α)η_m],   D = (1−c)δ_m
delivered = α(1 − ρD) / coverage
```

On RT1's own parameters with ρ=.8, these give coverage 0.344 and delivered error 34.9%, not 0.18 and 55.6%.

**Amendment.**
- Add tex 326–333 to R02's locations.
- Require all three "reduces delivered invalidity" sentences (tex 330, 620, 1204) to be rewritten with the precision criterion above and with coverage reported alongside.
- Replace RT1's example with, or add, the informative-critic example.
- State the ρ-general formulas.
- Replace the completion clause "the example above must no longer be described as improved" with an executable test: every surviving "delivered" claim names its denominator, and none implies improvement when η_m > (1−c)δ_m.
- Define "task completion" or drop the term. It appears once in RT1 and is never defined.

### D2 (R04) — Option 2 invalidates the corollary, and nothing warns the author

RT1 offers two ways to define a common-mode blind spot. Option 1 declares the blind class always missed. Option 2 introduces κ_m = Pr(any flag | E=1, U=1). RT1 then says only "choose one and propagate it." The options are not interchangeable. Option 1 leaves the theorem, the corollary, and all the "replicas cannot overcome shared blind spots" prose exactly correct.

Option 2, under the common removal probability ρ that RT1's own formulas use, erases the αc floor entirely. Blind critics that flag at random still get their flagged claims rejected. Take α=.2, c=.3, s=.5, per-critic blind-flag probability .1, and ρ=1. The residual invalidity is 0.124 at m=1, 0.0398 at m=5, and 0.00031 at m=50. From m=5 onward this is below the corollary's supposedly unreachable floor αc = 0.06, and it tends to zero. The corollary's "attainable only if ε > αc" (tex 588–601) and the introduction's "cannot overcome shared blind spots merely by adding more replicas" (tex 331–333) would then be false.

RT1's completion check only asks that three cases be "included." An author could add κ_m, keep tex 598–601 verbatim, and pass.

**Amendment.** State that Option 1 is the minimal fix. Option 2 requires class-dependent removal: a blind flag may trigger rejection but not informed repair, so ρ_blind must be modeled separately. Otherwise the corollary and tex 329–333 and 618–625 must be rewritten. Add to the completion check that, under the chosen definition, the corollary's attainability condition is re-derived and α_out(m) is tested against αc for large m.

The case labels in the check are also ambiguous. It asks for a "random-flag blind-spot case" that Option 1 excludes by definition, and "zero-flag case" versus "always-missed case" is never defined. Restate the check as: the paper states Pr(any flag | E=1, U=1) explicitly, and gives precision only for a positive denominator.

### D3 (R05) — The harm channel is not carried into agent-count sizing

R05 correctly derives the single-channel criterion hb < aΔb but never applies it to the headline result it most affects. Suppose each added peer introduces errors at rate h. The rate-model share becomes

```text
f(n) = (a + (n−1)h) / (a + (n−1)h + q + (n−1)d),   with floor h/(h+d).
```

A target ε is attainable only if h < εd/(1−ε), which is 0.0100 at the illustrative d = 0.19. The harm-adjusted count is

```text
n_min = 1 + ⌈[a(1/ε−1) − q] / (d − (1/ε−1)h)⌉,   valid when d > (1/ε−1)h.
```

At the illustrative parameters, the nine-agent 5% result becomes 11 agents at h=.002, 16 at h=.005, and unattainable at h=.01, which is 5% of d. At h=.01, nine agents give 9.0%.

RT1's list of limitations to "carry into every sizing discussion" (RT1 line 182) names only the Bernoulli and common-mode limitations. Its replacement agent-count paragraph (RT1 line 348) names only "independent correction capacity that remains constant per added peer." An author who pastes RT1's text would ship a sizing claim that does not disclose its most fragile assumption.

**Amendment.**
- Add the harm-adjusted formula and floor to R05.
- Add "no errors introduced by review, repair, or harmonization (h=0)" to R08's sizing list and to the replacement paragraph.
- Add tex 1201–1209 to R05's locations. Tex 1204–1206 restates the theorem's sufficiency conditions for the whole algorithm and drops the harmless-repair hypothesis.
- Make R05's "measure …" instructions conditional on retaining end-to-end effectiveness claims. As written they conflict with R11's explicit allowance for a theory-only revision.

### D4 (R07) — The completion check does not test the narrowing it prescribes

R07's headline is that "claims about propagation, network structure, and prediction are … broader than the actual derivation," and it orders "limit the title/contribution language accordingly." Its completion check tests only two things: that each quantity has a unit and a mapping to a FOO run, and that graph invariance is either demonstrated or acknowledged.

A revision that adds one limitation sentence passes both clauses, while these survive verbatim:

- the title "A Mathematical Theory of Discursive Networks" (tex 63);
- "actors as nodes in a network, with edges" (tex 631);
- "we can analyze and predict how invalidation affects … statements among actors in the network" (tex 654).

The symbol-separation instruction is not checked either. The overloading is also wider than RT1 says:

- **S** is the statement set (tex 640), the state space {r, f} (tex 693), and the invalid output set (tex 363).
- **N** is the network tuple (tex 638) and the tracked-item count (tex 1577).

R07 is also the only P1 item with no bullet in RT1's submission checklist.

**Amendment.**
- Add to the check: every propagation, prediction, or network-structure statement, including the title and contribution paragraphs, either follows from a derived coupled model or is explicitly scoped to the exogenous-rate two-state abstraction.
- Require that no symbol carries more than one of these meanings: actor count, tracked-item count, subnetwork count, agent count, statement set, state space, or invalid set.
- Add an R07 checklist bullet.

### D5 (R11) — The repository evidence is understated in both directions

RT1 treats the cited URL as a separate, unversioned link and hedges that this is "not proof that no implementation exists elsewhere." Two facts it did not establish change what the author should do.

1. **The cited URL is this package's own repository.** `origin` is `github.com/biomathematicus/FOO`, the remote HEAD equals the local HEAD (`a4b7601`), and the repository has two tags, `CGSI25` and `v0.1`. The `CGSI25` prerelease (commit `c1e6bd0`, July 2025) contains a candidate orchestration engine that was later removed from HEAD: `cls_foo.py`, `cls_openai.py`, `cls_anthropic.py`, `multillm.py`, `foo_gui.py`, and a `config.json`. That configuration matches the appendix's agent pool: one harmonizer plus specialists at temperatures 0.1 and 0.9 for OpenAI and Anthropic. Pinning that tag would satisfy RT1's "publish and identify" branch for the critique-and-harmonize loop without new work.
2. **No revision contains the asyncio or integrity-logging implementation.** Searching every commit on every branch and tag (`git log --all -S`) finds zero commits that add or remove `asyncio`, `hashlib`, `blockchain`, or `GENESIS` in any `.py`, `.json`, or `.ipynb` file. The claims of "Python 3.11 with asyncio concurrency" (tex 2015), verification on load with warnings (tex 2081), and per-agent chains with automatic migration (tex 2083) therefore describe software that does not exist at the cited location in any version. These are false as written, not a traceability gap.

**Amendment.** Replace RT1's hedge with these facts. Direct the author to pin `CGSI25`, or a successor commit, for the loop. The asyncio and logging-behavior sentences must either be deleted or backed by a published revision before any R13 or R14 claim is retained. Two smaller fixes: add a completion criterion for the review-log manifest that R11's remediation requires but its check never tests, and make the check's first sentence explicitly conditional on retaining implementation claims.

### D6 (R13) — The test battery misses three ways to rewrite history

RT1's remediation for the logging appendix is cryptographically sound. Its completion check, however, would pass a revision that is still exploitable.

1. **Missing canonical serialization.** The appendix hashes undelimited concatenations (h_c = H(m ‖ t ‖ σ), tex 2045). Moving bytes across a field boundary leaves the hash input identical. For example, the message "The dose is 1" with timestamp "2026-09-26T12:00:00Z" becomes the message "The dose is 12" with timestamp "026-09-26T12:00:00Z". The tampered chain returns VERIFIED, and its head still equals a trusted checkpoint. The attack needs no salt. RT1's own added fields collide the same way: sender‖receiver "alice"+"bob" equals "alic"+"ebob". A byte-modification test as usually written changes the hash input, is detected, and gives false confidence.
2. **Per-agent chains.** Tex 2083 says the implementation "maintains separate blockchains for each agent," which contradicts the single log in Algorithm `algo:foo-blockchain` (tex 1331). RT1 never mentions tex 2083. Dropping an entire agent's chain leaves every remaining chain verifying against its own checkpointed head. That removal of one party's contributions is exactly the attribution attack tex 2085 claims to prevent. The manuscript's own anchoring subsection (tex 2005–2007) already names the fix: a Merkle root over the heads.
3. **Migration laundering.** Tex 2083 says existing logs are "automatically migrated" into the chain. An edited legacy log becomes VERIFIED after migration, under both the appendix verifier and RT1's checkpointed verifier.

RT1 also does not make these points:

- The truncation, empty-log, and genesis attacks need no salt. Only fabrication and suffix rewriting do, and the salt cannot be kept secret, because the verifier requires it as input (tex 2061) and it sits in the system configuration (tex 2083). Anyone able to verify can forge.
- The appendix contradicts itself. Tex 2010–2012 correctly says a local chain is "tamper-evident under comparison to a stored head, not … tamper-proof," yet tex 2081 claims "computationally infeasible."
- The refuted claim reappears in the main text: "computationally infeasible to fabricate authorship claims" (tex 1779), "any tampering … invalidates the entire subsequent chain" (tex 1848), and "cryptographic integrity verification" (tex 101).
- Tex 1379–1381 says the construction "becomes a blockchain only if" it is distributed or anchored, yet the appendix calls itself a blockchain throughout.
- σ means a signature at tex 1383–1389 and a global salt at tex 2035 and 2042.

**Amendment.** Add the following to the completion-check list:

- an injectivity test: moving bytes across field boundaries must be rejected;
- omission of an entire agent chain;
- migrated-record status, which must be distinct from VERIFIED.

Also make these changes:

- Require one sequence-numbered run log, or a checkpoint that commits to all agent heads.
- Add tex 101, 1779, and 1848 to R13's locations.
- Replace the keyword search with a semantic one that keeps the correct negation at tex 2012.
- Require "tamper-evident log" terminology unless anchoring or consensus is implemented.
- Rename the salt symbol.

### D7 (R16) — A wholly unsupported citation inside RT1's own range

RT1 audited tex 279–302 but missed its worst miscitation. Tex 289–292 reads:

> "Research on social-media communities finds that clusters organized in bow-tie topologies … amplify low-quality or misleading messages more than high-quality ones \parencite{garimella2018}."

The full text of Garimella et al. (WWW 2018, arXiv 1801.01665) studies echo chambers, gatekeepers, and the price of bipartisanship on political Twitter. It contains no occurrence of "bow," "amplif," "misleading," or "misinformation." "Low-quality" appears only in a reference title. This sentence is the manuscript's only evidence for the amplification step of its spillover argument.

It escaped because RT1's claim-to-source table covers only "every quantitative sentence," and this sentence has no number. The same scope gap leaves two other sentences unexamined:

- The line-95 sentence "studies have shown that LLMs can generate false information even when explicitly prompted to be truthful" cites `evans2021truthful`, a governance agenda rather than an empirical study.
- The line-95 "up to 30%" figure also cites `ji2022survey`, which RT1 never examined. The survey reports only task-specific figures, such as 25% of summaries from three summarization systems and 74% of QMSum samples, and no universal rate. Together with TruthfulQA's best-model 42% untruthful share, both cited sources contradict "up to 30%" as an upper bound, not just its universality.

**Amendment.**
- Add a sixth R16 bullet for the Garimella sentence: delete it or cite a source that measures quality-dependent spread.
- Widen the table from "every quantitative sentence" to "every empirical attribution, quantitative or qualitative."
- Add the ji2022survey finding and the evans2021truthful attribution to bullet 1.

A few smaller points:

- RT1's GLTR example refutes a "moderation performance law," but in the manuscript GLTR supports the reader-identification range at tex 281, not the moderator claim at tex 300. GLTR's unassisted 54% falls below the manuscript's own 55–65% range.
- `tufts2024practical` reports TPR at a fixed FPR, not accuracy, so it cannot support "below 80% accuracy" (tex 297).
- Tex 232 ("billions of documents … thousands of times") is uncited.
- Tex 1827–1830 extrapolates a single-model result to propagation across a network.

### D8 (R17) — The bibliography audit is materially incomplete, and its method cannot find the errors

RT1 presents three entries as the "confirmed" defects. Two independent audit chains, checked against Crossref, arXiv, the ACL Anthology, and the doi.org handle service, confirm at least eleven more defective entries among the 73 rendered references. Most are the same class as RT1's.

| Entry (bib lines) | Defect | Correct record |
|---|---|---|
| `weidinger2021ethical` (80–86) | Invented coauthors (Michalewski, Everitt, Bakker, Chadwick); "Matthias" Rauh and "Christopher" Griffin; second author Mellor omitted | arXiv 2112.04359 (23 authors; Maribeth Rauh, Conor Griffin) |
| `ippolito2020` (378–385) | "Dani" Ippolito; invented Matt Stevens and Noah Fiedel; Duckworth omitted. Supports the 65% claim RT1 audited | Daphne Ippolito, Daniel Duckworth, Chris Callison-Burch, Douglas Eck, ACL 2020 |
| `park2023generative` (449–459) | Invented "Yang Li"; CHI '23, pp. 1–18 | UIST '23, pp. 1–22, six authors |
| `leifeld2014` (349–358) | *Policy Studies Journal* 42(3):465–487 matches no record; the DOI is an Oxford Handbook chapter | Oxford Handbook of Political Networks chapter, DOI 10.1093/oxfordhb/9780190228217.013.25 |
| `cohen2001states` (18–25) | DOI 10.1086/343211 resolves to a 2002 book *review* in AJS | Polity Press book; drop the DOI |
| `huang2025survey` (153–) | "ACM Computing Surveys" | ACM Transactions on Information Systems 43(2), DOI 10.1145/3703155 |
| `tufts2024practical` (482–490) | "ACL 2024," but the preprint is from December 2024 | Findings of NAACL 2025, pp. 4839–4856 |
| `maruvsic2011systematic` (535) | DOI lacks the `10.1371/` prefix; renders a dead link | 10.1371/journal.pone.0023477 |
| `castro1999pbft` (942) | Pseudo-DOI 10.5555/… returns 404; cited in the anchoring appendix | Remove the DOI; keep the USENIX OSDI '99 URL |
| `wei2022chain` (317–322), `bommasani2021opportunities` (292–298) | `and et al.` is parsed as a real author; renders "Jason Wei and et al." | Full author lists (Wei et al.: nine authors, NeurIPS 35) |
| `reynolds2021prompt` (325) | "McDonell, T." | Kyle McDonell |
| `bender2021dangers` / `Bender2021Parrots` | The same FAccT 2021 paper under two keys, rendered twice; one says "Shmitchell, Margaret" | Merge into one entry; byline "Shmargaret Shmitchell" |
| `Ji2023SelfReflection` (332–339) | arXiv title with the EMNLP Findings DOI | Use the Findings title with that DOI |
| `goffman1959presentation` (5) | "Woddstock, NY" (renders) | Woodstock, NY |

There are also preprint-versus-published mismatches that R17 names as a category but never lists: `huang2024robust`, `Zhang2024SelfAlignment`, `mundler2023selfcontradiction`, and `hoppe2025deductive`.

R17's remediation would not find these, for three reasons:

1. **Scope.** "Extend this identity audit to the load-bearing references in R16" reaches only entries cited at tex 95, 122–124, 190–200, and 279–302. Most defects above are cited elsewhere (tex 91, 128, 214, 228, 272, 1777). RT1's global checklist line 374 is broader than its own instruction, so the two conflict.
2. **Method.** "Manually compare rendered author lists" cannot work. The preamble leaves `maxbibnames` at its default, so every entry with more than three authors renders as "First et al." The PDF prints "Owain Evans et al." and "Arun James Thirunavukarasu et al.", which hides even RT1's own two coauthor defects.
3. **Duplicate check.** "No duplicate keys" guards a real risk: Biber keeps the first of any duplicate keys, so importing a corrected record under the old key could leave the wrong entry in force. But the check cannot catch the same work rendered under two different keys.

**Amendment.** Replace R17's scope with a full-bibliography audit of all 73 rendered entries, importing fields from Crossref, arXiv, or DBLP and comparing the `.bib` source field by field. Do not compare rendered strings. If a rendered check is wanted, build once with `maxbibnames=99`. Add a duplicate-DOI and duplicate-title check across keys. Add a DOI-resolution sweep that resolves each DOI, not just checks its syntax.

### D9 (R18) — RT1 overlooks the manuscript's existing formal validity predicate

R18 tells the author to "define a task-, context-, and standard-dependent predicate C(x; …)," as if none exists. The manuscript already defines one formally at tex 356–363: "a measurable validity predicate C: Ω → {0,1}, where C(x)=1 means that x satisfies the relevant standard," with invalid set S = {x : C(x)=0}. The KL floor lemma (tex 379–408) is stated for that standard-relative invalid mass.

Meanwhile, four other passages equate invalidity with falsity:

- tex 134: "fails to match a state of the world";
- tex 640: each statement "can be either true or false";
- tex 695: "r denotes a valid or true state and f denotes an invalid or false state";
- tex 1856: λ as "the production of false statements."

The flaw is therefore sharper than vague prose. The formal lower bound and the two-state dynamics refer to different events. Followed literally, RT1's remediation could leave two competing predicates in the paper instead of reconciling them.

The completion check also fails to test the half of R18 that its title states: "remove unsupported identity claims about cognition." Its only relevant clause targets the softmax sentence. An author could delete that sentence and pass while "manifest identically in biological neural networks and artificial transformers" (tex 234), "operates identically whether the medium is television, print journalism, or a large language model" (tex 230), "the same reality-distortion mechanisms" (tex 232), and the section heading "Invalidation as a Universal Feature of Human and Artificial Cognition" (tex 222) all survive.

**Amendment.**
- Change "define a predicate" to "extend the existing C at tex 356–363 to C(x; task, evidence, policy, time)." The state f and tex 134, 640, 695, and 1856 must then refer to that same predicate, or state explicitly that f aggregates C=0 across categories.
- Add completion bullets: the invalid set in the KL lemma and the state f are defined by the same predicate; and no passage in tex 222–248 asserts identity or sameness of mechanism between human cognition and model operations without direct evidence.
- Extend R18's range to tex 222 and 695.

### D10 (R19) — The novelty comparison lets the author choose the reference set

R19's remediation asks for "a compact comparison against the already cited nearest approaches," and its check asks that the contribution "survive comparison with its own cited predecessors." A novelty check whose reference set is chosen by the author cannot detect a novelty overclaim.

Closer uncited prior art exists. Xu et al. (2023), "Towards Reasoning in Large Language Models via Multi-Agent Peer Review Collaboration" (arXiv 2311.08152), has each agent produce a solution, review the others' solutions, and revise on receiving peer reviews. That is essentially the claimed "configurable loop in which any set of agents critique one another" (tex 77; "introduced" at tex 193 and 1844). Self-Refine (Madaan et al., 2023) is also uncited: tex 484 names "self-refinement," but the citation list at tex 486 contains no self-refinement paper. The `.bib` has no entry for either.

Other gaps in R19:

- **Line-266 sub-point.** RT1 raises the "passive conduit" contrast (tex 266) in its evidence but not in its remediation or completion check. The point is stronger than RT1 makes it: the manuscript's own source for the term, Kittler's *Discourse Networks 1800/1900* (`kittler1990`), treats media as active.
- **Epithesis definitions.** The abstract (tex 77) defines epithesis as occurring "when humans fail to engage in the discursive network," while the body (tex 1759–1760) defines it as seeking "authorship on an artifact to which they have contributed only superficial edits, or none at all." RT1 never cites tex 77, and its replacement abstract silently drops epithesis, which hides the inconsistency rather than resolving it.
- **Order of discussion.** RT1 reverses the manuscript's order. Tex 1755 names outsourced reasoning first, and the narrower epithesis definition follows.
- **Taxonomy claim.** The claim to "introduce" a three-category taxonomy (tex 188) is not addressed anywhere in RT1.
- **Moral-responsibility directive.** "Separate analytic roles for human and software nodes from moral responsibility" has no supporting evidence in R19. Its likely target is tex 77 ("treats people and LLMs as equal nodes") together with tex 1771–1779.

**Amendment.**
- Change the comparison to "the nearest prior work identified by a documented literature search, including uncited work," and cite what the search finds.
- Require a single definition of epithesis used identically in the abstract, the roadmap, and the ethics section.
- Add remediation for tex 188 and tex 266.

## Minor deficiencies, by item

**R01.**
- *Zero limit.* The sentence RT1 targets continues: "decreases monotonically with n and approaches zero in the limit" (tex 1875–1877). If the Bernoulli condition is substituted literally, this clause becomes false: the Bernoulli limit is a/(a+1) = 0.069767, and any common-mode fraction c > 0 also leaves a positive floor.
- *Monotone decrease.* Decrease in n holds whenever d > 0, in either regime, so it is not a property of truth dominance.
- *Missed locations.* Tex 1322 ("pushes the system into the truth-dominant regime predicted by the theory") and tex 1300–1301 ("an error overlooked by one model is likely to be flagged by at least one other") lie outside R01's locations and search terms.
- *Fix.* Add "truth-dominant," "approaches zero," "as soon as," and "λ>q" to the search, and route tex 1300–1301 to R04.

**R03.**
- *Locations.* Add the subsection heading "How Many Agents Guarantee a Target Falsehood Level?" (tex 1092), tex 1687–1737, and the conclusion's "right-sizing … prescribed levels of factual reliability" (tex 1881–1902).
- *Completion check.* It presupposes the optional guarantee branch; make it conditional.
- *Horizon risk.* The binomial-tail sizing rule bounds only a single snapshot. In a per-item continuous-time simulation, n=11 passes a per-snapshot 5% tail (0.015) but exceeds 5% at some point in 101 unit-time snapshots with probability ≈ 0.78. A horizon-wide guarantee needs about 14 agents.
- *Stochastic model.* The 22.5% figure assumes independent per-item continuous-time chains, which the manuscript never specifies for the rate branch. At n=9, b = 1.57 is not a valid Bernoulli probability. State where N=1000 comes from (tex 1601), and note that the exceedance probability is non-monotone in N: 0.40 at N=50, 0.225 at N=1000, and 0.017 at N=10,000.
- *Replacement text.* Add "expected" to the Bernoulli half of the agent-count paragraph.

**R06.**
- *Stronger counterexample.* RT1 relies on the b=1 idealization, which an author can dismiss. With realistic bounded detectors under generate-then-review, five agents meet the 5% target: b₅ = 0.5911 gives f* = 0.0493, while n=4 gives 0.0710. This directly falsifies tex 1667–1668 ("No one-round Bernoulli system can achieve this target").
- *Locations.* The only occurrence of "unattainable" is at tex 1149, outside R06's locations. The completion check's word search would miss tex 1667–1668 and 1733–1735 ("no matter how many").

**R08.**
- *Vacuous check.* "Exact versus approximate expressions are labeled" is already satisfied by the unrepaired manuscript, which labels expressions throughout. Reword it: no expression labeled exact may combine a = p+λ with an independent-channel b.
- *Bernoulli 1% target.* The Bernoulli branch cannot reach 1% at any n (B_ε = 7.425 ≥ 1; the floor is 6.98%). The check should require saying so next to the rate-branch 40.
- *Locations.* Add the parameter table (tex 1438–1498) and the agent-count section (tex 1637–1746).
- *Convention.* Note that the preserved values 0.2455 and 6.98% presuppose the declared additive convention (tex 1462–1467). The independent-channel mapping gives 0.2428 and 6.88%.

**R09.**
- *Tex 1856.* This is a second benchmark-to-λ claim, and it assigns "chain-of-thought drift" to λ even though tex 847 defines drift as p.
- *Tex 1939–1941.* A/B tests on unlabeled production traffic cannot recover hazards under RT1's own observation requirements. Widen the check beyond "benchmark shortcuts in the conclusion."
- *"Estimate only a and b."* This branch cannot support n_min, which needs q and d separately. A two-agent b = 0.24 arises from (q, d) = (0.05, 0.19), (0.14, 0.10), or (0, 0.24), which give n_min = 9, 14, and 7.

**R10.**
- *Generator name.* The completion check never verifies that tex 1601 and 1744 now name the canonical generator.
- *Agent-count figure.* Its caption (tex 1714–1721) is not cited. Under `interval=both`, that figure shows Monte Carlo terminal means with run intervals only, not both interval types, and the caption omits the Monte Carlo series entirely.
- *Legacy scripts.* Four tracked scripts write the paper's figure basenames: `FOO_Single_Network.py`, `FOO_Dual_Network.py`, `FOO_Agent_Count.py`, and `flaws5.py`. The committed HEAD PNGs are legacy 20-run outputs. Because `\includegraphics` has no extension, a build from a clean clone falls back to them.
- *Origin of d.* The `FOO_Dual_Network.py` docstring (lines 22–23) chose d ≈ 0.19 by solving the false criterion λ/d ≈ p/(p+q) from R01. The rationale in the parameter table was written afterwards.
- *Usage text.* The `--interval` examples in the ci script's docstring are at its lines 25 and 29, not in its "opening" example.

**R12.**
- *Failure paths.* The check never exercises a model failure, a timeout, a context overflow, or the recorded stop reason.
- *Unanimity clause.* The clause about "unanimous false output" is attached to a scenario with *two disagreeing critics*, so it is vacuous. Split the check into three scenarios: persistent disagreement, unanimous convergence on a planted false answer, and a tampered log.
- *Harmonizer answers.* Harmonizer answers are critiqued every round (tex 1332, 1335–1336) but never revised (tex 1342), and the convergence test's operands are unspecified (tex 1346).
- *"Verified" wording.* Rescope "independently verified" to log integrity plus a recorded stop reason.

**R14.**
- *Tex 1848.* Its claims of "decentralized" records and logs "verifiable without central oversight" are never addressed. The implementation is centralized, with one shared salt.
- *Tex 2032.* The same paragraph states that each block contains "the agent identity," so the salt-anonymity claim is vacuous on the paragraph's own terms, not just unproven.
- *Completion check.* Add an explicit test that no claim remains that hashing or a shared salt anonymizes agents.
- *Locations.* Cross-reference tex 1377–1410, where the signature and key material that R14's evidence discusses actually lives.

**R15.**
- *Backward pass.* The claim at tex 1782–1783 contradicts the manuscript's own tex 182 ("a single forward pass per token"), and the completion check would not catch the sentence surviving.
- *Harmonizer calls.* C = A(1+2R) assumes one call per harmonizer. If several harmonizers produce one J in one call, the count is A + R(2A−H+1). The two readings coincide for the paper's H=1 configuration.
- *Θ(N² log N).* Even a proved O(log N)-round result needs a stated per-round cost to yield this bound.

**R20.**
- *Completion check.* It verifies that boundary outputs are defined, not that they are correct.
- *Silent wrong answer.* At B_ε = 1 with d = 1 (for example a = .1, q = .05, ε = a/(a+1)), the code returns "unattainable," yet n = 2 attains the target exactly (f = 0.0909 = ε). A patch placed inside the existing `required_b < 1.0` branch would clear both exceptions and keep this error.
- *Named generator.* The manuscript-named `FOO_generate_plots.py` (lines 272–284) has the same crashes.
- *Floor formula.* Both scripts report the floor a/(a+1) regardless of d. At d = 0 the true limit is a/(a+q) = 0.60.
- *Build artifacts.* `FlawsOfOthers.bbl` and `.blg` predate the last `.tex` edit, so Biber did not rerun. That, not the log's timestamp, is why the existing log is not evidence of a clean build.

## Cross-cutting amendments

### Definitions that make RT1's criterion order-invariant

RT1's "truth dominance requires b > a" is correct for *every* one-round update order, but only if a and b are the effective whole-round transition probabilities at the point where output is measured. Under generate-then-review, A = a(1−b) and B = b. Under review-then-generate, A = a and B = b(1−a). In each case f* = A/(A+B), and truth dominance holds iff A < B. RT1 never states this definition, and its branch formulas (a = p+λ; b = 1−(1−q)(1−d)^(n−1)) hold only for the synchronous order. Add the one-line definition to R01 and the replacement abstract.

The order that matters for FOO depends on which object is delivered, which is decided under R12. At b = 1 the floors differ: 6.98% synchronous, 0 for generate-then-review, and 7.5% for review-then-generate. Settle R12's deliverable definition before R06's model.

### Replacement language

**Abstract.** Insert "expected." Define a and b as effective whole-round probabilities (or rates). Replace "identifies the effects of sensitivity, false positives, repair success, and shared blind spots" with "expresses residual invalidity in terms of." As written, "identifies" asserts the statistical identifiability that R09 says is absent.

**Agent-count interpretation.** Add: "It also assumes no common-mode blind spot and no errors introduced by review, repair, or harmonization; with per-peer introduced error h, the target is unreachable once h ≥ εd/(1−ε)." Say "expected" in the Bernoulli sentence as well. State that d is a rate per stated time unit in one branch and a per-round probability in the other. State that "nine agents" means the focal generator plus eight peers.

**Logging claim.** Add: "Signatures bind records to keys; they do not establish completeness, since truncation requires no new signature, or independent origin when one party holds all keys." Also note that redaction is compatible only with anchoring hiding commitments, not plaintext hashes.

### Submission checklist

RT1's checklist has no bullet for R07, R18, or R19, and it covers R20's mathematical boundary repairs only through the domain bullet. State that the per-item completion checks remain binding and the checklist is only a summary. Add these bullets:

- Network, propagation, and prediction claims are limited to what the exogenous-rate two-state model derives, and every count has its own symbol.
- A single validity predicate defines both the KL invalid set and the state f, and no human–model identity claim remains without direct evidence.
- The contribution claim survives comparison with a documented search of prior work, and epithesis has one definition.
- The full bibliography matches primary records field by field, and no work renders twice.
- The log serialization is injective, and the checkpoint commits to every agent's head.

### Sequence and priority

- **R13 and R14.** Move R14's threat model into step 1 alongside R13. R13's completion check requires "an explicit adversary model," but step 5 is labeled "source support and terminology" and never mentions security.
- **R12 and R06.** Flag that R12's deliverable decision (step 3) determines which update order R06 (step 2) must model.
- **Priorities.** R02 at P0 is defensible, because FOO does reject claims through a specialist veto (tex 1307) and "repaired or rejected" (tex 1206–1207). But R05 is structurally identical: the theorem is correct and the prose drops a hypothesis. Given D3, R05 has a comparable claim to P0. R17 at P1 fits better once it is framed as an integrity issue (invented coauthors) than as a precision issue.

## Challenges that did not survive

These criticisms of RT1 were raised during the audit and then refuted by the skeptic pass. RT1 is correct on each point:

- **R01 / R06.** The claim that "a < b" and the suggested abstract become false under R06's re-derived update order is refuted if a and b are effective transition probabilities; see the definitions above.
- **R02 priority.** The argument that R02 should be P1 because FOO never rejects fails: the manuscript explicitly allows rejection and veto.
- **R05 criterion.** The claim that the hb < aΔb criterion misclassifies cases under generate-then-review is refuted. Applied to effective increments, as RT1 states it, the criterion is exact.
- **R08.** "Define a first in every theorem" is not redundant: `prop:n_agents` and `lem:cross_vs_single` do not define a.
- **R08 and overall assessment.** The claim that "preserve 0.60/0.2455/6.98%" silently relies on a convention is refuted: the manuscript declares the additive convention at tex 1462–1467, and RT1 cites it.
- **R09.** "Same sum ⇒ same dynamics" is explicitly premised on a = p+λ and is exact under that premise.
- **R11.** The claim that RT1 understated a flat contradiction with the repository is refuted, since the `CGSI25` tag holds an engine. RT1's versioning diagnosis was right; D5 adds what it did not establish.
- **R13.** The claim that the empty-log attack lies outside the pseudocode's domain fails: RT1 already scopes it to a transcription, and loading an empty log is realistic (tex 2081).
- **R14.** The claim that R14's threat model duplicates tex 1407–1410 is refuted: those lines require a threat model but do not supply one.
- **R18.** The symbol C does not collide, because the manuscript already uses plain C for its validity predicate. "Stratify by error category" is actionable on the manuscript's estimation plans.
- **R19.** "Define epithesis" is not redundant, because the manuscript has two inconsistent definitions.
- **Manuscript line 132.** The claim that JSONSchemaBench is mischaracterized is refuted: the paper body documents schema-invalid outputs despite constrained decoding.
- **`.latexmkrc`.** The claim that the working-tree edit broke the build is unsupported: Biber still ran. RT1's point that the configuration comments are misleading stands.

## Recommended use of this review

1. Apply RT1 as written for R01, R03, R06, R08–R10, R12, R14, R15, and R20, together with the minor amendments above.
2. Replace RT1's remediation text with the amended versions in D1 (R02), D2 (R04), D3 (R05), D8 (R17), and D9 (R18). In these cases, RT1 followed literally leaves a false or unsupported statement in the paper or the bibliography.
3. Strengthen the completion checks and locations per D4 (R07), D6 (R13), D7 (R16), and D10 (R19), and the evidence per D5 (R11).
4. Use the amended replacement language, checklist, and sequence before rewriting the abstract and conclusion. That rewrite remains the final step, as RT1 recommends.
