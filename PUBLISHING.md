# Prepare a public GitHub repository

The public repository is `Pablos249/HA_Neo_Heat`, maintained under the public
GitHub alias `@Pablos249`.

1. Build the public export:

   ```sh
   python scripts/package_release.py --repository Pablos249/HA_Neo_Heat --maintainer Pablos249
   ```

2. Extract `dist/neoheat-public.zip` into a **new, empty** directory. Upload only
   its contents to GitHub. The builder replaces repository metadata in the
   export; it does not upload anything or create commits.
3. Run the GitHub tests, test installation in HA, then optionally tag `v0.1.0`.
4. Share the repository URL for installation as a HACS custom repository.

Without arguments the builder produces a privacy-filtered archive using the
repository metadata already stored in `manifest.json`.
Do not upload the whole research workspace. `.gitignore` is a second line of
defense; it cannot remove private files that have already been committed.

The GitHub alias identifies the hosting account. Configure Git author identity
and a private noreply email separately before committing. No real name is
needed in this project's license or README.

The integration has not been submitted to HACS's default directory. The layout
follows https://www.hacs.xyz/docs/publish/integration/ and uses a generic local
icon, not a manufacturer's logo. Live HA validation remains a release gate.
