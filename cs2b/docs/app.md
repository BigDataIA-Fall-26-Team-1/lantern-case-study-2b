# The app (read-only UI)

**Live:** http://13.184.184.213:8501 (EC2 `t3.small`, Ubuntu 24.04, `us-east-2`)

A read-only Streamlit app over the pipeline's outputs. It never runs the pipeline and needs no AWS keys.

| Page | Reads |
|---|---|
| Home | `reports/coverage.json`, `reports/cleaning_log.csv` |
| Coverage | `reports/coverage.csv` (filter admitted / excluded / triage category) |
| Triage | `reports/triage.md`, one `### NAME (adsh, form)` section per excluded filing (89 of 89) |
| Panel | `outputs/panel/holdings.parquet` (DVC), with an EDGAR link per filing |
| Spot checks | `reports/spot_check.csv`, `reports/dependency_check.md` |
| Reports | the Markdown deliverables in `reports/` and `docs/` |

Code: `cs2b/app/` (`Home.py`, `data.py`, `pages/`). Requirements: `cs2b/app/requirements-app.txt`
(pandas 3.1.0, pyarrow 26.0.0 and numpy as in `cs2b/requirements.txt`; streamlit 1.66.1), in its own venv,
so the pipeline's environment is unchanged. No DVC stage depends on `app/`.

## Run locally

Windows (PowerShell), from `cs2b/`, after `dvc pull` in the pipeline venv:

```powershell
python -m venv .venv-app; .\.venv-app\Scripts\Activate.ps1
pip install -r app/requirements-app.txt
streamlit run app/Home.py          # http://localhost:8501
```

Linux / macOS: the same with `python3 -m venv .venv-app && source .venv-app/bin/activate`.

## How it is deployed

- **Instance:** `lantern2b-ui`, `t3.small`, Ubuntu 24.04, 16 GB gp3. Security group `lantern2b-ui-sg`:
  SSH 22 from one IP only, TCP 8501 from anywhere. Key pair `.pem` kept outside the repo.
- **Code on the server, without Git credentials:** the organization disables deploy keys, so the server
  gets a copy of the committed `cs2b/` folder made with `git archive`, plus the panel, both sent with `scp`.
  No GitHub or AWS credentials are stored on the server.
- **Panel provenance:** on the server, `md5sum outputs/panel/holdings.parquet` gives
  `5402d3dfc237dd3189226298a4590c02`, the MD5 recorded for it in `dvc.lock`.
- **Service:** `/etc/systemd/system/lantern2b-ui.service` runs
  `streamlit run app/Home.py --server.port 8501 --server.address 0.0.0.0 --server.headless true`
  as user `ubuntu`, from `~/lantern2b/cs2b`, with `Restart=always`. It starts on boot.

## Update after a merge

Laptop (PowerShell), from the repository root:

```powershell
git switch main; git pull --ff-only
git archive --format=tar.gz -o "$HOME\lantern2b-app.tar.gz" main cs2b
scp -i "$HOME\.ssh\lantern2b-key.pem" "$HOME\lantern2b-app.tar.gz" ubuntu@13.184.184.213:~/
```

Server:

```bash
tar -xzf ~/lantern2b-app.tar.gz -C ~/lantern2b
sudo systemctl restart lantern2b-ui
curl -s http://localhost:8501/_stcore/health; echo     # ok
```

If the panel's MD5 in `dvc.lock` changed, also copy the new `cs2b/outputs/panel/holdings.parquet` with `scp`
into `~/lantern2b/cs2b/outputs/panel/` and check `md5sum` again.

## Notes

- The public IP changes if the instance is stopped and started. Update this file and the README if it does.
- Cost: about $0.02 per hour. After grades are returned: terminate the instance and delete the key pair
  and the security group.

**AI use:** the app, this file and the deployment steps were drafted with an AI assistant, and reviewed,
run and checked against the pipeline's outputs by the team.