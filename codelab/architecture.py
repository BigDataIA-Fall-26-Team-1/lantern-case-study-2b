"""Architecture diagram for the Case Study 2B Codelab.

Run:  python architecture.py   ->  architecture.png (in the folder you run it from)
Needs Graphviz (brew install graphviz) and the `diagrams` package (pip install diagrams).
"""
from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.storage import S3
from diagrams.generic.storage import Storage
from diagrams.onprem.client import Users
from diagrams.onprem.vcs import Github
from diagrams.programming.language import Python

graph = {"fontsize": "20", "pad": "0.4", "nodesep": "0.6", "ranksep": "0.9"}
node = {"fontsize": "12"}
pad = {"margin": "30"}

with Diagram("Project LANTERN 2B: a reconciled BDC holdings panel", filename="codelab/img/architecture",
             outformat="png", show=False, direction="LR", graph_attr=graph, node_attr=node):
    sec = Storage("SEC BDC data sets\n2026_01, 2026_02, 2026_03")

    with Cluster("dvc repro (dvc.yaml / dvc.lock)", graph_attr=pad):
        acquire = Python("acquire\nverify manifest\nand merged release\nscripts/acquire.py")
        parse = Python("parse\nmap by XBRL tag\nsplit periods\nscripts/parse.py")
        clean = Python("clean\ncoalesce + 7 TEAM_RULES\nwrites cleaning_log.csv\nscripts/clean.py")
        reconcile = Python("reconcile\nvs filed total\n(1% tolerance)\nscripts/p3a_reconcile.py")
        report = Python("report\ncoverage + triage\nevidence: p3b, p3c, p3d\nscripts/p3e_triage.py")
        acquire >> parse >> clean >> reconcile >> report

    with Cluster("Outputs", graph_attr=pad):
        reports = Storage("reports/\ncoverage, triage")
        panel = Storage("panel\n82 of 171 filings\n38.0% of filed fair value")

    # Declared in top-to-bottom order of the right-hand column: GitHub, app, then the remote,
    # so the dvc push arrow from the panel stays short and crosses nothing.
    repo = Github("GitHub repo\ncode + reports\n+ Codelab (Pages)")
    app = EC2("Streamlit app\n(EC2)")
    analyst = Users("credit team")
    with Cluster("DVC remote (public-read S3, us-east-2)", graph_attr=pad):
        remote = S3("raw release + outputs\n(dvc pull, no keys)")

    sec >> Edge(label="3 monthly ZIPs\nmerged to 2026q1") >> acquire
    report >> reports
    reconcile >> panel
    reports >> Edge(style="dashed") >> repo
    [reports, panel] >> app >> analyst
    panel >> Edge(style="dashed", label="dvc push") >> remote
