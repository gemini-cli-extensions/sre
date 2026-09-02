# Workspace Guidelines: Public Resources Mind Map

Whenever a new public asset (repository, article, blog post, codelab, etc.) is added to the SRE Extension ecosystem, the public resources mind map must be updated.

## Diagram Rules & Taxonomy

1. **Star Topology**:
   - The **🐙 SRE Extension** (`sre_extension`) node acts as the central hub.
   - All other nodes must have a link from the SRE Extension to them (and/or vice-versa if they refer back to it).

2. **Three Distinct Types**:
   - **🐙 Code (Repositories)**:
     - Graphviz Style: Rounded box, dark blue color (`shape=box, style="filled,rounded", color="#1a73e8", fillcolor="#1a73e8", fontcolor=white`).
     - Label format: Node title with emoji, and the repo path (e.g. `user/repo`) in a `<font face="Courier">` tag.
     - Hyperlink: Must include a `URL` attribute pointing to the GitHub repository.
   - **📝 Articles & Docs**:
     - Graphviz Style: Note shape, green color (`shape=note, style="filled", color="#34a853", fillcolor="#34a853", fontcolor=white`).
     - Label format: Title with emoji, and path/domain in a `<font face="Courier">` tag.
     - Hyperlink: Must include a `URL` attribute pointing to the article.
   - **🎓 Codelabs & Tutorials**:
     - Graphviz Style: Component shape, red/coral color (`shape=component, style="filled", color="#ea4335", fillcolor="#ea4335", fontcolor=white`).
     - Label format: Title with emoji, and domain in a `<font face="Courier">` tag.
     - Hyperlink: Must include a `URL` attribute pointing to the codelab.

## Update Workflow

1. Update the Graphviz DOT definition in `docs/public-resources-map.dot`.
2. Compile the updated DOT file to a PNG image by running:
   ```bash
   dot -Tpng docs/public-resources-map.dot -o docs/public-resources-map.png
   ```
3. Update the Mermaid diagram and the description table in `docs/public-resources-map.md`. Ensure that the Mermaid classes align with the exact type colors:
   - Code: `#1a73e8`
   - Docs: `#34a853`
   - Codelab: `#ea4335`
4. Confirm `just test` passes to ensure all project metadata is intact.
