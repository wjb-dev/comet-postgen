# cookiecutter-postgen

Shared **post-generation logic** used by multiple Cookiecutter templates
(Go/C++ micro-services, etc.).  Installable via `pip` so templates stay lean.

```bash
    pip install cookiecutter-postgen
```
Inside a Cookiecutter hook:
```python
from haraka import main, PostGenConfig
from pathlib import Path


if __name__ == "__main__":
    
    cfg = PostGenConfig(
        variant        = "{{ cookiecutter['__variant']  }}",
        project_slug   = "{{ cookiecutter.project_slug }}",
        author_gh      = "{{ cookiecutter['__author_gh']  }}",
        description    = "{{ cookiecutter.description }}",
        project_dir    = Path.cwd(),
        use_git        = "{{ cookiecutter['__use_git']  }}",
        confirm_remote = "{{ cookiecutter['__confirm_remote']  }}",
    )
    
    main(cfg) 
```
MIT-licensed.

---

## 3. Commit

```bash
    git add pyproject.toml README.md
    git commit -m "feat: make package installable (pyproject.toml, readme)"
    git push
```
