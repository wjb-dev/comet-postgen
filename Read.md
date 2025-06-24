# cookiecutter-postgen

Shared **post-generation logic** used by multiple Cookiecutter templates
(Go/C++ micro-services, etc.).  Installable via `pip` so templates stay lean.

```bash
    pip install cookiecutter-postgen
```
Inside a Cookiecutter hook:
```python
from post_gen import main
main()
```
MIT-licensed.

---

## 3. Commit

```bash
    git add pyproject.toml README.md
    git commit -m "feat: make package installable (pyproject.toml, readme)"
    git push
```
