# Django Template Scripts - Quick Reference

## 🚀 Quick Commands

```bash
# Fix all templates (run once)
python fix_django_templates.py

# Validate templates (run regularly)
python validate_django_templates.py
```

## 📦 What's Included

| File | Purpose | When to Use |
|------|---------|-------------|
| `fix_django_templates.py` | Automatically fixes template errors | Once to clean up existing issues |
| `validate_django_templates.py` | Checks templates without modifying | Before commits, in CI/CD |
| `TEMPLATE_FIXING_GUIDE.md` | Detailed documentation | Reference for usage & integration |
| `TEMPLATE_FIX_SUMMARY.md` | Project-specific results | See what was fixed in this project |

## ✅ Current Status

**All 430 templates validated - 0 errors, 0 warnings!**

## 🔍 What Gets Fixed

- ✅ Orphaned `{% endblock %}` tags
- ✅ Block names in endblocks (converts to `{% endblock %}`)
- ✅ Missing `{% load static %}` tags
- ✅ Template tag spacing issues
- ✅ Duplicate `{% extends %}` tags
- ✅ Duplicate `{% load %}` tags

## 📖 Documentation

- **Quick Start**: This file
- **Detailed Guide**: [TEMPLATE_FIXING_GUIDE.md](TEMPLATE_FIXING_GUIDE.md)
- **Project Results**: [TEMPLATE_FIX_SUMMARY.md](TEMPLATE_FIX_SUMMARY.md)

## 🎯 Integration Examples

### Pre-Commit Hook
```bash
#!/bin/bash
python validate_django_templates.py || exit 1
```

### GitHub Actions
```yaml
- name: Validate Templates
  run: python validate_django_templates.py
```

### VS Code Task
```json
{
  "label": "Validate Templates",
  "type": "shell",
  "command": "python validate_django_templates.py"
}
```

## 💡 Best Practices

1. **Fix Once**: Run fixer script once to clean up
2. **Validate Often**: Add validator to pre-commit or CI/CD
3. **Review Changes**: Use `git diff` after running fixer
4. **Keep Scripts**: Maintain both scripts for ongoing use

## 🆘 Need Help?

- Check error message and line number
- Review [TEMPLATE_FIXING_GUIDE.md](TEMPLATE_FIXING_GUIDE.md)
- Consult Django docs: https://docs.djangoproject.com/en/stable/ref/templates/

---

**Quick Tip**: Run `python validate_django_templates.py` before deploying!

