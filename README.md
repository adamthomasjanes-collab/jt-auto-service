# J&T Auto Service of BG

Marketing website for J&T Auto Service of BG in Bowling Green, Ohio.

## Deploying

This is a static site. Netlify publishes the repository root using `netlify.toml`.

The repository intentionally remains in private-preview SEO mode while the team
tests the site: pages are `noindex` and `robots.txt` blocks crawlers. Once the
real production domain is approved, use the controlled launch utility:

```powershell
python tools/prepare-seo-launch.py --domain https://jtautobg.com --commit
```

Review the resulting diff before deploying that launch switch.

## Quality checks

```powershell
python qa-prelaunch.py
python qa-navigation.py
python qa-title-system.py
```

## Notes

- Calls are the primary conversion path. There is no online service-request form.
- `assets/image-audit/` contains the approved concept imagery used by the site.
- Historical ZIP exports and archived snapshots stay out of this repository.
