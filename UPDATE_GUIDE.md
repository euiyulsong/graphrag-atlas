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
