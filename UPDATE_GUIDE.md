# Ontology & GraphRAG workshop — 2026-10-26

- Six executable ontology lessons separate schema, facts, constraints and the selected SELECT query.
- The server runs RDFLib, OWL RL and SHACL Core. It returns before/after query rows, main inference premises, validation focus/path, domain graph edges and linked source documents.
- The explanation of inference premises is an educational trace, not a complete proof tree of the OWL RL engine.
- Three fixed SPARQL SELECT queries are available; arbitrary remote queries, imports and executable SHACL extensions are not supported.
- The 60-slide downloadable PPTX and browser presentation cover ontology concepts, six labs, 13 research entries, examples, limitations and indexing/retrieval diagrams.
- All GraphRAG retrieval variants in the existing engine remain educational approximations. This release improves the ontology workshop and explanations, without claiming faithful reproduction of the original research algorithms.
- Ontology lessons do not call OpenAI. The existing live retrieval mode continues reading its key only from server environment variables.

Validation: 20 Python tests and a jsdom integration test cover lessons, ontology endpoints, graph/evidence presentation, error cases, and presentation navigation. PPTX package/layout/import checks pass. All slide previews were inspected. No native PowerPoint or authenticated production UI test is claimed.

References: https://wikidocs.net/book/19432 and https://wikidocs.net/book/19813 for learning context, W3C RDF/OWL/SHACL/SPARQL standards, and paper/repository URLs in research.json and slide speaker notes.

## Presentation wording revision

All 60 slides now use plain Korean labels. Speaker notes walk the visible rows or diagram columns, explain terminology with the logistics example, identify implementation limits, and transition to the next slide. The browser presentation uses the same script.

## Connected presentation revision

The 60-slide presentation now groups each method as concept, logistics question, and process diagram. Summary/group methods are adjacent, PPR precedes HippoRAG, and the former appendix diagrams are integrated with their examples. Each slide includes a visible narrative bridge and aligned conversational notes. Web presentation and downloadable PPTX use the same order and script.

## Guided lab instructions

Both lab screens now include four-step audience instructions and expandable presenter cues. Ontology instructions follow the selected lesson. Setup controls prepare a no-API ontology comparison and an offline HippoRAG/baseline exercise without running queries automatically. GraphRAG sample names are explained by their roles.

## Document-link teaching example

Slide 13 now shows the actual describes and text facts, the inferred system results, and the document lookup steps. The notes clarify the document-to-system direction, manually authored links, and Python evidence lookup after SPARQL.

## Ontology focus and error explanations

Each lesson now distinguishes comparison exercises from deliberately broken data. Schema, facts and SHACL show selected lines from the current input with token highlights and line numbers. Full editors are expandable. The inference setting is prominent near the lesson goal. Result summaries use actual query rows and SHACL violations, and warn when input has changed since the last run.

## Search-object visualization

Retrieval results now expose a typed graph containing the actual selected summaries, atoms, documents, uploaded-image sources and entity focus, with stored provenance links. Final evidence and computational focus are distinguished. Nodes open full source text. PPR frames update the graph brightness and focus using actual iteration scores; final-evidence outlines stay fixed. Entity/document ID collisions are isolated by typed IDs. Unavailable image content and educational approximations remain explicit.
