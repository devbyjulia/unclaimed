# 🎓 Unclaimed

Unclaimed helps students find "hidden" scholarship money: local, school-specific
and niche awards that are easy to miss on the big search sites. It matches a
student's profile against real scholarships in Palm Beach County, Florida, and
shows which ones they qualify for, which they might qualify for, and what
information is needed for a determination.


## 🧩 Current State

This is an early prototype. It has:

- **Data models** for scholarships and students ([models.py](models.py))
- **A matcher** that checks eligibility and ranks results ([matching.py](matching.py))
- **Demo data**: 4 real local scholarships and 7 fictional student profiles ([data/](data/))
- **A command-line script** that prints matches for each profile ([run_matches.py](run_matches.py))

There is no user interface, database or web app yet. The models assume clean,
complete data (a best-case scenario) and are deliberately kept simple.


## 🛠️ Setup

Requires Python 3.10 or newer (developed on 3.13). The only dependency is
[Pydantic](https://docs.pydantic.dev/) v2.

Windows (PowerShell):

```
python -m venv .venv
.venv\Scripts\python -m pip install pydantic
```

macOS / Linux:

```
python3 -m venv .venv
.venv/bin/python -m pip install pydantic
```


## 🖥️ Running the Matcher

From the project root:

```
.venv\Scripts\python run_matches.py          # all profiles
.venv\Scripts\python run_matches.py jordan   # only profiles whose name contains "jordan"
```

(On macOS / Linux, use `.venv/bin/python`.)

Example output:

```
4 scholarships loaded

Maya Torres: senior (high school), Palm Beach State College, GPA 3.7
  [FULL   ] Presidential Honors College Scholarship  |  $6,000/yr x 2 yrs  |  deadline not listed

Jordan Ellis: senior (high school), school not chosen, GPA 3.6
  [PARTIAL] Presidential Honors College Scholarship  |  $6,000/yr x 2 yrs  |  deadline not listed
            missing: institution, credits_per_term
  fill in to check more: institution (1), credits_per_term (1)

Marcus Reed: senior (high school), Palm Beach State College, GPA 3.4
  (no matches)
```

To try a "what if," edit a profile in [data/profiles.json](data/profiles.json)
and run the script again. Nothing is stored between runs.

Both data files are validated when they load. If an entry has a mistake, the
script stops and names the field that's wrong.


## ❓ How Matching Works

Each scholarship gets one of three results for a student:

| Result | Meaning |
|---|---|
| **Full** | The student meets every requirement the matcher checks. |
| **Partial** | Nothing rules it out, but the profile is missing something a requirement needs (for example, the student hasn't chosen a college). The output lists the missing fields. |
| **Excluded** | The student fails a requirement. It isn't shown. |

Rules:

- **A blank profile field never excludes.** It produces a partial match instead,
  so students still deciding (college, major, credits) still see their options.
- **FAFSA never excludes.** A student who hasn't filed yet gets a partial match,
  since they can still file.
- **Free-text requirements aren't checked.** Anything in a scholarship's
  `other_requirements` (essays, residency, first-generation status, etc.) is for
  the student to confirm.
- **Text comparisons ignore capitalization but not spelling.** School names in
  scholarships must match the names used in profiles exactly.

Results are ranked: full matches before partial, then by closest deadline,
then scholarships with no deadline listed. Ties are broken by total award value.
Scholarships whose deadline has passed are dropped.


## 👥 Demo Profiles

Each profile is built to show a different matcher path:

| Profile | Shows |
|---|---|
| Maya Torres | Full match (Presidential Honors, Palm Beach State College) |
| Jordan Ellis | Partial match: no school or credit load chosen yet |
| Marcus Reed | Excluded: GPA just under the cutoff |
| Sam Nguyen | Excluded: part-time and the wrong education level |
| Priya Shah | Full match (Kevin and Michelle Clark, FAU nursing) |
| Elena Brooks | Full match (Student Success Grant, South University), graduate student |
| Andre Baptiste | Full match (Lynn University Grant) |

## 📝 To Do
- [] Build web app in Streamlit
- [] Compile scholarship database & discovery system

## ⚠️ Known Limitations

- **One credit minimum per scholarship.** Scholarships with different minimums
  for undergraduate and graduate students store the lower one; the other goes
  in `other_requirements`.
- **Award ranges use the low end** for ranking, so a variable award may rank
  lower than what a particular student would receive.
- **Tags aren't validated** against the approved list. A typo will load fine
  but drop the scholarship from tag filters.
- **No excluded fields of study.** Programs a scholarship excludes are listed
  in `other_requirements` and aren't checked.
