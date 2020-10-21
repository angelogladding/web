"""

"""

import json
from importlib import import_module
import traceback

import kv
import gevent.queue

# TODO from .agent import Browser
from .framework import get_app_db

queue = gevent.queue.PriorityQueue()
worker_count = 20


def handle_job(job_identifier):  # , browser):
    """
    handle a freshly dequeued job

    """
    # TODO handle retries
    app_name, _, job_run_id = job_identifier.partition(":")
    db = get_app_db(app_name)
    job = db.select("job_runs AS r", what="s.rowid, *",
                    join="""job_signatures AS s
                            ON s.rowid = r.job_signature_id""",
                    where="r.job_id = ?", vals=[job_run_id])[0]
    _module = job["module"]
    _object = job["object"]
    _args = json.loads(job["args"])
    _kwargs = json.loads(job["kwargs"])
    print(f"{app_name}/{_module}:{_object}",
          *(_args + list(f"{k}={v}" for k, v in _kwargs.items())),
          sep="\n  ", flush=True)
    db.update("job_runs", where="job_id = ?", vals=[job_run_id],
              what="started = STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')")
    status = 0
    try:
        output = getattr(import_module(_module), _object)(db, *_args,
                                                          **_kwargs)
    except Exception as err:
        status = 1
        output = str(err)
        traceback.print_exc()
    db.update("job_runs", vals=[status, output, job_run_id],
              what="""finished = STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'),
                      status = ?, output = ?""", where="job_id = ?")
    run = db.select("job_runs", where="job_id = ?", vals=[job_run_id])[0]
    st, rt = run["started"] - run["created"], run["finished"] - run["started"]
    db.update("job_runs", what="start_time = ?, run_time = ?",
              where="job_id = ?", vals=[f"{st.seconds}.{st.microseconds}",
                                        f"{rt.seconds}.{rt.microseconds}",
                                        job_run_id])


def run_queue(redis_socket, worker_count=20):
    """"""
    kvdb = kv.db("web", ":", {"jobqueue": "list"}, socket=redis_socket)

    def run_worker():
        for job in kvdb["jobqueue"].keep_popping():
            handle_job(job)

    for _ in range(worker_count):
        gevent.spawn(run_worker)


# TODO @main.register()
class JobQueue:

    """manage the job queue"""

    def run(self, stdin, log):
        run_queue()
