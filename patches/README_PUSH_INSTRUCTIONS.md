# Pushing the ASEAN Macro Dashboard fixes to GitHub

The local `/workspace` repo has **no git remote configured**, so `git push`
cannot run from here. All fixes are committed on branch
`qwen-code-27ce282f-ddca-464f-afaa-c05d6a4ef8de` and ready to transfer.

## What's included (vs `master`)

| File | Change |
|---|---|
| `asean_macro_dashboard.py` | Timeout/retry fix, 'ME' frequency fix, PeriodIndex fix for CA forecast ("No supported index"), daily→monthly FX resample, keterangan labels, GDP rename |
| `tests/test_asean_macro_dashboard.py` | 17 unit tests (all passing) |
| `pytest.ini` | Test config |
| `README.md` | Updated forecasting docs |
| `.gitignore` | Excludes `__pycache__`, committed pyc artifacts removed |

## Option A — Apply patch series in your local clone of the GitHub repo

```bash
git clone https://github.com/<your-user>/other-projects.git
cd other-projects
git am /path/to/patches/0001-*.patch /path/to/patches/0002-*.patch ... 0009-*.patch
# or simply: git am /path/to/patches/*.patch
git push origin main   # (or master, matching your default branch)
```

If `git am` conflicts on the snapshot commits, you can skip them — the
essential ones are 0001 (timeouts/FX), 0003 (pandas deprecation),
0004 (index fix), 0006 (keterangan), 0007 (rename), 0009 (cleanup).

## Option B — Add a remote here (if credentials/network are available)

```bash
cd /workspace
git remote add origin https://github.com/<your-user>/other-projects.git
git push -u origin qwen-code-27ce282f-ddca-464f-afaa-c05d6a4ef8de
```

Then open a PR (or merge into your default branch) on GitHub. Streamlit
Cloud will redeploy automatically since it tracks the repo.

## Option C — Copy files manually

Copy these files over the versions in your GitHub repo and commit:
- `asean_macro_dashboard.py`
- `tests/test_asean_macro_dashboard.py`
- `pytest.ini`
- `README.md`
- `.gitignore`
