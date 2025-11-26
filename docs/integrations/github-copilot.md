# GitHub Copilot Integration

⚠️ **Why the official documentation doesn't work:** The official LiteLLM documentation for GitHub Copilot integration ([link](https://docs.litellm.ai/docs/tutorials/github_copilot_integration)) is incomplete. GitHub Copilot requires:
- Special `/v1/engines` endpoint for model discovery
- Complex authentication with temporary tokens (in headers or URL-encoded query parameters)
- Automatic URL rewriting (`/v1/engines/...` → `/v1/chat/completions`)
- Custom proxy service to handle these requirements

**Status:** Experimental. Requires custom Python proxy service and Nginx routing. Implementation involves:
- Custom Python proxy service to handle `/v1/engines` endpoint
- Nginx routing with token validation (supports both header and URL-encoded query parameters)
- Automatic URL rewriting from `/v1/engines/...` to `/v1/chat/completions`
- Model creation scripts for Copilot compatibility

💡 **Recommended alternative:** Use [Continue.dev](continue-dev.md) for VS Code instead. It's an open-source AI coding assistant that works seamlessly with AI Gateway through the Continue.dev Integration script. Continue.dev provides better control, customization, and doesn't require complex proxy setups.

