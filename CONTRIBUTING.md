# Contributing to AI Gateway

Thank you for your interest in the project! We welcome any contributions.

## How to Contribute

### Bug Reports

If you found a bug:
1. Check if it hasn't already been reported in Issues
2. Create a new Issue with description:
   - What happened
   - What was expected
   - Steps to reproduce
   - Python, Docker, OS versions

### Feature Suggestions

1. Create an Issue with your suggestion
2. Discuss the idea before starting work
3. After approval, create a Pull Request

### Pull Requests

1. **Fork** the repository
2. Create a **branch** for your feature (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. Open a **Pull Request**

### Code Standards

- Follow existing code style
- Use type hints for all functions
- Add docstrings in Google format
- Use structured logging instead of `print()`
- Handle exceptions specifically (don't use `except:` without specifying type)

### Project Structure

```
src/
├── core/           # Domain logic, exceptions, configuration
├── infrastructure/ # External dependencies (files, Docker, logging)
└── application/    # Business logic and services
```

### Testing

Before submitting PR:
- Make sure code works on your system
- Check that there are no linter errors
- Test on different platforms (Linux, macOS, Windows) if possible

### Questions?

Create an Issue with a question or discussion.

Thank you for your contribution! 🎉
