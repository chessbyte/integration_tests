# -*- coding: utf-8 -*-
import pytest
import yaml

from cfme.fixtures import pytest_selenium as sel
from cfme.intelligence.reports.dashboards import Dashboard
from cfme.intelligence.reports.reports import CustomReport
from cfme.intelligence.reports.schedules import Schedule
from cfme.intelligence.reports.widgets import ChartWidget, MenuWidget, ReportWidget, RSSFeedWidget
from utils.path import data_path
from utils.randomness import generate_random_string
from utils.update import update


report_crud_dir = data_path.join("reports_crud")
schedules_crud_dir = data_path.join("schedules_crud")


def crud_files_reports():
    result = []
    if not report_crud_dir.exists():
        report_crud_dir.mkdir()
    for file in report_crud_dir.listdir():
        if file.isfile() and file.basename.endswith(".yaml"):
            result.append(file.basename)
    return result


def crud_files_schedules():
    result = []
    if not schedules_crud_dir.exists():
        schedules_crud_dir.mkdir()
    for file in schedules_crud_dir.listdir():
        if file.isfile() and file.basename.endswith(".yaml"):
            result.append(file.basename)
    return result


@pytest.fixture(params=crud_files_reports())
def custom_report(request):
    with report_crud_dir.join(request.param).open(mode="r") as rep_yaml:
        return CustomReport(**yaml.load(rep_yaml))


@pytest.fixture(params=crud_files_schedules())
def schedule(request):
    with schedules_crud_dir.join(request.param).open(mode="r") as rep_yaml:
        data = yaml.load(rep_yaml)
        name = data.pop("name")
        description = data.pop("description")
        filter = data.pop("filter")
        return Schedule(name, description, filter, **data)


def test_custom_report_crud(custom_report):
    custom_report.create()
    with update(custom_report):
        custom_report.title += generate_random_string()
    custom_report.queue(wait_for_finish=True)
    for report in custom_report.get_saved_reports():
        report.data  # touch the results
    custom_report.delete()


def test_schedule_crud(schedule):
    schedule.create()
    with update(schedule):
        schedule.description = "badger badger badger"
    schedule.queue(wait_for_finish=True)
    schedule.delete()


def test_menuwidget_crud():
    w = MenuWidget(
        generate_random_string(),
        description=generate_random_string(),
        active=True,
        shortcuts={
            "Services / Catalogs": generate_random_string(),
            "Clouds / Providers": generate_random_string(),
        },
        visibility=["<By Role>", sel.ByText("EvmRole-administrator")]
    )
    w.create()
    with update(w):
        w.active = False
    w.delete()


def test_reportwidget_crud():
    w = ReportWidget(
        generate_random_string(),
        description=generate_random_string(),
        active=True,
        filter=["Events", "Operations", "Operations VMs Powered On/Off for Last Week"],
        columns=["VM Name", "Message"],
        rows="10",
        timer={"run": "Hourly", "hours": "Hour"},
        visibility=["<By Role>", sel.ByText("EvmRole-administrator")]
    )
    w.create()
    with update(w):
        w.active = False
    w.delete()


def test_chartwidget_crud():
    w = ChartWidget(
        generate_random_string(),
        description=generate_random_string(),
        active=True,
        filter="Configuration Management/Virtual Machines/Vendor and Guest OS",
        timer={"run": "Hourly", "hours": "Hour"},
        visibility=["<By Role>", sel.ByText("EvmRole-administrator")]
    )
    w.create()
    with update(w):
        w.active = False
    w.delete()


def test_rssfeedwidget_crud():
    w = RSSFeedWidget(
        generate_random_string(),
        description=generate_random_string(),
        active=True,
        type="Internal",
        feed="Administrative Events",
        rows="8",
        visibility=["<By Role>", sel.ByText("EvmRole-administrator")]
    )
    w.create()
    # Basic update
    with update(w):
        w.active = False
    # Different feed type
    with update(w):
        w.type = "External"
        w.external = "SlashDot"
    # and custom address
    with update(w):
        w.type = "External"
        w.external = "http://rss.example.com/"
    w.delete()


def test_dashboard_crud():
    d = Dashboard(
        generate_random_string(),
        "EvmGroup-administrator",
        generate_random_string(),
        locked=False,
        widgets=["Top CPU Consumers (weekly)", "Vendor and Guest OS Chart"]
    )
    d.create()
    with update(d):
        d.locked = True
    with update(d):
        d.locked = False
    with update(d):
        d.widgets = "Top Storage Consumers"
    d.delete()
