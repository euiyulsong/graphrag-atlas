# GraphRAG Atlas — public deployment

This application requires a running Python backend. Static hosting (GitHub Pages,
Netlify Drop, GitHub raw links) cannot execute `/api/index`, `/api/ask/stream`, or OpenAI generation.

## Render

1. Put this project directory into a Git repository you own.
2. Create a Render Blueprint using `render.yaml` in the project root, or create a Python Web Service.
3. Set `DEMO_PASSWORD` to a long random value. Never paste the password in public code.
4. Set `OPENAI_API_KEY` to a newly issued key in the Render secret environment settings.
5. Use the included service configuration. It reads the slide PPTX already bundled,
   so it does not require python-pptx during build.
6. Open the deployed `https://<name>.onrender.com` domain and authenticate with
   username `seminar` and your chosen password.
7. Run an Offline search and verify that the answer and evidence appear. Then run Live
   mode and verify streaming token deltas. Use `/api/health` to check health.

## Railway / any Docker host

Connect the repository to Railway or another Docker-capable host.
Use the included `Dockerfile` and `railway.json`; set the same two secrets.
Generate a publicly reachable domain in the hosting dashboard.

## Security

- Do **not** paste the API key into HTML, JS, or a GitHub repository.
- Revoke any previously exposed API key before deployment.
- Basic authentication is only a minimal seminar barrier. Set hard usage/spend caps,
  consider network restrictions, and turn the service off after the seminar.
- Indexes are in process memory and disappear after restart or instance rotation.
- Avoid multiple workers without adding shared session/index storage.
- For development, omit `DEMO_PASSWORD`. For public use, always set it.
